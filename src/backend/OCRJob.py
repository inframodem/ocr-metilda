import threading
from pathlib import Path
import time
import queue
import traceback


from .ModelInfo import ModelInfo
from .DeviceInfo import DeviceInfo
from .Exporter import Exporter
from .OCRs.OCREngines import OCREngine, ENGINES
from .DocumentLoader import DocumentLoader
from .Structs import DocumentResult, Page


class OCRJob(threading.Thread):
    """Loads the model (or reuses it), runs every file and posts progress messages to a queue for the window."""

    def __init__(self, files: list[Path], model: ModelInfo, device: DeviceInfo, exporter: Exporter,
                 events: "queue.Queue", engine_cache: dict):
        super().__init__(daemon=True)
        self.files, self.model, self.device, self.exporter = files, model, device, exporter
        self.events, self.engine_cache = events, engine_cache
        self.cancel = threading.Event()

    def _log(self, text: str):
        self.events.put(("log", text))

    def _engine(self) -> OCREngine:
        key = (str(self.model.path), self.device.kind)
        if key in self.engine_cache:
            self._log(f"Model '{self.model.name}' is already loaded")
            return self.engine_cache[key]
        self.events.put(("phase", "loading"))
        self._log(f"Loading model '{self.model.name}' on {self.device.description} ...")
        t0 = time.time()
        engine = ENGINES[self.model.model_type](self.model, self.device)
        engine.load(self._log)
        self.engine_cache.clear()                        # keep only one model in memory
        self.engine_cache[key] = engine
        self._log(f"Model loaded in {time.time() - t0:.1f}s")
        return engine

    def run(self):
        done_files, failed, cancelled = 0, 0, False
        t_start = time.time()
        try:
            self.events.put(("phase", "counting"))
            counts = {}
            for f in self.files:
                try:
                    counts[f] = DocumentLoader.page_count(f)
                except Exception as exc:
                    self._log(f"Cannot open {f.name}: {exc}")
            total = sum(counts.values())
            failed = len(self.files) - len(counts)
            if not counts:
                self._log("Nothing could be opened.")
                return
            engine = self._engine()
            self.events.put(("phase", "running"))
            self.events.put(("progress", 0, total))
            pages_done = 0
            for n, f in enumerate(counts, 1):
                if self.cancel.is_set():
                    cancelled = True
                    break
                t0 = time.time()
                pages: list[Page] = []
                try:
                    for pno, rgb in enumerate(DocumentLoader.pages(f), 1):
                        if self.cancel.is_set():
                            cancelled = True
                            break
                        lines = engine.recognize(rgb)
                        pages.append(Page(pno, rgb.shape[1], rgb.shape[0], lines))
                        pages_done += 1
                        self._log(f"[{n}/{len(counts)}] {f.name}: page {pno}/{counts[f]}, {len(lines)} lines")
                        self.events.put(("progress", pages_done, total))
                    if cancelled:
                        break
                    written = self.exporter.save(DocumentResult(f, pages, self.model, self.device, time.time() - t0))
                    done_files += 1
                    self._log(f"Finished {f.name} -> " + ", ".join(p.name for p in written))
                except Exception as exc:
                    failed += 1
                    pages_done += counts[f] - len(pages)
                    self.events.put(("progress", pages_done, total))
                    self._log(f"FAILED {f.name}: {exc}")
                    self._log(traceback.format_exc(limit=3).strip())
        except Exception as exc:
            self._log(f"ERROR: {exc}")
            self._log(traceback.format_exc(limit=4).strip())
        finally:
            summary = (f"{'Stopped' if cancelled else 'Done'}: {done_files} file(s) saved"
                       + (f", {failed} failed" if failed else "") + f" in {time.time() - t_start:.1f}s")
            self.events.put(("finished", summary))
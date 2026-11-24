"""Local OCR - a small desktop app around PaddleOCR (PyTorch / Transformers engine).

    python ocr_app.py

Folder layout, next to this file (or next to the executable):

    models/
        my-tuned-model/
            config.json        {"name": "My tuned model", "model_type": "paddleocr"}
            det/               detector (safetensors folder)
            rec/               recognizer (safetensors folder)

Needs: customtkinter pillow numpy pymupdf paddleocr transformers torch
"""
from __future__ import annotations

import queue

import sys
import threading

from pathlib import Path
from typing import Optional


from tkinter import filedialog

import customtkinter as ctk
from src.backend.ModelRegister import ModelRegistry
from src.backend.DeviceInfo import DeviceInfo, detect_device
from src.backend.OCRJob import OCRJob
from src.backend.Exporter import Exporter

from src.frontend.UIHelpers import set_enabled, GuideDialog
from src.frontend.ImportPanel import ImportPanel
from src.frontend.CenterPanel import CenterPanel
from src.frontend.ModelPanel import ModelPanel

APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
MODELS_DIR = APP_DIR / "models"


class App(ctk.CTk):
    def __init__(self, models_dir: Path = MODELS_DIR):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        super().__init__()
        self.title("Local OCR")
        self.geometry("1120x660")
        self.minsize(900, 520)

        self.registry = ModelRegistry(models_dir)
        self.events: queue.Queue = queue.Queue()
        self.engine_cache: dict = {}
        self.device: Optional[DeviceInfo] = None
        self.export_dir: Optional[str] = None
        self.job: Optional[OCRJob] = None
        self.dialogs: list[GuideDialog] = []

        self.grid_columnconfigure(0, weight=2, minsize=200, uniform="cols")
        self.grid_columnconfigure(1, weight=5, minsize=380, uniform="cols")
        self.grid_columnconfigure(2, weight=2, minsize=190, uniform="cols")
        self.grid_rowconfigure(0, weight=1)

        self.imports = ImportPanel(self, on_message=self.log)
        self.imports.grid(row=0, column=0, padx=(16, 8), pady=16, sticky="nsew")
        self.center = CenterPanel(self, on_choose_export=self.choose_export, on_run=self.start_run, on_stop=self.stop_run)
        self.center.grid(row=0, column=1, padx=8, pady=16, sticky="nsew")
        self.models = ModelPanel(self, on_refresh=self.refresh_models)
        self.models.grid(row=0, column=2, padx=(8, 16), pady=16, sticky="nsew")

        self.log(f"Models folder: {models_dir}")
        self.refresh_models(first=True)
        threading.Thread(target=self._detect_device, daemon=True).start()
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.after(100, self._poll)

    # ---- small things ----
    def log(self, text: str):
        self.center.append(text)

    def _detect_device(self):
        self.events.put(("device", detect_device()))

    def refresh_models(self, first: bool = False):
        found = self.registry.refresh()
        self.models.set_models(found)
        self.log(f"{'Found' if first else 'Model list refreshed:'} {len(found)} model(s)"
                 + (": " + ", ".join(m.label for m in found) if found else ""))
        for p in self.registry.problems:
            self.log(f"  skipped - {p}")

    def choose_export(self):
        folder = filedialog.askdirectory(title="Choose where to save the results")
        if folder:
            self.export_dir = folder
            self.center.set_export(folder)
            self.log(f"Export location: {folder}")

    # ---- running ----
    def stop_run(self):
        if self.job and self.job.is_alive():
            self.job.cancel.set()
            self.log("Stopping after the current page ...")
            set_enabled(self.center.stop_button, False)

    def _problems(self) -> list[tuple[str, str]]:
        out = []
        if not self.imports.files:
            out.append(("No files to process", "Use the import button to select files to process"))
        if not self.export_dir:
            out.append(("No export path", "Use the export button to chose where to export files"))
        if self.models.selected is None:
            out.append(("No model Selected", "Use the drop down to select which OCR model to use"))
        if not (self.center.want_txt or self.center.want_json):
            out.append(("No export format", "Tick plain text, full details, or both"))
        return out

    def start_run(self):
        if self.job and self.job.is_alive():            # a second click can never start a second job
            return
        for d in self.dialogs:
            if d.winfo_exists():
                d.destroy()
        problems = self._problems()
        if problems:
            self.dialogs = [GuideDialog(self, h, t, slot=i, count=len(problems)) for i, (h, t) in enumerate(problems)]
            return
        device = self.device or DeviceInfo("cpu", "CPU", "cpu")
        self.center.set_progress(0, 0)
        self._set_busy(True)
        exporter = Exporter(Path(self.export_dir), self.center.want_txt, self.center.want_json)
        self.job = OCRJob(list(self.imports.files), self.models.selected, device, exporter,
                          self.events, self.engine_cache)
        self.log(f"Starting: {len(self.imports.files)} file(s)")
        self.job.start()

    def _set_busy(self, busy: bool):
        self.center.set_running(busy)
        self.imports.set_enabled(not busy)
        self.models.set_enabled(not busy)

    def _poll(self):
        try:
            while True:
                kind, *data = self.events.get_nowait()
                if kind == "log":
                    self.log(data[0])
                elif kind == "device":
                    self.device = data[0]
                    self.models.set_device(self.device.description)
                    self.log(f"Hardware: {self.device.description}")
                elif kind == "phase":
                    self.center.set_busy_loading(data[0] in ("loading", "counting"))
                elif kind == "progress":
                    self.center.set_busy_loading(False)
                    self.center.set_progress(*data)
                elif kind == "finished":
                    self.center.set_busy_loading(False)
                    self.log(data[0])
                    self._set_busy(False)
                    self.job = None
        except queue.Empty:
            pass
        self.after(100, self._poll)

    def _close(self):
        if self.job and self.job.is_alive():
            self.job.cancel.set()
        self.destroy()


if __name__ == "__main__":
    App().mainloop()
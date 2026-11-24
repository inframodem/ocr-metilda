
import os
import numpy as np
import gc

from .OCREngines import OCREngine,register_engine, reading_order
from ..Structs import Line

@register_engine("paddleocr")
class PaddleOCREngine(OCREngine):
    def load(self, log):
        if self.device.kind == "mps":
            os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
        before = self._module_ids() if self.device.kind == "mps" else set()
        from paddleocr import PaddleOCR
        self._ocr = PaddleOCR(
            text_detection_model_dir=str(self.model.det_dir),
            text_recognition_model_dir=str(self.model.rec_dir),
            use_doc_orientation_classify=False, use_doc_unwarping=False, use_textline_orientation=False,
            engine="transformers", device=self.device.paddle_device)
        if self.device.kind == "mps":
            self._move_to_mps(before, log)

    # PaddleOCR only accepts Paddle device names, so on Apple silicon the PyTorch modules it created are moved by hand.
    @staticmethod
    def _module_ids() -> set:
        import torch
        ids = set()
        for o in gc.get_objects():
            try:
                if isinstance(o, torch.nn.Module):
                    ids.add(id(o))
            except Exception:
                pass
        return ids

    def _move_to_mps(self, before, log):
        import torch
        moved = 0
        for o in gc.get_objects():
            try:
                if isinstance(o, torch.nn.Module) and id(o) not in before:
                    o.to("mps")
                    moved += 1
            except Exception:
                pass
        log(f"Moved {moved} model parts to the Apple GPU" if moved else
            "Could not move the model to the Apple GPU; it will run on the CPU")

    def recognize(self, rgb):
        bgr = np.ascontiguousarray(rgb[:, :, ::-1])
        lines: list[Line] = []
        for res in self._ocr.predict(bgr):
            texts = list(res["rec_texts"])
            scores = [float(s) for s in res["rec_scores"]]
            polys = [np.asarray(p).astype(int) for p in res["rec_polys"]]
            boxes_raw = res.get("rec_boxes") if hasattr(res, "get") else None
            if boxes_raw is not None and len(boxes_raw) == len(texts):
                boxes = [tuple(int(v) for v in b) for b in boxes_raw]
            else:
                boxes = [(int(p[:, 0].min()), int(p[:, 1].min()), int(p[:, 0].max()), int(p[:, 1].max())) for p in polys]
            for i in reading_order(boxes):
                lines.append(Line(text=texts[i], confidence=scores[i], box=boxes[i], polygon=polys[i].tolist()))
        return lines
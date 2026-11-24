from dataclasses import dataclass, field
from pathlib import Path
from .DeviceInfo import DeviceInfo
from datetime import datetime
from CommonVars import PDF_EXTS, PDF_DPI

@dataclass
class ModelInfo:
    name: str
    model_type: str
    path: Path
    label: str = ""                # what the drop-down shows (name, plus the folder if two models share a name)

    @property
    def det_dir(self) -> Path:
        return self.path / "det"

    @property
    def rec_dir(self) -> Path:
        return self.path / "rec"

@dataclass
class Line:
    text: str
    confidence: float
    box: tuple[int, int, int, int]                       # x1, y1, x2, y2 of the detector's rectangle
    polygon: list[list[int]] = field(default_factory=list)   # the detector's four corners


@dataclass
class Page:
    number: int
    width: int
    height: int
    lines: list[Line]

@dataclass
class DocumentResult:
    source: Path
    pages: list[Page]
    model: ModelInfo
    device: DeviceInfo
    seconds: float

    def to_json_dict(self) -> dict:
        is_pdf = self.source.suffix.lower() in PDF_EXTS
        return {
            "file": self.source.name,
            "source_path": str(self.source),
            "file_type": "pdf" if is_pdf else "image",
            "ocr_model": {"name": self.model.name, "model_type": self.model.model_type},
            "device": self.device.kind,
            "processed_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "processing_seconds": round(self.seconds, 2),
            "coordinate_system": "pixels in the page image, origin top-left" +
                                 (f"; PDF pages were rendered at {PDF_DPI} dpi" if is_pdf else ""),
            "page_count": len(self.pages),
            "pages": [{
                "page": p.number,
                "width": p.width,
                "height": p.height,
                "line_count": len(p.lines),
                "lines": [{
                    "line": i,
                    "text": ln.text,
                    "confidence": round(ln.confidence, 4),
                    "bbox": {"x1": ln.box[0], "y1": ln.box[1], "x2": ln.box[2], "y2": ln.box[3],
                             "width": ln.box[2] - ln.box[0], "height": ln.box[3] - ln.box[1]},
                    "polygon": ln.polygon,
                } for i, ln in enumerate(p.lines, 1)],
            } for p in self.pages],
        }

    def to_text(self) -> str:
        """Raw text, one line per recognised line; a blank line between pages."""
        return "\n\n".join("\n".join(ln.text for ln in p.lines) for p in self.pages) + "\n"
from PIL import Image, ImageOps
from pathlib import Path
from ocr_app.CommonVars import SUPPORTED_EXTS, PDF_EXTS, PDF_DPI
import numpy as np
from typing import  Iterator

def _to_rgb(img: Image.Image) -> Image.Image:
    img = ImageOps.exif_transpose(img)
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        rgba = img.convert("RGBA")
        bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))     # transparent areas become white, not black
        bg.alpha_composite(rgba)
        return bg.convert("RGB")
    return img.convert("RGB")


def _pymupdf():
    try:
        import pymupdf
        return pymupdf
    except ImportError:                  # older PyMuPDF releases only offer the name "fitz"
        import fitz
        return fitz


class DocumentLoader:
    """Turns PDFs and every common image format into a sequence of RGB pages."""

    @staticmethod
    def is_supported(path: Path) -> bool:
        return path.suffix.lower() in SUPPORTED_EXTS

    @classmethod
    def collect(cls, paths: list[Path]) -> tuple[list[Path], list[Path]]:
        """Expand folders (including sub-folders). Returns (supported files, files that were skipped)."""
        found, skipped = [], []
        for p in paths:
            if p.is_dir():
                for f in sorted(x for x in p.rglob("*") if x.is_file()):
                    (found if cls.is_supported(f) else skipped).append(f)
            elif p.is_file():
                (found if cls.is_supported(p) else skipped).append(p)
        return found, skipped

    @staticmethod
    def page_count(path: Path) -> int:
        if path.suffix.lower() in PDF_EXTS:
            fitz = _pymupdf()
            with fitz.open(path) as doc:
                return doc.page_count
        with Image.open(path) as im:
            return max(1, getattr(im, "n_frames", 1))

    @staticmethod
    def pages(path: Path) -> Iterator[np.ndarray]:
        if path.suffix.lower() in PDF_EXTS:
            fitz = _pymupdf()
            with fitz.open(path) as doc:
                for page in doc:
                    pix = page.get_pixmap(dpi=PDF_DPI, alpha=False)
                    yield np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3].copy()
        else:
            with Image.open(path) as im:
                for i in range(max(1, getattr(im, "n_frames", 1))):
                    im.seek(i)
                    yield np.asarray(_to_rgb(im))

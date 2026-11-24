from pathlib import Path
import sys

PDF_DPI = 200                      # resolution PDF pages are rendered at before OCR
PDF_EXTS = {".pdf"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".jpe", ".jfif", ".webp", ".bmp", ".dib", ".tif", ".tiff", ".gif", ".jp2", ".ppm", ".pgm"}
SUPPORTED_EXTS = PDF_EXTS | IMAGE_EXTS
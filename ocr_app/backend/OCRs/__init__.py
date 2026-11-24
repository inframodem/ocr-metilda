from .OCREngines import ENGINES, OCREngine, register_engine, reading_order

# Importing an engine's module is what runs its @register_engine line. One line per engine.
from . import PaddleOCR      # noqa: F401
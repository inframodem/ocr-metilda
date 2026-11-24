from abc import ABC, abstractmethod
from typing import Callable
import numpy as np

from ..ModelInfo import ModelInfo
from ..DeviceInfo import DeviceInfo
from ..Structs import Line


ENGINES: dict[str, type["OCREngine"]] = {}


def register_engine(model_type: str):
    def wrap(cls):
        ENGINES[model_type] = cls
        return cls
    return wrap


def reading_order(boxes: list[tuple[int, int, int, int]]) -> list[int]:
    """Top-to-bottom, then left-to-right inside a row (boxes whose centres are close vertically share a row)."""
    if not boxes:
        return []
    heights = sorted(b[3] - b[1] for b in boxes)
    tol = 0.5 * max(1, heights[len(heights) // 2])
    rows: list[dict] = []
    for i in sorted(range(len(boxes)), key=lambda k: boxes[k][1] + boxes[k][3]):
        cy = (boxes[i][1] + boxes[i][3]) / 2
        if rows and abs(cy - rows[-1]["cy"]) <= tol:
            rows[-1]["items"].append(i)
            rows[-1]["cy"] = (rows[-1]["cy"] * (len(rows[-1]["items"]) - 1) + cy) / len(rows[-1]["items"])
        else:
            rows.append({"cy": cy, "items": [i]})
    return [i for r in rows for i in sorted(r["items"], key=lambda k: boxes[k][0])]


class OCREngine(ABC):
    """One kind of OCR model. To add another kind: subclass, implement load/recognize, and decorate with
    @register_engine("the_model_type_used_in_config_json")."""

    def __init__(self, model: ModelInfo, device: DeviceInfo):
        self.model, self.device = model, device

    @abstractmethod
    def load(self, log: Callable[[str], None]) -> None: ...

    @abstractmethod
    def recognize(self, rgb: np.ndarray) -> list[Line]: ...



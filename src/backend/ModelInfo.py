from dataclasses import dataclass, field
from pathlib import Path

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
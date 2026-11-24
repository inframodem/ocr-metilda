from .Structs import ModelInfo
import json
from pathlib import Path
from .OCRs.OCREngines import ENGINES

class ModelRegistry:
    """Finds the models under the models folder. Call refresh() to look again."""

    def __init__(self, root: Path):
        self.root = root
        self.models: list[ModelInfo] = []
        self.problems: list[str] = []

    def refresh(self) -> list[ModelInfo]:
        self.models, self.problems = [], []
        self.root.mkdir(parents=True, exist_ok=True)
        for folder in sorted(p for p in self.root.iterdir() if p.is_dir()):
            cfg_path = folder / "config.json"
            if not cfg_path.is_file():
                self.problems.append(f"{folder.name}: no config.json, skipped")
                continue
            try:
                cfg = json.loads(cfg_path.read_text(encoding="utf-8-sig"))
                name, mtype = str(cfg["name"]).strip(), str(cfg["model_type"]).strip().lower()
                if not name:
                    raise ValueError("'name' is empty")
            except Exception as exc:
                self.problems.append(f"{folder.name}: config.json is not usable ({exc}), skipped")
                continue
            if mtype not in ENGINES:
                self.problems.append(f"{folder.name}: model_type '{mtype}' is not supported "
                                     f"(known: {', '.join(sorted(ENGINES))}), skipped")
                continue
            missing = [d for d in ("det", "rec") if not (folder / d).is_dir()]
            if missing:
                self.problems.append(f"{folder.name}: missing folder(s) {', '.join(missing)}, skipped")
                continue
            self.models.append(ModelInfo(name=name, model_type=mtype, path=folder))
        names = [m.name for m in self.models]
        for m in self.models:
            m.label = m.name if names.count(m.name) == 1 else f"{m.name} ({m.path.name})"
        self.models.sort(key=lambda m: m.label.lower())
        return self.models
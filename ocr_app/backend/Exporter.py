import re
import json
from pathlib import Path
from .Structs import DocumentResult

def _compact(text: str) -> str:
    """Keep the JSON indented but put each polygon (four x, y pairs) on one line."""
    text = re.sub(r"\[\s*(-?\d+),\s*(-?\d+)\s*\]", r"[\1, \2]", text)
    return re.sub(r"\[\s*((?:\[-?\d+, -?\d+\],?\s*)+)\]",
                  lambda m: "[" + ", ".join(re.findall(r"\[-?\d+, -?\d+\]", m.group(1))) + "]", text)


class Exporter:
    def __init__(self, out_dir: Path, want_txt: bool, want_json: bool):
        self.out_dir, self.want_txt, self.want_json = out_dir, want_txt, want_json
        self._used: set[str] = set()

    def _stem(self, source: Path) -> str:
        stem, n = source.stem, 2
        while stem.lower() in self._used:                # two inputs with the same name, e.g. a.pdf and a.png
            stem, n = f"{source.stem}_{n}", n + 1
        self._used.add(stem.lower())
        return stem

    def save(self, doc: DocumentResult) -> list[Path]:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        stem, written = self._stem(doc.source), []
        if self.want_txt:
            p = self.out_dir / f"{stem}.txt"
            p.write_text(doc.to_text(), encoding="utf-8")
            written.append(p)
        if self.want_json:
            p = self.out_dir / f"{stem}.json"
            p.write_text(_compact(json.dumps(doc.to_json_dict(), ensure_ascii=False, indent=2)), encoding="utf-8")
            written.append(p)
        return written

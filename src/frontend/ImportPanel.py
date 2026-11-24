import customtkinter as ctk
from typing import Callable
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

from ..backend.DocumentLoader import DocumentLoader
from ..CommonVars import SUPPORTED_EXTS
from .UIHelpers import set_enabled


class ImportPanel(ctk.CTkFrame):
    def __init__(self, parent, on_message: Callable[[str], None]):
        super().__init__(parent)
        self.on_message = on_message
        self.files: list[Path] = []
        self._rows: dict[Path, ctk.CTkFrame] = {}
        self._remove_buttons: dict[Path, ctk.CTkButton] = {}
        self._enabled = True
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(self, text="Import List", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, padx=14, pady=(14, 8), sticky="w")
        self.button = ctk.CTkButton(self, text="Import...", command=self._popup)
        self.button.grid(row=1, column=0, padx=14, pady=(0, 10), sticky="ew")
        self.list = ctk.CTkScrollableFrame(self, fg_color=("gray95", "gray17"))
        self.list.grid(row=2, column=0, padx=14, sticky="nsew")
        self.list.grid_columnconfigure(0, weight=1)
        self.count = ctk.CTkLabel(self, text="No files", text_color="gray45", anchor="w")
        self.count.grid(row=3, column=0, padx=14, pady=(8, 12), sticky="ew")
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Add files...", command=self._pick_files)
        self.menu.add_command(label="Add folder...", command=self._pick_folder)

    def _popup(self):
        x, y = self.button.winfo_rootx(), self.button.winfo_rooty() + self.button.winfo_height()
        try:
            self.menu.tk_popup(x, y)
        finally:
            self.menu.grab_release()

    def _pick_files(self):
        exts = " ".join(f"*{e}" for e in sorted(SUPPORTED_EXTS))
        paths = filedialog.askopenfilenames(title="Select files to process",
                                            filetypes=[("PDFs and images", exts), ("All files", "*.*")])
        self.add_paths([Path(p) for p in paths])

    def _pick_folder(self):
        folder = filedialog.askdirectory(title="Select a folder to process (sub-folders are included)")
        if folder:
            self.add_paths([Path(folder)])

    def add_paths(self, paths: list[Path]):
        found, skipped = DocumentLoader.collect(paths)
        added = 0
        for f in found:
            if f not in self._rows:
                self._add_row(f)
                added += 1
        if paths:
            msg = f"Added {added} file(s) to the import list"
            if len(found) - added:
                msg += f", {len(found) - added} already listed"
            if skipped:
                msg += f", skipped {len(skipped)} unsupported file(s)"
            self.on_message(msg)

    def _add_row(self, path: Path):
        row = ctk.CTkFrame(self.list, fg_color="transparent")
        row.grid(sticky="ew", pady=1, column=0, row=len(self.files))
        row.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(row, text=path.name, anchor="w").grid(row=0, column=0, sticky="ew", padx=(6, 0))
        btn = ctk.CTkButton(row, text="x", width=24, height=24, fg_color="transparent", text_color=("gray30", "gray80"),
                            hover_color=("gray80", "gray30"), command=lambda p=path: self.remove(p),
                            state="normal" if self._enabled else "disabled")
        btn.grid(row=0, column=1)
        self._remove_buttons[path] = btn
        self.files.append(path)
        self._rows[path] = row
        self._update_count()

    def remove(self, path: Path):
        if not self._enabled:
            return
        self._rows.pop(path).destroy()
        self._remove_buttons.pop(path, None)
        self.files.remove(path)
        self._update_count()

    def _update_count(self):
        self.count.configure(text=f"{len(self.files)} file(s)" if self.files else "No files")

    def set_enabled(self, enabled: bool):
        self._enabled = enabled
        set_enabled(self.button, enabled)
        for b in self._remove_buttons.values():
            set_enabled(b, enabled)
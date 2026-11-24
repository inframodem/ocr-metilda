import customtkinter as ctk
from typing import Callable
import tkinter as tk
from datetime import datetime

from typing import Callable, Optional
from .UIHelpers import set_enabled, shorten_path

class CenterPanel(ctk.CTkFrame):
    """Log, export location and format, run button and progress bar."""

    def __init__(self, parent, on_choose_export: Callable, on_run: Callable, on_stop: Callable):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        log_card = ctk.CTkFrame(self)
        log_card.grid(row=0, column=0, sticky="nsew")
        log_card.grid_columnconfigure(0, weight=1)
        log_card.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(log_card, text="Progress", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, padx=14, pady=(14, 8), sticky="w")
        self.log_box = ctk.CTkTextbox(log_card, state="disabled", wrap="word",
                                      font=ctk.CTkFont(family="Consolas", size=12))
        self.log_box.grid(row=1, column=0, padx=14, pady=(0, 14), sticky="nsew")

        export = ctk.CTkFrame(self)
        export.grid(row=1, column=0, pady=(10, 0), sticky="ew")
        export.grid_columnconfigure(1, weight=1)
        self.export_button = ctk.CTkButton(export, text="Export location...", width=140, command=on_choose_export)
        self.export_button.grid(row=0, column=0, padx=14, pady=(12, 6))
        self.export_label = ctk.CTkLabel(export, text="No folder chosen", anchor="w", text_color="gray45")
        self.export_label.grid(row=0, column=1, padx=(0, 14), pady=(12, 6), sticky="ew")
        self.txt_var, self.json_var = tk.BooleanVar(value=True), tk.BooleanVar(value=True)
        fmt = ctk.CTkFrame(export, fg_color="transparent")
        fmt.grid(row=1, column=0, columnspan=2, padx=14, pady=(0, 12), sticky="w")
        ctk.CTkLabel(fmt, text="Save as:").pack(side="left", padx=(0, 10))
        self.txt_box = ctk.CTkCheckBox(fmt, text="Plain text (.txt)", variable=self.txt_var)
        self.txt_box.pack(side="left", padx=(0, 16))
        self.json_box = ctk.CTkCheckBox(fmt, text="Full details (.json)", variable=self.json_var)
        self.json_box.pack(side="left")

        run = ctk.CTkFrame(self)
        run.grid(row=2, column=0, pady=(10, 0), sticky="ew")
        run.grid_columnconfigure(2, weight=1)
        self.run_button = ctk.CTkButton(run, text="Run OCR", width=100, command=on_run)
        self.run_button.grid(row=0, column=0, padx=(14, 8), pady=14)
        self.stop_button = ctk.CTkButton(run, text="Stop", width=70, command=on_stop,
                                         fg_color="#b5483f", hover_color="#963a32")
        self.stop_button.grid(row=0, column=1, padx=(0, 12), pady=14)
        set_enabled(self.stop_button, False)
        self.bar = ctk.CTkProgressBar(run)
        self.bar.set(0)
        self.bar.grid(row=0, column=2, padx=(0, 10), pady=14, sticky="ew")
        self.percent = ctk.CTkLabel(run, text="0%", width=84, anchor="e")
        self.percent.grid(row=0, column=3, padx=(0, 14))

    def append(self, text: str):
        stamp = datetime.now().strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{stamp}] {text}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def set_export(self, path: Optional[str]):
        if path:
            self.export_label.configure(text=shorten_path(path), text_color=("gray10", "gray90"))
        else:
            self.export_label.configure(text="No folder chosen", text_color="gray45")

    @property
    def want_txt(self) -> bool:
        return bool(self.txt_var.get())

    @property
    def want_json(self) -> bool:
        return bool(self.json_var.get())

    def set_progress(self, done: int, total: int):
        frac = done / total if total else 0
        self.bar.set(frac)
        self.percent.configure(text=f"{frac:.0%}  {done}/{total}")

    _loading = False

    def set_busy_loading(self, loading: bool):
        """Moving stripe while the model loads; switches back to a plain bar only when it was showing the stripe."""
        if loading and not self._loading:
            self.bar.configure(mode="indeterminate")
            self.bar.start()
            self.percent.configure(text="loading...")
        elif not loading and self._loading:
            self.bar.stop()
            self.bar.configure(mode="determinate")
            self.bar.set(0)
            self.percent.configure(text="0%")
        self._loading = loading

    def set_running(self, running: bool):
        """While a job runs everything is locked except Stop, so nothing can be changed under it."""
        for w in (self.run_button, self.export_button, self.txt_box, self.json_box):
            set_enabled(w, not running)
        set_enabled(self.stop_button, running)

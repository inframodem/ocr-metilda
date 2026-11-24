import customtkinter as ctk
import os
from pathlib import Path
import tkinter as tk

LOCKED_FG = ("gray78", "gray30")


def set_enabled(widget, enabled: bool):
    """Enable or lock a widget. Locked buttons and menus also turn grey, because customtkinter's own disabled look
    (only a lighter label) is easy to miss."""
    widget.configure(state="normal" if enabled else "disabled")
    if isinstance(widget, ctk.CTkOptionMenu):
        if not hasattr(widget, "_normal_colors"):
            widget._normal_colors = (widget.cget("fg_color"), widget.cget("button_color"), widget.cget("button_hover_color"))
        fg, btn, hov = widget._normal_colors
        widget.configure(fg_color=fg if enabled else LOCKED_FG, button_color=btn if enabled else LOCKED_FG,
                         button_hover_color=hov if enabled else LOCKED_FG)
    elif isinstance(widget, ctk.CTkButton):
        if not hasattr(widget, "_normal_fg"):
            widget._normal_fg = widget.cget("fg_color")
        if widget._normal_fg != "transparent":
            widget.configure(fg_color=widget._normal_fg if enabled else LOCKED_FG)


def shorten_path(path: str, limit: int = 34) -> str:
    if len(path) <= limit:
        return path
    parts = Path(path).parts
    tail = ""
    for part in reversed(parts):
        cand = part if not tail else part.rstrip("\\/") + os.sep + tail
        if len(cand) + 4 > limit and tail:
            break
        tail = cand
    return "..." + os.sep + tail if tail != path else path


class GuideDialog(ctk.CTkToplevel):
    """A small always-on-top message: bold heading, one line of help."""

    def __init__(self, parent: ctk.CTk, heading: str, help_text: str, slot: int = 0, count: int = 1):
        super().__init__(parent)
        self.title(heading)
        self.resizable(False, False)
        self.attributes("-topmost", True)
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=28, pady=22)
        ctk.CTkLabel(body, text=heading, font=ctk.CTkFont(size=17, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(body, text=help_text, justify="left", wraplength=360).pack(anchor="w", pady=(8, 18))
        ctk.CTkButton(body, text="OK", width=90, command=self.destroy).pack(anchor="e")
        self.bind("<Return>", lambda e: self.destroy())
        self.bind("<Escape>", lambda e: self.destroy())
        self.update_idletasks()
        w, h = self.winfo_reqwidth(), self.winfo_reqheight()
        # several dialogs at once are stacked top to bottom around the window's centre so each one stays readable
        x = parent.winfo_rootx() + (parent.winfo_width() - w) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - h) // 2 + int((slot - (count - 1) / 2) * (h + 16))
        self.geometry(f"{w}x{h}+{max(0, x)}+{max(0, y)}")
        self.after(150, self._front)

    def _front(self):
        try:
            self.lift()
            self.attributes("-topmost", True)
            self.focus_force()
        except tk.TclError:
            pass
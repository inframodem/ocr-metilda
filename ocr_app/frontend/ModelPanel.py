import customtkinter as ctk
from typing import Callable
from typing import Optional

from backend.ModelInfo import ModelInfo
from CommonVars import SUPPORTED_EXTS
from .UIHelpers import set_enabled

class ModelPanel(ctk.CTkFrame):
    PLACEHOLDER = "Select a model..."

    def __init__(self, parent, on_refresh: Callable):
        super().__init__(parent)
        self.grid_columnconfigure(0, weight=1)
        self._by_label: dict[str, ModelInfo] = {}
        ctk.CTkLabel(self, text="OCR Model", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, padx=14, pady=(14, 8), sticky="w")
        self.refresh_button = ctk.CTkButton(self, text="Refresh", command=on_refresh)
        self.refresh_button.grid(row=1, column=0, padx=14, pady=(0, 10), sticky="ew")
        self.menu = ctk.CTkOptionMenu(self, values=[self.PLACEHOLDER], dynamic_resizing=False)
        self.menu.set(self.PLACEHOLDER)
        self.menu.grid(row=2, column=0, padx=14, sticky="ew")
        self.device_label = ctk.CTkLabel(self, text="Hardware: checking...", text_color="gray45",
                                         anchor="w", justify="left", wraplength=170)
        self.device_label.grid(row=3, column=0, padx=14, pady=(14, 14), sticky="ew")
        self.bind("<Configure>", lambda e: self.device_label.configure(wraplength=max(80, e.width - 30)))

    def set_models(self, models: list[ModelInfo]):
        current = self.menu.get()
        self._by_label = {m.label: m for m in models}
        values = list(self._by_label) or [self.PLACEHOLDER]
        if models:
            values = [self.PLACEHOLDER] + values
        self.menu.configure(values=values)
        self.menu.set(current if current in self._by_label else self.PLACEHOLDER)

    @property
    def selected(self) -> Optional[ModelInfo]:
        return self._by_label.get(self.menu.get())

    def set_device(self, text: str):
        self.device_label.configure(text=f"Hardware: {text}")

    def set_enabled(self, enabled: bool):
        set_enabled(self.refresh_button, enabled)
        set_enabled(self.menu, enabled)

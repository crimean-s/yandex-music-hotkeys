import os
from typing import Callable, Dict, List, Optional

import customtkinter as ctk
import keyboard

from core.constants import APP_NAME, APP_VERSION, DEFAULT_HOTKEYS, get_resource_path
from core.config import Config
from core.tools.listener import HotkeyListener


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

BG_MAIN = "#000000"
BG_GROUP = "#1C1C1E"
TITLE_COLOR = "#FFFFFF"
LABEL_COLOR = "#FFFFFF"
SECONDARY_COLOR = "#8E8E93"
BUTTON_BG = "#2C2C2E"
BUTTON_HOVER = "#3A3A3C"

MIN_WINDOW_WIDTH = 420
MIN_WINDOW_HEIGHT = 280
PADDING_H = 24
PADDING_V = 20
GROUP_RADIUS = 12
GROUP_GAP = 24
ROW_PADDING = 14

HOTKEY_LABELS: Dict[str, str] = {
    "next_track": "Next track",
    "previous_track": "Previous track",
    "play_pause": "Play/Pause",
}


class SettingsWindow:
    def __init__(
        self,
        config: Config,
        listener: HotkeyListener,
        on_close: Optional[Callable[[], None]] = None,
    ) -> None:
        self.config = config
        self.listener = listener
        self.on_close = on_close
        self.hotkey_buttons: Dict[str, ctk.CTkButton] = {}
        self.hotkey_values: Dict[str, str] = {}
        self.root = ctk.CTk()
        self._record_action_key: Optional[str] = None
        self._record_hook: Optional[Callable] = None

    def is_alive(self) -> bool:
        try:
            return self.root.winfo_exists()
        except Exception:
            return False

    def focus_window(self) -> None:
        if not self.is_alive():
            return
        try:
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
        except Exception:
            pass

    def request_close(self) -> None:
        if not self.is_alive():
            return
        try:
            self.root.after(0, self._on_close_window)
        except Exception:
            pass
        try:
            self.root.quit()
        except Exception:
            pass

    def _configure_root(self) -> None:
        self.root.title(f"{APP_NAME} — Settings")
        self.root.resizable(False, False)
        self.root.configure(fg_color=BG_MAIN)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close_window)
        self._set_window_icon()

    def _set_window_icon(self) -> None:
        icon_path = get_resource_path(os.path.join("assets", "icon.ico"))
        if not os.path.isfile(icon_path):
            return
        try:
            self.root.iconbitmap(icon_path)
        except Exception:
            pass

    def _build_ui(self) -> None:
        self._configure_root()
        main = ctk.CTkFrame(self.root, fg_color="transparent")
        main.pack(fill="both", expand=True)

        self._build_content_area(main)
        self._build_hotkeys_section()
        self._build_version_section()
        self._fit_window_to_content()

    def _fit_window_to_content(self) -> None:
        self.root.update_idletasks()
        width = max(self.root.winfo_reqwidth(), MIN_WINDOW_WIDTH)
        height = max(self.root.winfo_reqheight(), MIN_WINDOW_HEIGHT)
        self.root.geometry(f"{width}x{height}")
        self.root.minsize(width, height)

    def _build_content_area(self, parent: ctk.CTkFrame) -> None:
        self.content_area = ctk.CTkFrame(parent, fg_color=BG_MAIN, corner_radius=0)
        self.content_area.pack(fill="both", expand=True)

    def _build_hotkeys_section(self) -> None:
        ctk.CTkLabel(
            self.content_area,
            text="Settings",
            font=ctk.CTkFont(family="Segoe UI Black", size=34),
            text_color=TITLE_COLOR,
        ).pack(anchor="w", padx=PADDING_H, pady=(PADDING_V + 8, 4))

        ctk.CTkLabel(
            self.content_area,
            text="HOTKEYS",
            font=ctk.CTkFont(size=13),
            text_color=SECONDARY_COLOR,
        ).pack(anchor="w", padx=PADDING_H, pady=(8, 6))

        hotkeys_group = ctk.CTkFrame(
            self.content_area,
            fg_color=BG_GROUP,
            corner_radius=GROUP_RADIUS,
        )
        hotkeys_group.pack(fill="x", padx=PADDING_H, pady=(0, GROUP_GAP))

        self.hotkeys_content = ctk.CTkFrame(hotkeys_group, fg_color="transparent")
        self.hotkeys_content.pack(fill="x", padx=16, pady=4)
        hotkeys = self.config.get_hotkeys()
        for row, (key, combo) in enumerate(DEFAULT_HOTKEYS.items()):
            self.hotkey_values[key] = hotkeys.get(key, combo)
            self._build_hotkey_row(row, key)

        self.hotkeys_content.grid_columnconfigure(1, weight=1)

    def _build_hotkey_row(self, row: int, key: str) -> None:
        ctk.CTkLabel(
            self.hotkeys_content,
            text=HOTKEY_LABELS.get(key, key),
            font=ctk.CTkFont(size=17),
            text_color=LABEL_COLOR,
        ).grid(row=row, column=0, sticky="w", padx=(0, 16), pady=ROW_PADDING)

        button = ctk.CTkButton(
            self.hotkeys_content,
            text=self._format_combo_display(self.hotkey_values[key]),
            width=130,
            height=32,
            font=ctk.CTkFont(size=17),
            fg_color=BUTTON_BG,
            hover_color=BUTTON_HOVER,
            text_color=LABEL_COLOR,
            corner_radius=8,
            command=lambda k=key: self._start_record(k),
        )
        button.grid(row=row, column=1, sticky="e", padx=(0, 0), pady=ROW_PADDING)
        self.hotkey_buttons[key] = button

    def _build_version_section(self) -> None:
        version_group = ctk.CTkFrame(
            self.content_area,
            fg_color=BG_GROUP,
            corner_radius=GROUP_RADIUS,
        )
        version_group.pack(fill="x", padx=PADDING_H, pady=(0, PADDING_V + 12))

        version_inner = ctk.CTkFrame(version_group, fg_color="transparent")
        version_inner.pack(fill="x", padx=16, pady=ROW_PADDING)
        version_inner.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            version_inner,
            text="Version",
            font=ctk.CTkFont(size=17),
            text_color=LABEL_COLOR,
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            version_inner,
            text=APP_VERSION,
            font=ctk.CTkFont(size=17),
            text_color=SECONDARY_COLOR,
        ).grid(row=0, column=1, sticky="e")

    def _clear_recording(self) -> None:
        if self._record_hook is not None:
            try:
                keyboard.unhook(self._record_hook)
            except Exception:
                pass
            self._record_hook = None
        self._record_action_key = None

    def _on_close_window(self) -> None:
        self._clear_recording()
        if self.on_close:
            self.on_close()
        if not self.is_alive():
            return
        try:
            self.root.quit()
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            pass

    def _start_record(self, key: str) -> None:
        if self._record_hook is not None:
            return
        self._record_action_key = key

        def on_key_event(event: keyboard.KeyboardEvent) -> None:
            if self._record_action_key is None or event.event_type != "down":
                return
            mods = self._get_pressed_modifiers()
            name = (event.name or "").strip().lower()
            if not name or name in ("ctrl", "shift", "alt", "win"):
                return
            combo = "+".join(mods + [name]).lower()
            action_key = self._record_action_key
            self._clear_recording()
            try:
                if self.is_alive():
                    self.root.after(0, lambda: self._set_record_result(action_key, combo))
            except Exception:
                pass

        self._record_hook = keyboard.hook(on_key_event, suppress=False)

    def _get_pressed_modifiers(self) -> List[str]:
        mods: List[str] = []
        for mod in ("ctrl", "shift", "alt", "win"):
            try:
                if keyboard.is_pressed(mod):
                    mods.append(mod)
            except Exception:
                pass
        return mods

    @staticmethod
    def _format_combo_display(combo: str) -> str:
        if not combo:
            return "—"
        return "+".join(p.capitalize() for p in combo.lower().split("+"))

    def _set_record_result(self, key: str, combo: str) -> None:
        if not self.is_alive():
            return
        combo = combo.strip().lower()
        if not combo:
            return
        self.hotkey_values[key] = combo
        btn = self.hotkey_buttons.get(key)
        if btn:
            btn.configure(text=self._format_combo_display(combo))
        self._apply_hotkeys()

    def _apply_hotkeys(self) -> None:
        hotkeys: Dict[str, str] = {}
        for key in DEFAULT_HOTKEYS:
            value = (self.hotkey_values.get(key) or "").strip().lower()
            hotkeys[key] = value if value else DEFAULT_HOTKEYS[key]
        self.config.save_config(hotkeys)
        self.listener.reload()

    def run(self) -> None:
        self._build_ui()
        self.root.mainloop()

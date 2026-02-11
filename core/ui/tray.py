"""Иконка в трее и меню. Управляет жизненным циклом окна настроек."""
from __future__ import annotations

import os
import threading
from typing import Optional, TYPE_CHECKING

import pystray
from PIL import Image

from core.config import Config
from core.constants import APP_NAME, get_resource_path
from core.tools.listener import HotkeyListener
from core.ui.contracts import CloseReason

if TYPE_CHECKING:
    from core.ui.settings import SettingsWindow


def _enable_dark_tray_menu() -> None:
    """Включить тёмное контекстное меню (Windows)."""
    try:
        import ctypes
        uxtheme = ctypes.WinDLL("uxtheme")
        set_mode = uxtheme[135]
        set_mode.argtypes = [ctypes.c_int]
        set_mode.restype = ctypes.c_int
        set_mode(2)
        flush = uxtheme[136]
        flush.argtypes = []
        flush.restype = None
        flush()
    except Exception:
        pass


def _load_tray_icon() -> Image.Image:
    path = get_resource_path(os.path.join("assets", "icon.ico"))
    if os.path.isfile(path):
        return Image.open(path)
    return Image.new("RGBA", (64, 64), (88, 166, 255, 255))


class TrayIcon:
    """
    Системный трей: пункты Settings, Reload Config, Exit.
    Окно настроек создаётся один раз в отдельном потоке и переиспользуется (show/hide).
    """

    def __init__(self, listener: HotkeyListener, config: Config) -> None:
        self._listener = listener
        self._config = config
        self._icon: Optional[pystray.Icon] = None
        self._settings_window: Optional[SettingsWindow] = None
        self._settings_lock = threading.Lock()

    def run(self) -> None:
        _enable_dark_tray_menu()
        menu = pystray.Menu(
            pystray.MenuItem("Settings", self._on_settings_click, default=True),
            pystray.MenuItem("Reload Config", self._on_reload_click),
            pystray.MenuItem("Exit", self._on_exit_click),
        )
        self._icon = pystray.Icon(
            "yandex_music_hotkeys",
            _load_tray_icon(),
            APP_NAME,
            menu,
        )
        self._icon.run()

    def _on_settings_click(
        self,
        _icon: pystray.Icon,
        _item: pystray.MenuItem,
    ) -> None:
        if self._settings_window is not None:
            self._settings_window.focus_window()
            return
        if not self._settings_lock.acquire(blocking=False):
            return
        threading.Thread(target=self._run_settings_ui, daemon=True).start()

    def _on_reload_click(
        self,
        _icon: pystray.Icon,
        _item: pystray.MenuItem,
    ) -> None:
        self._listener.reload()

    def _on_exit_click(
        self,
        icon: pystray.Icon,
        _item: pystray.MenuItem,
    ) -> None:
        if self._settings_window is not None:
            self._settings_window.request_destroy()
            self._settings_window = None
        self._listener.stop()
        icon.stop()

    def _run_settings_ui(self) -> None:
        from core.ui.settings import SettingsWindow

        self._listener.stop()
        window = SettingsWindow(
            self._config,
            self._listener,
            on_close=self._when_settings_closed,
        )
        self._settings_window = window
        try:
            window.run()
        finally:
            self._when_settings_closed(CloseReason.DESTROYED)

    def _when_settings_closed(self, reason: CloseReason) -> None:
        if reason is CloseReason.DESTROYED:
            self._settings_window = None
        try:
            self._settings_lock.release()
        except RuntimeError:
            pass
        self._listener.reload()

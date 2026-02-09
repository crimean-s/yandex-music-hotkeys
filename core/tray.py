import os
import sys
import pystray
from PIL import Image
from typing import Optional

from core.listener import HotkeyListener
from core.constants import APP_NAME


class TrayIcon:
    def __init__(self, listener: HotkeyListener) -> None:
        self.listener = listener
        self.icon: Optional[pystray.Icon] = None

    def get_resource_path(self, relative_path: str) -> str:
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    def create_image(self) -> Image.Image:
        icon_path = self.get_resource_path(os.path.join("assets", "icon.ico"))
        if os.path.isfile(icon_path):
            return Image.open(icon_path)
        
        size = 64
        img = Image.new("RGBA", (size, size), (88, 166, 255, 255))
        return img

    def on_reload(self, icon: pystray.Icon, _item: pystray.MenuItem) -> None:
        self.listener.reload()

    def on_exit(self, icon: pystray.Icon, _item: pystray.MenuItem) -> None:
        self.listener.stop()
        icon.stop()

    def run(self) -> None:
        menu = pystray.Menu(
            pystray.MenuItem("Reload Config", self.on_reload),
            pystray.MenuItem("Exit", self.on_exit),
        )
        self.icon = pystray.Icon(
            "yandex_music_hotkeys",
            self.create_image(),
            APP_NAME,
            menu,
        )
        self.icon.run()

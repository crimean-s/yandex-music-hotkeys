from typing import Dict

APP_NAME = "YandexMusicHotkeys"
APP_VERSION = "0.8.0"

CONFIG_FILENAME = "config.json"

TARGET_WINDOW_TITLES = ["Yandex Music", "Яндекс Музыка"]

DEFAULT_HOTKEYS: Dict[str, str] = {
    "next_track": "ctrl+right",
    "previous_track": "ctrl+left",
    "play_pause": "ctrl+space",
}

WM_APPCOMMAND = 0x0319

APPCOMMAND_MEDIA_NEXTTRACK = 11
APPCOMMAND_MEDIA_PREVIOUSTRACK = 12
APPCOMMAND_MEDIA_PLAY_PAUSE = 14
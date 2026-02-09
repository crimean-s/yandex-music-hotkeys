from typing import Dict

WM_APPCOMMAND = 0x0319

APPCOMMAND_MEDIA_NEXTTRACK = 11
APPCOMMAND_MEDIA_PREVIOUSTRACK = 12
APPCOMMAND_MEDIA_PLAY_PAUSE = 14

APP_NAME = "YandexMusicHotkeys"
CONFIG_FILENAME = "config.json"

TARGET_WINDOW_TITLES = ["Yandex Music", "Яндекс Музыка"]

DEFAULT_HOTKEYS: Dict[str, str] = {
    "next_track": "ctrl+right",
    "previous_track": "ctrl+left",
    "play_pause": "ctrl+space",
}

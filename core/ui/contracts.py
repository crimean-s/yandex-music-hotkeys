"""Контракты и общие типы для UI."""
from enum import Enum
from typing import Protocol, runtime_checkable


class CloseReason(str, Enum):
    """Причина закрытия окна настроек."""
    HIDDEN = "hidden"      # пользователь нажал X, окно скрыто
    DESTROYED = "destroyed" # приложение завершается (Exit из трея)


@runtime_checkable
class SettingsWindowProtocol(Protocol):
    """Минимальный интерфейс окна настроек для трея."""

    def focus_window(self) -> None: ...
    def request_destroy(self) -> None: ...

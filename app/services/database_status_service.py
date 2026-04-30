from __future__ import annotations

from threading import Thread

from PySide6.QtCore import QObject, QTimer, Signal

from app.config.settings import DatabaseSettings
from app.database.health import DatabaseHealthResult, check_database_connection


class DatabaseStatusService(QObject):
    status_checked = Signal(object)
    status_changed = Signal(object)

    def __init__(
        self,
        settings: DatabaseSettings,
        interval_ms: int = 5000,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self.settings = settings
        self.interval_ms = interval_ms
        self._last_ok: bool | None = None
        self._is_checking = False
        self._timer = QTimer(self)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self.check_now)

    def start(self) -> None:
        self._timer.start()
        self.check_now()

    def stop(self) -> None:
        self._timer.stop()

    def check_now(self) -> None:
        if self._is_checking:
            return
        self._is_checking = True
        Thread(target=self._run_check, daemon=True).start()

    def _run_check(self) -> None:
        result = check_database_connection(self.settings)
        self.status_checked.emit(result)
        if self._last_ok is None or self._last_ok != result.ok:
            self._last_ok = result.ok
            self.status_changed.emit(result)
        self._is_checking = False

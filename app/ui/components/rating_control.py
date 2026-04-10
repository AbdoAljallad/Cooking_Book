from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget


class RatingControl(QWidget):
    rating_changed = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._rating: int | None = None
        self.setObjectName("ratingControl")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._buttons: list[QPushButton] = []
        for value in range(1, 6):
            button = QPushButton("★")
            button.setObjectName("ratingStar")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda _checked=False, current=value: self._handle_clicked(current))
            layout.addWidget(button)
            self._buttons.append(button)

        clear_button = QPushButton("Clear")
        clear_button.setObjectName("secondaryButton")
        clear_button.clicked.connect(lambda: self.set_rating(None, emit_signal=True))
        layout.addWidget(clear_button)

        layout.addStretch(1)
        self._sync_buttons()

    def rating(self) -> int | None:
        return self._rating

    def set_rating(self, rating: int | None, emit_signal: bool = False) -> None:
        self._rating = rating
        self._sync_buttons()
        if emit_signal:
            self.rating_changed.emit(rating)

    def _handle_clicked(self, rating: int) -> None:
        if self._rating == rating:
            self.set_rating(None, emit_signal=True)
            return
        self.set_rating(rating, emit_signal=True)

    def _sync_buttons(self) -> None:
        for index, button in enumerate(self._buttons, start=1):
            button.setProperty("active", self._rating is not None and index <= self._rating)
            button.style().unpolish(button)
            button.style().polish(button)

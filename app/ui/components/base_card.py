from PySide6.QtWidgets import QFrame, QVBoxLayout, QWidget


class BaseCard(QFrame):
    """Simple reusable surface container for future premium UI sections."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("baseCard")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(24, 24, 24, 24)
        self._layout.setSpacing(12)

    @property
    def content_layout(self) -> QVBoxLayout:
        return self._layout

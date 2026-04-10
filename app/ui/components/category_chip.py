from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QPushButton, QWidget


class CategoryChip(QPushButton):
    selected_changed = Signal(str, bool)

    def __init__(self, slug: str, label: str, parent: QWidget | None = None) -> None:
        super().__init__(label, parent)
        self.slug = slug
        self.setObjectName("categoryChip")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(self._emit_selected)

    def _emit_selected(self) -> None:
        self.selected_changed.emit(self.slug, self.isChecked())

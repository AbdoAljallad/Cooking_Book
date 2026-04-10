from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QWidget

from app.utils.i18n import translate


class SearchBar(QWidget):
    search_requested = Signal(str)
    clear_requested = Signal()

    def __init__(self, placeholder: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("searchBar")
        self._language_code = "en"

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.input = QLineEdit()
        self.input.setObjectName("searchInput")
        self.input.setPlaceholderText(placeholder)
        self.input.returnPressed.connect(self._emit_search)
        layout.addWidget(self.input, stretch=1)

        self.button = QPushButton("Search")
        self.button.setObjectName("secondaryButton")
        self.button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button.clicked.connect(self._emit_search)
        layout.addWidget(self.button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.setObjectName("secondaryButton")
        self.clear_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_button.clicked.connect(self._clear)
        layout.addWidget(self.clear_button)
        self.clear_button.hide()

        self.input.textChanged.connect(self._sync_clear_button)

    def set_language(self, language_code: str, placeholder: str | None = None) -> None:
        self._language_code = language_code
        self.button.setText(translate(language_code, "search.search"))
        self.clear_button.setText(translate(language_code, "search.clear"))
        if placeholder is not None:
            self.input.setPlaceholderText(placeholder)

    def text(self) -> str:
        return self.input.text()

    def set_text(self, value: str) -> None:
        self.input.setText(value)
        self._sync_clear_button(value)

    def _emit_search(self) -> None:
        self.search_requested.emit(self.input.text().strip())

    def _clear(self) -> None:
        self.input.clear()
        self.clear_requested.emit()

    def _sync_clear_button(self, value: str) -> None:
        self.clear_button.setVisible(bool(value.strip()))

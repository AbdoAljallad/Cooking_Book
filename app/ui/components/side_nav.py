from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from app.utils.i18n import translate


@dataclass(frozen=True, slots=True)
class NavItem:
    key: str
    label_key: str
    icon: str


class SideNav(QWidget):
    page_requested = Signal(str)
    collapsed_changed = Signal(bool)

    def __init__(self, items: list[NavItem], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("sideNav")
        self.items = items
        self.buttons: dict[str, QPushButton] = {}
        self._language_code = "en"
        self._collapsed = False
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        self.section_label = QLabel()
        self.section_label.setObjectName("navSectionLabel")
        layout.addWidget(self.section_label)

        self.toggle_button = QPushButton()
        self.toggle_button.setObjectName("navButton")
        self.toggle_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_button.clicked.connect(self.toggle_collapsed)
        layout.addWidget(self.toggle_button)

        for item in self.items:
            button = QPushButton()
            button.setObjectName("navButton")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda _checked=False, key=item.key: self.page_requested.emit(key))
            self.buttons[item.key] = button
            layout.addWidget(button)

        layout.addStretch(1)

    def set_language(self, language_code: str) -> None:
        self._language_code = language_code
        self.section_label.setText(translate(language_code, "nav.section"))
        self.toggle_button.setText("<  " + translate(language_code, "nav.collapse"))
        for item in self.items:
            self.buttons[item.key].setText(self._button_text(item))

    def set_active(self, key: str) -> None:
        for page_key, button in self.buttons.items():
            button.setProperty("active", page_key == key)
            button.style().unpolish(button)
            button.style().polish(button)

    def toggle_collapsed(self) -> None:
        self.set_collapsed(not self._collapsed)

    def set_collapsed(self, collapsed: bool) -> None:
        self._collapsed = collapsed
        self.section_label.setVisible(not collapsed)
        self.setFixedWidth(72 if collapsed else 230)
        self.toggle_button.setText(">" if collapsed else "<  " + translate(self._language_code, "nav.collapse"))
        for item in self.items:
            self.buttons[item.key].setText(item.icon if collapsed else self._button_text(item))
        self.collapsed_changed.emit(collapsed)

    def _button_text(self, item: NavItem) -> str:
        return f"{item.icon}  {translate(self._language_code, item.label_key)}"

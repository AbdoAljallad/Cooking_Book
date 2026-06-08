from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QPushButton, QStyle, QVBoxLayout, QWidget

from app.utils.i18n import translate


@dataclass(frozen=True, slots=True)
class NavItem:
    key: str
    label_key: str
    icon_name: str


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
        layout.setSpacing(8)

        self.section_label = QLabel()
        self.section_label.setObjectName("navSectionLabel")
        layout.addWidget(self.section_label)

        self.toggle_button = QPushButton()
        self.toggle_button.setObjectName("navButton")
        self.toggle_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_button.clicked.connect(self.toggle_collapsed)
        self.toggle_button.setProperty("navUtility", True)
        layout.addWidget(self.toggle_button)

        for item in self.items:
            button = QPushButton()
            button.setObjectName("navButton")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setIcon(self._icon_for_name(item.icon_name))
            button.setIconSize(self._icon_size())
            button.clicked.connect(lambda _checked=False, key=item.key: self.page_requested.emit(key))
            self.buttons[item.key] = button
            layout.addWidget(button)

        layout.addStretch(1)

    def set_language(self, language_code: str) -> None:
        self._language_code = language_code
        self.section_label.setText(translate(language_code, "nav.section"))
        self._refresh_button_texts()

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
        self.setFixedWidth(82 if collapsed else 238)
        self.toggle_button.setProperty("collapsed", collapsed)
        self._refresh_button_texts()
        self.collapsed_changed.emit(collapsed)

    def _button_text(self, item: NavItem) -> str:
        return translate(self._language_code, item.label_key)

    def _refresh_button_texts(self) -> None:
        self.toggle_button.setIcon(
            self._icon_for_name("expand") if self._collapsed else self._icon_for_name("collapse")
        )
        self.toggle_button.setIconSize(self._icon_size())
        self.toggle_button.setText("" if self._collapsed else translate(self._language_code, "nav.collapse"))
        self.toggle_button.setToolTip(translate(self._language_code, "nav.collapse"))

        for item in self.items:
            button = self.buttons[item.key]
            button.setText("" if self._collapsed else self._button_text(item))
            button.setToolTip(translate(self._language_code, item.label_key))

    def _icon_for_name(self, icon_name: str) -> QIcon:
        style = self.style()
        mapping = {
            "home": QStyle.StandardPixmap.SP_DirHomeIcon,
            "add": QStyle.StandardPixmap.SP_FileDialogNewFolder,
            "favorites": QStyle.StandardPixmap.SP_DialogYesButton,
            "categories": QStyle.StandardPixmap.SP_FileDialogDetailedView,
            "settings": QStyle.StandardPixmap.SP_FileDialogContentsView,
            "collapse": QStyle.StandardPixmap.SP_ArrowLeft,
            "expand": QStyle.StandardPixmap.SP_ArrowRight,
        }
        return style.standardIcon(mapping.get(icon_name, QStyle.StandardPixmap.SP_FileIcon))

    @staticmethod
    def _icon_size():
        from PySide6.QtCore import QSize

        return QSize(18, 18)

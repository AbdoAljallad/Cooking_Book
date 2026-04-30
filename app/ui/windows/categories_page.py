from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QWidget

from app.services import AppContextService
from app.ui.components.empty_state import EmptyState
from app.utils.i18n import translate


class CategoriesPage(QWidget):
    def __init__(self, context_service: AppContextService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.context_service = context_service
        self._build_ui()
        self.reload()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.empty_state = EmptyState("", "")
        layout.addWidget(self.empty_state)

    def reload(self) -> None:
        language_code = self.context_service.get_context().language_code
        self.empty_state.set_content(
            translate(language_code, "categories.title"),
            translate(language_code, "categories.subtitle"),
            badge_text=translate(language_code, "categories.badge"),
        )

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.services import AppContext, AppContextService, SettingsService
from app.services.models import SettingsViewData
from app.ui.components.base_card import BaseCard
from app.ui.components.section_header import SectionHeader
from app.utils.i18n import translate


class SettingsPage(QWidget):
    back_requested = Signal()
    settings_applied = Signal(object)

    def __init__(
        self,
        context_service: AppContextService,
        settings_service: SettingsService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.context_service = context_service
        self.settings_service = settings_service
        self._current_language_code = "en"
        self._build_ui()
        self.reload()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        outer.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        self.root_layout = QVBoxLayout(container)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(24)

        top_row = QVBoxLayout()
        top_row.setSpacing(10)

        self.back_button = QPushButton()
        self.back_button.setObjectName("secondaryButton")
        self.back_button.clicked.connect(self.back_requested.emit)
        top_row.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self.root_layout.addLayout(top_row)

        hero = BaseCard()
        hero.setObjectName("heroCard")
        self.eyebrow = QLabel()
        self.eyebrow.setObjectName("eyebrowLabel")
        hero.content_layout.addWidget(self.eyebrow)

        self.title = QLabel()
        self.title.setObjectName("detailsTitle")
        self.title.setWordWrap(True)
        hero.content_layout.addWidget(self.title)

        self.subtitle = QLabel()
        self.subtitle.setObjectName("heroSubtitle")
        self.subtitle.setWordWrap(True)
        hero.content_layout.addWidget(self.subtitle)

        self.feedback_label = QLabel()
        self.feedback_label.setObjectName("statusDetails")
        self.feedback_label.hide()
        hero.content_layout.addWidget(self.feedback_label)
        self.root_layout.addWidget(hero)

        preferences_card = BaseCard()
        self.section_header = SectionHeader("", "")
        preferences_card.content_layout.addWidget(self.section_header)
        form = QFormLayout()
        form.setSpacing(14)

        self.language_combo = QComboBox()
        self.language_combo.setObjectName("comboField")
        self.language_label = QLabel()
        form.addRow(self.language_label, self.language_combo)

        self.theme_combo = QComboBox()
        self.theme_combo.setObjectName("comboField")
        self.theme_label = QLabel()
        form.addRow(self.theme_label, self.theme_combo)

        preferences_card.content_layout.addLayout(form)

        self.language_note = QLabel()
        self.language_note.setObjectName("heroSubtitle")
        self.language_note.setWordWrap(True)
        preferences_card.content_layout.addWidget(self.language_note)

        self.save_button = QPushButton()
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self._save_settings)
        preferences_card.content_layout.addWidget(self.save_button, alignment=Qt.AlignmentFlag.AlignLeft)

        self.root_layout.addWidget(preferences_card)

    def reload(self) -> None:
        context = self.context_service.get_context()
        self._current_language_code = context.language_code
        self._apply_language(context.language_code)
        view_data = self.settings_service.get_settings_view_data(context)
        self._apply_view_data(view_data)

    def _apply_view_data(self, view_data: SettingsViewData) -> None:
        self.feedback_label.hide()
        self.language_combo.clear()
        for item in view_data.available_languages:
            self.language_combo.addItem(f"{item.label} · {item.native_name}", item.code)
        index = self.language_combo.findData(view_data.selected_language_code)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)

        self.theme_combo.clear()
        for item in view_data.available_themes:
            self.theme_combo.addItem(item.label, item.name)
        index = self.theme_combo.findData(view_data.selected_theme_name)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)

        self.language_note.setText(translate(view_data.context.language_code, "settings.note"))

    def _save_settings(self) -> None:
        try:
            updated_context = self.settings_service.save_settings(
                language_code=str(self.language_combo.currentData()),
                theme_name=str(self.theme_combo.currentData()),
            )
        except Exception as exc:
            self.feedback_label.setText(str(exc))
            self.feedback_label.show()
            return

        self._current_language_code = updated_context.language_code
        self._apply_language(updated_context.language_code)
        self.feedback_label.setText(translate(updated_context.language_code, "settings.applied"))
        self.feedback_label.show()
        self.settings_applied.emit(updated_context)

    def _apply_language(self, language_code: str) -> None:
        self.back_button.setText(translate(language_code, "settings.back"))
        self.eyebrow.setText(translate(language_code, "settings.eyebrow"))
        self.title.setText(translate(language_code, "settings.title"))
        self.subtitle.setText(translate(language_code, "settings.subtitle"))
        self.section_header.set_content(
            translate(language_code, "settings.section_title"),
            translate(language_code, "settings.section_subtitle"),
        )
        self.language_label.setText(translate(language_code, "settings.language"))
        self.theme_label.setText(translate(language_code, "settings.theme"))
        self.save_button.setText(translate(language_code, "settings.save"))

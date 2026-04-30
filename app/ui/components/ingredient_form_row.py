from __future__ import annotations

from decimal import Decimal

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QLineEdit,
    QPushButton,
    QWidget,
)

from app.services import CreateRecipeIngredientInput
from app.utils.i18n import translate


class IngredientFormRow(QWidget):
    remove_requested = Signal(QWidget)

    def __init__(self, units: list[tuple[int, str]], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("editorRow")
        self._language_code = "en"
        self._build_ui(units)

    def _build_ui(self, units: list[tuple[int, str]]) -> None:
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(10)

        self.name_en_input = QLineEdit()
        self.name_en_input.setObjectName("searchInput")
        self.name_en_input.setPlaceholderText("")
        layout.addWidget(self.name_en_input, 0, 0, 1, 2)

        self.name_ar_input = QLineEdit()
        self.name_ar_input.setObjectName("searchInput")
        self.name_ar_input.setPlaceholderText("")
        layout.addWidget(self.name_ar_input, 0, 2, 1, 2)

        self.name_ru_input = QLineEdit()
        self.name_ru_input.setObjectName("searchInput")
        self.name_ru_input.setPlaceholderText("")
        layout.addWidget(self.name_ru_input, 1, 0, 1, 2)

        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setObjectName("spinField")
        self.quantity_input.setDecimals(3)
        self.quantity_input.setMaximum(99999)
        self.quantity_input.setMinimum(0)
        self.quantity_input.setSpecialValueText("")
        self.quantity_input.setValue(0)
        layout.addWidget(self.quantity_input, 2, 0)

        self.unit_combo = QComboBox()
        self.unit_combo.setObjectName("comboField")
        self.unit_combo.addItem("", None)
        for unit_id, label in units:
            self.unit_combo.addItem(label, unit_id)
        layout.addWidget(self.unit_combo, 2, 1)

        self.quantity_override_input = QLineEdit()
        self.quantity_override_input.setObjectName("searchInput")
        self.quantity_override_input.setPlaceholderText("")
        layout.addWidget(self.quantity_override_input, 2, 2)

        self.preparation_note_input = QLineEdit()
        self.preparation_note_input.setObjectName("searchInput")
        self.preparation_note_input.setPlaceholderText("")
        layout.addWidget(self.preparation_note_input, 2, 3)

        self.scalable_checkbox = QCheckBox()
        self.scalable_checkbox.setChecked(True)
        layout.addWidget(self.scalable_checkbox, 3, 0)

        self.remove_button = QPushButton()
        self.remove_button.setObjectName("secondaryButton")
        self.remove_button.clicked.connect(lambda: self.remove_requested.emit(self))
        layout.addWidget(self.remove_button, 3, 3)

        self.set_language("en")

    def set_language(self, language_code: str) -> None:
        self._language_code = language_code
        self.name_en_input.setPlaceholderText(translate(language_code, "ingredient.name_en"))
        self.name_ar_input.setPlaceholderText(translate(language_code, "ingredient.name_ar"))
        self.name_ru_input.setPlaceholderText(translate(language_code, "ingredient.name_ru"))
        self.quantity_override_input.setPlaceholderText(translate(language_code, "ingredient.quantity_override"))
        self.preparation_note_input.setPlaceholderText(translate(language_code, "ingredient.preparation_note"))
        self.scalable_checkbox.setText(translate(language_code, "ingredient.scalable"))
        self.remove_button.setText(translate(language_code, "ingredient.remove"))
        self.unit_combo.setItemText(0, translate(language_code, "ingredient.no_unit"))

    def to_input(self) -> CreateRecipeIngredientInput:
        quantity = Decimal(str(self.quantity_input.value())) if self.quantity_input.value() > 0 else None
        return CreateRecipeIngredientInput(
            name_en=self.name_en_input.text(),
            name_ar=self.name_ar_input.text() or None,
            name_ru=self.name_ru_input.text() or None,
            quantity=quantity,
            unit_id=self.unit_combo.currentData(),
            is_scalable=self.scalable_checkbox.isChecked(),
            preparation_note=self.preparation_note_input.text() or None,
            quantity_text_override=self.quantity_override_input.text() or None,
        )

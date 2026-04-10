from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QWidget,
)

from app.services import CreateRecipeStepInput


class StepFormRow(QWidget):
    remove_requested = Signal(QWidget)

    def __init__(self, step_number: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.step_number = step_number
        self.setObjectName("editorRow")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(10)

        self.step_label = QLabel(f"Step {self.step_number}")
        self.step_label.setObjectName("eyebrowLabel")
        layout.addWidget(self.step_label, 0, 0)

        self.remove_button = QPushButton("Remove")
        self.remove_button.setObjectName("secondaryButton")
        self.remove_button.clicked.connect(lambda: self.remove_requested.emit(self))
        layout.addWidget(self.remove_button, 0, 1)

        self.instruction_en_input = QTextEdit()
        self.instruction_en_input.setObjectName("multilineField")
        self.instruction_en_input.setPlaceholderText("Instruction in English")
        self.instruction_en_input.setFixedHeight(88)
        layout.addWidget(self.instruction_en_input, 1, 0, 1, 2)

        self.instruction_ar_input = QTextEdit()
        self.instruction_ar_input.setObjectName("multilineField")
        self.instruction_ar_input.setPlaceholderText("Instruction in Arabic (optional)")
        self.instruction_ar_input.setFixedHeight(88)
        layout.addWidget(self.instruction_ar_input, 1, 2, 1, 2)

        self.estimated_minutes_input = QSpinBox()
        self.estimated_minutes_input.setObjectName("spinField")
        self.estimated_minutes_input.setMinimum(0)
        self.estimated_minutes_input.setMaximum(9999)
        self.estimated_minutes_input.setSpecialValueText("")
        layout.addWidget(self.estimated_minutes_input, 0, 3)

    def set_step_number(self, step_number: int) -> None:
        self.step_number = step_number
        self.step_label.setText(f"Step {step_number}")

    def to_input(self) -> CreateRecipeStepInput:
        estimated = self.estimated_minutes_input.value()
        return CreateRecipeStepInput(
            instruction_en=self.instruction_en_input.toPlainText(),
            instruction_ar=self.instruction_ar_input.toPlainText() or None,
            estimated_minutes=estimated if estimated > 0 else None,
        )

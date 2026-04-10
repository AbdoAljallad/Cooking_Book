from PySide6.QtWidgets import QPushButton, QWidget


class PrimaryButton(QPushButton):
    """Primary call-to-action button placeholder."""

    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setObjectName("primaryButton")

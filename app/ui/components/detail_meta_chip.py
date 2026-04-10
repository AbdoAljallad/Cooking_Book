from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class DetailMetaChip(QWidget):
    def __init__(self, label: str, value: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("detailMetaChip")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        label_widget = QLabel(label)
        label_widget.setObjectName("detailMetaLabel")
        layout.addWidget(label_widget)

        value_widget = QLabel(value)
        value_widget.setObjectName("detailMetaValue")
        layout.addWidget(value_widget)

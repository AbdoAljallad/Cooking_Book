from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class EmptyState(QWidget):
    def __init__(
        self,
        title: str,
        description: str,
        badge_text: str = "No recipes yet",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("emptyState")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(8)

        self.badge = QLabel(badge_text)
        self.badge.setObjectName("eyebrowLabel")
        self.badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.badge)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("emptyStateTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        self.description_label = QLabel(description)
        self.description_label.setObjectName("emptyStateDescription")
        self.description_label.setWordWrap(True)
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.description_label)

    def set_content(self, title: str, description: str, badge_text: str | None = None) -> None:
        if badge_text is not None:
            self.badge.setText(badge_text)
        self.title_label.setText(title)
        self.description_label.setText(description)

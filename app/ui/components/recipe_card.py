from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QWidget

from app.repositories import RecipeListItem
from app.services.image_service import ImageService
from app.ui.components.base_card import BaseCard
from app.utils.i18n import translate


class RecipeCard(BaseCard):
    clicked = Signal(int)

    def __init__(
        self,
        recipe: RecipeListItem,
        image_service: ImageService,
        language_code: str = "en",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("recipeCard")
        self.recipe = recipe
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        image_label = QLabel()
        image_label.setObjectName("recipeImage")
        image_label.setMinimumHeight(150)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_path = image_service.resolve_display_path(recipe.image_path)
        image_label.setPixmap(
            QPixmap(str(image_path)).scaled(
                420,
                150,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        self.content_layout.addWidget(image_label)

        category_label = QLabel(recipe.category_name or recipe.category_slug.replace("_", " ").title())
        category_label.setObjectName("eyebrowLabel")
        self.content_layout.addWidget(category_label)

        title_label = QLabel(recipe.title)
        title_label.setObjectName("recipeCardTitle")
        title_label.setWordWrap(True)
        self.content_layout.addWidget(title_label)

        description = recipe.short_description or translate(language_code, "recipe_card.description_fallback")
        description_label = QLabel(description)
        description_label.setObjectName("recipeCardDescription")
        description_label.setWordWrap(True)
        self.content_layout.addWidget(description_label)

        meta_label = QLabel(
            translate(
                language_code,
                "recipe_card.meta",
                total=recipe.total_time_minutes,
                servings=recipe.base_servings,
                difficulty=recipe.difficulty_level.title(),
            )
        )
        meta_label.setObjectName("recipeCardMeta")
        meta_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content_layout.addWidget(meta_label)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.recipe.id)
        super().mousePressEvent(event)

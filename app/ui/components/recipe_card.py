from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QSizePolicy, QWidget

from app.repositories import RecipeListItem
from app.services.image_service import ImageService
from app.ui.components.base_card import BaseCard
from app.utils.i18n import translate


class RecipeCard(BaseCard):
    clicked = Signal(int)
    IMAGE_WIDTH = 336
    IMAGE_HEIGHT = 174
    CARD_PADDING = 14

    def __init__(
        self,
        recipe: RecipeListItem,
        image_service: ImageService,
        language_code: str = "en",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("recipeCard")
        self.image_service = image_service
        self.content_layout.setContentsMargins(
            self.CARD_PADDING,
            self.CARD_PADDING,
            self.CARD_PADDING,
            self.CARD_PADDING,
        )
        self.recipe = recipe
        self._current_card_width: int | None = None
        self.setMinimumWidth(self.IMAGE_WIDTH)
        self.setMaximumWidth(390)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        image_label = QLabel()
        image_label.setObjectName("recipeImage")
        image_label.setFixedHeight(self.IMAGE_HEIGHT)
        image_label.setMinimumWidth(self.IMAGE_WIDTH)
        image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label = image_label
        self._update_image(self.IMAGE_WIDTH)
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

        if recipe.tags:
            tags_label = QLabel("  ".join(recipe.tags[:3]))
            tags_label.setObjectName("tagPill")
            tags_label.setWordWrap(True)
            self.content_layout.addWidget(tags_label)

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

    def set_card_width(self, width: int) -> None:
        safe_width = max(260, min(width, 390))
        if self._current_card_width == safe_width:
            return

        self._current_card_width = safe_width
        self.setFixedWidth(safe_width)
        image_width = max(220, safe_width - (self.CARD_PADDING * 2))
        self.image_label.setFixedWidth(image_width)
        self._update_image(image_width)

    def _update_image(self, width: int) -> None:
        self.image_label.setPixmap(
            self.image_service.get_cover_pixmap(
                self.recipe.image_path,
                width,
                self.IMAGE_HEIGHT,
            )
        )

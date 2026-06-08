from __future__ import annotations

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QGridLayout, QScrollArea, QVBoxLayout, QWidget

from app.services import AppContextService, RecipeService
from app.services.image_service import ImageService
from app.ui.components.base_card import BaseCard
from app.ui.components.empty_state import EmptyState
from app.ui.components.recipe_card import RecipeCard
from app.ui.components.section_header import SectionHeader
from app.utils.i18n import translate


class FavoritesPage(QWidget):
    recipe_selected = Signal(int)

    def __init__(
        self,
        recipe_service: RecipeService,
        context_service: AppContextService,
        image_service: ImageService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.recipe_service = recipe_service
        self.context_service = context_service
        self.image_service = image_service
        self._cards: list[RecipeCard] = []
        self._last_columns: int | None = None
        self._last_card_width: int | None = None
        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self._apply_responsive_layout)
        self._build_ui()
        self.reload()

    def _build_ui(self) -> None:
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        outer_layout.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        self.page_layout = QVBoxLayout(container)
        self.page_layout.setContentsMargins(0, 0, 0, 0)
        self.page_layout.setSpacing(24)

        self.hero_card = BaseCard()
        self.hero_header = SectionHeader("", "")
        self.hero_card.content_layout.addWidget(self.hero_header)
        self.page_layout.addWidget(self.hero_card)

        self.grid_card = BaseCard()
        self.grid_header = SectionHeader("", "")
        self.grid_card.content_layout.addWidget(self.grid_header)
        self.recipe_grid = QGridLayout()
        self.recipe_grid.setHorizontalSpacing(16)
        self.recipe_grid.setVerticalSpacing(16)
        self.grid_card.content_layout.addLayout(self.recipe_grid)
        self.page_layout.addWidget(self.grid_card)

        self.empty_state = EmptyState("", "")
        self.page_layout.addWidget(self.empty_state)

    def reload(self) -> None:
        context = self.context_service.get_context()
        language_code = context.language_code
        self.hero_header.set_content(
            translate(language_code, "favorites.hero_title"),
            translate(language_code, "favorites.hero_subtitle"),
        )
        self.grid_header.set_content(
            translate(language_code, "favorites.saved_title"),
            translate(language_code, "favorites.saved_subtitle"),
        )
        self.empty_state.set_content(
            translate(language_code, "favorites.empty_title"),
            translate(language_code, "favorites.empty_description"),
            badge_text=translate(language_code, "favorites.empty_badge"),
        )

        recipes = self.recipe_service.list_favorite_recipes(
            profile_id=context.profile_id,
            language_code=context.language_code,
            limit=30,
        )

        self._cards = []
        self._clear_grid()
        columns = self._recipe_columns()
        card_width = self._recipe_card_width(columns)
        for index, recipe in enumerate(recipes):
            row = index // columns
            column = index % columns
            card = RecipeCard(recipe, self.image_service, context.language_code)
            card.set_card_width(card_width)
            card.clicked.connect(self.recipe_selected.emit)
            self._cards.append(card)
            self.recipe_grid.addWidget(card, row, column)

        self._last_columns = columns
        self._last_card_width = card_width

        self.grid_card.setVisible(bool(recipes))
        self.empty_state.setVisible(not recipes)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self._cards:
            self._resize_timer.start(80)

    def _apply_responsive_layout(self) -> None:
        columns = self._recipe_columns()
        card_width = self._recipe_card_width(columns)
        if columns == self._last_columns and card_width == self._last_card_width:
            return

        self.setUpdatesEnabled(False)
        try:
            self._clear_grid(preserve_existing=True)
            for index, card in enumerate(self._cards):
                card.set_card_width(card_width)
                self.recipe_grid.addWidget(card, index // columns, index % columns)
        finally:
            self.setUpdatesEnabled(True)

        self._last_columns = columns
        self._last_card_width = card_width

    def _clear_grid(self, preserve_existing: bool = False) -> None:
        while self.recipe_grid.count():
            item = self.recipe_grid.takeAt(0)
            widget = item.widget()
            if widget is not None and not preserve_existing:
                widget.deleteLater()

    def _recipe_columns(self) -> int:
        width = max(self.width() - 80, 280)
        return max(1, min(3, width // 340))

    def _recipe_card_width(self, columns: int) -> int:
        width = max(self.width() - 120, 280)
        return max(280, min(380, (width - ((columns - 1) * 16)) // max(columns, 1)))

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QScrollArea, QVBoxLayout, QWidget

from app.services import AppContextService, RecipeService
from app.services.image_service import ImageService
from app.ui.components.base_card import BaseCard
from app.ui.components.empty_state import EmptyState
from app.ui.components.recipe_card import RecipeCard
from app.ui.components.section_header import SectionHeader


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
        self.hero_card.setObjectName("heroCard")
        self.hero_card.content_layout.addWidget(
            SectionHeader("Favorites", "A personal shelf for the recipes you want close at hand.")
        )
        self.page_layout.addWidget(self.hero_card)

        self.grid_card = BaseCard()
        self.grid_card.content_layout.addWidget(
            SectionHeader("Saved Recipes", "Profile-scoped favorites rendered with the same discovery cards used across the app.")
        )
        self.recipe_grid = QGridLayout()
        self.recipe_grid.setHorizontalSpacing(16)
        self.recipe_grid.setVerticalSpacing(16)
        self.grid_card.content_layout.addLayout(self.recipe_grid)
        self.page_layout.addWidget(self.grid_card)

        self.empty_state = EmptyState(
            "No favorites yet.",
            "Mark recipes as favorites from the details screen and they will collect here for quick access.",
            badge_text="Favorites empty",
        )
        self.page_layout.addWidget(self.empty_state)

    def reload(self) -> None:
        context = self.context_service.get_context()
        recipes = self.recipe_service.list_favorite_recipes(
            profile_id=context.profile_id,
            language_code=context.language_code,
            limit=30,
        )

        self._clear_grid()
        for index, recipe in enumerate(recipes):
            row = index // 3
            column = index % 3
            card = RecipeCard(recipe, self.image_service, context.language_code)
            card.clicked.connect(self.recipe_selected.emit)
            self.recipe_grid.addWidget(card, row, column)

        self.grid_card.setVisible(bool(recipes))
        self.empty_state.setVisible(not recipes)

    def _clear_grid(self) -> None:
        while self.recipe_grid.count():
            item = self.recipe_grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

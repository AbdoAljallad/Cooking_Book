from __future__ import annotations

from PySide6.QtCore import Signal
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

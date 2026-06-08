from __future__ import annotations

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QGridLayout, QScrollArea, QVBoxLayout, QWidget

from app.services import AppContextService, CategoryService, RecipeService
from app.services.image_service import ImageService
from app.ui.components.base_card import BaseCard
from app.ui.components.category_chip import CategoryChip
from app.ui.components.empty_state import EmptyState
from app.ui.components.recipe_card import RecipeCard
from app.ui.components.section_header import SectionHeader
from app.utils.i18n import translate


class CategoriesPage(QWidget):
    recipe_selected = Signal(int)

    def __init__(
        self,
        context_service: AppContextService,
        category_service: CategoryService,
        recipe_service: RecipeService,
        image_service: ImageService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.context_service = context_service
        self.category_service = category_service
        self.recipe_service = recipe_service
        self.image_service = image_service
        self._selected_category_slug: str | None = None
        self._category_widgets: list[CategoryChip] = []
        self._recipe_cards: list[RecipeCard] = []
        self._last_chip_columns: int | None = None
        self._last_recipe_columns: int | None = None
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

        self.categories_card = BaseCard()
        self.categories_header = SectionHeader("", "")
        self.categories_card.content_layout.addWidget(self.categories_header)
        self.categories_grid = QGridLayout()
        self.categories_grid.setHorizontalSpacing(10)
        self.categories_grid.setVerticalSpacing(10)
        self.categories_card.content_layout.addLayout(self.categories_grid)
        self.page_layout.addWidget(self.categories_card)

        self.recipes_card = BaseCard()
        self.recipes_header = SectionHeader("", "")
        self.recipes_card.content_layout.addWidget(self.recipes_header)
        self.recipe_grid = QGridLayout()
        self.recipe_grid.setHorizontalSpacing(16)
        self.recipe_grid.setVerticalSpacing(16)
        self.recipes_card.content_layout.addLayout(self.recipe_grid)
        self.page_layout.addWidget(self.recipes_card)

        self.empty_state = EmptyState("", "")
        self.page_layout.addWidget(self.empty_state)

    def reload(self) -> None:
        context = self.context_service.get_context()
        language_code = context.language_code
        categories = self.category_service.list_categories(language_code)

        self.hero_header.set_content(
            translate(language_code, "categories.title"),
            translate(language_code, "categories.subtitle"),
        )
        self.categories_header.set_content(
            translate(language_code, "categories.browse_title"),
            translate(language_code, "categories.browse_subtitle"),
        )

        if categories and self._selected_category_slug is None:
            self._selected_category_slug = categories[0].slug
        elif categories and self._selected_category_slug not in {item.slug for item in categories}:
            self._selected_category_slug = categories[0].slug
        elif not categories:
            self._selected_category_slug = None

        self._populate_category_chips(categories, language_code)
        self._populate_recipe_cards(language_code)

    def _populate_category_chips(self, categories, language_code: str) -> None:
        self._clear_grid(self.categories_grid)
        self._category_widgets = []
        columns = self._chip_columns()

        for index, category in enumerate(categories):
            chip = CategoryChip(category.slug, category.display_name)
            chip.setChecked(category.slug == self._selected_category_slug)
            chip.selected_changed.connect(self._handle_category_selected)
            self._category_widgets.append(chip)
            self.categories_grid.addWidget(chip, index // columns, index % columns)

        self._last_chip_columns = columns
        self.categories_card.setVisible(bool(categories))

        if not categories:
            self.recipes_card.hide()
            self.empty_state.set_content(
                translate(language_code, "categories.empty_title"),
                translate(language_code, "categories.empty_description"),
                badge_text=translate(language_code, "categories.badge"),
            )
            self.empty_state.show()

    def _populate_recipe_cards(self, language_code: str) -> None:
        self._clear_grid(self.recipe_grid)
        self._recipe_cards = []

        if self._selected_category_slug is None:
            self.recipes_card.hide()
            return

        recipes = self.recipe_service.list_by_category(
            self._selected_category_slug,
            language_code,
        )

        columns = self._recipe_columns()
        card_width = self._recipe_card_width(columns)

        for index, recipe in enumerate(recipes):
            card = RecipeCard(recipe, self.image_service, language_code)
            card.set_card_width(card_width)
            card.clicked.connect(self.recipe_selected.emit)
            self._recipe_cards.append(card)
            self.recipe_grid.addWidget(card, index // columns, index % columns)

        self._last_recipe_columns = columns
        self._last_card_width = card_width

        self.recipes_header.set_content(
            translate(language_code, "categories.recipes_title"),
            translate(language_code, "categories.recipes_subtitle"),
        )
        self.recipes_card.setVisible(bool(recipes))
        self.empty_state.setVisible(not recipes)

        if not recipes:
            self.empty_state.set_content(
                translate(language_code, "categories.no_recipes_title"),
                translate(language_code, "categories.no_recipes_description"),
                badge_text=translate(language_code, "categories.badge"),
            )

    def _handle_category_selected(self, slug: str, checked: bool) -> None:
        if not checked:
            return
        self._selected_category_slug = slug
        self.reload()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self._category_widgets or self._recipe_cards:
            self._resize_timer.start(80)

    def _apply_responsive_layout(self) -> None:
        chip_columns = self._chip_columns()
        if chip_columns != self._last_chip_columns:
            self._relayout_grid(self.categories_grid, self._category_widgets, chip_columns)
            self._last_chip_columns = chip_columns

        recipe_columns = self._recipe_columns()
        card_width = self._recipe_card_width(recipe_columns)
        if recipe_columns == self._last_recipe_columns and card_width == self._last_card_width:
            return

        self.setUpdatesEnabled(False)
        try:
            for card in self._recipe_cards:
                card.set_card_width(card_width)
            self._relayout_grid(self.recipe_grid, self._recipe_cards, recipe_columns)
        finally:
            self.setUpdatesEnabled(True)

        self._last_recipe_columns = recipe_columns
        self._last_card_width = card_width

    @staticmethod
    def _clear_grid(layout: QGridLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    @staticmethod
    def _relayout_grid(layout: QGridLayout, widgets: list[QWidget], columns: int) -> None:
        while layout.count():
            layout.takeAt(0)

        safe_columns = max(columns, 1)
        for index, widget in enumerate(widgets):
            layout.addWidget(widget, index // safe_columns, index % safe_columns)

    def _chip_columns(self) -> int:
        width = max(self.width() - 80, 220)
        return max(1, min(6, width // 180))

    def _recipe_columns(self) -> int:
        width = max(self.width() - 80, 280)
        return max(1, min(3, width // 340))

    def _recipe_card_width(self, columns: int) -> int:
        width = max(self.width() - 120, 280)
        return max(280, min(380, (width - ((columns - 1) * 16)) // max(columns, 1)))

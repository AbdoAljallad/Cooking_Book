from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from app.repositories import RecipeListItem
from app.services import HomeDashboardData, HomeService
from app.services.image_service import ImageService
from app.ui.components.base_card import BaseCard
from app.ui.components.category_chip import CategoryChip
from app.ui.components.empty_state import EmptyState
from app.ui.components.recipe_card import RecipeCard
from app.ui.components.search_bar import SearchBar
from app.ui.components.section_header import SectionHeader
from app.utils.i18n import language_label, translate


class HomePage(QWidget):
    recipe_selected = Signal(int)

    def __init__(self, home_service: HomeService, image_service: ImageService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.home_service = home_service
        self.image_service = image_service
        self._dashboard_data: HomeDashboardData | None = None
        self._search_text = ""
        self._selected_category_slug: str | None = None
        self._latest_recipes: list[RecipeListItem] = []
        self._featured_recipes: list[RecipeListItem] = []
        self._tag_widgets: list[QLabel] = []
        self._category_widgets: list[CategoryChip] = []
        self._featured_cards: list[RecipeCard] = []
        self._latest_cards: list[RecipeCard] = []
        self._last_chip_columns: int | None = None
        self._last_recipe_columns: int | None = None
        self._last_featured_columns: int | None = None
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
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setObjectName("pageScrollArea")
        outer_layout.addWidget(scroll)

        container = QWidget()
        container.setObjectName("homePage")
        scroll.setWidget(container)

        self.page_layout = QVBoxLayout(container)
        self.page_layout.setContentsMargins(0, 0, 0, 0)
        self.page_layout.setSpacing(28)

        self.hero_card = BaseCard()
        self.hero_card.setObjectName("heroCard")
        self.page_layout.addWidget(self.hero_card)

        self.eyebrow_label = QLabel()
        self.eyebrow_label.setObjectName("eyebrowLabel")
        self.hero_card.content_layout.addWidget(self.eyebrow_label)

        self.hero_title = QLabel()
        self.hero_title.setObjectName("heroTitle")
        self.hero_title.setWordWrap(True)
        self.hero_card.content_layout.addWidget(self.hero_title)

        self.hero_subtitle = QLabel()
        self.hero_subtitle.setObjectName("heroSubtitle")
        self.hero_subtitle.setWordWrap(True)
        self.hero_card.content_layout.addWidget(self.hero_subtitle)

        self.search_bar = SearchBar("")
        self.search_bar.search_requested.connect(self._handle_search)
        self.search_bar.clear_requested.connect(self._clear_filters)
        self.hero_card.content_layout.addWidget(self.search_bar)

        self.tag_grid = QGridLayout()
        self.tag_grid.setHorizontalSpacing(8)
        self.tag_grid.setVerticalSpacing(8)
        self.hero_card.content_layout.addLayout(self.tag_grid)

        self.active_filters_card = BaseCard()
        self.active_filters_header = SectionHeader("", "")
        self.active_filters_card.content_layout.addWidget(self.active_filters_header)
        active_row = QHBoxLayout()
        active_row.setSpacing(12)
        self.active_filters_label = QLabel()
        self.active_filters_label.setObjectName("heroSubtitle")
        self.active_filters_label.setWordWrap(True)
        active_row.addWidget(self.active_filters_label, stretch=1)
        self.clear_filters_button = QPushButton()
        self.clear_filters_button.setObjectName("secondaryButton")
        self.clear_filters_button.clicked.connect(self._clear_filters)
        active_row.addWidget(self.clear_filters_button)
        self.active_filters_card.content_layout.addLayout(active_row)
        self.page_layout.addWidget(self.active_filters_card)

        self.category_section = BaseCard()
        self.category_header = SectionHeader("", "")
        self.category_section.content_layout.addWidget(self.category_header)
        self.category_grid = QGridLayout()
        self.category_grid.setHorizontalSpacing(10)
        self.category_grid.setVerticalSpacing(10)
        self.category_section.content_layout.addLayout(self.category_grid)
        self.page_layout.addWidget(self.category_section)

        self.featured_section = BaseCard()
        self.featured_header = SectionHeader("", "")
        self.featured_section.content_layout.addWidget(self.featured_header)
        self.featured_grid = QGridLayout()
        self.featured_grid.setHorizontalSpacing(16)
        self.featured_grid.setVerticalSpacing(16)
        self.featured_section.content_layout.addLayout(self.featured_grid)
        self.page_layout.addWidget(self.featured_section)

        self.latest_section = BaseCard()
        self.latest_header = SectionHeader("", "")
        self.latest_section.content_layout.addWidget(self.latest_header)
        self.latest_grid = QGridLayout()
        self.latest_grid.setHorizontalSpacing(16)
        self.latest_grid.setVerticalSpacing(16)
        self.latest_section.content_layout.addLayout(self.latest_grid)
        self.page_layout.addWidget(self.latest_section)

        self.empty_state = EmptyState("", "")
        self.page_layout.addWidget(self.empty_state)
        self.active_filters_card.hide()

    def reload(self) -> None:
        self._search_text = ""
        self._selected_category_slug = None
        self._dashboard_data = self.home_service.get_dashboard_data()
        self._apply_dashboard(self._dashboard_data)

    def _apply_dashboard(self, dashboard: HomeDashboardData) -> None:
        self._search_text = dashboard.search_text
        self._selected_category_slug = dashboard.selected_category_slug
        language_code = dashboard.context.language_code

        self._apply_translations(language_code)
        self.search_bar.set_language(language_code, translate(language_code, "home.search_placeholder"))
        self.hero_subtitle.setText(
            translate(
                language_code,
                "home.subtitle",
                profile_name=dashboard.context.profile_name,
                language_name=language_label(language_code),
            )
        )
        self.search_bar.set_text(dashboard.search_text)
        self._populate_tags(dashboard)
        self._populate_categories(dashboard)
        self._update_active_filters(dashboard)
        self._render_recipe_sections(dashboard.latest_recipes, dashboard.featured_recipes)

    def _apply_translations(self, language_code: str) -> None:
        self.eyebrow_label.setText(translate(language_code, "home.eyebrow"))
        self.hero_title.setText(translate(language_code, "home.title"))
        self.active_filters_header.set_content(
            translate(language_code, "home.active_view_title"),
            translate(language_code, "home.active_view_subtitle"),
        )
        self.clear_filters_button.setText(translate(language_code, "home.clear_filters"))
        self.category_header.set_content(
            translate(language_code, "home.browse_categories_title"),
            translate(language_code, "home.browse_categories_subtitle"),
        )
        self.featured_header.set_content(
            translate(language_code, "home.featured_title"),
            translate(language_code, "home.featured_subtitle"),
        )
        self.latest_header.set_content(
            translate(language_code, "home.latest_title"),
            translate(language_code, "home.latest_subtitle"),
        )

    def _populate_tags(self, dashboard: HomeDashboardData) -> None:
        self._clear_grid(self.tag_grid)
        self._tag_widgets = []
        columns = self._chip_columns()
        for index, tag in enumerate(dashboard.tags[:8]):
            tag_label = QLabel(tag.display_name)
            tag_label.setObjectName("tagPill")
            self._tag_widgets.append(tag_label)
            self.tag_grid.addWidget(tag_label, index // columns, index % columns)
        self._last_chip_columns = columns

    def _populate_categories(self, dashboard: HomeDashboardData) -> None:
        self._clear_grid(self.category_grid)
        language_code = dashboard.context.language_code
        chips: list[CategoryChip] = []

        all_chip = CategoryChip("all", translate(language_code, "home.category.all"))
        all_chip.setChecked(self._selected_category_slug in {None, "all"})
        all_chip.selected_changed.connect(self._handle_category_selected)
        chips.append(all_chip)

        for category in dashboard.categories:
            chip = CategoryChip(category.slug, category.display_name)
            chip.setChecked(category.slug == self._selected_category_slug)
            chip.selected_changed.connect(self._handle_category_selected)
            chips.append(chip)

        columns = self._chip_columns()
        for index, chip in enumerate(chips):
            self.category_grid.addWidget(chip, index // columns, index % columns)
        self._category_widgets = chips
        self._last_chip_columns = columns

    def _handle_category_selected(self, slug: str, checked: bool) -> None:
        self._selected_category_slug = None if slug == "all" else (slug if checked else None)
        self._refresh_filtered_dashboard()

    def _handle_search(self, query_text: str) -> None:
        self._search_text = query_text.strip()
        self._refresh_filtered_dashboard()

    def _clear_filters(self) -> None:
        self._search_text = ""
        self._selected_category_slug = None
        self._refresh_filtered_dashboard()

    def _refresh_filtered_dashboard(self) -> None:
        dashboard = self.home_service.get_filtered_dashboard_data(
            query_text=self._search_text,
            category_slug=self._selected_category_slug,
        )
        self._dashboard_data = dashboard
        self._apply_dashboard(dashboard)

    def _update_active_filters(self, dashboard: HomeDashboardData) -> None:
        if not dashboard.has_active_filters:
            self.active_filters_card.hide()
            return

        language_code = dashboard.context.language_code
        parts: list[str] = []
        if dashboard.search_text:
            parts.append(translate(language_code, "home.filter.search", value=dashboard.search_text))
        if dashboard.selected_category_name:
            parts.append(translate(language_code, "home.filter.category", value=dashboard.selected_category_name))
        self.active_filters_label.setText(" - ".join(parts))
        self.active_filters_card.show()

    def _render_recipe_sections(self, recipes: list[RecipeListItem], featured_recipes: list[RecipeListItem]) -> None:
        self._clear_grid(self.featured_grid)
        self._clear_grid(self.latest_grid)
        language_code = self._dashboard_data.context.language_code if self._dashboard_data else "en"
        self._latest_recipes = recipes
        self._featured_recipes = featured_recipes
        latest_columns = self._recipe_columns()
        featured_columns = min(3, latest_columns)
        card_width = self._recipe_card_width(latest_columns)
        self._featured_cards = []
        self._latest_cards = []

        for index, recipe in enumerate(featured_recipes[:3]):
            card = RecipeCard(recipe, self.image_service, language_code)
            card.set_card_width(card_width)
            card.clicked.connect(self.recipe_selected.emit)
            self._featured_cards.append(card)
            self.featured_grid.addWidget(card, index // featured_columns, index % featured_columns)

        for index, recipe in enumerate(recipes):
            row = index // latest_columns
            column = index % latest_columns
            card = RecipeCard(recipe, self.image_service, language_code)
            card.set_card_width(card_width)
            card.clicked.connect(self.recipe_selected.emit)
            self._latest_cards.append(card)
            self.latest_grid.addWidget(card, row, column)

        self._last_recipe_columns = latest_columns
        self._last_featured_columns = featured_columns
        self._last_card_width = card_width

        has_recipes = bool(recipes)
        self.featured_section.setVisible(bool(featured_recipes))
        self.latest_section.setVisible(has_recipes)
        if not has_recipes:
            if self._dashboard_data is not None and self._dashboard_data.has_active_filters:
                self.empty_state.set_content(
                    translate(language_code, "home.no_matches_title"),
                    translate(language_code, "home.no_matches_description"),
                    badge_text=translate(language_code, "home.no_matches_badge"),
                )
            else:
                self.empty_state.set_content(
                    translate(language_code, "home.empty_title"),
                    translate(language_code, "home.empty_description"),
                    badge_text=translate(language_code, "home.empty_badge"),
                )
        self.empty_state.setVisible(not has_recipes)

    @staticmethod
    def _clear_grid(layout: QGridLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self._dashboard_data is not None:
            self._resize_timer.start(80)

    def _recipe_columns(self) -> int:
        width = max(self.width() - 80, 280)
        return max(1, min(4, width // 340))

    def _recipe_card_width(self, columns: int) -> int:
        width = max(self.width() - 120, 280)
        return max(280, min(380, (width - ((columns - 1) * 16)) // max(columns, 1)))

    def _chip_columns(self) -> int:
        width = max(self.width() - 80, 220)
        return max(1, min(6, width // 180))

    def _apply_responsive_layout(self) -> None:
        chip_columns = self._chip_columns()
        if chip_columns != self._last_chip_columns:
            self._relayout_grid(self.tag_grid, self._tag_widgets, chip_columns)
            self._relayout_grid(self.category_grid, self._category_widgets, chip_columns)
            self._last_chip_columns = chip_columns

        recipe_columns = self._recipe_columns()
        featured_columns = min(3, recipe_columns)
        card_width = self._recipe_card_width(recipe_columns)

        should_relayout_cards = (
            recipe_columns != self._last_recipe_columns
            or featured_columns != self._last_featured_columns
            or card_width != self._last_card_width
        )
        if not should_relayout_cards:
            return

        self.setUpdatesEnabled(False)
        try:
            for card in self._featured_cards:
                card.set_card_width(card_width)
            for card in self._latest_cards:
                card.set_card_width(card_width)

            self._relayout_grid(self.featured_grid, self._featured_cards, featured_columns)
            self._relayout_grid(self.latest_grid, self._latest_cards, recipe_columns)
        finally:
            self.setUpdatesEnabled(True)

        self._last_recipe_columns = recipe_columns
        self._last_featured_columns = featured_columns
        self._last_card_width = card_width

    @staticmethod
    def _relayout_grid(layout: QGridLayout, widgets: list[QWidget], columns: int) -> None:
        while layout.count():
            layout.takeAt(0)

        safe_columns = max(columns, 1)
        for index, widget in enumerate(widgets):
            layout.addWidget(widget, index // safe_columns, index % safe_columns)

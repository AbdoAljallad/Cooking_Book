from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.repositories import RecipeListItem
from app.services import HomeDashboardData, HomeService
from app.services.image_service import ImageService
from app.ui.components.base_card import BaseCard
from app.ui.components.category_chip import CategoryChip
from app.ui.components.empty_state import EmptyState
from app.ui.components.recipe_card import RecipeCard
from app.ui.components.search_bar import SearchBar
from app.ui.components.section_header import SectionHeader
from app.utils.i18n import translate


class HomePage(QWidget):
    recipe_selected = Signal(int)

    def __init__(self, home_service: HomeService, image_service: ImageService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.home_service = home_service
        self.image_service = image_service
        self._dashboard_data: HomeDashboardData | None = None
        self._search_text: str = ""
        self._selected_category_slug: str | None = None

        self._build_ui()
        self.reload()

    def _build_ui(self) -> None:
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
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

        self.eyebrow_label = QLabel("Curated kitchen workspace")
        self.eyebrow_label.setObjectName("eyebrowLabel")
        self.hero_card.content_layout.addWidget(self.eyebrow_label)

        self.hero_title = QLabel("Cook beautifully, even before the first recipe lands.")
        self.hero_title.setObjectName("heroTitle")
        self.hero_title.setWordWrap(True)
        self.hero_card.content_layout.addWidget(self.hero_title)

        self.hero_subtitle = QLabel()
        self.hero_subtitle.setObjectName("heroSubtitle")
        self.hero_subtitle.setWordWrap(True)
        self.hero_card.content_layout.addWidget(self.hero_subtitle)

        self.search_bar = SearchBar("Search recipes, ingredients, or inspiration")
        self.search_bar.search_requested.connect(self._handle_search)
        self.search_bar.clear_requested.connect(self._clear_filters)
        self.hero_card.content_layout.addWidget(self.search_bar)

        self.tag_row = QHBoxLayout()
        self.tag_row.setSpacing(8)
        self.hero_card.content_layout.addLayout(self.tag_row)

        self.active_filters_card = BaseCard()
        self.active_filters_card.content_layout.addWidget(
            SectionHeader("Active View", "Search and category filters are applied through the service layer.")
        )
        active_row = QHBoxLayout()
        active_row.setSpacing(12)
        self.active_filters_label = QLabel()
        self.active_filters_label.setObjectName("heroSubtitle")
        self.active_filters_label.setWordWrap(True)
        active_row.addWidget(self.active_filters_label, stretch=1)
        self.clear_filters_button = QPushButton("Clear Filters")
        self.clear_filters_button.setObjectName("secondaryButton")
        self.clear_filters_button.clicked.connect(self._clear_filters)
        active_row.addWidget(self.clear_filters_button)
        self.active_filters_card.content_layout.addLayout(active_row)
        self.page_layout.addWidget(self.active_filters_card)

        self.category_section = BaseCard()
        self.category_section.content_layout.addWidget(
            SectionHeader("Browse Categories", "Loaded from your reference data in the active UI language.")
        )
        self.category_row = QHBoxLayout()
        self.category_row.setSpacing(10)
        self.category_section.content_layout.addLayout(self.category_row)
        self.page_layout.addWidget(self.category_section)

        self.featured_section = BaseCard()
        self.featured_section.content_layout.addWidget(
            SectionHeader("Featured Recipes", "A premium landing strip for the first recipes you publish.")
        )
        self.featured_grid = QGridLayout()
        self.featured_grid.setHorizontalSpacing(16)
        self.featured_grid.setVerticalSpacing(16)
        self.featured_section.content_layout.addLayout(self.featured_grid)
        self.page_layout.addWidget(self.featured_section)

        self.latest_section = BaseCard()
        self.latest_section.content_layout.addWidget(
            SectionHeader("Latest Recipes", "Modern data-bound cards designed for future details and editing flows.")
        )
        self.latest_grid = QGridLayout()
        self.latest_grid.setHorizontalSpacing(16)
        self.latest_grid.setVerticalSpacing(16)
        self.latest_section.content_layout.addLayout(self.latest_grid)
        self.page_layout.addWidget(self.latest_section)

        self.empty_state = EmptyState(
            "Your cookbook is structurally ready.",
            "Categories, tags, language settings, and theme-aware layouts are already in place. "
            "As soon as recipes are created, this becomes the discovery surface of the app.",
        )
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
        self.search_bar.set_language(dashboard.context.language_code, translate(dashboard.context.language_code, "home.search_placeholder"))
        self.hero_subtitle.setText(
            f"{dashboard.context.profile_name}, your workspace is configured in {dashboard.context.language_code.upper()} and ready for a polished recipe experience."
        )
        self.search_bar.set_text(dashboard.search_text)
        self._populate_tags(dashboard)
        self._populate_categories(dashboard)
        self._update_active_filters(dashboard)
        self._render_recipe_sections(dashboard.latest_recipes, dashboard.featured_recipes)

    def _populate_tags(self, dashboard: HomeDashboardData) -> None:
        self._clear_box(self.tag_row)
        for tag in dashboard.tags[:5]:
            tag_label = QLabel(tag.display_name)
            tag_label.setObjectName("tagPill")
            self.tag_row.addWidget(tag_label)
        self.tag_row.addStretch(1)

    def _populate_categories(self, dashboard: HomeDashboardData) -> None:
        self._clear_box(self.category_row)

        all_chip = CategoryChip("all", "All")
        all_chip.setChecked(self._selected_category_slug in {None, "all"})
        all_chip.selected_changed.connect(self._handle_category_selected)
        self.category_row.addWidget(all_chip)

        for category in dashboard.categories:
            chip = CategoryChip(category.slug, category.display_name)
            chip.setChecked(category.slug == self._selected_category_slug)
            chip.selected_changed.connect(self._handle_category_selected)
            self.category_row.addWidget(chip)

        self.category_row.addStretch(1)

    def _handle_category_selected(self, slug: str, checked: bool) -> None:
        if slug == "all":
            self._selected_category_slug = None
        else:
            self._selected_category_slug = slug if checked else None
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

        parts: list[str] = []
        if dashboard.search_text:
            parts.append(f'Search: "{dashboard.search_text}"')
        if dashboard.selected_category_name:
            parts.append(f"Category: {dashboard.selected_category_name}")
        self.active_filters_label.setText(" • ".join(parts))
        self.active_filters_card.show()

    def _render_recipe_sections(
        self,
        recipes: list[RecipeListItem],
        featured_recipes: list[RecipeListItem],
    ) -> None:
        self._clear_grid(self.featured_grid)
        self._clear_grid(self.latest_grid)

        for index, recipe in enumerate(featured_recipes[:3]):
            card = RecipeCard(recipe, self.image_service, dashboard.context.language_code)
            card.clicked.connect(self.recipe_selected.emit)
            self.featured_grid.addWidget(card, 0, index)

        for index, recipe in enumerate(recipes):
            row = index // 3
            column = index % 3
            card = RecipeCard(recipe, self.image_service, self._dashboard_data.context.language_code if self._dashboard_data else "en")
            card.clicked.connect(self.recipe_selected.emit)
            self.latest_grid.addWidget(card, row, column)

        has_recipes = bool(recipes)
        self.featured_section.setVisible(bool(featured_recipes))
        self.latest_section.setVisible(has_recipes)
        if not has_recipes:
            if self._dashboard_data is not None and self._dashboard_data.has_active_filters:
                self.empty_state.set_content(
                    "No recipes match the current view.",
                    "Try clearing the search, switching categories, or broadening the phrase to bring recipes back into view.",
                    badge_text="No matching results",
                )
            else:
                self.empty_state.set_content(
                    "Your cookbook is structurally ready.",
                    "Categories, tags, language settings, and theme-aware layouts are already in place. "
                    "As soon as recipes are created, this becomes the discovery surface of the app.",
                    badge_text="No recipes yet",
                )
        self.empty_state.setVisible(not has_recipes)

    @staticmethod
    def _clear_box(layout: QHBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    @staticmethod
    def _clear_grid(layout: QGridLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

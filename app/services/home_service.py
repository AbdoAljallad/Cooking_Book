from __future__ import annotations

from app.services.app_context_service import AppContextService
from app.services.category_service import CategoryService
from app.services.models import HomeDashboardData
from app.services.recipe_service import RecipeService
from app.services.tag_service import TagService


class HomeService:
    def __init__(
        self,
        context_service: AppContextService,
        category_service: CategoryService,
        tag_service: TagService,
        recipe_service: RecipeService,
    ) -> None:
        self.context_service = context_service
        self.category_service = category_service
        self.tag_service = tag_service
        self.recipe_service = recipe_service

    def get_dashboard_data(self) -> HomeDashboardData:
        return self.get_filtered_dashboard_data()

    def get_filtered_dashboard_data(
        self,
        query_text: str = "",
        category_slug: str | None = None,
    ) -> HomeDashboardData:
        context = self.context_service.get_context()
        categories = self.category_service.list_categories(context.language_code)
        tags = self.tag_service.list_tags(context.language_code)
        normalized_query = query_text.strip()
        selected_category = next((item for item in categories if item.slug == category_slug), None)
        latest = self.recipe_service.list_filtered_recipes(
            context.language_code,
            query_text=normalized_query or None,
            category_slug=category_slug,
            limit=12,
        )
        featured = [] if (normalized_query or category_slug) else self.recipe_service.list_featured_recipes(
            context.language_code,
            limit=3,
        )
        return HomeDashboardData(
            context=context,
            categories=categories,
            tags=tags,
            featured_recipes=featured,
            latest_recipes=latest,
            search_text=normalized_query,
            selected_category_slug=category_slug,
            selected_category_name=selected_category.display_name if selected_category is not None else None,
        )

    def search_dashboard_recipes(self, query_text: str) -> HomeDashboardData:
        return self.get_filtered_dashboard_data(query_text=query_text)

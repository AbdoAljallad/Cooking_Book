from __future__ import annotations

from sqlalchemy import Select, func, literal, select

from app.models import Category, CategoryTranslation, Language
from app.repositories.base import BaseRepository
from app.repositories.projections import LocalizedCategory


class CategoryRepository(BaseRepository[Category]):
    def list_all(self, language_code: str | None = None) -> list[LocalizedCategory]:
        statement = self._localized_statement(language_code).order_by(
            Category.sort_order.asc(),
            Category.id.asc(),
        )
        rows = self.session.execute(statement).all()
        return [self._to_projection(row) for row in rows]

    def get_by_slug(
        self,
        slug: str,
        language_code: str | None = None,
    ) -> LocalizedCategory | None:
        statement = self._localized_statement(language_code).where(Category.slug == slug)
        row = self.session.execute(statement).one_or_none()
        return None if row is None else self._to_projection(row)

    def _localized_statement(self, language_code: str | None) -> Select:
        target_language = language_code or "en"
        requested_name = (
            select(CategoryTranslation.name)
            .join(Language, Language.id == CategoryTranslation.language_id)
            .where(
                CategoryTranslation.category_id == Category.id,
                Language.code == target_language,
            )
            .correlate(Category)
            .scalar_subquery()
        )
        english_name = (
            select(CategoryTranslation.name)
            .join(Language, Language.id == CategoryTranslation.language_id)
            .where(
                CategoryTranslation.category_id == Category.id,
                Language.code == "en",
            )
            .correlate(Category)
            .scalar_subquery()
        )
        statement = select(
            Category,
            func.coalesce(func.nullif(requested_name, ""), english_name, Category.slug),
            literal(target_language),
        )
        return statement

    @staticmethod
    def _to_projection(row) -> LocalizedCategory:
        category, display_name, language_code = row
        return LocalizedCategory(
            id=category.id,
            slug=category.slug,
            sort_order=category.sort_order,
            is_active=category.is_active,
            display_name=display_name or category.slug,
            language_code=language_code,
        )

from __future__ import annotations

from sqlalchemy import Select, and_, delete, or_, select
from sqlalchemy.orm import joinedload

from app.models import (
    Category,
    CategoryTranslation,
    Favorite,
    Ingredient,
    IngredientTranslation,
    Language,
    Recipe,
    RecipeIngredient,
    RecipeNote,
    RecipeRating,
    RecipeStep,
    RecipeStepTranslation,
    RecipeTag,
    RecipeTranslation,
    Tag,
    TagTranslation,
    Unit,
    UnitTranslation,
)
from app.repositories.base import BaseRepository
from app.repositories.projections import RecipeListItem


class RecipeRepository(BaseRepository[Recipe]):
    def add(self, recipe: Recipe) -> Recipe:
        self.session.add(recipe)
        self.session.flush()
        return recipe

    def list_all_basic(
        self,
        limit: int | None = None,
        offset: int = 0,
        language_code: str | None = None,
    ) -> list[RecipeListItem]:
        statement = self._basic_list_statement(language_code).offset(offset)
        if limit is not None:
            statement = statement.limit(limit)
        rows = self.session.execute(statement).all()
        return [self._to_list_item(row) for row in rows]

    def get_by_id(self, recipe_id: int) -> Recipe | None:
        statement = (
            select(Recipe)
            .options(
                joinedload(Recipe.category),
                joinedload(Recipe.category)
                .joinedload(Category.translations)
                .joinedload(CategoryTranslation.language),
                joinedload(Recipe.created_by_profile),
                joinedload(Recipe.translations).joinedload(RecipeTranslation.language),
                joinedload(Recipe.ingredients).joinedload(RecipeIngredient.unit),
                joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient),
                joinedload(Recipe.ingredients)
                .joinedload(RecipeIngredient.unit)
                .joinedload(Unit.translations)
                .joinedload(UnitTranslation.language),
                joinedload(Recipe.ingredients)
                .joinedload(RecipeIngredient.ingredient)
                .joinedload(Ingredient.translations)
                .joinedload(IngredientTranslation.language),
                joinedload(Recipe.steps)
                .joinedload(RecipeStep.translations)
                .joinedload(RecipeStepTranslation.language),
                joinedload(Recipe.tag_links)
                .joinedload(RecipeTag.tag)
                .joinedload(Tag.translations)
                .joinedload(TagTranslation.language),
            )
            .where(Recipe.id == recipe_id)
        )
        return self.session.execute(statement).unique().scalar_one_or_none()

    def is_favorite(self, recipe_id: int, profile_id: int) -> bool:
        statement = select(Favorite).where(
            Favorite.recipe_id == recipe_id,
            Favorite.profile_id == profile_id,
        )
        return self.session.execute(statement).scalar_one_or_none() is not None

    def set_favorite(self, recipe_id: int, profile_id: int, is_favorite: bool) -> bool:
        existing = self.session.execute(
            select(Favorite).where(
                Favorite.recipe_id == recipe_id,
                Favorite.profile_id == profile_id,
            )
        ).scalar_one_or_none()
        if is_favorite:
            if existing is None:
                self.session.add(Favorite(recipe_id=recipe_id, profile_id=profile_id))
                self.session.flush()
            return True
        if existing is not None:
            self.session.delete(existing)
            self.session.flush()
        return False

    def get_note(self, recipe_id: int, profile_id: int) -> RecipeNote | None:
        statement = select(RecipeNote).where(
            RecipeNote.recipe_id == recipe_id,
            RecipeNote.profile_id == profile_id,
        )
        return self.session.execute(statement).scalar_one_or_none()

    def save_note(self, recipe_id: int, profile_id: int, note_text: str) -> RecipeNote | None:
        normalized = note_text.strip()
        existing = self.get_note(recipe_id, profile_id)
        if not normalized:
            if existing is not None:
                self.session.delete(existing)
                self.session.flush()
            return None

        if existing is None:
            existing = RecipeNote(
                recipe_id=recipe_id,
                profile_id=profile_id,
                note_text=normalized,
            )
            self.session.add(existing)
        else:
            existing.note_text = normalized
        self.session.flush()
        return existing

    def get_rating(self, recipe_id: int, profile_id: int) -> RecipeRating | None:
        statement = select(RecipeRating).where(
            RecipeRating.recipe_id == recipe_id,
            RecipeRating.profile_id == profile_id,
        )
        return self.session.execute(statement).scalar_one_or_none()

    def save_rating(self, recipe_id: int, profile_id: int, rating: int | None) -> RecipeRating | None:
        existing = self.get_rating(recipe_id, profile_id)
        if rating is None:
            if existing is not None:
                self.session.delete(existing)
                self.session.flush()
            return None

        if existing is None:
            existing = RecipeRating(
                recipe_id=recipe_id,
                profile_id=profile_id,
                rating=rating,
            )
            self.session.add(existing)
        else:
            existing.rating = rating
        self.session.flush()
        return existing

    def list_favorite_basic(
        self,
        profile_id: int,
        language_code: str | None = None,
        limit: int | None = 20,
        offset: int = 0,
    ) -> list[RecipeListItem]:
        statement = (
            self._basic_list_statement(language_code)
            .join(Favorite, Favorite.recipe_id == Recipe.id)
            .where(Favorite.profile_id == profile_id)
            .offset(offset)
        )
        if limit is not None:
            statement = statement.limit(limit)
        rows = self.session.execute(statement).all()
        return [self._to_list_item(row) for row in rows]

    def list_by_category(
        self,
        category_slug: str,
        language_code: str | None = None,
    ) -> list[RecipeListItem]:
        return self.list_filtered_basic(
            language_code=language_code,
            category_slug=category_slug,
        )

    def search_basic(
        self,
        query_text: str,
        language_code: str | None = None,
        limit: int = 20,
    ) -> list[RecipeListItem]:
        return self.list_filtered_basic(
            language_code=language_code,
            query_text=query_text,
            limit=limit,
        )

    def list_filtered_basic(
        self,
        language_code: str | None = None,
        query_text: str | None = None,
        category_slug: str | None = None,
        limit: int | None = 20,
        offset: int = 0,
    ) -> list[RecipeListItem]:
        statement = self._basic_list_statement(language_code)
        normalized = (query_text or "").strip()
        if normalized:
            pattern = f"%{normalized}%"
            statement = statement.where(
                or_(
                    RecipeTranslation.title.ilike(pattern),
                    RecipeTranslation.short_description.ilike(pattern),
                )
            )
        if category_slug:
            statement = statement.where(Category.slug == category_slug)
        statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)
        rows = self.session.execute(statement).all()
        return [self._to_list_item(row) for row in rows]

    def _basic_list_statement(self, language_code: str | None) -> Select:
        language_match = Language.code == language_code if language_code else Language.code == "en"
        statement = (
            select(
                Recipe,
                RecipeTranslation.title,
                RecipeTranslation.short_description,
                Category.slug,
                CategoryTranslation.name,
            )
            .join(Category, Category.id == Recipe.category_id)
            .join(
                RecipeTranslation,
                RecipeTranslation.recipe_id == Recipe.id,
            )
            .join(
                Language,
                and_(
                    Language.id == RecipeTranslation.language_id,
                    language_match,
                ),
            )
            .outerjoin(
                CategoryTranslation,
                and_(
                    CategoryTranslation.category_id == Category.id,
                    CategoryTranslation.language_id == Language.id,
                ),
            )
            .where(Recipe.is_active.is_(True))
            .order_by(Recipe.updated_at.desc(), Recipe.id.desc())
        )
        return statement

    @staticmethod
    def _to_list_item(row) -> RecipeListItem:
        recipe, title, short_description, category_slug, category_name = row
        return RecipeListItem(
            id=recipe.id,
            title=title,
            short_description=short_description,
            category_slug=category_slug,
            category_name=category_name,
            prep_time_minutes=recipe.prep_time_minutes,
            cook_time_minutes=recipe.cook_time_minutes,
            total_time_minutes=recipe.total_time_minutes,
            base_servings=recipe.base_servings,
            difficulty_level=recipe.difficulty_level.value,
            source_type=recipe.source_type.value,
            image_path=recipe.image_path,
            created_at=recipe.created_at,
            updated_at=recipe.updated_at,
        )

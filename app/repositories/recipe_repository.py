from __future__ import annotations

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import selectinload

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
        return self._with_tags(
            [self._to_list_item(row) for row in rows],
            language_code,
        )

    def get_by_id(self, recipe_id: int) -> Recipe | None:
        statement = (
            select(Recipe)
            .options(
                selectinload(Recipe.category)
                .selectinload(Category.translations)
                .selectinload(CategoryTranslation.language),

                selectinload(Recipe.created_by_profile),

                selectinload(Recipe.translations)
                .selectinload(RecipeTranslation.language),

                selectinload(Recipe.ingredients)
                .selectinload(RecipeIngredient.unit)
                .selectinload(Unit.translations)
                .selectinload(UnitTranslation.language),

                selectinload(Recipe.ingredients)
                .selectinload(RecipeIngredient.ingredient)
                .selectinload(Ingredient.translations)
                .selectinload(IngredientTranslation.language),

                selectinload(Recipe.steps)
                .selectinload(RecipeStep.translations)
                .selectinload(RecipeStepTranslation.language),

                selectinload(Recipe.tag_links)
                .selectinload(RecipeTag.tag)
                .selectinload(Tag.translations)
                .selectinload(TagTranslation.language),
            )
            .where(Recipe.id == recipe_id)
        )

        return self.session.execute(statement).scalar_one_or_none()

    def is_favorite(self, recipe_id: int, profile_id: int) -> bool:
        statement = select(Favorite).where(
            Favorite.recipe_id == recipe_id,
            Favorite.profile_id == profile_id,
        )
        return self.session.execute(statement).scalar_one_or_none() is not None

    def set_favorite(
        self,
        recipe_id: int,
        profile_id: int,
        is_favorite: bool,
    ) -> bool:
        existing = self.session.execute(
            select(Favorite).where(
                Favorite.recipe_id == recipe_id,
                Favorite.profile_id == profile_id,
            )
        ).scalar_one_or_none()

        if is_favorite:
            if existing is None:
                self.session.add(
                    Favorite(recipe_id=recipe_id, profile_id=profile_id)
                )
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

    def save_note(
        self,
        recipe_id: int,
        profile_id: int,
        note_text: str,
    ) -> RecipeNote | None:
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

    def save_rating(
        self,
        recipe_id: int,
        profile_id: int,
        rating: int | None,
    ) -> RecipeRating | None:
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
        return self._with_tags(
            [self._to_list_item(row) for row in rows],
            language_code,
        )

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

            search_recipe_translation = (
                select(RecipeTranslation.id)
                .where(
                    RecipeTranslation.recipe_id == Recipe.id,
                    or_(
                        RecipeTranslation.title.ilike(pattern),
                        RecipeTranslation.short_description.ilike(pattern),
                    ),
                )
                .correlate(Recipe)
                .exists()
            )

            search_ingredient_translation = (
                select(RecipeIngredient.id)
                .join(Ingredient, Ingredient.id == RecipeIngredient.ingredient_id)
                .join(
                    IngredientTranslation,
                    IngredientTranslation.ingredient_id == Ingredient.id,
                )
                .where(
                    RecipeIngredient.recipe_id == Recipe.id,
                    IngredientTranslation.name.ilike(pattern),
                )
                .correlate(Recipe)
                .exists()
            )

            search_category_translation = (
                select(CategoryTranslation.id)
                .where(
                    CategoryTranslation.category_id == Recipe.category_id,
                    CategoryTranslation.name.ilike(pattern),
                )
                .correlate(Recipe)
                .exists()
            )

            search_tag_translation = (
                select(RecipeTag.recipe_id)
                .join(Tag, Tag.id == RecipeTag.tag_id)
                .join(TagTranslation, TagTranslation.tag_id == Tag.id)
                .where(
                    RecipeTag.recipe_id == Recipe.id,
                    TagTranslation.name.ilike(pattern),
                )
                .correlate(Recipe)
                .exists()
            )

            statement = statement.where(
                or_(
                    search_recipe_translation,
                    search_ingredient_translation,
                    search_category_translation,
                    search_tag_translation,
                )
            )

        if category_slug:
            statement = statement.where(Category.slug == category_slug)

        statement = statement.offset(offset)

        if limit is not None:
            statement = statement.limit(limit)

        rows = self.session.execute(statement).all()
        return self._with_tags(
            [self._to_list_item(row) for row in rows],
            language_code,
        )

    def _basic_list_statement(self, language_code: str | None) -> Select:
        target_language = language_code or "en"

        requested_title = (
            select(RecipeTranslation.title)
            .join(Language, Language.id == RecipeTranslation.language_id)
            .where(
                RecipeTranslation.recipe_id == Recipe.id,
                Language.code == target_language,
            )
            .correlate(Recipe)
            .scalar_subquery()
        )

        requested_description = (
            select(RecipeTranslation.short_description)
            .join(Language, Language.id == RecipeTranslation.language_id)
            .where(
                RecipeTranslation.recipe_id == Recipe.id,
                Language.code == target_language,
            )
            .correlate(Recipe)
            .scalar_subquery()
        )

        english_title = (
            select(RecipeTranslation.title)
            .join(Language, Language.id == RecipeTranslation.language_id)
            .where(
                RecipeTranslation.recipe_id == Recipe.id,
                Language.code == "en",
            )
            .correlate(Recipe)
            .scalar_subquery()
        )

        english_description = (
            select(RecipeTranslation.short_description)
            .join(Language, Language.id == RecipeTranslation.language_id)
            .where(
                RecipeTranslation.recipe_id == Recipe.id,
                Language.code == "en",
            )
            .correlate(Recipe)
            .scalar_subquery()
        )

        requested_category = (
            select(CategoryTranslation.name)
            .join(Language, Language.id == CategoryTranslation.language_id)
            .where(
                CategoryTranslation.category_id == Category.id,
                Language.code == target_language,
            )
            .correlate(Category)
            .scalar_subquery()
        )

        english_category = (
            select(CategoryTranslation.name)
            .join(Language, Language.id == CategoryTranslation.language_id)
            .where(
                CategoryTranslation.category_id == Category.id,
                Language.code == "en",
            )
            .correlate(Category)
            .scalar_subquery()
        )

        statement = (
            select(
                Recipe,
                func.coalesce(
                    func.nullif(requested_title, ""),
                    english_title,
                    "Untitled",
                ),
                func.coalesce(
                    func.nullif(requested_description, ""),
                    english_description,
                ),
                Category.slug,
                func.coalesce(
                    func.nullif(requested_category, ""),
                    english_category,
                    Category.slug,
                ),
            )
            .join(Category, Category.id == Recipe.category_id)
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
            tags=[],
            created_at=recipe.created_at,
            updated_at=recipe.updated_at,
        )

    def _with_tags(
        self,
        recipes: list[RecipeListItem],
        language_code: str | None,
    ) -> list[RecipeListItem]:
        if not recipes:
            return recipes

        recipe_ids = [recipe.id for recipe in recipes]
        target_language = language_code or "en"

        requested_tag = (
            select(TagTranslation.name)
            .join(Language, Language.id == TagTranslation.language_id)
            .where(
                TagTranslation.tag_id == Tag.id,
                Language.code == target_language,
            )
            .correlate(Tag)
            .scalar_subquery()
        )

        english_tag = (
            select(TagTranslation.name)
            .join(Language, Language.id == TagTranslation.language_id)
            .where(
                TagTranslation.tag_id == Tag.id,
                Language.code == "en",
            )
            .correlate(Tag)
            .scalar_subquery()
        )

        rows = self.session.execute(
            select(
                RecipeTag.recipe_id,
                func.coalesce(
                    func.nullif(requested_tag, ""),
                    english_tag,
                    Tag.slug,
                ),
            )
            .join(Tag, Tag.id == RecipeTag.tag_id)
            .where(RecipeTag.recipe_id.in_(recipe_ids))
            .order_by(Tag.slug.asc())
        ).all()

        tags_by_recipe: dict[int, list[str]] = {
            recipe_id: [] for recipe_id in recipe_ids
        }

        for recipe_id, tag_name in rows:
            tags_by_recipe.setdefault(recipe_id, []).append(tag_name)

        return [
            RecipeListItem(
                id=recipe.id,
                title=recipe.title,
                short_description=recipe.short_description,
                category_slug=recipe.category_slug,
                category_name=recipe.category_name,
                prep_time_minutes=recipe.prep_time_minutes,
                cook_time_minutes=recipe.cook_time_minutes,
                total_time_minutes=recipe.total_time_minutes,
                base_servings=recipe.base_servings,
                difficulty_level=recipe.difficulty_level,
                source_type=recipe.source_type,
                image_path=recipe.image_path,
                tags=tags_by_recipe.get(recipe.id, []),
                created_at=recipe.created_at,
                updated_at=recipe.updated_at,
            )
            for recipe in recipes
        ]
from __future__ import annotations

from decimal import Decimal
import re
from typing import Iterable

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.models import (
    Ingredient,
    IngredientTranslation,
    Language,
    Recipe,
    RecipeIngredient,
    RecipeStep,
    RecipeStepTranslation,
    RecipeTag,
    RecipeTranslation,
)
from app.models.enums import DifficultyLevel, RecipeSourceType
from app.repositories import IngredientRepository, RecipeListItem, RecipeRepository
from app.services.base import BaseService
from app.services.image_service import ImageService, ImageValidationError
from app.services.models import (
    CreateRecipeIngredientInput,
    CreateRecipeInput,
    CreateRecipeStepInput,
    EditRecipeFormData,
    RecipeDetailsData,
    RecipeIngredientDetail,
    RecipeStepDetail,
)
from app.utils.i18n import translate


class RecipeValidationError(ValueError):
    """Raised when create-recipe input fails validation."""


class RecipeService(BaseService):
    def __init__(
        self,
        session_factory: sessionmaker[Session] | None = None,
        image_service: ImageService | None = None,
    ) -> None:
        super().__init__(session_factory)
        self.image_service = image_service

    def list_home_recipes(
        self,
        language_code: str,
        limit: int = 8,
    ) -> list[RecipeListItem]:
        try:
            with self._open_session() as session:
                return RecipeRepository(session).list_all_basic(
                    language_code=language_code,
                    limit=limit,
                )
        except (SQLAlchemyError, Exception):
            return []

    def list_featured_recipes(
        self,
        language_code: str,
        limit: int = 3,
    ) -> list[RecipeListItem]:
        return self.list_home_recipes(language_code=language_code, limit=limit)

    def list_by_category(
        self,
        category_slug: str,
        language_code: str,
    ) -> list[RecipeListItem]:
        try:
            with self._open_session() as session:
                return RecipeRepository(session).list_by_category(
                    category_slug,
                    language_code=language_code,
                )
        except (SQLAlchemyError, Exception):
            return []

    def list_filtered_recipes(
        self,
        language_code: str,
        query_text: str | None = None,
        category_slug: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[RecipeListItem]:
        try:
            with self._open_session() as session:
                return RecipeRepository(session).list_filtered_basic(
                    language_code=language_code,
                    query_text=query_text,
                    category_slug=category_slug,
                    limit=limit,
                    offset=offset,
                )
        except (SQLAlchemyError, Exception):
            return []

    def search_recipes(
        self,
        query_text: str,
        language_code: str,
        limit: int = 20,
    ) -> list[RecipeListItem]:
        return self.list_filtered_recipes(
            language_code=language_code,
            query_text=query_text,
            limit=limit,
        )

    def get_recipe(self, recipe_id: int) -> Recipe | None:
        try:
            with self._open_session() as session:
                return RecipeRepository(session).get_by_id(recipe_id)
        except (SQLAlchemyError, Exception):
            return None

    def create_recipe(
        self,
        input_data: CreateRecipeInput,
        created_by_profile_id: int,
    ) -> int:
        self._validate_create_input(input_data)

        with self._open_session() as session:
            try:
                english = self._get_language(session, "en")
                arabic = self._get_language(session, "ar")
                russian = self._get_language(session, "ru")

                recipe = Recipe(
                    category_id=input_data.category_id,
                    image_path=input_data.image_path or None,
                    prep_time_minutes=input_data.prep_time_minutes,
                    cook_time_minutes=input_data.cook_time_minutes,
                    base_servings=input_data.base_servings,
                    difficulty_level=DifficultyLevel(input_data.difficulty_level),
                    source_type=RecipeSourceType(input_data.source_type),
                    is_active=True,
                    created_by_profile_id=created_by_profile_id,
                )
                RecipeRepository(session).add(recipe)

                for language, title, description in (
                    (english, input_data.title_en, input_data.short_description_en),
                    (arabic, input_data.title_ar, input_data.short_description_ar),
                    (russian, input_data.title_ru, input_data.short_description_ru),
                ):
                    session.add(
                        RecipeTranslation(
                            recipe_id=recipe.id,
                            language_id=language.id,
                            title=title.strip() if title is not None else "",
                            short_description=self._clean_optional_text(description),
                        )
                    )

                for tag_id in input_data.tag_ids:
                    session.add(RecipeTag(recipe_id=recipe.id, tag_id=tag_id))

                ingredient_repository = IngredientRepository(session)

                for index, ingredient_input in enumerate(input_data.ingredients, start=1):
                    ingredient = self._resolve_or_create_ingredient(
                        session=session,
                        ingredient_repository=ingredient_repository,
                        english_language_id=english.id,
                        arabic_language_id=arabic.id,
                        russian_language_id=russian.id,
                        name_en=ingredient_input.name_en,
                        name_ar=ingredient_input.name_ar,
                        name_ru=ingredient_input.name_ru,
                        default_unit_id=ingredient_input.unit_id,
                    )

                    session.add(
                        RecipeIngredient(
                            recipe_id=recipe.id,
                            ingredient_id=ingredient.id,
                            unit_id=ingredient_input.unit_id,
                            quantity=ingredient_input.quantity,
                            is_scalable=ingredient_input.is_scalable,
                            sort_order=index,
                            preparation_note=self._clean_optional_text(
                                ingredient_input.preparation_note
                            ),
                            text_override=self._clean_optional_text(
                                ingredient_input.quantity_text_override
                            ),
                        )
                    )

                for index, step_input in enumerate(input_data.steps, start=1):
                    step = RecipeStep(
                        recipe_id=recipe.id,
                        sort_order=index,
                        estimated_minutes=step_input.estimated_minutes,
                    )
                    session.add(step)
                    session.flush()

                    session.add(
                        RecipeStepTranslation(
                            recipe_step_id=step.id,
                            language_id=english.id,
                            instruction=step_input.instruction_en.strip(),
                        )
                    )

                    if self._clean_optional_text(step_input.instruction_ar):
                        session.add(
                            RecipeStepTranslation(
                                recipe_step_id=step.id,
                                language_id=arabic.id,
                                instruction=step_input.instruction_ar.strip(),
                            )
                        )

                    if self._clean_optional_text(step_input.instruction_ru):
                        session.add(
                            RecipeStepTranslation(
                                recipe_step_id=step.id,
                                language_id=russian.id,
                                instruction=step_input.instruction_ru.strip(),
                            )
                        )

                if input_data.image_input is not None:
                    if self.image_service is None:
                        raise RecipeValidationError(
                            translate("en", "service.validation.image_not_configured")
                        )

                    try:
                        recipe.image_path = self.image_service.store_recipe_image(
                            recipe.id,
                            input_data.image_input,
                        )
                    except ImageValidationError as exc:
                        raise RecipeValidationError(str(exc)) from exc

                session.commit()
                return recipe.id

            except Exception:
                session.rollback()
                raise

    def get_recipe_for_edit(self, recipe_id: int) -> EditRecipeFormData | None:
        recipe = self.get_recipe(recipe_id)
        if recipe is None:
            return None

        title_by_language: dict[str, str | None] = {"en": None, "ar": None, "ru": None}
        description_by_language: dict[str, str | None] = {"en": None, "ar": None, "ru": None}

        for translation in recipe.translations:
            language = getattr(translation, "language", None)
            if language is None or language.code not in title_by_language:
                continue
            title_by_language[language.code] = translation.title
            description_by_language[language.code] = translation.short_description

        tag_ids = [tag_link.tag_id for tag_link in recipe.tag_links]

        ingredients: list[CreateRecipeIngredientInput] = []
        for ingredient in recipe.ingredients:
            names: dict[str, str | None] = {"en": None, "ar": None, "ru": None}
            if ingredient.ingredient is not None:
                for translation in ingredient.ingredient.translations:
                    language = getattr(translation, "language", None)
                    if language is None or language.code not in names:
                        continue
                    names[language.code] = translation.name

            ingredients.append(
                CreateRecipeIngredientInput(
                    name_en=names["en"] or "",
                    name_ar=names["ar"],
                    name_ru=names["ru"],
                    quantity=ingredient.quantity,
                    unit_id=ingredient.unit_id,
                    is_scalable=ingredient.is_scalable,
                    preparation_note=ingredient.preparation_note,
                    quantity_text_override=ingredient.text_override,
                )
            )

        steps: list[CreateRecipeStepInput] = []
        for step in recipe.steps:
            instructions: dict[str, str | None] = {"en": None, "ar": None, "ru": None}
            for translation in step.translations:
                language = getattr(translation, "language", None)
                if language is None or language.code not in instructions:
                    continue
                instructions[language.code] = translation.instruction

            steps.append(
                CreateRecipeStepInput(
                    instruction_en=instructions["en"] or "",
                    instruction_ar=instructions["ar"],
                    instruction_ru=instructions["ru"],
                    estimated_minutes=step.estimated_minutes,
                )
            )

        return EditRecipeFormData(
            recipe_id=recipe.id,
            title_en=title_by_language["en"] or "",
            title_ar=title_by_language["ar"],
            title_ru=title_by_language["ru"],
            short_description_en=description_by_language["en"],
            short_description_ar=description_by_language["ar"],
            short_description_ru=description_by_language["ru"],
            category_id=recipe.category_id,
            image_path=recipe.image_path,
            prep_time_minutes=recipe.prep_time_minutes,
            cook_time_minutes=recipe.cook_time_minutes,
            base_servings=recipe.base_servings,
            difficulty_level=recipe.difficulty_level.value,
            source_type=recipe.source_type.value,
            tag_ids=tag_ids,
            ingredients=ingredients,
            steps=steps,
        )

    def update_recipe(
        self,
        recipe_id: int,
        input_data: CreateRecipeInput,
    ) -> int:
        self._validate_create_input(input_data)

        with self._open_session() as session:
            try:
                recipe = RecipeRepository(session).get_by_id(recipe_id)
                if recipe is None:
                    raise RecipeValidationError(
                        translate("en", "details.feedback.recipe_missing")
                    )

                english = self._get_language(session, "en")
                arabic = self._get_language(session, "ar")
                russian = self._get_language(session, "ru")

                recipe.category_id = input_data.category_id
                recipe.prep_time_minutes = input_data.prep_time_minutes
                recipe.cook_time_minutes = input_data.cook_time_minutes
                recipe.base_servings = input_data.base_servings
                recipe.difficulty_level = DifficultyLevel(input_data.difficulty_level)
                recipe.source_type = RecipeSourceType(input_data.source_type)

                self._upsert_recipe_translation(
                    session,
                    recipe.id,
                    english.id,
                    input_data.title_en,
                    input_data.short_description_en,
                )
                self._upsert_recipe_translation(
                    session,
                    recipe.id,
                    arabic.id,
                    input_data.title_ar or "",
                    input_data.short_description_ar,
                )
                self._upsert_recipe_translation(
                    session,
                    recipe.id,
                    russian.id,
                    input_data.title_ru or "",
                    input_data.short_description_ru,
                )

                recipe.tag_links.clear()
                recipe.tag_links.extend(RecipeTag(recipe_id=recipe.id, tag_id=tag_id) for tag_id in input_data.tag_ids)

                ingredient_repository = IngredientRepository(session)
                recipe.ingredients.clear()
                session.flush()

                for index, ingredient_input in enumerate(input_data.ingredients, start=1):
                    ingredient = self._resolve_or_create_ingredient(
                        session=session,
                        ingredient_repository=ingredient_repository,
                        english_language_id=english.id,
                        arabic_language_id=arabic.id,
                        russian_language_id=russian.id,
                        name_en=ingredient_input.name_en,
                        name_ar=ingredient_input.name_ar,
                        name_ru=ingredient_input.name_ru,
                        default_unit_id=ingredient_input.unit_id,
                    )
                    recipe.ingredients.append(
                        RecipeIngredient(
                            ingredient_id=ingredient.id,
                            unit_id=ingredient_input.unit_id,
                            quantity=ingredient_input.quantity,
                            is_scalable=ingredient_input.is_scalable,
                            sort_order=index,
                            preparation_note=self._clean_optional_text(ingredient_input.preparation_note),
                            text_override=self._clean_optional_text(ingredient_input.quantity_text_override),
                        )
                    )

                recipe.steps.clear()
                session.flush()

                for index, step_input in enumerate(input_data.steps, start=1):
                    step = RecipeStep(
                        sort_order=index,
                        estimated_minutes=step_input.estimated_minutes,
                    )
                    step.translations.extend(
                        [
                            RecipeStepTranslation(
                                language_id=english.id,
                                instruction=step_input.instruction_en.strip(),
                            ),
                            RecipeStepTranslation(
                                language_id=arabic.id,
                                instruction=(step_input.instruction_ar or "").strip(),
                            ),
                            RecipeStepTranslation(
                                language_id=russian.id,
                                instruction=(step_input.instruction_ru or "").strip(),
                            ),
                        ]
                    )
                    recipe.steps.append(step)

                if input_data.image_input is not None:
                    if self.image_service is None:
                        raise RecipeValidationError(
                            translate("en", "service.validation.image_not_configured")
                        )
                    recipe.image_path = self.image_service.store_recipe_image(recipe.id, input_data.image_input)

                session.commit()
                return recipe.id
            except Exception:
                session.rollback()
                raise

    def delete_recipe(self, recipe_id: int) -> None:
        with self._open_session() as session:
            try:
                recipe = RecipeRepository(session).get_by_id(recipe_id)
                if recipe is None:
                    raise RecipeValidationError(
                        translate("en", "details.feedback.recipe_missing")
                    )
                session.delete(recipe)
                session.commit()
            except Exception:
                session.rollback()
                raise

    def get_recipe_details(
        self,
        recipe_id: int,
        language_code: str,
        profile_id: int | None = None,
        target_servings: Decimal | None = None,
    ) -> RecipeDetailsData | None:
        recipe = self.get_recipe(recipe_id)

        if recipe is None:
            return None

        translation = self._pick_translation(recipe.translations, language_code)
        category_translation = self._pick_translation(
            recipe.category.translations,
            language_code,
        )

        tags = []
        for tag_link in recipe.tag_links:
            tag_translation = self._pick_translation(
                tag_link.tag.translations,
                language_code,
            )
            tags.append(
                tag_translation.name
                if tag_translation is not None
                else tag_link.tag.slug.replace("_", " ").title()
            )

        ingredients = []

        for ingredient in recipe.ingredients:
            ingredient_name = translate(language_code, "service.recipe.custom_ingredient")

            if ingredient.ingredient is not None:
                ingredient_translation = self._pick_translation(
                    ingredient.ingredient.translations,
                    language_code,
                )
                ingredient_name = (
                    ingredient_translation.name
                    if ingredient_translation is not None
                    else ingredient.ingredient.slug.replace("_", " ").title()
                )

            unit_label = None

            if ingredient.unit is not None:
                unit_translation = self._pick_translation(
                    ingredient.unit.translations,
                    language_code,
                )
                unit_label = (
                    unit_translation.abbreviation
                    if unit_translation is not None and unit_translation.abbreviation
                    else ingredient.unit.code
                )

            ingredients.append(
                RecipeIngredientDetail(
                    item_name=ingredient_name,
                    quantity=ingredient.quantity,
                    unit_label=unit_label,
                    is_scalable=ingredient.is_scalable,
                    quantity_text_override=ingredient.text_override,
                    display_quantity=self._format_ingredient_quantity(
                        quantity=ingredient.quantity,
                        unit_label=unit_label,
                        text_override=ingredient.text_override,
                        language_code=language_code,
                    ),
                    preparation_note=ingredient.preparation_note,
                )
            )

        steps = []

        for step in recipe.steps:
            step_translation = self._pick_translation(step.translations, language_code)

            steps.append(
                RecipeStepDetail(
                    sort_order=step.sort_order,
                    instruction=(
                        step_translation.instruction
                        if step_translation is not None
                        else translate(language_code, "service.recipe.step_unavailable")
                    ),
                    estimated_minutes=step.estimated_minutes,
                )
            )

        is_favorite = False
        personal_note = None
        personal_rating = None

        if profile_id is not None:
            try:
                with self._open_session() as session:
                    repository = RecipeRepository(session)
                    is_favorite = repository.is_favorite(recipe_id, profile_id)
                    note = repository.get_note(recipe_id, profile_id)
                    rating = repository.get_rating(recipe_id, profile_id)
                    personal_note = note.note_text if note is not None else None
                    personal_rating = rating.rating if rating is not None else None
            except (SQLAlchemyError, Exception):
                is_favorite = False
                personal_note = None
                personal_rating = None

        details = RecipeDetailsData(
            id=recipe.id,
            title=(
                translation.title
                if translation is not None
                else translate(language_code, "service.recipe.untitled")
            ),
            short_description=(
                translation.short_description if translation is not None else None
            ),
            image_path=recipe.image_path,
            category_name=(
                category_translation.name
                if category_translation is not None
                else recipe.category.slug.replace("_", " ").title()
            ),
            prep_time_minutes=recipe.prep_time_minutes,
            cook_time_minutes=recipe.cook_time_minutes,
            total_time_minutes=recipe.total_time_minutes,
            base_servings=recipe.base_servings,
            base_servings_display=self._format_decimal(recipe.base_servings),
            selected_servings=recipe.base_servings,
            selected_servings_display=self._format_decimal(recipe.base_servings),
            difficulty_level=recipe.difficulty_level.value,
            source_type=recipe.source_type.value,
            is_favorite=is_favorite,
            personal_rating=personal_rating,
            personal_note=personal_note,
            tags=tags,
            ingredients=ingredients,
            steps=steps,
        )

        if target_servings is None:
            return details

        return self.scale_recipe_details(details, target_servings)

    def list_favorite_recipes(
        self,
        profile_id: int | None,
        language_code: str,
        limit: int = 24,
    ) -> list[RecipeListItem]:
        if profile_id is None:
            return []

        try:
            with self._open_session() as session:
                return RecipeRepository(session).list_favorite_basic(
                    profile_id=profile_id,
                    language_code=language_code,
                    limit=limit,
                )
        except (SQLAlchemyError, Exception):
            return []

    def toggle_favorite(
        self,
        recipe_id: int,
        profile_id: int | None,
    ) -> bool:
        if profile_id is None:
            return False

        with self._open_session() as session:
            try:
                repository = RecipeRepository(session)
                new_state = not repository.is_favorite(recipe_id, profile_id)
                persisted = repository.set_favorite(recipe_id, profile_id, new_state)
                session.commit()
                return persisted
            except Exception:
                session.rollback()
                raise

    def save_personal_note(
        self,
        recipe_id: int,
        profile_id: int | None,
        note_text: str,
    ) -> str | None:
        if profile_id is None:
            return None

        with self._open_session() as session:
            try:
                note = RecipeRepository(session).save_note(
                    recipe_id,
                    profile_id,
                    note_text,
                )
                session.commit()
                return note.note_text if note is not None else None
            except Exception:
                session.rollback()
                raise

    def save_personal_rating(
        self,
        recipe_id: int,
        profile_id: int | None,
        rating: int | None,
    ) -> int | None:
        if profile_id is None:
            return None

        if rating is not None and not 1 <= rating <= 5:
            raise RecipeValidationError(
                translate("en", "service.validation.rating_range")
            )

        with self._open_session() as session:
            try:
                saved = RecipeRepository(session).save_rating(
                    recipe_id,
                    profile_id,
                    rating,
                )
                session.commit()
                return saved.rating if saved is not None else None
            except Exception:
                session.rollback()
                raise

    def scale_recipe_details(
        self,
        details: RecipeDetailsData,
        target_servings: Decimal | int | float,
    ) -> RecipeDetailsData:
        target_value = self._coerce_servings_decimal(target_servings)

        if target_value <= 0:
            target_value = details.base_servings

        ratio = (
            target_value / details.base_servings
            if details.base_servings > 0
            else Decimal("1")
        )

        scaled_ingredients = [
            RecipeIngredientDetail(
                item_name=ingredient.item_name,
                quantity=ingredient.quantity,
                unit_label=ingredient.unit_label,
                is_scalable=ingredient.is_scalable,
                quantity_text_override=ingredient.quantity_text_override,
                display_quantity=self._format_scaled_ingredient_quantity(
                    ingredient,
                    ratio,
                ),
                preparation_note=ingredient.preparation_note,
            )
            for ingredient in details.ingredients
        ]

        return RecipeDetailsData(
            id=details.id,
            title=details.title,
            short_description=details.short_description,
            image_path=details.image_path,
            category_name=details.category_name,
            prep_time_minutes=details.prep_time_minutes,
            cook_time_minutes=details.cook_time_minutes,
            total_time_minutes=details.total_time_minutes,
            base_servings=details.base_servings,
            base_servings_display=details.base_servings_display,
            selected_servings=target_value,
            selected_servings_display=self._format_decimal(target_value),
            difficulty_level=details.difficulty_level,
            source_type=details.source_type,
            is_favorite=details.is_favorite,
            personal_rating=details.personal_rating,
            personal_note=details.personal_note,
            tags=details.tags,
            ingredients=scaled_ingredients,
            steps=details.steps,
        )

    @staticmethod
    def _pick_translation(translations: Iterable, language_code: str):
        english_translation = None

        for translation in translations:
            language = getattr(translation, "language", None)

            if language is not None and language.code == "en":
                english_translation = translation

            if language is not None and language.code == language_code:
                title = getattr(translation, "title", None)
                name = getattr(translation, "name", None)
                instruction = getattr(translation, "instruction", None)

                if (title or name or instruction) not in {None, ""}:
                    return translation

        return english_translation or next(iter(translations), None)

    def _format_scaled_ingredient_quantity(
        self,
        ingredient: RecipeIngredientDetail,
        ratio: Decimal,
    ) -> str:
        if ingredient.quantity_text_override:
            return ingredient.quantity_text_override

        if ingredient.quantity is None:
            return self._format_ingredient_quantity(
                quantity=None,
                unit_label=ingredient.unit_label,
                text_override=None,
                language_code="en",
            )

        scaled_quantity = (
            ingredient.quantity
            if not ingredient.is_scalable
            else ingredient.quantity * ratio
        )

        return self._format_ingredient_quantity(
            quantity=scaled_quantity,
            unit_label=ingredient.unit_label,
            text_override=None,
            language_code="en",
        )

    def _format_ingredient_quantity(
        self,
        quantity: Decimal | None,
        unit_label: str | None,
        text_override: str | None,
        language_code: str = "en",
    ) -> str:
        if text_override:
            return text_override

        parts: list[str] = []

        if quantity is not None:
            parts.append(self._format_decimal(quantity))

        if unit_label:
            parts.append(unit_label)

        if parts:
            return " ".join(parts)

        if language_code == "ru":
            return "по необходимости"

        if language_code == "ar":
            return "حسب الحاجة"

        return translate("en", "service.recipe.as_needed")

    @staticmethod
    def _coerce_servings_decimal(value: Decimal | int | float) -> Decimal:
        if isinstance(value, Decimal):
            return value

        return Decimal(str(value))

    @staticmethod
    def _format_decimal(value: Decimal) -> str:
        normalized = value.normalize()
        text = format(normalized, "f")

        if "." in text:
            text = text.rstrip("0").rstrip(".")

        return text

    def _resolve_or_create_ingredient(
        self,
        session: Session,
        ingredient_repository: IngredientRepository,
        english_language_id: int,
        arabic_language_id: int,
        russian_language_id: int,
        name_en: str,
        name_ar: str | None,
        name_ru: str | None,
        default_unit_id: int | None,
    ) -> Ingredient:
        cleaned_en = name_en.strip()
        cleaned_ar = self._clean_optional_text(name_ar)
        cleaned_ru = self._clean_optional_text(name_ru)

        ingredient = ingredient_repository.get_by_translation_name(cleaned_en, "en")

        if ingredient is None and cleaned_ar:
            ingredient = ingredient_repository.get_by_translation_name(cleaned_ar, "ar")

        if ingredient is None and cleaned_ru:
            ingredient = ingredient_repository.get_by_translation_name(cleaned_ru, "ru")

        if ingredient is not None:
            if ingredient.default_unit_id is None:
                ingredient.default_unit_id = default_unit_id

            if cleaned_en:
                self._ensure_ingredient_translation(
                    session=session,
                    ingredient_id=ingredient.id,
                    language_id=english_language_id,
                    name=cleaned_en,
                )

            if cleaned_ar:
                self._ensure_ingredient_translation(
                    session=session,
                    ingredient_id=ingredient.id,
                    language_id=arabic_language_id,
                    name=cleaned_ar,
                )

            if cleaned_ru:
                self._ensure_ingredient_translation(
                    session=session,
                    ingredient_id=ingredient.id,
                    language_id=russian_language_id,
                    name=cleaned_ru,
                )

            return ingredient

        slug = self._generate_unique_slug(
            session,
            cleaned_en or cleaned_ar or cleaned_ru or "ingredient",
        )

        ingredient = ingredient_repository.add(
            Ingredient(
                slug=slug,
                default_unit_id=default_unit_id,
                is_active=True,
            )
        )

        session.add(
            IngredientTranslation(
                ingredient_id=ingredient.id,
                language_id=english_language_id,
                name=cleaned_en,
            )
        )

        if cleaned_ar:
            session.add(
                IngredientTranslation(
                    ingredient_id=ingredient.id,
                    language_id=arabic_language_id,
                    name=cleaned_ar,
                )
            )

        if cleaned_ru:
            session.add(
                IngredientTranslation(
                    ingredient_id=ingredient.id,
                    language_id=russian_language_id,
                    name=cleaned_ru,
                )
            )

        return ingredient

    def _ensure_ingredient_translation(
        self,
        session: Session,
        ingredient_id: int,
        language_id: int,
        name: str,
    ) -> None:
        cleaned_name = name.strip()

        if not cleaned_name:
            return

        existing_translation = (
            session.query(IngredientTranslation)
            .filter(
                IngredientTranslation.ingredient_id == ingredient_id,
                IngredientTranslation.language_id == language_id,
            )
            .first()
        )

        if existing_translation is None:
            session.add(
                IngredientTranslation(
                    ingredient_id=ingredient_id,
                    language_id=language_id,
                    name=cleaned_name,
                )
            )
            return

        if not existing_translation.name:
            existing_translation.name = cleaned_name

    def _upsert_recipe_translation(
        self,
        session: Session,
        recipe_id: int,
        language_id: int,
        title: str,
        description: str | None,
    ) -> None:
        translation = (
            session.query(RecipeTranslation)
            .filter(
                RecipeTranslation.recipe_id == recipe_id,
                RecipeTranslation.language_id == language_id,
            )
            .first()
        )

        cleaned_title = title.strip()
        cleaned_description = self._clean_optional_text(description)

        if translation is None:
            session.add(
                RecipeTranslation(
                    recipe_id=recipe_id,
                    language_id=language_id,
                    title=cleaned_title,
                    short_description=cleaned_description,
                )
            )
            return

        translation.title = cleaned_title
        translation.short_description = cleaned_description

    @staticmethod
    def _clean_optional_text(value: str | None) -> str | None:
        if value is None:
            return None

        stripped = value.strip()
        return stripped or None

    def _get_language(self, session: Session, code: str) -> Language:
        language = session.query(Language).filter(Language.code == code).one()
        return language

    def _generate_unique_slug(self, session: Session, text: str) -> str:
        base_slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_") or "ingredient"
        candidate = base_slug
        counter = 2

        while session.query(Ingredient).filter(Ingredient.slug == candidate).first() is not None:
            candidate = f"{base_slug}_{counter}"
            counter += 1

        return candidate

    def _validate_create_input(self, input_data: CreateRecipeInput) -> None:
        if not input_data.title_en.strip():
            raise RecipeValidationError(
                translate("en", "service.validation.title_required")
            )

        if not self._clean_optional_text(input_data.title_ar):
            raise RecipeValidationError(
                translate("en", "service.validation.title_ar_required")
            )

        if not self._clean_optional_text(input_data.title_ru):
            raise RecipeValidationError(
                translate("en", "service.validation.title_ru_required")
            )

        if not input_data.category_id or input_data.category_id <= 0:
            raise RecipeValidationError(
                translate("en", "service.validation.category_required")
            )

        if input_data.prep_time_minutes < 0 or input_data.cook_time_minutes < 0:
            raise RecipeValidationError(
                translate("en", "service.validation.time_non_negative")
            )

        if input_data.base_servings <= 0:
            raise RecipeValidationError(
                translate("en", "service.validation.servings_positive")
            )

        if not input_data.ingredients:
            raise RecipeValidationError(
                translate("en", "service.validation.ingredient_required")
            )

        if not input_data.steps:
            raise RecipeValidationError(
                translate("en", "service.validation.step_required")
            )

        for ingredient in input_data.ingredients:
            if not ingredient.name_en.strip():
                raise RecipeValidationError(
                    translate("en", "service.validation.ingredient_name_required")
                )

            if ingredient.quantity is not None and ingredient.quantity < 0:
                raise RecipeValidationError(
                    translate(
                        "en",
                        "service.validation.ingredient_quantity_non_negative",
                    )
                )

        for step in input_data.steps:
            if not step.instruction_en.strip():
                raise RecipeValidationError(
                    translate("en", "service.validation.step_instruction_required")
                )

            if not self._clean_optional_text(step.instruction_ar):
                raise RecipeValidationError(
                    translate("en", "service.validation.step_instruction_ar_required")
                )

            if not self._clean_optional_text(step.instruction_ru):
                raise RecipeValidationError(
                    translate("en", "service.validation.step_instruction_ru_required")
                )

            if step.estimated_minutes is not None and step.estimated_minutes < 0:
                raise RecipeValidationError(
                    translate("en", "service.validation.step_minutes_non_negative")
                )

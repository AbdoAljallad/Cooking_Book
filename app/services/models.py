from __future__ import annotations

from dataclasses import dataclass

from decimal import Decimal

from app.repositories.projections import LocalizedCategory, LocalizedTag, LocalizedUnit, RecipeListItem
from app.services.image_service import RecipeImageInput


@dataclass(frozen=True, slots=True)
class AppContext:
    profile_id: int | None
    profile_name: str
    language_code: str
    theme_name: str
    layout_direction: str


@dataclass(frozen=True, slots=True)
class HomeDashboardData:
    context: AppContext
    categories: list[LocalizedCategory]
    tags: list[LocalizedTag]
    featured_recipes: list[RecipeListItem]
    latest_recipes: list[RecipeListItem]
    search_text: str
    selected_category_slug: str | None
    selected_category_name: str | None

    @property
    def has_active_filters(self) -> bool:
        return bool(self.search_text or self.selected_category_slug)


@dataclass(frozen=True, slots=True)
class RecipeIngredientDetail:
    item_name: str
    quantity: Decimal | None
    unit_label: str | None
    is_scalable: bool
    quantity_text_override: str | None
    display_quantity: str
    preparation_note: str | None


@dataclass(frozen=True, slots=True)
class RecipeStepDetail:
    sort_order: int
    instruction: str
    estimated_minutes: int | None


@dataclass(frozen=True, slots=True)
class RecipeDetailsData:
    id: int
    title: str
    short_description: str | None
    image_path: str | None
    category_name: str
    prep_time_minutes: int
    cook_time_minutes: int
    total_time_minutes: int
    base_servings: Decimal
    base_servings_display: str
    selected_servings: Decimal
    selected_servings_display: str
    difficulty_level: str
    source_type: str
    is_favorite: bool
    personal_rating: int | None
    personal_note: str | None
    tags: list[str]
    ingredients: list[RecipeIngredientDetail]
    steps: list[RecipeStepDetail]


@dataclass(frozen=True, slots=True)
class CreateRecipeIngredientInput:
    name_en: str
    name_ar: str | None
    name_ru: str | None
    quantity: Decimal | None
    unit_id: int | None
    is_scalable: bool
    preparation_note: str | None
    quantity_text_override: str | None


@dataclass(frozen=True, slots=True)
class CreateRecipeStepInput:
    instruction_en: str
    instruction_ar: str | None
    instruction_ru: str | None
    estimated_minutes: int | None


@dataclass(frozen=True, slots=True)
class CreateRecipeInput:
    title_en: str
    title_ar: str | None
    title_ru: str | None
    short_description_en: str | None
    short_description_ar: str | None
    short_description_ru: str | None
    category_id: int
    image_path: str | None
    prep_time_minutes: int
    cook_time_minutes: int
    base_servings: Decimal
    difficulty_level: str
    source_type: str
    tag_ids: list[int]
    ingredients: list[CreateRecipeIngredientInput]
    steps: list[CreateRecipeStepInput]
    image_input: RecipeImageInput | None = None


@dataclass(frozen=True, slots=True)
class EditRecipeFormData:
    recipe_id: int
    title_en: str
    title_ar: str | None
    title_ru: str | None
    short_description_en: str | None
    short_description_ar: str | None
    short_description_ru: str | None
    category_id: int
    image_path: str | None
    prep_time_minutes: int
    cook_time_minutes: int
    base_servings: Decimal
    difficulty_level: str
    source_type: str
    tag_ids: list[int]
    ingredients: list[CreateRecipeIngredientInput]
    steps: list[CreateRecipeStepInput]


@dataclass(frozen=True, slots=True)
class CreateRecipeFormData:
    context: AppContext
    categories: list[LocalizedCategory]
    units: list[LocalizedUnit]
    tags: list[LocalizedTag]


@dataclass(frozen=True, slots=True)
class LanguageOption:
    code: str
    label: str
    native_name: str
    is_rtl: bool


@dataclass(frozen=True, slots=True)
class ThemeOption:
    name: str
    label: str


@dataclass(frozen=True, slots=True)
class SettingsViewData:
    context: AppContext
    available_languages: list[LanguageOption]
    available_themes: list[ThemeOption]
    selected_language_code: str
    selected_theme_name: str
    layout_direction: str

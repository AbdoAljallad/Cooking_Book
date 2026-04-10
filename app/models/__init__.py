"""ORM model exports for metadata registration and Alembic discovery."""

from app.models.category import Category, CategoryTranslation
from app.models.ingredient import Ingredient, IngredientTranslation
from app.models.language import Language
from app.models.profile import Profile
from app.models.recipe import (
    Favorite,
    Recipe,
    RecipeIngredient,
    RecipeNote,
    RecipeRating,
    RecipeStep,
    RecipeStepTranslation,
    RecipeTag,
    RecipeTranslation,
)
from app.models.settings import AppSetting
from app.models.tag import Tag, TagTranslation
from app.models.unit import Unit, UnitTranslation

__all__ = [
    "AppSetting",
    "Category",
    "CategoryTranslation",
    "Favorite",
    "Ingredient",
    "IngredientTranslation",
    "Language",
    "Profile",
    "Recipe",
    "RecipeIngredient",
    "RecipeNote",
    "RecipeRating",
    "RecipeStep",
    "RecipeStepTranslation",
    "RecipeTag",
    "RecipeTranslation",
    "Tag",
    "TagTranslation",
    "Unit",
    "UnitTranslation",
]

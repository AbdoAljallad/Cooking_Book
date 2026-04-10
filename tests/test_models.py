import app.models as models
from app.database.base import Base
from app.models.recipe import Recipe
from migrations.env import target_metadata


EXPECTED_TABLES = {
    "languages",
    "profiles",
    "app_settings",
    "categories",
    "category_translations",
    "recipes",
    "recipe_translations",
    "ingredients",
    "ingredient_translations",
    "units",
    "unit_translations",
    "recipe_ingredients",
    "recipe_steps",
    "recipe_step_translations",
    "tags",
    "tag_translations",
    "recipe_tags",
    "favorites",
    "recipe_notes",
    "recipe_ratings",
}


def test_model_exports_import_cleanly() -> None:
    assert models.Recipe is Recipe
    assert models.Language.__tablename__ == "languages"


def test_metadata_contains_expected_tables() -> None:
    assert EXPECTED_TABLES.issubset(Base.metadata.tables.keys())


def test_alembic_target_metadata_matches_base_metadata() -> None:
    assert target_metadata is Base.metadata


def test_recipe_total_time_property() -> None:
    recipe = Recipe(
        category_id=1,
        prep_time_minutes=20,
        cook_time_minutes=35,
        base_servings=4,
        created_by_profile_id=1,
    )

    assert recipe.total_time_minutes == 55

from decimal import Decimal
from pathlib import Path

import app.models  # noqa: F401
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.config.settings import AppSettings, DatabaseSettings, UISettings
from app.database.base import Base
from app.models import (
    Category,
    Ingredient,
    IngredientTranslation,
    Profile,
    Recipe,
    RecipeIngredient,
    RecipeStep,
    RecipeStepTranslation,
    RecipeTag,
    RecipeTranslation,
    Tag,
    Unit,
)
from app.models.enums import DifficultyLevel, RecipeSourceType
from app.seeds.runner import run_seed
from app.services import (
    AppContextService,
    CategoryService,
    CreateRecipeIngredientInput,
    CreateRecipeInput,
    CreateRecipeStepInput,
    HomeService,
    RecipeService,
    SettingsService,
    TagService,
)
from app.ui.themes.manager import ThemeManager


def _build_session_factory(tmp_path: Path):
    engine = create_engine(f"sqlite:///{tmp_path / 'service_test.db'}", future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def _build_settings() -> AppSettings:
    return AppSettings(
        database=DatabaseSettings(name="service_test"),
        ui=UISettings(default_theme="dark", language="en", direction="ltr"),
    )


def _insert_recipe(session_factory) -> int:
    with session_factory() as session:
        profile = session.execute(select(Profile).where(Profile.email == "local@cookbook.app")).scalar_one()
        category = session.execute(select(Category).where(Category.slug == "soups")).scalar_one()
        recipe = Recipe(
            category_id=category.id,
            image_path=None,
            prep_time_minutes=10,
            cook_time_minutes=20,
            base_servings=Decimal("2.00"),
            difficulty_level=DifficultyLevel.EASY,
            source_type=RecipeSourceType.ORIGINAL,
            is_active=True,
            created_by_profile_id=profile.id,
        )
        session.add(recipe)
        session.flush()
        session.add(
            RecipeTranslation(
                recipe_id=recipe.id,
                language_id=1,
                title="Tomato Soup",
                short_description="Silky tomato soup.",
            )
        )
        session.commit()
        return recipe.id


def _insert_second_home_recipe(session_factory) -> None:
    with session_factory() as session:
        profile = session.execute(select(Profile).where(Profile.email == "local@cookbook.app")).scalar_one()
        category = session.execute(select(Category).where(Category.slug == "desserts")).scalar_one()
        recipe = Recipe(
            category_id=category.id,
            image_path=None,
            prep_time_minutes=18,
            cook_time_minutes=32,
            base_servings=Decimal("6.00"),
            difficulty_level=DifficultyLevel.MEDIUM,
            source_type=RecipeSourceType.ADAPTED,
            is_active=True,
            created_by_profile_id=profile.id,
        )
        session.add(recipe)
        session.flush()
        session.add_all(
            [
                RecipeTranslation(
                    recipe_id=recipe.id,
                    language_id=1,
                    title="Date Cake",
                    short_description="Soft cake with warm spices.",
                ),
                RecipeTranslation(
                    recipe_id=recipe.id,
                    language_id=2,
                    title="كيك التمر",
                    short_description="كيك طري بنكهة دافئة.",
                ),
            ]
        )
        session.commit()


def _insert_detailed_recipe(session_factory) -> int:
    with session_factory() as session:
        profile = session.execute(select(Profile).where(Profile.email == "local@cookbook.app")).scalar_one()
        category = session.execute(select(Category).where(Category.slug == "soups")).scalar_one()
        gram_unit = session.execute(select(Unit).where(Unit.code == "gram")).scalar_one()
        piece_unit = session.execute(select(Unit).where(Unit.code == "piece")).scalar_one()
        tag = session.execute(select(Tag).where(Tag.slug == "healthy")).scalar_one()

        red_lentils = Ingredient(slug="red_lentils", default_unit_id=gram_unit.id, is_active=True)
        bay_leaf = Ingredient(slug="bay_leaf", default_unit_id=piece_unit.id, is_active=True)
        salt = Ingredient(slug="salt", default_unit_id=None, is_active=True)
        session.add_all([red_lentils, bay_leaf, salt])
        session.flush()

        session.add_all(
            [
                IngredientTranslation(ingredient_id=red_lentils.id, language_id=1, name="Red Lentils"),
                IngredientTranslation(ingredient_id=red_lentils.id, language_id=2, name="عدس أحمر"),
                IngredientTranslation(ingredient_id=bay_leaf.id, language_id=1, name="Bay Leaf"),
                IngredientTranslation(ingredient_id=bay_leaf.id, language_id=2, name="ورق غار"),
                IngredientTranslation(ingredient_id=salt.id, language_id=1, name="Salt"),
                IngredientTranslation(ingredient_id=salt.id, language_id=2, name="ملح"),
            ]
        )

        recipe = Recipe(
            category_id=category.id,
            image_path=None,
            prep_time_minutes=12,
            cook_time_minutes=28,
            base_servings=Decimal("4.00"),
            difficulty_level=DifficultyLevel.EASY,
            source_type=RecipeSourceType.ORIGINAL,
            is_active=True,
            created_by_profile_id=profile.id,
        )
        session.add(recipe)
        session.flush()

        session.add_all(
            [
                RecipeTranslation(
                    recipe_id=recipe.id,
                    language_id=1,
                    title="Lentil Soup",
                    short_description="A bright and comforting soup.",
                ),
                RecipeTranslation(
                    recipe_id=recipe.id,
                    language_id=2,
                    title="شوربة عدس",
                    short_description="شوربة مريحة ودافئة.",
                ),
                RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_id=red_lentils.id,
                    unit_id=gram_unit.id,
                    quantity=Decimal("250.000"),
                    is_scalable=True,
                    sort_order=1,
                    preparation_note="Rinsed well",
                ),
                RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_id=bay_leaf.id,
                    unit_id=piece_unit.id,
                    quantity=Decimal("1.000"),
                    is_scalable=False,
                    sort_order=2,
                ),
                RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_id=salt.id,
                    unit_id=None,
                    quantity=None,
                    is_scalable=True,
                    sort_order=3,
                    text_override="To taste",
                ),
                RecipeStep(
                    recipe_id=recipe.id,
                    sort_order=1,
                    estimated_minutes=10,
                ),
                RecipeTag(recipe_id=recipe.id, tag_id=tag.id),
            ]
        )
        session.flush()

        step = session.execute(select(RecipeStep).where(RecipeStep.recipe_id == recipe.id)).scalar_one()
        session.add_all(
            [
                RecipeStepTranslation(
                    recipe_step_id=step.id,
                    language_id=1,
                    instruction="Saute the aromatics, then simmer the lentils.",
                ),
                RecipeStepTranslation(
                    recipe_step_id=step.id,
                    language_id=2,
                    instruction="شوح النكهات ثم اطه العدس على نار هادئة.",
                ),
            ]
        )
        session.commit()
        return recipe.id


def test_app_context_service_uses_seeded_profile_settings(tmp_path: Path) -> None:
    session_factory = _build_session_factory(tmp_path)
    run_seed(session_factory)

    service = AppContextService(settings=_build_settings(), session_factory=session_factory)
    context = service.get_context()

    assert context.profile_name == "Local User"
    assert context.language_code == "en"
    assert context.theme_name == "dark"


def test_app_context_service_falls_back_on_non_sqlalchemy_connection_error() -> None:
    settings = _build_settings()

    def broken_session_factory():
        raise RuntimeError("driver dependency missing")

    service = AppContextService(settings=settings, session_factory=broken_session_factory)  # type: ignore[arg-type]
    context = service.get_context()

    assert context.profile_id is None
    assert context.profile_name == "Local User"
    assert context.language_code == "en"
    assert context.theme_name == "dark"


def test_home_service_returns_seeded_dashboard_without_recipes(tmp_path: Path) -> None:
    session_factory = _build_session_factory(tmp_path)
    run_seed(session_factory)
    settings = _build_settings()

    home_service = HomeService(
        context_service=AppContextService(settings=settings, session_factory=session_factory),
        category_service=CategoryService(session_factory=session_factory),
        tag_service=TagService(session_factory=session_factory),
        recipe_service=RecipeService(session_factory=session_factory),
    )

    dashboard = home_service.get_dashboard_data()

    assert len(dashboard.categories) == 14
    assert len(dashboard.tags) == 8
    assert dashboard.latest_recipes == []
    assert dashboard.featured_recipes == []
    assert dashboard.search_text == ""
    assert dashboard.selected_category_slug is None


def test_home_service_combines_search_and_category_filters(tmp_path: Path) -> None:
    session_factory = _build_session_factory(tmp_path)
    run_seed(session_factory)
    _insert_recipe(session_factory)
    _insert_second_home_recipe(session_factory)
    settings = _build_settings()

    home_service = HomeService(
        context_service=AppContextService(settings=settings, session_factory=session_factory),
        category_service=CategoryService(session_factory=session_factory),
        tag_service=TagService(session_factory=session_factory),
        recipe_service=RecipeService(session_factory=session_factory),
    )

    filtered = home_service.get_filtered_dashboard_data(query_text="cake", category_slug="desserts")
    none_found = home_service.get_filtered_dashboard_data(query_text="cake", category_slug="soups")

    assert filtered.search_text == "cake"
    assert filtered.selected_category_slug == "desserts"
    assert filtered.selected_category_name == "Desserts"
    assert filtered.featured_recipes == []
    assert len(filtered.latest_recipes) == 1
    assert filtered.latest_recipes[0].title == "Date Cake"
    assert none_found.has_active_filters is True
    assert none_found.latest_recipes == []


def test_home_service_returns_russian_reference_labels(tmp_path: Path) -> None:
    session_factory = _build_session_factory(tmp_path)
    run_seed(session_factory)
    settings = AppSettings(
        database=DatabaseSettings(name="service_test"),
        ui=UISettings(default_theme="dark", language="ru", direction="ltr"),
    )
    SettingsService(
        settings=settings,
        theme_manager=ThemeManager(),
        session_factory=session_factory,
    ).save_settings(language_code="ru", theme_name="dark")

    home_service = HomeService(
        context_service=AppContextService(settings=settings, session_factory=session_factory),
        category_service=CategoryService(session_factory=session_factory),
        tag_service=TagService(session_factory=session_factory),
        recipe_service=RecipeService(session_factory=session_factory),
    )

    dashboard = home_service.get_dashboard_data()

    assert dashboard.context.language_code == "ru"
    assert any(item.display_name == "Супы" for item in dashboard.categories)
    assert any(item.display_name == "Быстро" for item in dashboard.tags)


def test_recipe_service_reads_home_recipes(tmp_path: Path) -> None:
    session_factory = _build_session_factory(tmp_path)
    run_seed(session_factory)
    _insert_recipe(session_factory)

    service = RecipeService(session_factory=session_factory)
    recipes = service.list_home_recipes("en")

    assert len(recipes) == 1
    assert recipes[0].title == "Tomato Soup"


def test_recipe_service_builds_language_aware_details(tmp_path: Path) -> None:
    session_factory = _build_session_factory(tmp_path)
    run_seed(session_factory)
    recipe_id = _insert_detailed_recipe(session_factory)

    service = RecipeService(session_factory=session_factory)
    details = service.get_recipe_details(recipe_id, "ar")

    assert details is not None
    assert details.title == "شوربة عدس"
    assert details.category_name == "شوربات"
    assert details.tags == ["صحي"]
    assert len(details.ingredients) == 3
    assert details.ingredients[0].item_name == "عدس أحمر"
    assert details.steps[0].instruction.startswith("شوح")


def test_recipe_service_scales_ingredients_for_target_servings(tmp_path: Path) -> None:
    session_factory = _build_session_factory(tmp_path)
    run_seed(session_factory)
    recipe_id = _insert_detailed_recipe(session_factory)

    service = RecipeService(session_factory=session_factory)
    details = service.get_recipe_details(recipe_id, "en", target_servings=Decimal("8"))

    assert details is not None
    assert details.base_servings_display == "4"
    assert details.selected_servings_display == "8"
    assert details.ingredients[0].display_quantity == "500 g"
    assert details.ingredients[1].display_quantity == "1 pc"
    assert details.ingredients[2].display_quantity == "To taste"


def test_recipe_service_can_create_recipe_with_related_records(tmp_path: Path) -> None:
    session_factory = _build_session_factory(tmp_path)
    run_seed(session_factory)

    with session_factory() as session:
        profile = session.execute(select(Profile).where(Profile.email == "local@cookbook.app")).scalar_one()
        category = session.execute(select(Category).where(Category.slug == "soups")).scalar_one()
        tag = session.execute(select(Tag).where(Tag.slug == "quick")).scalar_one()
        unit = session.execute(select(Unit).where(Unit.code == "gram")).scalar_one()

    service = RecipeService(session_factory=session_factory)
    recipe_id = service.create_recipe(
        CreateRecipeInput(
            title_en="Weeknight Soup",
            title_ru="Quick Soup RU",
            title_ar="شوربة سريعة",
            short_description_en="Quick soup for testing.",
            short_description_ru="Quick soup Russian summary.",
            short_description_ar="شوربة سريعة للاختبار.",
            category_id=category.id,
            image_path=None,
            prep_time_minutes=8,
            cook_time_minutes=22,
            base_servings=Decimal("3.00"),
            difficulty_level="easy",
            source_type="original",
            tag_ids=[tag.id],
            ingredients=[
                CreateRecipeIngredientInput(
                    name_en="Carrot",
                    name_ru="Carrot RU",
                    name_ar="جزر",
                    quantity=Decimal("150.000"),
                    unit_id=unit.id,
                    is_scalable=True,
                    preparation_note="Diced small",
                    quantity_text_override=None,
                )
            ],
            steps=[
                CreateRecipeStepInput(
                    instruction_en="Cook everything until tender.",
                    instruction_ru="Cook everything RU.",
                    instruction_ar="اطبخ كل شيء حتى ينضج.",
                    estimated_minutes=15,
                )
            ],
        ),
        created_by_profile_id=profile.id,
    )

    details = service.get_recipe_details(recipe_id, "ar")

    assert details is not None
    assert details.title == "شوربة سريعة"
    assert details.tags == ["سريع"]
    assert details.ingredients[0].item_name == "جزر"
    assert details.steps[0].instruction == "اطبخ كل شيء حتى ينضج."


    ru_details = service.get_recipe_details(recipe_id, "ru")
    assert ru_details is not None
    assert ru_details.title == "Quick Soup RU"
    assert ru_details.ingredients[0].item_name == "Carrot RU"
    assert ru_details.steps[0].instruction == "Cook everything RU."


def test_recipe_service_handles_favorites_notes_and_ratings(tmp_path: Path) -> None:
    session_factory = _build_session_factory(tmp_path)
    run_seed(session_factory)
    recipe_id = _insert_recipe(session_factory)

    with session_factory() as session:
        profile = session.execute(select(Profile).where(Profile.email == "local@cookbook.app")).scalar_one()

    service = RecipeService(session_factory=session_factory)

    is_favorite = service.toggle_favorite(recipe_id, profile.id)
    saved_rating = service.save_personal_rating(recipe_id, profile.id, 5)
    saved_note = service.save_personal_note(recipe_id, profile.id, "Brighten with lemon at the end.")
    details = service.get_recipe_details(recipe_id, "en", profile_id=profile.id)
    favorites = service.list_favorite_recipes(profile.id, "en")

    assert is_favorite is True
    assert saved_rating == 5
    assert saved_note == "Brighten with lemon at the end."
    assert details is not None
    assert details.is_favorite is True
    assert details.personal_rating == 5
    assert details.personal_note == "Brighten with lemon at the end."
    assert len(favorites) == 1
    assert favorites[0].title == "Tomato Soup"

    cleared_favorite = service.toggle_favorite(recipe_id, profile.id)
    cleared_rating = service.save_personal_rating(recipe_id, profile.id, None)
    cleared_note = service.save_personal_note(recipe_id, profile.id, "")
    refreshed = service.get_recipe_details(recipe_id, "en", profile_id=profile.id)

    assert cleared_favorite is False
    assert cleared_rating is None
    assert cleared_note is None
    assert refreshed is not None
    assert refreshed.is_favorite is False
    assert refreshed.personal_rating is None
    assert refreshed.personal_note is None


def test_settings_service_persists_language_theme_and_direction(tmp_path: Path) -> None:
    session_factory = _build_session_factory(tmp_path)
    run_seed(session_factory)
    settings = _build_settings()
    theme_manager = ThemeManager()

    context_service = AppContextService(settings=settings, session_factory=session_factory)
    service = SettingsService(
        settings=settings,
        theme_manager=theme_manager,
        session_factory=session_factory,
    )

    initial_context = context_service.get_context()
    assert initial_context.language_code == "en"

    updated_context = service.save_settings(language_code="ar", theme_name="light")
    view = service.get_settings_view_data(updated_context)
    refreshed_context = context_service.get_context()

    assert updated_context.language_code == "ar"
    assert updated_context.theme_name == "light"
    assert updated_context.layout_direction == "rtl"
    assert refreshed_context.language_code == "ar"
    assert refreshed_context.theme_name == "light"
    assert refreshed_context.layout_direction == "rtl"
    assert {item.code for item in view.available_languages} == {"en", "ar", "ru"}
    assert {item.name for item in view.available_themes} >= {"dark", "light"}

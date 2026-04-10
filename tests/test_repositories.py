from decimal import Decimal
from pathlib import Path

import app.models  # noqa: F401
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.models import Category, Favorite, Profile, Recipe, RecipeNote, RecipeRating, RecipeTranslation
from app.models.enums import DifficultyLevel, RecipeSourceType
from app.repositories import (
    AppSettingRepository,
    CategoryRepository,
    LanguageRepository,
    ProfileRepository,
    RecipeRepository,
    TagRepository,
    UnitRepository,
)
from app.seeds.runner import run_seed


def _build_session_factory(tmp_path: Path):
    database_file = tmp_path / "repository_test.db"
    engine = create_engine(f"sqlite:///{database_file}", future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def _insert_recipe(
    session_factory,
    *,
    category_slug: str,
    title_en: str,
    title_ar: str,
    description_en: str,
    description_ar: str,
) -> int:
    with session_factory() as session:
        profile = session.execute(select(Profile).where(Profile.email == "local@cookbook.app")).scalar_one()
        category = session.execute(select(Category).where(Category.slug == category_slug)).scalar_one()
        recipe = Recipe(
            category_id=category.id,
            image_path=None,
            prep_time_minutes=15,
            cook_time_minutes=35,
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
                    title=title_en,
                    short_description=description_en,
                ),
                RecipeTranslation(
                    recipe_id=recipe.id,
                    language_id=2,
                    title=title_ar,
                    short_description=description_ar,
                ),
            ]
        )
        session.commit()
        return recipe.id


def test_reference_repositories_read_seeded_data(tmp_path: Path) -> None:
    session_factory = _build_session_factory(tmp_path)
    run_seed(session_factory)

    with session_factory() as session:
        languages = LanguageRepository(session).list_all()
        default_profile = ProfileRepository(session).get_default_profile()
        app_setting = AppSettingRepository(session).get_for_profile(default_profile.id)  # type: ignore[arg-type]
        categories = CategoryRepository(session).list_all(language_code="ar")
        units = UnitRepository(session).list_all(language_code="en")
        tags = TagRepository(session).list_all(language_code="ar")

        assert [language.code for language in languages] == ["ar", "en", "ru"]
        assert default_profile is not None
        assert default_profile.email == "local@cookbook.app"
        assert app_setting is not None
        assert app_setting.ui_language.code == "en"
        assert categories[0].display_name
        assert categories[0].language_code == "ar"
        assert units[0].display_name
        assert units[0].language_code == "en"
        assert tags[0].display_name
        assert tags[0].language_code == "ar"


def test_single_record_repository_methods(tmp_path: Path) -> None:
    session_factory = _build_session_factory(tmp_path)
    run_seed(session_factory)

    with session_factory() as session:
        assert LanguageRepository(session).get_by_code("en") is not None
        assert ProfileRepository(session).get_by_email("local@cookbook.app") is not None
        assert CategoryRepository(session).get_by_slug("desserts", language_code="ar") is not None
        assert UnitRepository(session).get_by_code("gram", language_code="ar") is not None
        assert TagRepository(session).get_by_slug("quick", language_code="en") is not None


def test_app_setting_repository_updates_profile_settings(tmp_path: Path) -> None:
    session_factory = _build_session_factory(tmp_path)
    run_seed(session_factory)

    with session_factory() as session:
        profile = ProfileRepository(session).get_default_profile()
        arabic = LanguageRepository(session).get_by_code("ar")
        assert profile is not None
        assert arabic is not None

        saved = AppSettingRepository(session).save_for_profile(
            profile_id=profile.id,
            language_id=arabic.id,
            theme_name="light",
            layout_direction="rtl",
        )
        session.commit()

        assert saved.theme_name == "light"
        assert saved.layout_direction == "rtl"

        refreshed = AppSettingRepository(session).get_for_profile(profile.id)
        assert refreshed is not None
        assert refreshed.ui_language_id == arabic.id
        assert refreshed.theme_name == "light"
        assert refreshed.layout_direction == "rtl"


def test_recipe_repository_returns_search_and_combined_filters(tmp_path: Path) -> None:
    session_factory = _build_session_factory(tmp_path)
    run_seed(session_factory)
    soup_id = _insert_recipe(
        session_factory,
        category_slug="soups",
        title_en="Lentil Soup",
        title_ar="شوربة عدس",
        description_en="Comforting red lentil soup.",
        description_ar="شوربة عدس دافئة.",
    )
    _insert_recipe(
        session_factory,
        category_slug="desserts",
        title_en="Date Cake",
        title_ar="كيك التمر",
        description_en="Soft cake with warm spices.",
        description_ar="كيك طري بنكهة دافئة.",
    )

    with session_factory() as session:
        repository = RecipeRepository(session)

        all_items = repository.list_all_basic(language_code="en")
        by_category = repository.list_by_category("soups", language_code="en")
        search_items = repository.search_basic("lentil", language_code="en")
        arabic_search = repository.search_basic("عدس", language_code="ar")
        combined = repository.list_filtered_basic(
            language_code="en",
            query_text="cake",
            category_slug="desserts",
        )
        no_match = repository.list_filtered_basic(
            language_code="en",
            query_text="cake",
            category_slug="soups",
        )
        recipe = repository.get_by_id(soup_id)

        assert len(all_items) == 2
        assert {item.title for item in all_items} == {"Lentil Soup", "Date Cake"}
        assert len(by_category) == 1
        assert by_category[0].title == "Lentil Soup"
        assert len(search_items) == 1
        assert search_items[0].title == "Lentil Soup"
        assert len(arabic_search) == 1
        assert arabic_search[0].title == "شوربة عدس"
        assert len(combined) == 1
        assert combined[0].title == "Date Cake"
        assert no_match == []
        assert recipe is not None
        assert recipe.id == soup_id


def test_recipe_repository_persists_favorites_notes_and_ratings(tmp_path: Path) -> None:
    session_factory = _build_session_factory(tmp_path)
    run_seed(session_factory)
    recipe_id = _insert_recipe(
        session_factory,
        category_slug="soups",
        title_en="Lentil Soup",
        title_ar="شوربة عدس",
        description_en="Comforting red lentil soup.",
        description_ar="شوربة عدس دافئة.",
    )

    with session_factory() as session:
        profile = session.execute(select(Profile).where(Profile.email == "local@cookbook.app")).scalar_one()
        repository = RecipeRepository(session)

        assert repository.is_favorite(recipe_id, profile.id) is False
        assert repository.set_favorite(recipe_id, profile.id, True) is True
        repository.save_note(recipe_id, profile.id, "Use less cumin next time.")
        repository.save_rating(recipe_id, profile.id, 4)
        session.commit()

    with session_factory() as session:
        profile = session.execute(select(Profile).where(Profile.email == "local@cookbook.app")).scalar_one()
        repository = RecipeRepository(session)

        favorites = repository.list_favorite_basic(profile.id, language_code="en")
        note = repository.get_note(recipe_id, profile.id)
        rating = repository.get_rating(recipe_id, profile.id)

        assert len(favorites) == 1
        assert favorites[0].title == "Lentil Soup"
        assert note is not None
        assert note.note_text == "Use less cumin next time."
        assert rating is not None
        assert rating.rating == 4

        repository.set_favorite(recipe_id, profile.id, False)
        repository.save_note(recipe_id, profile.id, "")
        repository.save_rating(recipe_id, profile.id, None)
        session.commit()

        assert session.execute(select(Favorite)).scalars().all() == []
        assert session.execute(select(RecipeNote)).scalars().all() == []
        assert session.execute(select(RecipeRating)).scalars().all() == []

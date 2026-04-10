from pathlib import Path

import app.models  # noqa: F401
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.models import (
    AppSetting,
    Category,
    CategoryTranslation,
    Language,
    Profile,
    Recipe,
    Tag,
    TagTranslation,
    Unit,
    UnitTranslation,
)
from app.seeds.runner import run_seed


def test_reference_seed_is_idempotent(tmp_path: Path) -> None:
    database_file = tmp_path / "seed_test.db"
    engine = create_engine(f"sqlite:///{database_file}", future=True)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    first = run_seed(session_factory)
    second = run_seed(session_factory)

    assert first.languages == 3
    assert second.languages == 3
    assert second.profiles == 1
    assert second.app_settings == 1
    assert second.categories == 14
    assert second.category_translations == 28
    assert second.units == 8
    assert second.unit_translations == 16
    assert second.tags == 8
    assert second.tag_translations == 16
    assert second.recipes == 0

    with session_factory() as session:
        assert session.query(Language).count() == 3
        assert session.query(Profile).count() == 1
        assert session.query(AppSetting).count() == 1
        assert session.query(Category).count() == 14
        assert session.query(CategoryTranslation).count() == 28
        assert session.query(Unit).count() == 8
        assert session.query(UnitTranslation).count() == 16
        assert session.query(Tag).count() == 8
        assert session.query(TagTranslation).count() == 16
        assert session.query(Recipe).count() == 0


def test_seed_links_default_profile_and_language(tmp_path: Path) -> None:
    database_file = tmp_path / "seed_link_test.db"
    engine = create_engine(f"sqlite:///{database_file}", future=True)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    run_seed(session_factory)

    with session_factory() as session:
        profile = session.execute(
            select(Profile).where(Profile.email == "local@cookbook.app")
        ).scalar_one()
        english = session.execute(
            select(Language).where(Language.code == "en")
        ).scalar_one()
        app_setting = session.execute(
            select(AppSetting).where(AppSetting.profile_id == profile.id)
        ).scalar_one()

        assert app_setting.ui_language_id == english.id
        assert app_setting.theme_name == "dark"
        assert app_setting.layout_direction == "ltr"

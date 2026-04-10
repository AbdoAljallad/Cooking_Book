from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import os

import app.models  # noqa: F401
from PySide6.QtCore import QBuffer, QByteArray, QIODevice
from PySide6.QtGui import QColor, QImage
from PySide6.QtWidgets import QApplication
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.config.settings import AppSettings, DatabaseSettings, UISettings
from app.database.base import Base
from app.models import Category, Profile, Recipe, RecipeTranslation, Tag, Unit
from app.models.enums import DifficultyLevel, RecipeSourceType
from app.seeds.runner import run_seed
from app.services import CreateRecipeIngredientInput, CreateRecipeInput, CreateRecipeStepInput, ImageService, RecipeService
from app.services.image_service import RecipeImageInput


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
_APP = QApplication.instance() or QApplication([])


def _build_session_factory(tmp_path: Path):
    engine = create_engine(f"sqlite:///{tmp_path / 'image_service_test.db'}", future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def _png_bytes(color: str = "#A57445") -> bytes:
    image = QImage(64, 64, QImage.Format.Format_ARGB32)
    image.fill(QColor(color))
    byte_array = QByteArray()
    buffer = QBuffer(byte_array)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(byte_array)


def test_image_service_creates_placeholder_and_resolves_display_path(tmp_path: Path) -> None:
    service = ImageService(base_dir=tmp_path)

    placeholder = service.ensure_placeholder_image()
    resolved = service.resolve_display_path(None)

    assert placeholder.exists()
    assert resolved == placeholder
    assert placeholder.name == "no_image.png"


def test_image_service_stores_recipe_image_with_predictable_name(tmp_path: Path) -> None:
    service = ImageService(base_dir=tmp_path)

    relative_path = service.store_recipe_image(17, RecipeImageInput(image_bytes=_png_bytes(), source_name="sample.png"))
    stored_file = tmp_path / relative_path

    assert relative_path == "assets/images/recipes/17.png"
    assert stored_file.exists()


def test_recipe_service_persists_managed_image_path_after_creation(tmp_path: Path) -> None:
    session_factory = _build_session_factory(tmp_path)
    run_seed(session_factory)
    image_service = ImageService(base_dir=tmp_path)
    recipe_service = RecipeService(session_factory=session_factory, image_service=image_service)

    with session_factory() as session:
        profile = session.execute(select(Profile).where(Profile.email == "local@cookbook.app")).scalar_one()
        category = session.execute(select(Category).where(Category.slug == "soups")).scalar_one()
        tag = session.execute(select(Tag).where(Tag.slug == "quick")).scalar_one()
        unit = session.execute(select(Unit).where(Unit.code == "gram")).scalar_one()

    recipe_id = recipe_service.create_recipe(
        CreateRecipeInput(
            title_en="Image Test Soup",
            title_ar=None,
            short_description_en="Recipe with managed image.",
            short_description_ar=None,
            category_id=category.id,
            image_path=None,
            prep_time_minutes=10,
            cook_time_minutes=20,
            base_servings=Decimal("2.00"),
            difficulty_level="easy",
            source_type="original",
            tag_ids=[tag.id],
            ingredients=[
                CreateRecipeIngredientInput(
                    name_en="Water",
                    name_ar=None,
                    quantity=Decimal("500.000"),
                    unit_id=unit.id,
                    is_scalable=True,
                    preparation_note=None,
                    quantity_text_override=None,
                )
            ],
            steps=[
                CreateRecipeStepInput(
                    instruction_en="Heat and serve.",
                    instruction_ar=None,
                    estimated_minutes=5,
                )
            ],
            image_input=RecipeImageInput(image_bytes=_png_bytes("#4A90E2"), source_name="clipboard.png"),
        ),
        created_by_profile_id=profile.id,
    )

    with session_factory() as session:
        recipe = session.execute(select(Recipe).where(Recipe.id == recipe_id)).scalar_one()
        translation = session.execute(select(RecipeTranslation).where(RecipeTranslation.recipe_id == recipe_id)).scalar_one()

    assert translation.title == "Image Test Soup"
    assert recipe.image_path == f"assets/images/recipes/{recipe_id}.png"
    assert (tmp_path / recipe.image_path).exists()

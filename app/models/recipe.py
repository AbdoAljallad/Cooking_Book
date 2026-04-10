from __future__ import annotations

from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import DifficultyLevel, RecipeSourceType
from app.models.mixins import PrimaryKeyMixin, TimestampMixin


def _enum_values(enum_cls: type) -> list[str]:
    return [member.value for member in enum_cls]


class Recipe(PrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "recipes"
    __table_args__ = (
        CheckConstraint("prep_time_minutes >= 0", name="prep_time_nonnegative"),
        CheckConstraint("cook_time_minutes >= 0", name="cook_time_nonnegative"),
        CheckConstraint("base_servings > 0", name="base_servings_positive"),
        Index("ix_recipes_category_active", "category_id", "is_active"),
        Index("ix_recipes_created_by_profile_id", "created_by_profile_id"),
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
    )
    image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    prep_time_minutes: Mapped[int] = mapped_column(nullable=False, default=0)
    cook_time_minutes: Mapped[int] = mapped_column(nullable=False, default=0)
    base_servings: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    difficulty_level: Mapped[DifficultyLevel] = mapped_column(
        Enum(
            DifficultyLevel,
            name="difficulty_level_enum",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            values_callable=_enum_values,
        ),
        nullable=False,
        default=DifficultyLevel.MEDIUM,
    )
    source_type: Mapped[RecipeSourceType] = mapped_column(
        Enum(
            RecipeSourceType,
            name="recipe_source_type_enum",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            values_callable=_enum_values,
        ),
        nullable=False,
        default=RecipeSourceType.ORIGINAL,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    created_by_profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="RESTRICT"),
        nullable=False,
    )

    category: Mapped["Category"] = relationship(back_populates="recipes")
    created_by_profile: Mapped["Profile"] = relationship(back_populates="created_recipes")
    favorites: Mapped[list["Favorite"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
    )
    ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="RecipeIngredient.sort_order",
    )
    notes: Mapped[list["RecipeNote"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
    )
    ratings: Mapped[list["RecipeRating"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
    )
    steps: Mapped[list["RecipeStep"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="RecipeStep.sort_order",
    )
    tag_links: Mapped[list["RecipeTag"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
    )
    translations: Mapped[list["RecipeTranslation"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
    )

    @hybrid_property
    def total_time_minutes(self) -> int:
        return (self.prep_time_minutes or 0) + (self.cook_time_minutes or 0)

    @total_time_minutes.expression
    def total_time_minutes(cls):
        return func.coalesce(cls.prep_time_minutes, 0) + func.coalesce(
            cls.cook_time_minutes, 0
        )

    def __repr__(self) -> str:
        return f"Recipe(id={self.id!r}, category_id={self.category_id!r})"


class RecipeTranslation(PrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "recipe_translations"
    __table_args__ = (
        CheckConstraint("length(title) > 0", name="title_nonempty"),
        Index("ix_recipe_translations_title", "title"),
        Index("ix_recipe_translations_recipe_language", "recipe_id", "language_id", unique=True),
    )

    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
    )
    language_id: Mapped[int] = mapped_column(
        ForeignKey("languages.id", ondelete="RESTRICT"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    short_description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    recipe: Mapped["Recipe"] = relationship(back_populates="translations")
    language: Mapped["Language"] = relationship(back_populates="recipe_translations")


class RecipeIngredient(PrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "recipe_ingredients"
    __table_args__ = (
        CheckConstraint("quantity IS NULL OR quantity >= 0", name="quantity_nonnegative"),
        CheckConstraint("sort_order >= 0", name="sort_order_nonnegative"),
        Index("ix_recipe_ingredients_recipe_sort_order", "recipe_id", "sort_order"),
    )

    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
    )
    ingredient_id: Mapped[int | None] = mapped_column(
        ForeignKey("ingredients.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    unit_id: Mapped[int | None] = mapped_column(
        ForeignKey("units.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True)
    is_scalable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(nullable=False, default=0)
    preparation_note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    text_override: Mapped[str | None] = mapped_column(String(120), nullable=True)

    ingredient: Mapped["Ingredient | None"] = relationship(back_populates="recipe_ingredients")
    recipe: Mapped["Recipe"] = relationship(back_populates="ingredients")
    unit: Mapped["Unit | None"] = relationship(back_populates="recipe_ingredients")


class RecipeStep(PrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "recipe_steps"
    __table_args__ = (
        CheckConstraint("sort_order >= 0", name="sort_order_nonnegative"),
        CheckConstraint(
            "estimated_minutes IS NULL OR estimated_minutes >= 0",
            name="estimated_minutes_nonnegative",
        ),
        Index("ix_recipe_steps_recipe_sort_order", "recipe_id", "sort_order", unique=True),
    )

    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
    )
    sort_order: Mapped[int] = mapped_column(nullable=False)
    estimated_minutes: Mapped[int | None] = mapped_column(nullable=True)

    recipe: Mapped["Recipe"] = relationship(back_populates="steps")
    translations: Mapped[list["RecipeStepTranslation"]] = relationship(
        back_populates="recipe_step",
        cascade="all, delete-orphan",
    )


class RecipeStepTranslation(PrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "recipe_step_translations"
    __table_args__ = (
        Index("ix_recipe_step_translations_recipe_step_language", "recipe_step_id", "language_id", unique=True),
    )

    recipe_step_id: Mapped[int] = mapped_column(
        ForeignKey("recipe_steps.id", ondelete="CASCADE"),
        nullable=False,
    )
    language_id: Mapped[int] = mapped_column(
        ForeignKey("languages.id", ondelete="RESTRICT"),
        nullable=False,
    )
    instruction: Mapped[str] = mapped_column(Text, nullable=False)

    language: Mapped["Language"] = relationship(back_populates="recipe_step_translations")
    recipe_step: Mapped["RecipeStep"] = relationship(back_populates="translations")


class RecipeTag(Base):
    __tablename__ = "recipe_tags"

    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    )

    recipe: Mapped["Recipe"] = relationship(back_populates="tag_links")
    tag: Mapped["Tag"] = relationship(back_populates="recipe_links")


class Favorite(TimestampMixin, Base):
    __tablename__ = "favorites"

    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"),
        primary_key=True,
    )

    profile: Mapped["Profile"] = relationship(back_populates="favorites")
    recipe: Mapped["Recipe"] = relationship(back_populates="favorites")


class RecipeNote(PrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "recipe_notes"
    __table_args__ = (
        Index("ix_recipe_notes_profile_recipe", "profile_id", "recipe_id", unique=True),
    )

    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
    )
    note_text: Mapped[str] = mapped_column(Text, nullable=False)

    profile: Mapped["Profile"] = relationship(back_populates="notes")
    recipe: Mapped["Recipe"] = relationship(back_populates="notes")


class RecipeRating(PrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "recipe_ratings"
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="rating_range"),
        Index("ix_recipe_ratings_profile_recipe", "profile_id", "recipe_id", unique=True),
    )

    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
    )
    rating: Mapped[int] = mapped_column(nullable=False)

    profile: Mapped["Profile"] = relationship(back_populates="ratings")
    recipe: Mapped["Recipe"] = relationship(back_populates="ratings")

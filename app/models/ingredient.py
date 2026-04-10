from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import PrimaryKeyMixin, TimestampMixin


class Ingredient(PrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "ingredients"
    __table_args__ = (Index("ix_ingredients_is_active", "is_active"),)

    slug: Mapped[str] = mapped_column(String(191), unique=True, nullable=False)
    default_unit_id: Mapped[int | None] = mapped_column(
        ForeignKey("units.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    default_unit: Mapped["Unit | None"] = relationship(back_populates="ingredients")
    recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="ingredient"
    )
    translations: Mapped[list["IngredientTranslation"]] = relationship(
        back_populates="ingredient",
        cascade="all, delete-orphan",
    )


class IngredientTranslation(PrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "ingredient_translations"
    __table_args__ = (
        UniqueConstraint("ingredient_id", "language_id", name="uq_ingredient_language"),
        Index("ix_ingredient_translations_name", "name"),
    )

    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="CASCADE"),
        nullable=False,
    )
    language_id: Mapped[int] = mapped_column(
        ForeignKey("languages.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(191), nullable=False)

    ingredient: Mapped["Ingredient"] = relationship(back_populates="translations")
    language: Mapped["Language"] = relationship(back_populates="ingredient_translations")

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import PrimaryKeyMixin, TimestampMixin


class Unit(PrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "units"
    __table_args__ = (Index("ix_units_is_active", "is_active"),)

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    symbol: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_fractional: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    ingredients: Mapped[list["Ingredient"]] = relationship(back_populates="default_unit")
    recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship(back_populates="unit")
    translations: Mapped[list["UnitTranslation"]] = relationship(
        back_populates="unit",
        cascade="all, delete-orphan",
    )


class UnitTranslation(PrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "unit_translations"
    __table_args__ = (
        UniqueConstraint("unit_id", "language_id", name="uq_unit_language"),
        Index("ix_unit_translations_name", "name"),
    )

    unit_id: Mapped[int] = mapped_column(
        ForeignKey("units.id", ondelete="CASCADE"),
        nullable=False,
    )
    language_id: Mapped[int] = mapped_column(
        ForeignKey("languages.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    abbreviation: Mapped[str | None] = mapped_column(String(50), nullable=True)

    language: Mapped["Language"] = relationship(back_populates="unit_translations")
    unit: Mapped["Unit"] = relationship(back_populates="translations")

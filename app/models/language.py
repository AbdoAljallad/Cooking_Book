from __future__ import annotations

from sqlalchemy import Boolean, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import PrimaryKeyMixin, TimestampMixin


class Language(PrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "languages"
    __table_args__ = (Index("ix_languages_is_active", "is_active"),)

    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    native_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_rtl: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    category_translations: Mapped[list["CategoryTranslation"]] = relationship(
        back_populates="language"
    )
    ingredient_translations: Mapped[list["IngredientTranslation"]] = relationship(
        back_populates="language"
    )
    recipe_step_translations: Mapped[list["RecipeStepTranslation"]] = relationship(
        back_populates="language"
    )
    recipe_translations: Mapped[list["RecipeTranslation"]] = relationship(
        back_populates="language"
    )
    settings: Mapped[list["AppSetting"]] = relationship(back_populates="ui_language")
    tag_translations: Mapped[list["TagTranslation"]] = relationship(
        back_populates="language"
    )
    unit_translations: Mapped[list["UnitTranslation"]] = relationship(
        back_populates="language"
    )

    def __repr__(self) -> str:
        return f"Language(id={self.id!r}, code={self.code!r})"

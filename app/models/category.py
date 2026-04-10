from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import PrimaryKeyMixin, TimestampMixin


class Category(PrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "categories"
    __table_args__ = (
        Index("ix_categories_sort_order", "sort_order"),
        Index("ix_categories_is_active", "is_active"),
    )

    slug: Mapped[str] = mapped_column(String(191), unique=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    recipes: Mapped[list["Recipe"]] = relationship(back_populates="category")
    translations: Mapped[list["CategoryTranslation"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
    )


class CategoryTranslation(PrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "category_translations"
    __table_args__ = (
        UniqueConstraint("category_id", "language_id", name="uq_category_language"),
        Index("ix_category_translations_name", "name"),
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
    )
    language_id: Mapped[int] = mapped_column(
        ForeignKey("languages.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(191), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    category: Mapped["Category"] = relationship(back_populates="translations")
    language: Mapped["Language"] = relationship(back_populates="category_translations")

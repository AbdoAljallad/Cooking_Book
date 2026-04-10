from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import PrimaryKeyMixin, TimestampMixin


class Tag(PrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "tags"
    __table_args__ = (Index("ix_tags_is_active", "is_active"),)

    slug: Mapped[str] = mapped_column(String(191), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    recipe_links: Mapped[list["RecipeTag"]] = relationship(
        back_populates="tag",
        cascade="all, delete-orphan",
    )
    translations: Mapped[list["TagTranslation"]] = relationship(
        back_populates="tag",
        cascade="all, delete-orphan",
    )


class TagTranslation(PrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "tag_translations"
    __table_args__ = (
        UniqueConstraint("tag_id", "language_id", name="uq_tag_language"),
        Index("ix_tag_translations_name", "name"),
    )

    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"),
        nullable=False,
    )
    language_id: Mapped[int] = mapped_column(
        ForeignKey("languages.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    language: Mapped["Language"] = relationship(back_populates="tag_translations")
    tag: Mapped["Tag"] = relationship(back_populates="translations")

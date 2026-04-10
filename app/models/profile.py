from __future__ import annotations

from sqlalchemy import Boolean, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import PrimaryKeyMixin, TimestampMixin


class Profile(PrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "profiles"
    __table_args__ = (
        Index("ix_profiles_is_active", "is_active"),
    )

    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str | None] = mapped_column(String(191), unique=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    app_setting: Mapped["AppSetting | None"] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan",
        uselist=False,
    )
    created_recipes: Mapped[list["Recipe"]] = relationship(
        back_populates="created_by_profile"
    )
    favorites: Mapped[list["Favorite"]] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan",
    )
    notes: Mapped[list["RecipeNote"]] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan",
    )
    ratings: Mapped[list["RecipeRating"]] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Profile(id={self.id!r}, display_name={self.display_name!r})"

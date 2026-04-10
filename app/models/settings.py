from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import PrimaryKeyMixin, TimestampMixin


class AppSetting(PrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "app_settings"

    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    ui_language_id: Mapped[int] = mapped_column(
        ForeignKey("languages.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    theme_name: Mapped[str] = mapped_column(String(50), nullable=False, default="dark")
    layout_direction: Mapped[str] = mapped_column(String(10), nullable=False, default="ltr")

    profile: Mapped["Profile"] = relationship(back_populates="app_setting")
    ui_language: Mapped["Language"] = relationship(back_populates="settings")

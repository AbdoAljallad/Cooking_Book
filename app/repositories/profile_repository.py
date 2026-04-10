from __future__ import annotations

from sqlalchemy import select

from app.models import Profile
from app.repositories.base import BaseRepository


class ProfileRepository(BaseRepository[Profile]):
    DEFAULT_EMAIL = "local@cookbook.app"

    def get_default_profile(self) -> Profile | None:
        return self.get_by_email(self.DEFAULT_EMAIL)

    def get_by_email(self, email: str) -> Profile | None:
        statement = select(Profile).where(Profile.email == email)
        return self._one_or_none(statement)

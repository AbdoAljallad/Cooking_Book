from __future__ import annotations

from sqlalchemy import select

from app.models import Language
from app.repositories.base import BaseRepository


class LanguageRepository(BaseRepository[Language]):
    def list_all(self) -> list[Language]:
        statement = select(Language).order_by(Language.code.asc())
        return self._all(statement)

    def get_by_code(self, code: str) -> Language | None:
        statement = select(Language).where(Language.code == code)
        return self._one_or_none(statement)

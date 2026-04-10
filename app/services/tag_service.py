from __future__ import annotations

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.repositories import LocalizedTag, TagRepository
from app.services.base import BaseService


class TagService(BaseService):
    def __init__(self, session_factory: sessionmaker[Session] | None = None) -> None:
        super().__init__(session_factory)

    def list_tags(self, language_code: str) -> list[LocalizedTag]:
        try:
            with self._open_session() as session:
                return TagRepository(session).list_all(language_code=language_code)
        except (SQLAlchemyError, Exception):
            return []

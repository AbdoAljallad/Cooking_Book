from __future__ import annotations

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.repositories import CategoryRepository, LocalizedCategory
from app.services.base import BaseService


class CategoryService(BaseService):
    def __init__(self, session_factory: sessionmaker[Session] | None = None) -> None:
        super().__init__(session_factory)

    def list_categories(self, language_code: str) -> list[LocalizedCategory]:
        try:
            with self._open_session() as session:
                return CategoryRepository(session).list_all(language_code=language_code)
        except (SQLAlchemyError, Exception):
            return []

from __future__ import annotations

from sqlalchemy.orm import Session, sessionmaker

from app.database.session import get_session_factory


class BaseService:
    def __init__(self, session_factory: sessionmaker[Session] | None = None) -> None:
        self.session_factory = session_factory or get_session_factory()

    def _open_session(self) -> Session:
        return self.session_factory()

from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy import Select
from sqlalchemy.orm import Session


T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Thin base class with small helpers for explicit repository queries."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def _one_or_none(self, statement: Select[tuple[T]]) -> T | None:
        return self.session.execute(statement).scalar_one_or_none()

    def _all(self, statement: Select[tuple[T]]) -> list[T]:
        return list(self.session.execute(statement).scalars().all())

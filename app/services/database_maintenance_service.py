from __future__ import annotations

from dataclasses import dataclass

import app.models  # noqa: F401
from sqlalchemy import inspect
from sqlalchemy.orm import Session, sessionmaker

from app.database.base import Base
from app.database.session import create_mysql_engine, get_session_factory
from app.config.settings import DatabaseSettings
from app.seeds.runner import SeedSummary, run_seed


@dataclass(frozen=True, slots=True)
class DatabaseMaintenanceSummary:
    existing_tables: int
    required_tables: int
    created_missing_tables: bool
    seed_summary: SeedSummary


class DatabaseMaintenanceService:
    def __init__(
        self,
        settings: DatabaseSettings | None = None,
        session_factory: sessionmaker[Session] | None = None,
    ) -> None:
        self.settings = settings
        self.session_factory = session_factory

    def ensure_ready(self) -> DatabaseMaintenanceSummary:
        if self.session_factory is not None:
            engine = self.session_factory.kw["bind"]
            session_factory = self.session_factory
        else:
            engine = create_mysql_engine(self.settings) if self.settings is not None else None
            session_factory = get_session_factory()

        if engine is None:
            raise RuntimeError("Database engine is not available.")

        required_tables = set(Base.metadata.tables.keys())
        existing_tables = set(inspect(engine).get_table_names())
        missing_tables = required_tables - existing_tables
        if missing_tables:
            Base.metadata.create_all(bind=engine, tables=[Base.metadata.tables[name] for name in sorted(missing_tables)])

        seed_summary = run_seed(session_factory)
        return DatabaseMaintenanceSummary(
            existing_tables=len(existing_tables),
            required_tables=len(required_tables),
            created_missing_tables=bool(missing_tables),
            seed_summary=seed_summary,
        )

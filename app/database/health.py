from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.config.settings import DatabaseSettings, load_settings
from app.database.session import create_mysql_engine


@dataclass(slots=True)
class DatabaseHealthResult:
    ok: bool
    message: str
    error: str | None = None


def check_database_connection(
    settings: DatabaseSettings | None = None,
) -> DatabaseHealthResult:
    database_settings = settings or load_settings().database
    engine = create_mysql_engine(database_settings)

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return DatabaseHealthResult(ok=True, message="MySQL connection is available.")
    except (SQLAlchemyError, Exception) as exc:
        return DatabaseHealthResult(
            ok=False,
            message="MySQL connection is unavailable.",
            error=str(exc),
        )
    finally:
        engine.dispose()

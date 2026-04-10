from __future__ import annotations

from contextlib import contextmanager
from functools import lru_cache
from typing import Iterator

from sqlalchemy import URL, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import DatabaseSettings, load_settings


def build_database_url(settings: DatabaseSettings) -> URL:
    return URL.create(
        drivername=settings.driver,
        username=settings.user,
        password=settings.password,
        host=settings.host,
        port=settings.port,
        database=settings.name,
        query={"charset": settings.charset},
    )


def create_mysql_engine(settings: DatabaseSettings | None = None) -> Engine:
    database_settings = settings or load_settings().database
    return create_engine(
        build_database_url(database_settings),
        echo=database_settings.echo,
        pool_pre_ping=database_settings.pool_pre_ping,
        pool_recycle=database_settings.pool_recycle,
        pool_size=database_settings.pool_size,
        max_overflow=database_settings.max_overflow,
        connect_args={"connect_timeout": database_settings.connect_timeout},
        future=True,
    )


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return create_mysql_engine()


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(
        bind=get_engine(),
        autoflush=False,
        expire_on_commit=False,
        class_=Session,
    )


def create_session() -> Session:
    return get_session_factory()()


@contextmanager
def session_scope() -> Iterator[Session]:
    session = create_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

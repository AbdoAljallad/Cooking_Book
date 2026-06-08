from __future__ import annotations

from pathlib import Path
import re
import sys

import pymysql
from sqlalchemy import create_engine, inspect

from app.config.settings import load_settings
from app.database.session import build_database_url


SOURCE_SQL_PATH = Path("data.sql")
TABLE_NAME_MAP = {
    "app_setting": "app_settings",
    "favorite": "favorites",
    "elemic_version": "alembic_version",
}
INSERT_PATTERN = re.compile(
    r"INSERT INTO\s+`(?P<table>[^`]+)`\s*\((?P<columns>.*?)\)\s*VALUES\s*(?P<values>.*?);",
    flags=re.IGNORECASE | re.DOTALL,
)


def split_rows(values_blob: str) -> list[str]:
    rows: list[str] = []
    current: list[str] = []
    in_quote = False
    escape = False
    depth = 0

    for char in values_blob:
        if escape:
            if depth > 0:
                current.append(char)
            escape = False
            continue

        if char == "\\":
            if depth > 0:
                current.append(char)
                escape = True
            continue

        if char == "'":
            if depth > 0:
                current.append(char)
            in_quote = not in_quote
            continue

        if in_quote:
            if depth > 0:
                current.append(char)
            continue

        if char == "(":
            if depth == 0:
                current = []
            depth += 1
            current.append(char)
        elif char == ")":
            if depth > 0:
                current.append(char)
            depth -= 1
            if depth == 0:
                row = "".join(current).strip()
                if row:
                    rows.append(row)
                current = []
        elif depth > 0:
            current.append(char)

    return rows


def split_fields(row_sql: str) -> list[str]:
    inner = row_sql.strip()
    if inner.startswith("(") and inner.endswith(")"):
        inner = inner[1:-1]

    fields: list[str] = []
    current: list[str] = []
    in_quote = False
    escape = False

    for char in inner:
        if escape:
            current.append(char)
            escape = False
            continue

        if char == "\\":
            current.append(char)
            escape = True
            continue

        if char == "'":
            current.append(char)
            in_quote = not in_quote
            continue

        if char == "," and not in_quote:
            fields.append("".join(current).strip())
            current = []
            continue

        current.append(char)

    if current:
        fields.append("".join(current).strip())

    return fields


def normalize_row(target_table: str, columns: list[str], fields: list[str]) -> list[str]:
    normalized = list(fields)

    if target_table == "ingredients" and "default_unit_id" in columns:
        index = columns.index("default_unit_id")
        if normalized[index] == "0":
            normalized[index] = "NULL"

    return normalized


def build_insert_statement(target_table: str, columns: list[str], rows: list[list[str]]) -> str:
    quoted_columns = ", ".join(f"`{column}`" for column in columns)
    values_sql = ",\n".join(f"({', '.join(row)})" for row in rows)
    updates_sql = ", ".join(f"`{column}` = VALUES(`{column}`)" for column in columns)
    return (
        f"INSERT INTO `{target_table}` ({quoted_columns}) VALUES\n"
        f"{values_sql}\n"
        f"ON DUPLICATE KEY UPDATE {updates_sql};"
    )


def load_schema_tables() -> set[str]:
    settings = load_settings()
    engine = create_engine(build_database_url(settings.database), future=True)
    with engine.connect() as connection:
        return set(inspect(connection).get_table_names())


def import_sql_file() -> int:
    if not SOURCE_SQL_PATH.exists():
        print(f"Missing SQL file: {SOURCE_SQL_PATH}")
        return 1

    sql_text = SOURCE_SQL_PATH.read_text(encoding="utf-8", errors="replace")
    schema_tables = load_schema_tables()
    settings = load_settings()

    statements = list(INSERT_PATTERN.finditer(sql_text))
    if not statements:
        print("No INSERT statements found in data.sql")
        return 1

    connection = pymysql.connect(
        host=settings.database.host,
        port=settings.database.port,
        user=settings.database.user,
        password=settings.database.password,
        database=settings.database.name,
        charset=settings.database.charset,
        autocommit=False,
        client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS,
    )

    imported_tables: list[str] = []
    skipped_tables: list[str] = []

    try:
        with connection.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

            for match in statements:
                source_table = match.group("table")
                target_table = TABLE_NAME_MAP.get(source_table, source_table)

                if target_table not in schema_tables:
                    skipped_tables.append(source_table)
                    continue

                columns = [part.strip().strip("`") for part in match.group("columns").split(",")]
                source_rows = split_rows(match.group("values"))
                normalized_rows = [
                    normalize_row(
                        target_table,
                        columns,
                        split_fields(row_sql),
                    )
                    for row_sql in source_rows
                ]

                sql_statement = build_insert_statement(target_table, columns, normalized_rows)
                cursor.execute(sql_statement)
                imported_tables.append(target_table)

            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    unique_imported = ", ".join(dict.fromkeys(imported_tables))
    unique_skipped = ", ".join(dict.fromkeys(skipped_tables)) or "none"
    print(f"Imported tables: {unique_imported}")
    print(f"Skipped source tables: {unique_skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(import_sql_file())

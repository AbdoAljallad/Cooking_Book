from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import tomllib


BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_FILE = Path(__file__).resolve().with_name("app_config.toml")


class SettingsValidationError(ValueError):
    """Raised when application configuration is structurally invalid."""


@dataclass(slots=True)
class DatabaseSettings:
    driver: str = "mysql+pymysql"
    host: str = "127.0.0.1"
    port: int = 3306
    name: str = "cookbook_db"
    user: str = "root"
    password: str = ""
    charset: str = "utf8mb4"
    connect_timeout: int = 3
    pool_pre_ping: bool = True
    pool_recycle: int = 1800
    pool_size: int = 5
    max_overflow: int = 10
    echo: bool = False

    def __post_init__(self) -> None:
        if not self.driver.strip():
            raise SettingsValidationError("Database driver must not be empty.")
        if not self.host.strip():
            raise SettingsValidationError("Database host must not be empty.")
        if not self.name.strip():
            raise SettingsValidationError("Database name must not be empty.")
        if not self.user.strip():
            raise SettingsValidationError("Database user must not be empty.")
        if self.port <= 0:
            raise SettingsValidationError("Database port must be a positive integer.")
        if self.connect_timeout <= 0:
            raise SettingsValidationError("Database connect_timeout must be positive.")
        if self.pool_recycle < 0:
            raise SettingsValidationError("Database pool_recycle cannot be negative.")
        if self.pool_size < 1:
            raise SettingsValidationError("Database pool_size must be at least 1.")
        if self.max_overflow < 0:
            raise SettingsValidationError("Database max_overflow cannot be negative.")


@dataclass(slots=True)
class UISettings:
    default_theme: str = "dark"
    language: str = "en"
    direction: str = "ltr"

    def __post_init__(self) -> None:
        self.default_theme = self.default_theme.strip() or "dark"
        self.language = self.language.strip().lower() or "en"
        self.direction = self.direction.strip().lower() or "ltr"
        if self.direction not in {"ltr", "rtl"}:
            raise SettingsValidationError("UI direction must be either 'ltr' or 'rtl'.")


@dataclass(slots=True)
class AppSettings:
    database: DatabaseSettings
    ui: UISettings


def _read_toml_config(config_file: Path) -> dict[str, Any]:
    if not config_file.exists():
        return {}

    with config_file.open("rb") as handle:
        data = tomllib.load(handle)
        if not isinstance(data, dict):
            raise SettingsValidationError("Application config must be a TOML table.")
        return data


def _to_bool(value: Any, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
    raise SettingsValidationError(f"Expected a boolean value, got {value!r}.")


def load_settings(config_file: Path | None = None) -> AppSettings:
    raw_config = _read_toml_config(config_file or CONFIG_FILE)
    database_raw = raw_config.get("database", {})
    ui_raw = raw_config.get("ui", {})

    if not isinstance(database_raw, dict):
        raise SettingsValidationError("The [database] section must be a TOML table.")
    if not isinstance(ui_raw, dict):
        raise SettingsValidationError("The [ui] section must be a TOML table.")

    return AppSettings(
        database=DatabaseSettings(
            driver=str(database_raw.get("driver", "mysql+pymysql")),
            host=str(database_raw.get("host", "127.0.0.1")),
            port=int(database_raw.get("port", 3306)),
            name=str(database_raw.get("name", "cookbook_db")),
            user=str(database_raw.get("user", "root")),
            password=str(database_raw.get("password", "")),
            charset=str(database_raw.get("charset", "utf8mb4")),
            connect_timeout=int(database_raw.get("connect_timeout", 3)),
            pool_pre_ping=_to_bool(database_raw.get("pool_pre_ping"), True),
            pool_recycle=int(database_raw.get("pool_recycle", 1800)),
            pool_size=int(database_raw.get("pool_size", 5)),
            max_overflow=int(database_raw.get("max_overflow", 10)),
            echo=_to_bool(database_raw.get("echo"), False),
        ),
        ui=UISettings(
            default_theme=str(ui_raw.get("default_theme", "dark")),
            language=str(ui_raw.get("language", "en")),
            direction=str(ui_raw.get("direction", "ltr")),
        ),
    )

from app.config.settings import DatabaseSettings, SettingsValidationError
from app.database.health import check_database_connection
from app.database.session import build_database_url


def test_build_database_url_uses_mysql_driver() -> None:
    settings = DatabaseSettings(
        host="localhost",
        port=3306,
        name="cookbook_db",
        user="root",
        password="secret",
    )

    url = build_database_url(settings)

    assert url.drivername == "mysql+pymysql"
    assert url.database == "cookbook_db"


def test_invalid_database_port_raises_validation_error() -> None:
    try:
        DatabaseSettings(
            host="localhost",
            port=0,
            name="cookbook_db",
            user="root",
            password="secret",
        )
    except SettingsValidationError:
        return

    raise AssertionError("Expected SettingsValidationError for invalid port.")


def test_health_check_fails_gracefully_for_unreachable_database() -> None:
    result = check_database_connection(
        DatabaseSettings(
            host="127.0.0.1",
            port=65000,
            name="cookbook_db",
            user="root",
            password="secret",
            connect_timeout=1,
        )
    )

    assert result.ok is False
    assert result.message

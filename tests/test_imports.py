from app.config.settings import load_settings
from app.ui.themes.manager import ThemeManager


def test_basic_imports() -> None:
    settings = load_settings()
    manager = ThemeManager()

    assert settings.ui.default_theme in manager.available_themes()

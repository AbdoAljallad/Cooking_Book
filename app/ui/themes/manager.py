from __future__ import annotations

from PySide6.QtWidgets import QApplication

from app.ui.themes.base import ThemeDefinition
from app.ui.themes.builtins import BUILTIN_THEMES
from app.ui.themes.styles import build_stylesheet


class ThemeManager:
    """Registers and applies themes to the QApplication."""

    def __init__(self) -> None:
        self._themes = dict(BUILTIN_THEMES)
        self._active_theme = next(iter(self._themes.values()))

    def register_theme(self, theme: ThemeDefinition) -> None:
        self._themes[theme.name] = theme

    def available_themes(self) -> list[str]:
        return list(self._themes.keys())

    def get_theme(self, theme_name: str) -> ThemeDefinition:
        return self._themes.get(theme_name, self._themes["dark"])

    @property
    def active_theme(self) -> ThemeDefinition:
        return self._active_theme

    @property
    def active_theme_name(self) -> str:
        return self._active_theme.name

    def apply_theme(self, app: QApplication, theme_name: str) -> ThemeDefinition:
        theme = self.get_theme(theme_name)
        app.setStyleSheet(build_stylesheet(theme))
        self._active_theme = theme
        return theme

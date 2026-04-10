from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.config.settings import AppSettings, load_settings
from app.ui.themes.manager import ThemeManager
from app.ui.windows.main_window import MainWindow


def create_application() -> QApplication:
    app = QApplication(sys.argv)
    app.setApplicationName("Premium Cookbook")
    app.setOrganizationName("Cooking Book")
    return app


def bootstrap_theme(app: QApplication, settings: AppSettings) -> ThemeManager:
    theme_manager = ThemeManager()
    theme_manager.apply_theme(app, settings.ui.default_theme)
    return theme_manager


def run() -> int:
    settings = load_settings()
    app = create_application()
    theme_manager = bootstrap_theme(app, settings)

    window = MainWindow(settings=settings, theme_manager=theme_manager)
    window.show()
    return app.exec()

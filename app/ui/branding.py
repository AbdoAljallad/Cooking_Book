from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap

from app.config.settings import BASE_DIR


BRANDING_DIR = BASE_DIR / "assets" / "icons"
APP_LOGO_PNG = BRANDING_DIR / "app_logo.png"
APP_ICON_ICO = BRANDING_DIR / "app_icon.ico"


def app_icon_path() -> Path:
    if APP_ICON_ICO.exists():
        return APP_ICON_ICO
    return APP_LOGO_PNG


def load_app_icon() -> QIcon:
    return QIcon(str(app_icon_path()))


def load_brand_pixmap(size: int = 56) -> QPixmap:
    pixmap = QPixmap(str(APP_LOGO_PNG))
    if pixmap.isNull():
        return QPixmap()
    return pixmap.scaled(
        size,
        size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )

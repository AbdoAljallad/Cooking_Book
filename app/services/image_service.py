from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QImage, QImageReader, QLinearGradient, QPainter, QPixmap

from app.config.settings import BASE_DIR


@dataclass(frozen=True, slots=True)
class RecipeImageInput:
    image_bytes: bytes
    source_name: str | None = None


class ImageValidationError(ValueError):
    """Raised when provided image input is unsupported or unreadable."""


class ImageService:
    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or BASE_DIR
        self.recipes_dir = self.base_dir / "assets" / "images" / "recipes"
        self.placeholders_dir = self.base_dir / "assets" / "images" / "placeholders"
        self.placeholder_path = self.placeholders_dir / "no_image.png"
        self._pixmap_cache: dict[str, QPixmap] = {}
        self._cover_cache: dict[tuple[str, int, int], QPixmap] = {}
        self._contain_cache: dict[tuple[str, int, int], QPixmap] = {}
        self._ensure_directories()
        self.ensure_placeholder_image()

    def get_supported_suffixes(self) -> set[str]:
        return {
            f".{bytes(fmt).decode('ascii', errors='ignore').lower()}"
            for fmt in QImageReader.supportedImageFormats()
        }

    def validate_image_file(self, file_path: str | Path) -> RecipeImageInput:
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            raise ImageValidationError("The selected file does not exist.")
        if path.suffix.lower() not in self.get_supported_suffixes():
            raise ImageValidationError("The selected file is not a supported image.")
        return self.validate_image_bytes(path.read_bytes(), source_name=path.name)

    def validate_image_bytes(self, image_bytes: bytes, source_name: str | None = None) -> RecipeImageInput:
        image = QImage.fromData(image_bytes)
        if image.isNull():
            raise ImageValidationError("The provided image could not be read.")
        return RecipeImageInput(image_bytes=image_bytes, source_name=source_name)

    def build_recipe_image_path(self, recipe_id: int) -> Path:
        return self.recipes_dir / f"{recipe_id}.png"

    def build_recipe_image_relative_path(self, recipe_id: int) -> str:
        return self.build_recipe_image_path(recipe_id).relative_to(self.base_dir).as_posix()

    def store_recipe_image(self, recipe_id: int, image_input: RecipeImageInput) -> str:
        image = QImage.fromData(image_input.image_bytes)
        if image.isNull():
            raise ImageValidationError("The provided image could not be read.")

        self._ensure_directories()
        normalized = image.convertToFormat(QImage.Format.Format_ARGB32)
        destination = self.build_recipe_image_path(recipe_id)
        if not normalized.save(str(destination), "PNG"):
            raise ImageValidationError("The image could not be stored in the managed recipe images folder.")
        self._invalidate_path_cache(destination)
        return destination.relative_to(self.base_dir).as_posix()

    def ensure_placeholder_image(self) -> Path:
        if self.placeholder_path.exists():
            return self.placeholder_path

        image = QImage(1200, 800, QImage.Format.Format_ARGB32)
        gradient = QLinearGradient(0, 0, 1200, 800)
        gradient.setColorAt(0, QColor("#EEF2F7"))
        gradient.setColorAt(1, QColor("#B9C5D6"))
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.fillRect(image.rect(), gradient)
        painter.setPen(QColor("#4B5A6E"))
        font = QFont("Segoe UI", 48)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(image.rect(), Qt.AlignmentFlag.AlignCenter, "No Image")
        painter.end()
        image.save(str(self.placeholder_path), "PNG")
        return self.placeholder_path

    def resolve_display_path(self, stored_path: str | None) -> Path:
        if stored_path:
            absolute_path = self.base_dir / Path(stored_path)
            if absolute_path.exists():
                return absolute_path
        return self.ensure_placeholder_image()

    def get_pixmap(self, stored_path: str | None) -> QPixmap:
        display_path = self.resolve_display_path(stored_path)
        cache_key = str(display_path.resolve())
        cached = self._pixmap_cache.get(cache_key)
        if cached is not None:
            return cached

        pixmap = QPixmap(cache_key)
        self._pixmap_cache[cache_key] = pixmap
        return pixmap

    def get_cover_pixmap(self, stored_path: str | None, width: int, height: int) -> QPixmap:
        source_pixmap = self.get_pixmap(stored_path)
        if source_pixmap.isNull():
            return QPixmap()

        display_path = self.resolve_display_path(stored_path)
        cache_key = (str(display_path.resolve()), width, height)
        cached = self._cover_cache.get(cache_key)
        if cached is not None:
            return cached

        scaled = source_pixmap.scaled(
            width,
            height,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        x = max((scaled.width() - width) // 2, 0)
        y = max((scaled.height() - height) // 2, 0)
        cover = scaled.copy(x, y, min(width, scaled.width()), min(height, scaled.height()))
        self._cover_cache[cache_key] = cover
        return cover

    def get_contain_pixmap(self, stored_path: str | None, width: int, height: int) -> QPixmap:
        source_pixmap = self.get_pixmap(stored_path)
        if source_pixmap.isNull():
            return QPixmap()

        display_path = self.resolve_display_path(stored_path)
        cache_key = (str(display_path.resolve()), width, height)
        cached = self._contain_cache.get(cache_key)
        if cached is not None:
            return cached

        contained = source_pixmap.scaled(
            width,
            height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._contain_cache[cache_key] = contained
        return contained

    def _ensure_directories(self) -> None:
        self.recipes_dir.mkdir(parents=True, exist_ok=True)
        self.placeholders_dir.mkdir(parents=True, exist_ok=True)

    def _invalidate_path_cache(self, path: Path) -> None:
        resolved = str(path.resolve())
        self._pixmap_cache.pop(resolved, None)
        stale_cover_keys = [key for key in self._cover_cache if key[0] == resolved]
        for key in stale_cover_keys:
            self._cover_cache.pop(key, None)
        stale_contain_keys = [key for key in self._contain_cache if key[0] == resolved]
        for key in stale_contain_keys:
            self._contain_cache.pop(key, None)

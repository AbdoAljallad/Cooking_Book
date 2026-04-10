from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QImage, QImageReader, QPainter

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
        return destination.relative_to(self.base_dir).as_posix()

    def ensure_placeholder_image(self) -> Path:
        if self.placeholder_path.exists():
            return self.placeholder_path

        image = QImage(1200, 800, QImage.Format.Format_ARGB32)
        image.fill(QColor("#D7DEE8"))
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(QColor("#4B5A6E"))
        font = QFont("Segoe UI", 44)
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

    def _ensure_directories(self) -> None:
        self.recipes_dir.mkdir(parents=True, exist_ok=True)
        self.placeholders_dir.mkdir(parents=True, exist_ok=True)

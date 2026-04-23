from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, Qt, Signal
from PySide6.QtGui import QAction, QDragEnterEvent, QDropEvent, QImage, QKeySequence, QPixmap
from PySide6.QtWidgets import QApplication, QFileDialog, QHBoxLayout, QLabel, QPushButton, QWidget

from app.services.image_service import ImageService, ImageValidationError, RecipeImageInput
from app.ui.components.base_card import BaseCard
from app.utils.i18n import translate


class RecipeImageInputCard(BaseCard):
    image_changed = Signal()

    def __init__(
        self,
        image_service: ImageService,
        language_code: str = "en",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("imageDropCard")
        self.setAcceptDrops(True)
        self.image_service = image_service
        self.language_code = language_code
        self._image_input: RecipeImageInput | None = None
        self._current_drop_active = False

        self._build_ui()
        self._apply_language()
        self._sync_preview()

    def recipe_image_input(self) -> RecipeImageInput | None:
        return self._image_input

    def clear_selection(self) -> None:
        self._image_input = None
        self.feedback_label.clear()
        self.feedback_label.hide()
        self._sync_preview()
        self.image_changed.emit()

    def set_language(self, language_code: str) -> None:
        self.language_code = language_code
        self._apply_language()
        self._sync_preview()

    def _build_ui(self) -> None:
        self.title_label = QLabel()
        self.title_label.setObjectName("sectionTitle")
        self.content_layout.addWidget(self.title_label)

        self.subtitle_label = QLabel()
        self.subtitle_label.setObjectName("sectionSubtitle")
        self.subtitle_label.setWordWrap(True)
        self.content_layout.addWidget(self.subtitle_label)

        self.preview_label = QLabel()
        self.preview_label.setObjectName("recipeImage")
        self.preview_label.setMinimumHeight(220)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(self.preview_label)

        actions_row = QHBoxLayout()
        actions_row.setSpacing(10)

        self.choose_button = QPushButton()
        self.choose_button.setObjectName("secondaryButton")
        self.choose_button.clicked.connect(self._choose_image)
        actions_row.addWidget(self.choose_button)

        self.paste_button = QPushButton()
        self.paste_button.setObjectName("secondaryButton")
        self.paste_button.clicked.connect(self._paste_from_clipboard)
        actions_row.addWidget(self.paste_button)

        self.clear_button = QPushButton()
        self.clear_button.setObjectName("secondaryButton")
        self.clear_button.clicked.connect(self.clear_selection)
        actions_row.addWidget(self.clear_button)
        actions_row.addStretch(1)
        self.content_layout.addLayout(actions_row)

        self.hint_label = QLabel()
        self.hint_label.setObjectName("heroSubtitle")
        self.hint_label.setWordWrap(True)
        self.content_layout.addWidget(self.hint_label)

        self.feedback_label = QLabel()
        self.feedback_label.setObjectName("formErrorBanner")
        self.feedback_label.hide()
        self.content_layout.addWidget(self.feedback_label)

        paste_action = QAction(self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self._paste_from_clipboard)
        self.addAction(paste_action)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            urls = [url for url in event.mimeData().urls() if url.isLocalFile()]
            if urls:
                event.acceptProposedAction()
                self._current_drop_active = True
                self._refresh_drop_state()
                return
        event.ignore()

    def dragLeaveEvent(self, event) -> None:
        self._current_drop_active = False
        self._refresh_drop_state()
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        self._current_drop_active = False
        self._refresh_drop_state()
        local_files = [Path(url.toLocalFile()) for url in event.mimeData().urls() if url.isLocalFile()]
        if not local_files:
            event.ignore()
            return
        self._apply_file(local_files[0])
        event.acceptProposedAction()

    def _choose_image(self) -> None:
        file_path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            self.choose_button.text(),
            "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp *.gif)",
        )
        if not file_path:
            return
        self._apply_file(Path(file_path))

    def _paste_from_clipboard(self) -> None:
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        if mime_data is None or not mime_data.hasImage():
            self._show_error(translate(self.language_code, "image.error.clipboard_empty"))
            return

        image = clipboard.image()
        if image.isNull():
            self._show_error(translate(self.language_code, "image.error.clipboard_empty"))
            return

        try:
            payload = self.image_service.validate_image_bytes(self._image_to_png_bytes(image), source_name="clipboard.png")
        except ImageValidationError:
            self._show_error(translate(self.language_code, "image.error.invalid_image"))
            return
        self._set_image_payload(payload)

    def _apply_file(self, path: Path) -> None:
        try:
            payload = self.image_service.validate_image_file(path)
        except ImageValidationError as exc:
            message = str(exc)
            if "supported image" in message.lower():
                message = translate(self.language_code, "image.error.unsupported_file")
            elif "read" in message.lower():
                message = translate(self.language_code, "image.error.invalid_image")
            self._show_error(message)
            return
        self._set_image_payload(payload)

    def _set_image_payload(self, payload: RecipeImageInput) -> None:
        self._image_input = payload
        self.feedback_label.hide()
        self._sync_preview()
        self.image_changed.emit()

    def _sync_preview(self) -> None:
        pixmap = QPixmap()
        if self._image_input is not None:
            pixmap.loadFromData(self._image_input.image_bytes)
        if pixmap.isNull():
            pixmap = QPixmap(str(self.image_service.ensure_placeholder_image()))

        self.preview_label.setPixmap(
            pixmap.scaled(
                900,
                220,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        self.preview_label.setText("")
        if self._image_input is None:
            self.hint_label.setText(
                f"{translate(self.language_code, 'image.drop_here')} • "
                f"{translate(self.language_code, 'image.no_image_selected')}\n"
                f"{translate(self.language_code, 'image.hint')}"
            )
        else:
            name = self._image_input.source_name or translate(self.language_code, "image.preview_alt")
            self.hint_label.setText(f"{name}\n{translate(self.language_code, 'image.hint')}")

    def _refresh_drop_state(self) -> None:
        self.setProperty("dropActive", self._current_drop_active)
        self.style().unpolish(self)
        self.style().polish(self)

    def _show_error(self, message: str) -> None:
        self.feedback_label.setText(message)
        self.feedback_label.show()

    def _apply_language(self) -> None:
        self.title_label.setText(translate(self.language_code, "image.title"))
        self.subtitle_label.setText(translate(self.language_code, "image.hint"))
        self.choose_button.setText(translate(self.language_code, "image.choose"))
        self.paste_button.setText(translate(self.language_code, "image.paste"))
        self.clear_button.setText(translate(self.language_code, "image.clear"))

    @staticmethod
    def _image_to_png_bytes(image: QImage) -> bytes:
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        image.save(buffer, "PNG")
        return bytes(byte_array)

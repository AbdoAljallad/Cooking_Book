from __future__ import annotations

from decimal import Decimal
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QDoubleSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.services import AppContextService, RecipeService
from app.services.image_service import ImageService
from app.services.models import RecipeDetailsData
from app.ui.components.base_card import BaseCard
from app.ui.components.detail_meta_chip import DetailMetaChip
from app.ui.components.empty_state import EmptyState
from app.ui.components.rating_control import RatingControl
from app.ui.components.section_header import SectionHeader


class RecipeDetailsPage(QWidget):
    back_requested = Signal()

    def __init__(
        self,
        recipe_service: RecipeService,
        context_service: AppContextService,
        image_service: ImageService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.recipe_service = recipe_service
        self.context_service = context_service
        self.image_service = image_service
        self.current_recipe_id: int | None = None
        self.base_details: RecipeDetailsData | None = None
        self.current_profile_id: int | None = None
        self.current_language_code: str = "en"

        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        outer.addWidget(scroll)

        container = QWidget()
        container.setObjectName("detailsPage")
        scroll.setWidget(container)

        self.layout_root = QVBoxLayout(container)
        self.layout_root.setContentsMargins(0, 0, 0, 0)
        self.layout_root.setSpacing(24)

        back_row = QHBoxLayout()
        self.back_button = QPushButton("Back to Home")
        self.back_button.setObjectName("secondaryButton")
        self.back_button.clicked.connect(self.back_requested.emit)
        back_row.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignLeft)
        back_row.addStretch(1)
        self.layout_root.addLayout(back_row)

        self.hero_card = BaseCard()
        self.hero_card.setObjectName("detailsHeroCard")
        self.layout_root.addWidget(self.hero_card)

        self.category_label = QLabel()
        self.category_label.setObjectName("eyebrowLabel")
        self.hero_card.content_layout.addWidget(self.category_label)

        self.title_label = QLabel()
        self.title_label.setObjectName("detailsTitle")
        self.title_label.setWordWrap(True)
        self.hero_card.content_layout.addWidget(self.title_label)

        self.description_label = QLabel()
        self.description_label.setObjectName("heroSubtitle")
        self.description_label.setWordWrap(True)
        self.hero_card.content_layout.addWidget(self.description_label)

        actions_row = QHBoxLayout()
        actions_row.setSpacing(12)

        self.favorite_button = QPushButton("Save to Favorites")
        self.favorite_button.setObjectName("secondaryButton")
        self.favorite_button.clicked.connect(self._toggle_favorite)
        actions_row.addWidget(self.favorite_button, alignment=Qt.AlignmentFlag.AlignLeft)

        self.detail_feedback = QLabel()
        self.detail_feedback.setObjectName("statusDetails")
        self.detail_feedback.hide()
        actions_row.addWidget(self.detail_feedback, stretch=1, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.hero_card.content_layout.addLayout(actions_row)

        self.image_label = QLabel()
        self.image_label.setObjectName("recipeImage")
        self.image_label.setMinimumHeight(260)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hero_card.content_layout.addWidget(self.image_label)

        self.meta_card = BaseCard()
        self.meta_card.content_layout.addWidget(
            SectionHeader("Recipe Snapshot", "A quick, structured overview prepared for future scaling and interaction.")
        )
        servings_row = QHBoxLayout()
        servings_row.setSpacing(12)

        servings_copy = QVBoxLayout()
        servings_copy.setSpacing(4)

        servings_label = QLabel("Servings Scaling")
        servings_label.setObjectName("sectionTitle")
        servings_copy.addWidget(servings_label)

        self.servings_caption = QLabel("Adjust the target yield and ingredient quantities update instantly.")
        self.servings_caption.setObjectName("sectionSubtitle")
        self.servings_caption.setWordWrap(True)
        servings_copy.addWidget(self.servings_caption)
        servings_row.addLayout(servings_copy, stretch=1)

        controls_row = QHBoxLayout()
        controls_row.setSpacing(8)

        self.decrease_servings_button = QPushButton("-")
        self.decrease_servings_button.setObjectName("secondaryButton")
        self.decrease_servings_button.clicked.connect(lambda: self._step_servings(-1))
        controls_row.addWidget(self.decrease_servings_button)

        self.servings_input = QDoubleSpinBox()
        self.servings_input.setObjectName("spinField")
        self.servings_input.setDecimals(2)
        self.servings_input.setMinimum(0.25)
        self.servings_input.setMaximum(999)
        self.servings_input.setSingleStep(1)
        self.servings_input.valueChanged.connect(self._handle_servings_changed)
        controls_row.addWidget(self.servings_input)

        self.increase_servings_button = QPushButton("+")
        self.increase_servings_button.setObjectName("secondaryButton")
        self.increase_servings_button.clicked.connect(lambda: self._step_servings(1))
        controls_row.addWidget(self.increase_servings_button)

        servings_row.addLayout(controls_row)
        self.meta_card.content_layout.addLayout(servings_row)

        self.meta_grid = QGridLayout()
        self.meta_grid.setHorizontalSpacing(14)
        self.meta_grid.setVerticalSpacing(14)
        self.meta_card.content_layout.addLayout(self.meta_grid)
        self.layout_root.addWidget(self.meta_card)

        self.tags_card = BaseCard()
        self.tags_card.content_layout.addWidget(
            SectionHeader("Tags", "Lightweight contextual labels for faster scanning.")
        )
        self.tags_row = QHBoxLayout()
        self.tags_row.setSpacing(8)
        self.tags_card.content_layout.addLayout(self.tags_row)
        self.layout_root.addWidget(self.tags_card)

        self.personal_card = BaseCard()
        self.personal_card.content_layout.addWidget(
            SectionHeader("Your Take", "Keep favorites, a personal rating, and a lightweight note tied to your local profile.")
        )

        rating_row = QVBoxLayout()
        rating_row.setSpacing(6)
        rating_label = QLabel("Your Rating")
        rating_label.setObjectName("sectionTitle")
        rating_row.addWidget(rating_label)

        self.rating_control = RatingControl()
        self.rating_control.rating_changed.connect(self._save_rating)
        rating_row.addWidget(self.rating_control)
        self.personal_card.content_layout.addLayout(rating_row)

        notes_label = QLabel("Personal Note")
        notes_label.setObjectName("sectionTitle")
        self.personal_card.content_layout.addWidget(notes_label)

        self.note_editor = QTextEdit()
        self.note_editor.setObjectName("multilineField")
        self.note_editor.setFixedHeight(140)
        self.note_editor.setPlaceholderText("Capture your tweaks, reminders, and serving notes here.")
        self.personal_card.content_layout.addWidget(self.note_editor)

        note_actions = QHBoxLayout()
        note_actions.setSpacing(12)
        note_actions.addStretch(1)
        self.save_note_button = QPushButton("Save Note")
        self.save_note_button.setObjectName("primaryButton")
        self.save_note_button.clicked.connect(self._save_note)
        note_actions.addWidget(self.save_note_button)
        self.personal_card.content_layout.addLayout(note_actions)
        self.layout_root.addWidget(self.personal_card)

        self.ingredients_card = BaseCard()
        self.ingredients_card.content_layout.addWidget(
            SectionHeader("Ingredients", "Structured for future servings scaling while already readable today.")
        )
        self.ingredients_layout = QVBoxLayout()
        self.ingredients_layout.setSpacing(10)
        self.ingredients_card.content_layout.addLayout(self.ingredients_layout)
        self.layout_root.addWidget(self.ingredients_card)

        self.steps_card = BaseCard()
        self.steps_card.content_layout.addWidget(
            SectionHeader("Method", "Clear, ordered steps with room for future timers and progress tracking.")
        )
        self.steps_layout = QVBoxLayout()
        self.steps_layout.setSpacing(12)
        self.steps_card.content_layout.addLayout(self.steps_layout)
        self.layout_root.addWidget(self.steps_card)

        self.missing_state = EmptyState(
            "Recipe not available.",
            "This recipe could not be loaded. It may have been removed or the database is currently unavailable.",
        )
        self.layout_root.addWidget(self.missing_state)
        self.missing_state.hide()

    def load_recipe(self, recipe_id: int) -> None:
        context = self.context_service.get_context()
        self.current_profile_id = context.profile_id
        self.current_language_code = context.language_code
        details = self.recipe_service.get_recipe_details(
            recipe_id,
            context.language_code,
            profile_id=context.profile_id,
        )
        if details is None:
            self.current_recipe_id = recipe_id
            self.base_details = None
            self._show_missing_state()
            return

        self.current_recipe_id = recipe_id
        self.base_details = details
        self.note_editor.setPlainText(details.personal_note or "")
        self.rating_control.set_rating(details.personal_rating)
        self._sync_favorite_button(details.is_favorite)
        self.detail_feedback.hide()
        self._set_servings_value(details.base_servings)
        self._apply_scaled_view()

    def _show_recipe(self, details: RecipeDetailsData) -> None:
        self.hero_card.show()
        self.meta_card.show()
        self.tags_card.show()
        self.personal_card.show()
        self.ingredients_card.show()
        self.steps_card.show()
        self.missing_state.hide()

        self.category_label.setText(details.category_name)
        self.title_label.setText(details.title)
        self.description_label.setText(
            details.short_description or "A refined recipe canvas with all essential structure in place."
        )
        self.servings_caption.setText(
            f"Base {details.base_servings_display} servings, currently viewing {details.selected_servings_display}."
        )
        self._set_image(details.image_path, details.title)
        self._populate_meta(details)
        self._populate_tags(details)
        self._populate_ingredients(details)
        self._populate_steps(details)

    def _show_missing_state(self) -> None:
        self.hero_card.hide()
        self.meta_card.hide()
        self.tags_card.hide()
        self.personal_card.hide()
        self.ingredients_card.hide()
        self.steps_card.hide()
        self.missing_state.show()

    def _set_image(self, image_path: str | None, title: str) -> None:
        path = self.image_service.resolve_display_path(image_path)
        pixmap = QPixmap(str(path))
        if not pixmap.isNull():
            self.image_label.setPixmap(
                pixmap.scaled(
                    940,
                    300,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            self.image_label.setText("")
            return

        self.image_label.setPixmap(QPixmap())
        self.image_label.setText(title)

    def _populate_meta(self, details: RecipeDetailsData) -> None:
        self._clear_grid(self.meta_grid)
        chips = [
            ("Prep", f"{details.prep_time_minutes} min"),
            ("Cook", f"{details.cook_time_minutes} min"),
            ("Total", f"{details.total_time_minutes} min"),
            ("Base", details.base_servings_display),
            ("Selected", details.selected_servings_display),
            ("Difficulty", details.difficulty_level.title()),
            ("Source", details.source_type.replace("_", " ").title()),
        ]
        for index, (label, value) in enumerate(chips):
            row = index // 3
            column = index % 3
            self.meta_grid.addWidget(DetailMetaChip(label, value), row, column)

    def _populate_tags(self, details: RecipeDetailsData) -> None:
        self._clear_box(self.tags_row)
        if not details.tags:
            placeholder = QLabel("No tags assigned yet")
            placeholder.setObjectName("heroSubtitle")
            self.tags_row.addWidget(placeholder)
            self.tags_row.addStretch(1)
            return

        for tag in details.tags:
            pill = QLabel(tag)
            pill.setObjectName("tagPill")
            self.tags_row.addWidget(pill)
        self.tags_row.addStretch(1)

    def _populate_ingredients(self, details: RecipeDetailsData) -> None:
        self._clear_column(self.ingredients_layout)
        if not details.ingredients:
            placeholder = QLabel("Ingredients have not been added yet.")
            placeholder.setObjectName("heroSubtitle")
            self.ingredients_layout.addWidget(placeholder)
            return

        for ingredient in details.ingredients:
            row = QLabel(
                f"{ingredient.display_quantity}  {ingredient.item_name}"
                if ingredient.display_quantity
                else ingredient.item_name
            )
            row.setObjectName("detailLinePrimary")
            row.setWordWrap(True)
            self.ingredients_layout.addWidget(row)

            if ingredient.preparation_note:
                note = QLabel(ingredient.preparation_note)
                note.setObjectName("detailLineSecondary")
                note.setWordWrap(True)
                self.ingredients_layout.addWidget(note)

    def _apply_scaled_view(self) -> None:
        if self.base_details is None:
            return
        target_servings = Decimal(str(self.servings_input.value()))
        scaled_details = self.recipe_service.scale_recipe_details(self.base_details, target_servings)
        self._show_recipe(scaled_details)

    def _handle_servings_changed(self, _value: float) -> None:
        self._apply_scaled_view()

    def _set_servings_value(self, servings: Decimal) -> None:
        self.servings_input.blockSignals(True)
        self.servings_input.setValue(float(servings))
        self.servings_input.blockSignals(False)

    def _step_servings(self, direction: int) -> None:
        step = self.servings_input.singleStep() * direction
        self.servings_input.setValue(max(self.servings_input.minimum(), self.servings_input.value() + step))

    def _toggle_favorite(self) -> None:
        if self.current_recipe_id is None:
            return
        if self.current_profile_id is None:
            self._show_feedback("A local profile is required to save favorites.")
            return
        try:
            is_favorite = self.recipe_service.toggle_favorite(self.current_recipe_id, self.current_profile_id)
        except Exception as exc:
            self._show_feedback(str(exc))
            return
        if self.base_details is not None:
            self.base_details = self._replace_personal_state(self.base_details, is_favorite=is_favorite)
        self._sync_favorite_button(is_favorite)
        self._show_feedback("Saved to favorites." if is_favorite else "Removed from favorites.")

    def _save_rating(self, rating: int | None) -> None:
        if self.current_recipe_id is None:
            return
        if self.current_profile_id is None:
            self._show_feedback("A local profile is required to save ratings.")
            return
        try:
            saved_rating = self.recipe_service.save_personal_rating(
                self.current_recipe_id,
                self.current_profile_id,
                rating,
            )
        except Exception as exc:
            self._show_feedback(str(exc))
            return
        if self.base_details is not None:
            self.base_details = self._replace_personal_state(self.base_details, personal_rating=saved_rating)
        self._show_feedback("Rating saved." if saved_rating is not None else "Rating cleared.")

    def _save_note(self) -> None:
        if self.current_recipe_id is None:
            return
        if self.current_profile_id is None:
            self._show_feedback("A local profile is required to save notes.")
            return
        try:
            saved_note = self.recipe_service.save_personal_note(
                self.current_recipe_id,
                self.current_profile_id,
                self.note_editor.toPlainText(),
            )
        except Exception as exc:
            self._show_feedback(str(exc))
            return
        if self.base_details is not None:
            self.base_details = self._replace_personal_state(self.base_details, personal_note=saved_note)
        self.note_editor.setPlainText(saved_note or "")
        self._show_feedback("Note saved." if saved_note else "Note cleared.")

    def _replace_personal_state(
        self,
        details: RecipeDetailsData,
        *,
        is_favorite: bool | None = None,
        personal_rating: int | None | object = ...,
        personal_note: str | None | object = ...,
    ) -> RecipeDetailsData:
        rating_value = details.personal_rating if personal_rating is ... else personal_rating
        note_value = details.personal_note if personal_note is ... else personal_note
        updated = RecipeDetailsData(
            id=details.id,
            title=details.title,
            short_description=details.short_description,
            image_path=details.image_path,
            category_name=details.category_name,
            prep_time_minutes=details.prep_time_minutes,
            cook_time_minutes=details.cook_time_minutes,
            total_time_minutes=details.total_time_minutes,
            base_servings=details.base_servings,
            base_servings_display=details.base_servings_display,
            selected_servings=details.selected_servings,
            selected_servings_display=details.selected_servings_display,
            difficulty_level=details.difficulty_level,
            source_type=details.source_type,
            is_favorite=details.is_favorite if is_favorite is None else is_favorite,
            personal_rating=rating_value,
            personal_note=note_value,
            tags=details.tags,
            ingredients=details.ingredients,
            steps=details.steps,
        )
        return updated

    def _sync_favorite_button(self, is_favorite: bool) -> None:
        self.favorite_button.setText("Favorited" if is_favorite else "Save to Favorites")
        self.favorite_button.setProperty("active", is_favorite)
        self.favorite_button.style().unpolish(self.favorite_button)
        self.favorite_button.style().polish(self.favorite_button)

    def _show_feedback(self, message: str) -> None:
        self.detail_feedback.setText(message)
        self.detail_feedback.show()

    def _populate_steps(self, details: RecipeDetailsData) -> None:
        self._clear_column(self.steps_layout)
        if not details.steps:
            placeholder = QLabel("Steps have not been added yet.")
            placeholder.setObjectName("heroSubtitle")
            self.steps_layout.addWidget(placeholder)
            return

        for step in details.steps:
            card = BaseCard()
            card.setObjectName("stepCard")

            number = QLabel(f"Step {step.sort_order}")
            number.setObjectName("eyebrowLabel")
            card.content_layout.addWidget(number)

            instruction = QLabel(step.instruction)
            instruction.setObjectName("detailLinePrimary")
            instruction.setWordWrap(True)
            card.content_layout.addWidget(instruction)

            if step.estimated_minutes is not None:
                estimate = QLabel(f"Estimated {step.estimated_minutes} min")
                estimate.setObjectName("detailLineSecondary")
                card.content_layout.addWidget(estimate)

            self.steps_layout.addWidget(card)

    @staticmethod
    def _clear_box(layout: QHBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    @staticmethod
    def _clear_column(layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    @staticmethod
    def _clear_grid(layout: QGridLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

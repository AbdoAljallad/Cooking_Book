from __future__ import annotations

from decimal import Decimal

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QDoubleSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.repositories import LocalizedTag
from app.services import (
    AppContextService,
    CategoryService,
    CreateRecipeInput,
    ImageService,
    RecipeService,
    TagService,
    UnitService,
)
from app.ui.components.base_card import BaseCard
from app.ui.components.category_chip import CategoryChip
from app.ui.components.recipe_image_input import RecipeImageInputCard
from app.ui.components.ingredient_form_row import IngredientFormRow
from app.ui.components.step_form_row import StepFormRow
from app.ui.components.section_header import SectionHeader
from app.utils.i18n import translate


class AddRecipePage(QWidget):
    back_requested = Signal()
    recipe_created = Signal(int)

    def __init__(
        self,
        context_service: AppContextService,
        category_service: CategoryService,
        tag_service: TagService,
        unit_service: UnitService,
        recipe_service: RecipeService,
        image_service: ImageService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.context_service = context_service
        self.category_service = category_service
        self.tag_service = tag_service
        self.unit_service = unit_service
        self.recipe_service = recipe_service
        self.image_service = image_service
        self.tag_chips: list[tuple[CategoryChip, LocalizedTag]] = []
        self.ingredient_rows: list[IngredientFormRow] = []
        self.step_rows: list[StepFormRow] = []

        self._build_ui()
        self.load_form_options()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        outer.addWidget(scroll)

        container = QWidget()
        container.setObjectName("addRecipePage")
        scroll.setWidget(container)

        self.root_layout = QVBoxLayout(container)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(24)

        top_row = QHBoxLayout()
        self.back_button = QPushButton("Back")
        self.back_button.setObjectName("secondaryButton")
        self.back_button.clicked.connect(self.back_requested.emit)
        top_row.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignLeft)
        top_row.addStretch(1)
        self.save_button = QPushButton("Save Recipe")
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self._handle_save)
        top_row.addWidget(self.save_button, alignment=Qt.AlignmentFlag.AlignRight)
        self.root_layout.addLayout(top_row)

        self.hero_card = BaseCard()
        self.hero_card.setObjectName("heroCard")
        self.root_layout.addWidget(self.hero_card)

        eyebrow = QLabel("Create recipe")
        eyebrow.setObjectName("eyebrowLabel")
        self.hero_card.content_layout.addWidget(eyebrow)

        title = QLabel("Compose a polished new recipe entry.")
        title.setObjectName("detailsTitle")
        title.setWordWrap(True)
        self.hero_card.content_layout.addWidget(title)

        subtitle = QLabel(
            "Enter the core recipe data once, save both languages where available, and land directly in the finished details view."
        )
        subtitle.setObjectName("heroSubtitle")
        subtitle.setWordWrap(True)
        self.hero_card.content_layout.addWidget(subtitle)

        self.error_banner = QLabel()
        self.error_banner.setObjectName("formErrorBanner")
        self.error_banner.hide()
        self.hero_card.content_layout.addWidget(self.error_banner)

        self._build_basic_info_section()
        self._build_metadata_section()
        self._build_tags_section()
        self._build_ingredients_section()
        self._build_steps_section()

    def _build_basic_info_section(self) -> None:
        card = BaseCard()
        card.content_layout.addWidget(
            SectionHeader("Basic Info", "English is required. Arabic can be added now and expanded later.")
        )
        form = QFormLayout()
        form.setSpacing(12)

        self.title_en_input = QLineEdit()
        self.title_en_input.setObjectName("searchInput")
        form.addRow("Title (EN)", self.title_en_input)

        self.title_ar_input = QLineEdit()
        self.title_ar_input.setObjectName("searchInput")
        form.addRow("Title (AR)", self.title_ar_input)

        self.description_en_input = QTextEdit()
        self.description_en_input.setObjectName("multilineField")
        self.description_en_input.setFixedHeight(86)
        form.addRow("Description (EN)", self.description_en_input)

        self.description_ar_input = QTextEdit()
        self.description_ar_input.setObjectName("multilineField")
        self.description_ar_input.setFixedHeight(86)
        form.addRow("Description (AR)", self.description_ar_input)

        card.content_layout.addLayout(form)
        self.image_input_card = RecipeImageInputCard(self.image_service)
        card.content_layout.addWidget(self.image_input_card)
        self.root_layout.addWidget(card)

    def _build_metadata_section(self) -> None:
        card = BaseCard()
        card.content_layout.addWidget(
            SectionHeader("Metadata", "Core recipe timing, servings, category, and type settings.")
        )
        form = QFormLayout()
        form.setSpacing(12)

        self.category_combo = QComboBox()
        form.addRow("Category", self.category_combo)

        self.prep_time_input = QSpinBox()
        self.prep_time_input.setMaximum(9999)
        form.addRow("Prep Time (min)", self.prep_time_input)

        self.cook_time_input = QSpinBox()
        self.cook_time_input.setMaximum(9999)
        form.addRow("Cook Time (min)", self.cook_time_input)

        self.base_servings_input = QDoubleSpinBox()
        self.base_servings_input.setDecimals(2)
        self.base_servings_input.setMinimum(0.25)
        self.base_servings_input.setMaximum(999)
        self.base_servings_input.setValue(4)
        form.addRow("Base Servings", self.base_servings_input)

        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["easy", "medium", "hard"])
        form.addRow("Difficulty", self.difficulty_combo)

        self.source_type_combo = QComboBox()
        self.source_type_combo.addItems(["original", "imported", "adapted"])
        form.addRow("Source Type", self.source_type_combo)

        card.content_layout.addLayout(form)
        self.root_layout.addWidget(card)

    def _build_tags_section(self) -> None:
        self.tags_card = BaseCard()
        self.tags_card.content_layout.addWidget(
            SectionHeader("Tags", "Select the labels that best frame the new recipe.")
        )
        self.tags_row = QHBoxLayout()
        self.tags_row.setSpacing(8)
        self.tags_card.content_layout.addLayout(self.tags_row)
        self.root_layout.addWidget(self.tags_card)

    def _build_ingredients_section(self) -> None:
        self.ingredients_card = BaseCard()
        self.ingredients_card.content_layout.addWidget(
            SectionHeader("Ingredients", "Type ingredient names directly. Existing ingredients are reused automatically when names match.")
        )
        self.ingredients_container = QVBoxLayout()
        self.ingredients_container.setSpacing(14)
        self.ingredients_card.content_layout.addLayout(self.ingredients_container)

        add_button = QPushButton("Add Ingredient")
        add_button.setObjectName("secondaryButton")
        add_button.clicked.connect(self._add_ingredient_row)
        self.ingredients_card.content_layout.addWidget(add_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self.root_layout.addWidget(self.ingredients_card)

    def _build_steps_section(self) -> None:
        self.steps_card = BaseCard()
        self.steps_card.content_layout.addWidget(
            SectionHeader("Steps", "Write the method in order. English is required, Arabic remains optional.")
        )
        self.steps_container = QVBoxLayout()
        self.steps_container.setSpacing(14)
        self.steps_card.content_layout.addLayout(self.steps_container)

        add_button = QPushButton("Add Step")
        add_button.setObjectName("secondaryButton")
        add_button.clicked.connect(self._add_step_row)
        self.steps_card.content_layout.addWidget(add_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self.root_layout.addWidget(self.steps_card)

    def load_form_options(self) -> None:
        context = self.context_service.get_context()
        self.image_input_card.set_language(context.language_code)
        categories = self.category_service.list_categories(context.language_code)
        tags = self.tag_service.list_tags(context.language_code)
        units = self.unit_service.list_units(context.language_code)

        self.category_combo.clear()
        for category in categories:
            self.category_combo.addItem(category.display_name, category.id)

        self._populate_tag_chips(tags)
        self._reset_static_fields()
        self._reset_rows([(unit.id, unit.display_name) for unit in units])

    def _reset_static_fields(self) -> None:
        self.title_en_input.clear()
        self.title_ar_input.clear()
        self.description_en_input.clear()
        self.description_ar_input.clear()
        self.image_input_card.clear_selection()
        self.prep_time_input.setValue(0)
        self.cook_time_input.setValue(0)
        self.base_servings_input.setValue(4)
        self.difficulty_combo.setCurrentText("easy")
        self.source_type_combo.setCurrentText("original")
        self.error_banner.hide()
        for chip, _tag in self.tag_chips:
            chip.setChecked(False)

    def _populate_tag_chips(self, tags: list[LocalizedTag]) -> None:
        self.tag_chips.clear()
        while self.tags_row.count():
            item = self.tags_row.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for tag in tags:
            chip = CategoryChip(tag.slug, tag.display_name)
            self.tag_chips.append((chip, tag))
            self.tags_row.addWidget(chip)
        self.tags_row.addStretch(1)

    def _reset_rows(self, units: list[tuple[int, str]]) -> None:
        for row in self.ingredient_rows:
            row.deleteLater()
        self.ingredient_rows.clear()
        for row in self.step_rows:
            row.deleteLater()
        self.step_rows.clear()

        self.available_units = units
        self._add_ingredient_row()
        self._add_step_row()

    def _add_ingredient_row(self) -> None:
        row = IngredientFormRow(self.available_units)
        row.remove_requested.connect(self._remove_ingredient_row)
        self.ingredient_rows.append(row)
        self.ingredients_container.addWidget(row)

    def _remove_ingredient_row(self, row: QWidget) -> None:
        if len(self.ingredient_rows) == 1:
            return
        self.ingredient_rows.remove(row)  # type: ignore[arg-type]
        row.deleteLater()

    def _add_step_row(self) -> None:
        row = StepFormRow(len(self.step_rows) + 1)
        row.remove_requested.connect(self._remove_step_row)
        self.step_rows.append(row)
        self.steps_container.addWidget(row)

    def _remove_step_row(self, row: QWidget) -> None:
        if len(self.step_rows) == 1:
            return
        self.step_rows.remove(row)  # type: ignore[arg-type]
        row.deleteLater()
        for index, step_row in enumerate(self.step_rows, start=1):
            step_row.set_step_number(index)

    def _handle_save(self) -> None:
        context = self.context_service.get_context()
        if context.profile_id is None:
            self._show_error("A valid local profile is required before recipes can be created.")
            return

        try:
            recipe_input = self._build_create_input()
            recipe_id = self.recipe_service.create_recipe(recipe_input, created_by_profile_id=context.profile_id)
        except Exception as exc:
            self._show_error(str(exc))
            return

        self.error_banner.hide()
        self.recipe_created.emit(recipe_id)

    def _build_create_input(self) -> CreateRecipeInput:
        return CreateRecipeInput(
            title_en=self.title_en_input.text(),
            title_ar=self.title_ar_input.text() or None,
            short_description_en=self.description_en_input.toPlainText() or None,
            short_description_ar=self.description_ar_input.toPlainText() or None,
            category_id=self.category_combo.currentData(),
            image_path=None,
            prep_time_minutes=self.prep_time_input.value(),
            cook_time_minutes=self.cook_time_input.value(),
            base_servings=Decimal(str(self.base_servings_input.value())),
            difficulty_level=self.difficulty_combo.currentText(),
            source_type=self.source_type_combo.currentText(),
            tag_ids=[tag.id for chip, tag in self.tag_chips if chip.isChecked()],
            ingredients=[row.to_input() for row in self.ingredient_rows],
            steps=[row.to_input() for row in self.step_rows],
            image_input=self.image_input_card.recipe_image_input(),
        )

    def _show_error(self, message: str) -> None:
        self.error_banner.setText(message)
        self.error_banner.show()

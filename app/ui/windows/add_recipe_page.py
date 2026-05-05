from __future__ import annotations

from decimal import Decimal

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QPlainTextEdit,
    QScrollArea,
    QSpinBox,
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
from app.ui.components.ingredient_form_row import IngredientFormRow
from app.ui.components.recipe_image_input import RecipeImageInputCard
from app.ui.components.section_header import SectionHeader
from app.ui.components.step_form_row import StepFormRow
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
        self.available_units: list[tuple[int, str]] = []
        self._current_language_code = "en"

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

        self.back_button = QPushButton()
        self.back_button.setObjectName("secondaryButton")
        self.back_button.clicked.connect(self.back_requested.emit)
        top_row.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignLeft)

        top_row.addStretch(1)

        self.import_button = QPushButton("Import Recipe")
        self.import_button.setObjectName("secondaryButton")
        self.import_button.clicked.connect(self._open_import_dialog)
        top_row.addWidget(self.import_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.save_button = QPushButton()
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self._handle_save)
        top_row.addWidget(self.save_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.root_layout.addLayout(top_row)

        self.hero_card = BaseCard()
        self.hero_card.setObjectName("heroCard")
        self.root_layout.addWidget(self.hero_card)

        self.eyebrow = QLabel()
        self.eyebrow.setObjectName("eyebrowLabel")
        self.hero_card.content_layout.addWidget(self.eyebrow)

        self.title_label = QLabel()
        self.title_label.setObjectName("detailsTitle")
        self.title_label.setWordWrap(True)
        self.hero_card.content_layout.addWidget(self.title_label)

        self.subtitle_label = QLabel()
        self.subtitle_label.setObjectName("heroSubtitle")
        self.subtitle_label.setWordWrap(True)
        self.hero_card.content_layout.addWidget(self.subtitle_label)

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
        self.basic_info_header = SectionHeader("", "")
        card.content_layout.addWidget(self.basic_info_header)

        form = QFormLayout()
        form.setSpacing(12)

        self.title_en_input = QLineEdit()
        self.title_en_input.setObjectName("searchInput")
        self.title_en_label = QLabel()
        form.addRow(self.title_en_label, self.title_en_input)

        self.title_ar_input = QLineEdit()
        self.title_ar_input.setObjectName("searchInput")
        self.title_ar_label = QLabel()
        form.addRow(self.title_ar_label, self.title_ar_input)

        self.title_ru_input = QLineEdit()
        self.title_ru_input.setObjectName("searchInput")
        self.title_ru_label = QLabel()
        form.addRow(self.title_ru_label, self.title_ru_input)

        self.description_en_input = QTextEdit()
        self.description_en_input.setObjectName("multilineField")
        self.description_en_input.setFixedHeight(86)
        self.description_en_label = QLabel()
        form.addRow(self.description_en_label, self.description_en_input)

        self.description_ar_input = QTextEdit()
        self.description_ar_input.setObjectName("multilineField")
        self.description_ar_input.setFixedHeight(86)
        self.description_ar_label = QLabel()
        form.addRow(self.description_ar_label, self.description_ar_input)

        self.description_ru_input = QTextEdit()
        self.description_ru_input.setObjectName("multilineField")
        self.description_ru_input.setFixedHeight(86)
        self.description_ru_label = QLabel()
        form.addRow(self.description_ru_label, self.description_ru_input)

        card.content_layout.addLayout(form)

        self.image_input_card = RecipeImageInputCard(self.image_service)
        card.content_layout.addWidget(self.image_input_card)

        self.root_layout.addWidget(card)

    def _build_metadata_section(self) -> None:
        card = BaseCard()
        self.metadata_header = SectionHeader("", "")
        card.content_layout.addWidget(self.metadata_header)

        form = QFormLayout()
        form.setSpacing(12)

        self.category_combo = QComboBox()
        self.category_label = QLabel()
        form.addRow(self.category_label, self.category_combo)

        self.prep_time_input = QSpinBox()
        self.prep_time_input.setMaximum(9999)
        self.prep_time_label = QLabel()
        form.addRow(self.prep_time_label, self.prep_time_input)

        self.cook_time_input = QSpinBox()
        self.cook_time_input.setMaximum(9999)
        self.cook_time_label = QLabel()
        form.addRow(self.cook_time_label, self.cook_time_input)

        self.base_servings_input = QDoubleSpinBox()
        self.base_servings_input.setDecimals(2)
        self.base_servings_input.setMinimum(0.25)
        self.base_servings_input.setMaximum(999)
        self.base_servings_input.setValue(4)
        self.base_servings_label = QLabel()
        form.addRow(self.base_servings_label, self.base_servings_input)

        self.difficulty_combo = QComboBox()
        self.difficulty_label = QLabel()
        form.addRow(self.difficulty_label, self.difficulty_combo)

        self.source_type_combo = QComboBox()
        self.source_type_label = QLabel()
        form.addRow(self.source_type_label, self.source_type_combo)

        card.content_layout.addLayout(form)
        self.root_layout.addWidget(card)

    def _build_tags_section(self) -> None:
        self.tags_card = BaseCard()
        self.tags_header = SectionHeader("", "")
        self.tags_card.content_layout.addWidget(self.tags_header)

        self.tags_row = QHBoxLayout()
        self.tags_row.setSpacing(8)
        self.tags_card.content_layout.addLayout(self.tags_row)

        self.root_layout.addWidget(self.tags_card)

    def _build_ingredients_section(self) -> None:
        self.ingredients_card = BaseCard()
        self.ingredients_header = SectionHeader("", "")
        self.ingredients_card.content_layout.addWidget(self.ingredients_header)

        self.ingredients_container = QVBoxLayout()
        self.ingredients_container.setSpacing(14)
        self.ingredients_card.content_layout.addLayout(self.ingredients_container)

        self.add_ingredient_button = QPushButton()
        self.add_ingredient_button.setObjectName("secondaryButton")
        self.add_ingredient_button.clicked.connect(self._add_ingredient_row)
        self.ingredients_card.content_layout.addWidget(
            self.add_ingredient_button,
            alignment=Qt.AlignmentFlag.AlignLeft,
        )

        self.root_layout.addWidget(self.ingredients_card)

    def _build_steps_section(self) -> None:
        self.steps_card = BaseCard()
        self.steps_header = SectionHeader("", "")
        self.steps_card.content_layout.addWidget(self.steps_header)

        self.steps_container = QVBoxLayout()
        self.steps_container.setSpacing(14)
        self.steps_card.content_layout.addLayout(self.steps_container)

        self.add_step_button = QPushButton()
        self.add_step_button.setObjectName("secondaryButton")
        self.add_step_button.clicked.connect(self._add_step_row)
        self.steps_card.content_layout.addWidget(
            self.add_step_button,
            alignment=Qt.AlignmentFlag.AlignLeft,
        )

        self.root_layout.addWidget(self.steps_card)

    def load_form_options(self) -> None:
        context = self.context_service.get_context()
        self._current_language_code = context.language_code

        self._apply_translations(context.language_code)
        self.image_input_card.set_language(context.language_code)

        categories = self.category_service.list_categories(context.language_code)
        tags = self.tag_service.list_tags(context.language_code)
        units = self.unit_service.list_units(context.language_code)

        self.category_combo.clear()
        for category in categories:
            self.category_combo.addItem(category.display_name, category.id)

        self._populate_difficulty_options()
        self._populate_source_options()
        self._populate_tag_chips(tags)
        self._reset_static_fields()
        self._reset_rows([(unit.id, unit.display_name) for unit in units])

    def _safe_translate(self, language_code: str, key: str, fallback: str) -> str:
        value = translate(language_code, key)
        return fallback if value == key else value

    def _apply_translations(self, language_code: str) -> None:
        self.back_button.setText(translate(language_code, "add_recipe.back"))
        self.save_button.setText(translate(language_code, "add_recipe.save"))
        self.import_button.setText("Import Recipe")

        self.eyebrow.setText(translate(language_code, "add_recipe.eyebrow"))
        self.title_label.setText(translate(language_code, "add_recipe.title"))
        self.subtitle_label.setText(translate(language_code, "add_recipe.subtitle"))

        self.basic_info_header.set_content(
            translate(language_code, "add_recipe.basic_info_title"),
            translate(language_code, "add_recipe.basic_info_subtitle"),
        )

        self.title_en_label.setText(translate(language_code, "add_recipe.field.title_en"))
        self.title_ar_label.setText(translate(language_code, "add_recipe.field.title_ar"))
        self.title_ru_label.setText(
            self._safe_translate(language_code, "add_recipe.field.title_ru", "Title (RU)")
        )

        self.description_en_label.setText(translate(language_code, "add_recipe.field.description_en"))
        self.description_ar_label.setText(translate(language_code, "add_recipe.field.description_ar"))
        self.description_ru_label.setText(
            self._safe_translate(language_code, "add_recipe.field.description_ru", "Description (RU)")
        )

        self.metadata_header.set_content(
            translate(language_code, "add_recipe.metadata_title"),
            translate(language_code, "add_recipe.metadata_subtitle"),
        )

        self.category_label.setText(translate(language_code, "add_recipe.field.category"))
        self.prep_time_label.setText(translate(language_code, "add_recipe.field.prep_time"))
        self.cook_time_label.setText(translate(language_code, "add_recipe.field.cook_time"))
        self.base_servings_label.setText(translate(language_code, "add_recipe.field.base_servings"))
        self.difficulty_label.setText(translate(language_code, "add_recipe.field.difficulty"))
        self.source_type_label.setText(translate(language_code, "add_recipe.field.source_type"))

        self.tags_header.set_content(
            translate(language_code, "add_recipe.tags_title"),
            translate(language_code, "add_recipe.tags_subtitle"),
        )

        self.ingredients_header.set_content(
            translate(language_code, "add_recipe.ingredients_title"),
            translate(language_code, "add_recipe.ingredients_subtitle"),
        )
        self.add_ingredient_button.setText(translate(language_code, "add_recipe.add_ingredient"))

        self.steps_header.set_content(
            translate(language_code, "add_recipe.steps_title"),
            translate(language_code, "add_recipe.steps_subtitle"),
        )
        self.add_step_button.setText(translate(language_code, "add_recipe.add_step"))

    def _populate_difficulty_options(self) -> None:
        current = self.difficulty_combo.currentData()
        self.difficulty_combo.clear()

        for value in ("easy", "medium", "hard"):
            self.difficulty_combo.addItem(
                translate(self._current_language_code, f"add_recipe.difficulty.{value}"),
                value,
            )

        index = self.difficulty_combo.findData(current or "easy")
        self.difficulty_combo.setCurrentIndex(max(index, 0))

    def _populate_source_options(self) -> None:
        current = self.source_type_combo.currentData()
        self.source_type_combo.clear()

        for value in ("original", "imported", "adapted"):
            self.source_type_combo.addItem(
                translate(self._current_language_code, f"add_recipe.source.{value}"),
                value,
            )

        index = self.source_type_combo.findData(current or "original")
        self.source_type_combo.setCurrentIndex(max(index, 0))

    def _reset_static_fields(self) -> None:
        self.title_en_input.clear()
        self.title_ar_input.clear()
        self.title_ru_input.clear()

        self.description_en_input.clear()
        self.description_ar_input.clear()
        self.description_ru_input.clear()

        self.image_input_card.clear_selection()

        self.prep_time_input.setValue(0)
        self.cook_time_input.setValue(0)
        self.base_servings_input.setValue(4)

        difficulty_index = self.difficulty_combo.findData("easy")
        self.difficulty_combo.setCurrentIndex(max(difficulty_index, 0))

        source_index = self.source_type_combo.findData("original")
        self.source_type_combo.setCurrentIndex(max(source_index, 0))

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
        row.set_language(self._current_language_code)
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
        row.set_language(self._current_language_code)
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
            step_row.set_language(self._current_language_code)

    def _handle_save(self) -> None:
        context = self.context_service.get_context()

        if context.profile_id is None:
            self._show_error(translate(self._current_language_code, "add_recipe.error.profile_required"))
            return

        try:
            recipe_input = self._build_create_input()
            recipe_id = self.recipe_service.create_recipe(
                recipe_input,
                created_by_profile_id=context.profile_id,
            )
        except Exception as exc:
            self._show_error(str(exc))
            return

        self.error_banner.hide()
        self.recipe_created.emit(recipe_id)

    def _build_create_input(self) -> CreateRecipeInput:
        return CreateRecipeInput(
            title_en=self.title_en_input.text(),
            title_ar=self.title_ar_input.text() or None,
            title_ru=self.title_ru_input.text() or None,
            short_description_en=self.description_en_input.toPlainText() or None,
            short_description_ar=self.description_ar_input.toPlainText() or None,
            short_description_ru=self.description_ru_input.toPlainText() or None,
            category_id=self.category_combo.currentData(),
            image_path=None,
            prep_time_minutes=self.prep_time_input.value(),
            cook_time_minutes=self.cook_time_input.value(),
            base_servings=Decimal(str(self.base_servings_input.value())),
            difficulty_level=str(self.difficulty_combo.currentData()),
            source_type=str(self.source_type_combo.currentData()),
            tag_ids=[tag.id for chip, tag in self.tag_chips if chip.isChecked()],
            ingredients=[row.to_input() for row in self.ingredient_rows],
            steps=[row.to_input() for row in self.step_rows],
            image_input=self.image_input_card.recipe_image_input(),
        )

    def _open_import_dialog(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Import Recipe")
        dialog.resize(850, 700)

        layout = QVBoxLayout(dialog)

        hint = QLabel(
            "Paste the full recipe here, then click OK.\n\n"
            "New format:\n"
            "Title (EN): ...\n"
            "Title (AR): ...\n"
            "Title (RU): ...\n"
            "Description (EN): ...\n"
            "Description (AR): ...\n"
            "Description (RU): ...\n"
            "Category: ...\n"
            "Prep Time: ...\n"
            "Cook Time: ...\n"
            "Base Servings: ...\n"
            "Difficulty: easy / medium / hard\n"
            "Source Type: original\n\n"
            "Ingredients:\n"
            "Name EN | Name AR | Name RU | Amount | Unit\n\n"
            "Steps:\n"
            "1. English step | Arabic step | Russian step"
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)

        text_input = QPlainTextEdit()
        text_input.setPlaceholderText(
            "Title (EN): Chicken Biryani\n"
            "Title (AR): برياني دجاج\n"
            "Title (RU): Бириани с курицей\n\n"
            "Description (EN): A flavorful rice dish with chicken.\n"
            "Description (AR): طبق رز غني بالنكهة مع الدجاج.\n"
            "Description (RU): Ароматное блюдо из риса с курицей.\n\n"
            "Category: Rice Dishes\n"
            "Prep Time: 15\n"
            "Cook Time: 55\n"
            "Base Servings: 1\n"
            "Difficulty: medium\n"
            "Source Type: original\n\n"
            "Ingredients:\n"
            "Rice | رز | Рис | 80 | g\n"
            "Chicken | دجاج | Курица | 150 | g\n\n"
            "Steps:\n"
            "1. Boil the rice until half cooked. | اسلقي الرز حتى نصف الاستواء | Отварите рис до полуготовности."
        )
        layout.addWidget(text_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        layout.addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._import_recipe_text(text_input.toPlainText())

    def _import_recipe_text(self, text: str) -> None:
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        section: str | None = None
        ingredient_lines: list[str] = []
        step_lines: list[str] = []

        for line in lines:
            lower = line.lower()

            if lower.startswith("ingredients"):
                section = "ingredients"
                continue

            if lower.startswith("steps"):
                section = "steps"
                continue

            if section == "ingredients":
                ingredient_lines.append(line)
                continue

            if section == "steps":
                step_lines.append(line)
                continue

            if line.startswith("Title (EN):"):
                self.title_en_input.setText(line.split(":", 1)[1].strip())

            elif line.startswith("Title (AR):"):
                self.title_ar_input.setText(line.split(":", 1)[1].strip())

            elif line.startswith("Title (RU):"):
                self.title_ru_input.setText(line.split(":", 1)[1].strip())

            elif line.startswith("Description (EN):"):
                self.description_en_input.setPlainText(line.split(":", 1)[1].strip())

            elif line.startswith("Description (AR):"):
                self.description_ar_input.setPlainText(line.split(":", 1)[1].strip())

            elif line.startswith("Description (RU):"):
                self.description_ru_input.setPlainText(line.split(":", 1)[1].strip())

            elif line.startswith("Category:"):
                self._select_combo_by_text_or_data(
                    self.category_combo,
                    line.split(":", 1)[1].strip(),
                )

            elif line.startswith("Prep Time:"):
                self.prep_time_input.setValue(self._extract_int(line))

            elif line.startswith("Cook Time:"):
                self.cook_time_input.setValue(self._extract_int(line))

            elif line.startswith("Base Servings:"):
                self.base_servings_input.setValue(self._extract_float(line))

            elif line.startswith("Difficulty:"):
                self._select_combo_by_text_or_data(
                    self.difficulty_combo,
                    line.split(":", 1)[1].strip().lower(),
                )

            elif line.startswith("Source Type:"):
                self._select_combo_by_text_or_data(
                    self.source_type_combo,
                    line.split(":", 1)[1].strip().lower(),
                )

        self._import_ingredients(ingredient_lines)
        self._import_steps(step_lines)

    def _extract_int(self, line: str) -> int:
        value = line.split(":", 1)[1].strip()
        digits = "".join(ch for ch in value if ch.isdigit())
        return int(digits) if digits else 0

    def _extract_float(self, line: str) -> float:
        value = line.split(":", 1)[1].strip().replace(",", ".")
        try:
            return float(value)
        except ValueError:
            return 1.0

    def _select_combo_by_text_or_data(self, combo: QComboBox, value: str) -> None:
        value_lower = value.lower().strip()

        for index in range(combo.count()):
            text = combo.itemText(index).lower().strip()
            data = str(combo.itemData(index)).lower().strip()

            if value_lower == text or value_lower == data:
                combo.setCurrentIndex(index)
                return

    def _import_ingredients(self, ingredient_lines: list[str]) -> None:
        if not ingredient_lines:
            return

        while len(self.ingredient_rows) > 1:
            self._remove_ingredient_row(self.ingredient_rows[-1])

        first = True

        for line in ingredient_lines:
            parts = [part.strip() for part in line.split("|")]

            if len(parts) >= 5:
                name_en = parts[0]
                name_ar = parts[1]
                name_ru = parts[2]
                amount = parts[3]
                unit = parts[4]
            elif len(parts) >= 4:
                name_en = parts[0]
                name_ar = parts[1]
                name_ru = ""
                amount = parts[2]
                unit = parts[3]
            else:
                continue

            if first:
                row = self.ingredient_rows[0]
                first = False
            else:
                self._add_ingredient_row()
                row = self.ingredient_rows[-1]

            self._try_set_widget_value(
                row,
                ["name_en_input", "ingredient_en_input", "english_name_input", "name_input_en"],
                name_en,
            )

            self._try_set_widget_value(
                row,
                ["name_ar_input", "ingredient_ar_input", "arabic_name_input", "name_input_ar"],
                name_ar,
            )

            self._try_set_widget_value(
                row,
                ["name_ru_input", "ingredient_ru_input", "russian_name_input", "name_input_ru"],
                name_ru,
            )

            self._try_set_widget_value(
                row,
                ["quantity_input", "amount_input", "quantity_spin"],
                amount,
            )

            self._try_set_combo_value(
                row,
                ["unit_combo", "unit_input"],
                unit,
            )

    def _import_steps(self, step_lines: list[str]) -> None:
        if not step_lines:
            return

        while len(self.step_rows) > 1:
            self._remove_step_row(self.step_rows[-1])

        first = True

        for line in step_lines:
            cleaned = line.strip()

            if "." in cleaned:
                number_part, text_part = cleaned.split(".", 1)
                if number_part.strip().isdigit():
                    cleaned = text_part.strip()

            parts = [part.strip() for part in cleaned.split("|")]

            instruction_en = parts[0] if len(parts) >= 1 else ""
            instruction_ar = parts[1] if len(parts) >= 2 else ""
            instruction_ru = parts[2] if len(parts) >= 3 else ""

            if first:
                row = self.step_rows[0]
                first = False
            else:
                self._add_step_row()
                row = self.step_rows[-1]

            self._try_set_widget_value(
                row,
                ["instruction_en_input", "step_en_input", "text_en_input"],
                instruction_en,
            )

            self._try_set_widget_value(
                row,
                ["instruction_ar_input", "step_ar_input", "text_ar_input"],
                instruction_ar,
            )

            self._try_set_widget_value(
                row,
                ["instruction_ru_input", "step_ru_input", "text_ru_input"],
                instruction_ru,
            )

    def _try_set_widget_value(
        self,
        row: QWidget,
        possible_names: list[str],
        value: str,
    ) -> None:
        for name in possible_names:
            widget = getattr(row, name, None)

            if widget is None:
                continue

            if hasattr(widget, "setPlainText"):
                widget.setPlainText(value)
                return

            if hasattr(widget, "setText"):
                widget.setText(value)
                return

            if hasattr(widget, "setValue"):
                number = self._safe_float(value)
                if number is not None:
                    widget.setValue(number)
                return

    def _try_set_combo_value(
        self,
        row: QWidget,
        possible_names: list[str],
        value: str,
    ) -> None:
        for name in possible_names:
            combo = getattr(row, name, None)

            if combo is None or not hasattr(combo, "count"):
                continue

            value_lower = value.lower().strip()

            for index in range(combo.count()):
                text = combo.itemText(index).lower().strip()
                data = str(combo.itemData(index)).lower().strip()

                if value_lower == text or value_lower == data:
                    combo.setCurrentIndex(index)
                    return

    def _safe_float(self, value: str) -> float | None:
        value = value.strip().replace(",", ".")

        if value.lower() in {
            "to taste",
            "as needed",
            "for frying",
            "for serving",
            "",
        }:
            return None

        try:
            return float(value)
        except ValueError:
            return None

    def _show_error(self, message: str) -> None:
        self.error_banner.setText(message)
        self.error_banner.show()
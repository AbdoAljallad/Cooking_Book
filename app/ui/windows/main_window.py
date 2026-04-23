from __future__ import annotations

from threading import Thread

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.config.settings import AppSettings
from app.database.health import DatabaseHealthResult, check_database_connection
from app.services import (
    AppContext,
    AppContextService,
    CategoryService,
    HomeService,
    ImageService,
    RecipeService,
    SettingsService,
    TagService,
    UnitService,
)
from app.ui.themes.manager import ThemeManager
from app.ui.windows.add_recipe_page import AddRecipePage
from app.ui.windows.favorites_page import FavoritesPage
from app.ui.windows.home_page import HomePage
from app.ui.windows.recipe_details_page import RecipeDetailsPage
from app.ui.windows.settings_page import SettingsPage
from app.utils.i18n import translate


class DatabaseHealthSignals(QObject):
    finished = Signal(object)


class MainWindow(QMainWindow):
    def __init__(self, settings: AppSettings, theme_manager: ThemeManager) -> None:
        super().__init__()
        self.settings = settings
        self.theme_manager = theme_manager
        self.database_health_signals = DatabaseHealthSignals()
        self.context_service = AppContextService(settings=settings)
        self.current_context = self.context_service.get_context()
        self.image_service = ImageService()
        self.category_service = CategoryService()
        self.tag_service = TagService()
        self.unit_service = UnitService()
        self.recipe_service = RecipeService(image_service=self.image_service)
        self.settings_service = SettingsService(settings=settings, theme_manager=theme_manager)
        self.home_service = HomeService(
            context_service=self.context_service,
            category_service=self.category_service,
            tag_service=self.tag_service,
            recipe_service=self.recipe_service,
        )

        self.setWindowTitle("Premium Cookbook")
        self.resize(1320, 860)
        self.setMinimumSize(1100, 700)

        self._apply_context(self.current_context)
        self._build_ui()
        self._start_database_health_check()
        self._return_page = None

    def _apply_layout_direction(self, direction: str) -> None:
        qt_direction = Qt.RightToLeft if direction == "rtl" else Qt.LeftToRight
        self.setLayoutDirection(qt_direction)

    def _apply_context(self, context: AppContext) -> None:
        self.current_context = context
        self._apply_layout_direction(context.layout_direction)
        application = QApplication.instance()
        if application is not None:
            self.theme_manager.apply_theme(application, context.theme_name)

    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("mainWindowRoot")

        layout = QVBoxLayout(root)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        top_bar = QHBoxLayout()
        top_bar.setSpacing(16)

        brand_block = QVBoxLayout()
        brand_block.setSpacing(2)
        self.product_name = QLabel("Premium Cookbook")
        self.product_name.setObjectName("windowTitleLabel")
        brand_block.addWidget(self.product_name)

        self.product_caption = QLabel("Theme-aware multilingual desktop cooking workspace")
        self.product_caption.setObjectName("windowSubtitleLabel")
        brand_block.addWidget(self.product_caption)
        top_bar.addLayout(brand_block, stretch=1)

        self.connection_badge = QLabel("Checking database")
        self.connection_badge.setObjectName("statusBadge")
        self._set_status_badge("checking")
        top_bar.addWidget(self.connection_badge, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.add_recipe_button = QPushButton("Add Recipe")
        self.add_recipe_button.setObjectName("primaryButton")
        self.add_recipe_button.clicked.connect(self._show_add_recipe_page)
        top_bar.addWidget(self.add_recipe_button, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.favorites_button = QPushButton("Favorites")
        self.favorites_button.setObjectName("secondaryButton")
        self.favorites_button.clicked.connect(self._show_favorites_page)
        top_bar.addWidget(self.favorites_button, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.theme_selector = QComboBox()
        self.theme_selector.addItems(self.theme_manager.available_themes())
        self.theme_selector.setCurrentText(self.current_context.theme_name)
        self.theme_selector.currentTextChanged.connect(self._on_theme_changed)
        self.theme_selector.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        top_bar.addWidget(self.theme_selector, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.settings_button = QPushButton("Settings")
        self.settings_button.setObjectName("secondaryButton")
        self.settings_button.clicked.connect(self._show_settings_page)
        top_bar.addWidget(self.settings_button, alignment=Qt.AlignmentFlag.AlignVCenter)

        layout.addLayout(top_bar)

        self.home_page = HomePage(self.home_service, self.image_service)
        self.home_page.recipe_selected.connect(self._open_recipe_details)

        self.favorites_page = FavoritesPage(
            recipe_service=self.recipe_service,
            context_service=self.context_service,
            image_service=self.image_service,
        )
        self.favorites_page.recipe_selected.connect(self._open_recipe_details_from_favorites)

        self.add_recipe_page = AddRecipePage(
            context_service=self.context_service,
            category_service=self.category_service,
            tag_service=self.tag_service,
            unit_service=self.unit_service,
            recipe_service=self.recipe_service,
            image_service=self.image_service,
        )
        self.add_recipe_page.back_requested.connect(self._show_home_page)
        self.add_recipe_page.recipe_created.connect(self._handle_recipe_created)

        self.settings_page = SettingsPage(
            context_service=self.context_service,
            settings_service=self.settings_service,
        )
        self.settings_page.back_requested.connect(self._show_home_page)
        self.settings_page.settings_applied.connect(self._handle_settings_applied)

        self.recipe_details_page = RecipeDetailsPage(
            recipe_service=self.recipe_service,
            context_service=self.context_service,
            image_service=self.image_service,
        )
        self.recipe_details_page.back_requested.connect(self._return_from_details)

        self.page_stack = QStackedWidget()
        self.page_stack.addWidget(self.home_page)
        self.page_stack.addWidget(self.favorites_page)
        self.page_stack.addWidget(self.add_recipe_page)
        self.page_stack.addWidget(self.settings_page)
        self.page_stack.addWidget(self.recipe_details_page)
        layout.addWidget(self.page_stack, stretch=1)

        self.setCentralWidget(root)
        self._refresh_texts()

    def _set_status_badge(self, status: str) -> None:
        self.connection_badge.setProperty("status", status)
        self.connection_badge.style().unpolish(self.connection_badge)
        self.connection_badge.style().polish(self.connection_badge)

    def _start_database_health_check(self) -> None:
        self.database_health_signals.finished.connect(self._update_database_status)
        Thread(target=self._run_database_health_check, daemon=True).start()

    def _run_database_health_check(self) -> None:
        result = check_database_connection()
        self.database_health_signals.finished.emit(result)

    def _update_database_status(self, result: DatabaseHealthResult) -> None:
        if result.ok:
            self.connection_badge.setText(translate(self.current_context.language_code, "status.database_connected"))
            self._set_status_badge("success")
            self.connection_badge.setToolTip("")
            return

        self.connection_badge.setText(translate(self.current_context.language_code, "status.database_unavailable"))
        self._set_status_badge("error")
        self.connection_badge.setToolTip(result.error or result.message)

    def _on_theme_changed(self, theme_name: str) -> None:
        application = QApplication.instance()
        if application is not None:
            self.theme_manager.apply_theme(application, theme_name)
        if theme_name == self.current_context.theme_name:
            return
        try:
            updated = self.settings_service.save_settings(
                language_code=self.current_context.language_code,
                theme_name=theme_name,
            )
        except Exception:
            self.current_context = AppContext(
                profile_id=self.current_context.profile_id,
                profile_name=self.current_context.profile_name,
                language_code=self.current_context.language_code,
                theme_name=theme_name,
                layout_direction=self.current_context.layout_direction,
            )
            return
        self._apply_context(updated)

    def _open_recipe_details(self, recipe_id: int) -> None:
        self._return_page = self.home_page
        self.recipe_details_page.load_recipe(recipe_id)
        self.page_stack.setCurrentWidget(self.recipe_details_page)

    def _open_recipe_details_from_favorites(self, recipe_id: int) -> None:
        self._return_page = self.favorites_page
        self.recipe_details_page.load_recipe(recipe_id)
        self.page_stack.setCurrentWidget(self.recipe_details_page)

    def _show_home_page(self) -> None:
        self.home_page.reload()
        self.page_stack.setCurrentWidget(self.home_page)

    def _show_favorites_page(self) -> None:
        self.favorites_page.reload()
        self.page_stack.setCurrentWidget(self.favorites_page)

    def _show_settings_page(self) -> None:
        self.settings_page.reload()
        self.page_stack.setCurrentWidget(self.settings_page)

    def _return_from_details(self) -> None:
        if self._return_page is self.favorites_page:
            self._show_favorites_page()
            return
        self._show_home_page()

    def _show_add_recipe_page(self) -> None:
        self.add_recipe_page.load_form_options()
        self.page_stack.setCurrentWidget(self.add_recipe_page)

    def _handle_recipe_created(self, recipe_id: int) -> None:
        self.home_page.reload()
        self._open_recipe_details(recipe_id)

    def _handle_settings_applied(self, context: AppContext) -> None:
        self._apply_context(context)
        self._refresh_texts()
        self.theme_selector.blockSignals(True)
        self.theme_selector.setCurrentText(context.theme_name)
        self.theme_selector.blockSignals(False)
        self.home_page.reload()
        self.favorites_page.reload()
        self.add_recipe_page.load_form_options()
        self.recipe_details_page.refresh_language()

    def _refresh_texts(self) -> None:
        language_code = self.current_context.language_code
        self.setWindowTitle(translate(language_code, "app.title"))
        self.product_name.setText(translate(language_code, "app.title"))
        self.product_caption.setText(translate(language_code, "app.subtitle"))
        self.add_recipe_button.setText(translate(language_code, "nav.add_recipe"))
        self.favorites_button.setText(translate(language_code, "nav.favorites"))
        self.settings_button.setText(translate(language_code, "nav.settings"))
        status = self.connection_badge.property("status")
        if status == "checking":
            self.connection_badge.setText(translate(language_code, "status.database_checking"))
        elif status == "success":
            self.connection_badge.setText(translate(language_code, "status.database_connected"))
        elif status == "error":
            self.connection_badge.setText(translate(language_code, "status.database_unavailable"))

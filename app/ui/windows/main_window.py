from __future__ import annotations

from threading import Thread

from PySide6.QtCore import Qt, QTimer
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
from app.database.health import DatabaseHealthResult
from app.services import (
    AppContext,
    AppContextService,
    CategoryService,
    DatabaseStatusService,
    DatabaseMaintenanceService,
    HomeService,
    ImageService,
    RecipeService,
    SettingsService,
    TagService,
    UnitService,
)
from app.ui.components.side_nav import NavItem, SideNav
from app.ui.themes.manager import ThemeManager
from app.ui.windows.add_recipe_page import AddRecipePage
from app.ui.windows.categories_page import CategoriesPage
from app.ui.windows.favorites_page import FavoritesPage
from app.ui.windows.home_page import HomePage
from app.ui.windows.recipe_details_page import RecipeDetailsPage
from app.ui.windows.settings_page import SettingsPage
from app.utils.i18n import translate


class MainWindow(QMainWindow):
    def __init__(self, settings: AppSettings, theme_manager: ThemeManager) -> None:
        super().__init__()
        self.settings = settings
        self.theme_manager = theme_manager
        self.database_status_service = DatabaseStatusService(settings.database)
        self.database_maintenance_service = DatabaseMaintenanceService(settings.database)
        self._maintenance_running = False
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
        self._set_initial_window_size()
        self.setMinimumSize(920, 620)

        self._apply_context(self.current_context)
        self._build_ui()
        self._start_database_monitor()
        self._return_page = None
        self._active_page_key = "home"

    def _set_initial_window_size(self) -> None:
        screen = QApplication.primaryScreen()
        if screen is None:
            self.resize(1280, 820)
            return
        available = screen.availableGeometry()
        width = min(1320, max(980, int(available.width() * 0.82)))
        height = min(860, max(680, int(available.height() * 0.82)))
        self.resize(width, height)

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

        self.theme_selector = QComboBox()
        self.theme_selector.addItems(self.theme_manager.available_themes())
        self.theme_selector.setCurrentText(self.current_context.theme_name)
        self.theme_selector.currentTextChanged.connect(self._on_theme_changed)
        self.theme_selector.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        top_bar.addWidget(self.theme_selector, alignment=Qt.AlignmentFlag.AlignVCenter)

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

        self.categories_page = CategoriesPage(self.context_service)

        self.recipe_details_page = RecipeDetailsPage(
            recipe_service=self.recipe_service,
            context_service=self.context_service,
            image_service=self.image_service,
        )
        self.recipe_details_page.back_requested.connect(self._return_from_details)

        content_shell = QHBoxLayout()
        content_shell.setSpacing(18)
        self.side_nav = SideNav(
            [
                NavItem("home", "nav.home", "H"),
                NavItem("add", "nav.add_recipe", "+"),
                NavItem("favorites", "nav.favorites", "*"),
                NavItem("categories", "nav.categories", "C"),
                NavItem("settings", "nav.settings", "S"),
            ]
        )
        self.side_nav.setFixedWidth(230)
        self.side_nav.page_requested.connect(self._show_page)
        content_shell.addWidget(self.side_nav)

        self.page_stack = QStackedWidget()
        self.page_stack.addWidget(self.home_page)
        self.page_stack.addWidget(self.favorites_page)
        self.page_stack.addWidget(self.add_recipe_page)
        self.page_stack.addWidget(self.categories_page)
        self.page_stack.addWidget(self.settings_page)
        self.page_stack.addWidget(self.recipe_details_page)
        content_shell.addWidget(self.page_stack, stretch=1)
        layout.addLayout(content_shell, stretch=1)

        self.setCentralWidget(root)
        self._refresh_texts()

    def _set_status_badge(self, status: str) -> None:
        self.connection_badge.setProperty("status", status)
        self.connection_badge.style().unpolish(self.connection_badge)
        self.connection_badge.style().polish(self.connection_badge)

    def _start_database_monitor(self) -> None:
        self.database_status_service.status_checked.connect(self._update_database_status)
        self.database_status_service.status_changed.connect(self._handle_database_status_changed)
        self.database_status_service.start()

    def _update_database_status(self, result: DatabaseHealthResult) -> None:
        if result.ok:
            self.connection_badge.setText(translate(self.current_context.language_code, "status.database_connected"))
            self._set_status_badge("success")
            self.connection_badge.setToolTip("")
            return

        self.connection_badge.setText(translate(self.current_context.language_code, "status.database_unavailable"))
        self._set_status_badge("error")
        self.connection_badge.setToolTip(result.error or result.message)

    def _handle_database_status_changed(self, result: DatabaseHealthResult) -> None:
        if result.ok:
            self._run_database_maintenance()

    def _run_database_maintenance(self) -> None:
        if self._maintenance_running:
            return
        self._maintenance_running = True

        def worker() -> None:
            try:
                self.database_maintenance_service.ensure_ready()
            except Exception:
                pass
            finally:
                self._maintenance_running = False
                self.database_status_service.check_now()
                QTimer.singleShot(0, self._refresh_active_page)

        Thread(target=worker, daemon=True).start()

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
        self._active_page_key = "home"
        self.side_nav.set_active("home")
        self.home_page.reload()
        self.page_stack.setCurrentWidget(self.home_page)

    def _show_favorites_page(self) -> None:
        self._active_page_key = "favorites"
        self.side_nav.set_active("favorites")
        self.favorites_page.reload()
        self.page_stack.setCurrentWidget(self.favorites_page)

    def _show_settings_page(self) -> None:
        self._active_page_key = "settings"
        self.side_nav.set_active("settings")
        self.settings_page.reload()
        self.page_stack.setCurrentWidget(self.settings_page)

    def _return_from_details(self) -> None:
        if self._return_page is self.favorites_page:
            self._show_favorites_page()
            return
        self._show_home_page()

    def _show_add_recipe_page(self) -> None:
        self._active_page_key = "add"
        self.side_nav.set_active("add")
        self.add_recipe_page.load_form_options()
        self.page_stack.setCurrentWidget(self.add_recipe_page)

    def _show_categories_page(self) -> None:
        self._active_page_key = "categories"
        self.side_nav.set_active("categories")
        self.categories_page.reload()
        self.page_stack.setCurrentWidget(self.categories_page)

    def _show_page(self, key: str) -> None:
        if key == "home":
            self._show_home_page()
        elif key == "add":
            self._show_add_recipe_page()
        elif key == "favorites":
            self._show_favorites_page()
        elif key == "categories":
            self._show_categories_page()
        elif key == "settings":
            self._show_settings_page()

    def _refresh_active_page(self) -> None:
        widget = self.page_stack.currentWidget()
        if hasattr(widget, "reload"):
            widget.reload()
        elif widget is self.add_recipe_page:
            self.add_recipe_page.load_form_options()
        elif widget is self.recipe_details_page:
            self.recipe_details_page.refresh_language()

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
        self.categories_page.reload()

    def _refresh_texts(self) -> None:
        language_code = self.current_context.language_code
        self.setWindowTitle(translate(language_code, "app.title"))
        self.product_name.setText(translate(language_code, "app.title"))
        self.product_caption.setText(translate(language_code, "app.subtitle"))
        self.add_recipe_button.setText(translate(language_code, "nav.add_recipe"))
        self.side_nav.set_language(language_code)
        self.side_nav.set_active(getattr(self, "_active_page_key", "home"))
        status = self.connection_badge.property("status")
        if status == "checking":
            self.connection_badge.setText(translate(language_code, "status.database_checking"))
        elif status == "success":
            self.connection_badge.setText(translate(language_code, "status.database_connected"))
        elif status == "error":
            self.connection_badge.setText(translate(language_code, "status.database_unavailable"))

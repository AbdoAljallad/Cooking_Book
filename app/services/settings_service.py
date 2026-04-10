from __future__ import annotations

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import AppSettings
from app.repositories import AppSettingRepository, LanguageRepository, ProfileRepository
from app.services.base import BaseService
from app.services.models import AppContext, LanguageOption, SettingsViewData, ThemeOption
from app.ui.themes.manager import ThemeManager
from app.utils.i18n import direction_for_language, localized_native_language_name


class SettingsService(BaseService):
    def __init__(
        self,
        settings: AppSettings,
        theme_manager: ThemeManager,
        session_factory: sessionmaker[Session] | None = None,
    ) -> None:
        super().__init__(session_factory)
        self.settings = settings
        self.theme_manager = theme_manager

    def get_settings_view_data(self, context: AppContext) -> SettingsViewData:
        try:
            with self._open_session() as session:
                languages = LanguageRepository(session).list_all()
                return SettingsViewData(
                    context=context,
                    available_languages=[
                        LanguageOption(
                            code=language.code,
                            label=language.name,
                            native_name=language.native_name,
                            is_rtl=language.is_rtl,
                        )
                        for language in languages
                    ],
                    available_themes=[
                        ThemeOption(name=name, label=name.replace("_", " ").title())
                        for name in self.theme_manager.available_themes()
                    ],
                    selected_language_code=context.language_code,
                    selected_theme_name=context.theme_name,
                    layout_direction=context.layout_direction,
                )
        except (SQLAlchemyError, Exception):
            return SettingsViewData(
                context=context,
                available_languages=[
                    LanguageOption(code="en", label="English", native_name=localized_native_language_name("en"), is_rtl=False),
                    LanguageOption(code="ar", label="Arabic", native_name=localized_native_language_name("ar"), is_rtl=True),
                    LanguageOption(code="ru", label="Russian", native_name=localized_native_language_name("ru"), is_rtl=False),
                ],
                available_themes=[
                    ThemeOption(name=name, label=name.replace("_", " ").title())
                    for name in self.theme_manager.available_themes()
                ],
                selected_language_code=context.language_code,
                selected_theme_name=context.theme_name,
                layout_direction=context.layout_direction,
            )

    def save_settings(
        self,
        language_code: str,
        theme_name: str,
    ) -> AppContext:
        if theme_name not in self.theme_manager.available_themes():
            raise ValueError("Selected theme is not available.")

        with self._open_session() as session:
            try:
                profile = ProfileRepository(session).get_default_profile()
                if profile is None:
                    raise ValueError("A default local profile is required before settings can be saved.")

                language = LanguageRepository(session).get_by_code(language_code)
                if language is None:
                    raise ValueError("Selected language is not available.")

                layout_direction = direction_for_language(language.code, language.is_rtl)
                AppSettingRepository(session).save_for_profile(
                    profile_id=profile.id,
                    language_id=language.id,
                    theme_name=theme_name,
                    layout_direction=layout_direction,
                )
                session.commit()
                return AppContext(
                    profile_id=profile.id,
                    profile_name=profile.display_name,
                    language_code=language.code,
                    theme_name=theme_name,
                    layout_direction=layout_direction,
                )
            except Exception:
                session.rollback()
                raise

from __future__ import annotations

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import AppSettings
from app.repositories import AppSettingRepository, ProfileRepository
from app.services.base import BaseService
from app.services.models import AppContext


class AppContextService(BaseService):
    def __init__(
        self,
        settings: AppSettings,
        session_factory: sessionmaker[Session] | None = None,
    ) -> None:
        super().__init__(session_factory)
        self.settings = settings

    def get_context(self) -> AppContext:
        try:
            with self._open_session() as session:
                profile = ProfileRepository(session).get_default_profile()
                if profile is None:
                    return self._fallback_context()

                app_setting = AppSettingRepository(session).get_for_profile(profile.id)
                if app_setting is None:
                    return AppContext(
                        profile_id=profile.id,
                        profile_name=profile.display_name,
                        language_code=self.settings.ui.language,
                        theme_name=self.settings.ui.default_theme,
                        layout_direction=self.settings.ui.direction,
                    )

                return AppContext(
                    profile_id=profile.id,
                    profile_name=profile.display_name,
                    language_code=app_setting.ui_language.code,
                    theme_name=app_setting.theme_name,
                    layout_direction=app_setting.layout_direction,
                )
        except (SQLAlchemyError, Exception):
            return self._fallback_context()

    def _fallback_context(self) -> AppContext:
        return AppContext(
            profile_id=None,
            profile_name="Local User",
            language_code=self.settings.ui.language,
            theme_name=self.settings.ui.default_theme,
            layout_direction=self.settings.ui.direction,
        )

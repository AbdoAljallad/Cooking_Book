from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.models import AppSetting
from app.repositories.base import BaseRepository


class AppSettingRepository(BaseRepository[AppSetting]):
    def get_for_profile(self, profile_id: int) -> AppSetting | None:
        statement = (
            select(AppSetting)
            .options(joinedload(AppSetting.ui_language), joinedload(AppSetting.profile))
            .where(AppSetting.profile_id == profile_id)
        )
        return self._one_or_none(statement)

    def save_for_profile(
        self,
        profile_id: int,
        language_id: int,
        theme_name: str,
        layout_direction: str,
    ) -> AppSetting:
        setting = self.get_for_profile(profile_id)
        if setting is None:
            setting = AppSetting(
                profile_id=profile_id,
                ui_language_id=language_id,
                theme_name=theme_name,
                layout_direction=layout_direction,
            )
            self.session.add(setting)
        else:
            setting.ui_language_id = language_id
            setting.theme_name = theme_name
            setting.layout_direction = layout_direction
        self.session.flush()
        return setting

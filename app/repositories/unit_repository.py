from __future__ import annotations

from sqlalchemy import Select, func, literal, select

from app.models import Language, Unit, UnitTranslation
from app.repositories.base import BaseRepository
from app.repositories.projections import LocalizedUnit


class UnitRepository(BaseRepository[Unit]):
    def list_all(self, language_code: str | None = None) -> list[LocalizedUnit]:
        statement = self._localized_statement(language_code).order_by(Unit.id.asc())
        rows = self.session.execute(statement).all()
        return [self._to_projection(row) for row in rows]

    def get_by_code(
        self,
        code: str,
        language_code: str | None = None,
    ) -> LocalizedUnit | None:
        statement = self._localized_statement(language_code).where(Unit.code == code)
        row = self.session.execute(statement).one_or_none()
        return None if row is None else self._to_projection(row)

    def _localized_statement(self, language_code: str | None) -> Select:
        target_language = language_code or "en"
        requested_name = (
            select(UnitTranslation.name)
            .join(Language, Language.id == UnitTranslation.language_id)
            .where(UnitTranslation.unit_id == Unit.id, Language.code == target_language)
            .correlate(Unit)
            .scalar_subquery()
        )
        requested_abbreviation = (
            select(UnitTranslation.abbreviation)
            .join(Language, Language.id == UnitTranslation.language_id)
            .where(UnitTranslation.unit_id == Unit.id, Language.code == target_language)
            .correlate(Unit)
            .scalar_subquery()
        )
        english_name = (
            select(UnitTranslation.name)
            .join(Language, Language.id == UnitTranslation.language_id)
            .where(UnitTranslation.unit_id == Unit.id, Language.code == "en")
            .correlate(Unit)
            .scalar_subquery()
        )
        english_abbreviation = (
            select(UnitTranslation.abbreviation)
            .join(Language, Language.id == UnitTranslation.language_id)
            .where(UnitTranslation.unit_id == Unit.id, Language.code == "en")
            .correlate(Unit)
            .scalar_subquery()
        )
        statement = select(
            Unit,
            func.coalesce(func.nullif(requested_name, ""), english_name, Unit.code),
            func.coalesce(func.nullif(requested_abbreviation, ""), english_abbreviation, Unit.symbol),
            literal(target_language),
        )
        return statement

    @staticmethod
    def _to_projection(row) -> LocalizedUnit:
        unit, display_name, abbreviation, language_code = row
        return LocalizedUnit(
            id=unit.id,
            code=unit.code,
            symbol=unit.symbol,
            is_fractional=unit.is_fractional,
            is_active=unit.is_active,
            display_name=display_name or unit.code,
            abbreviation=abbreviation or unit.symbol,
            language_code=language_code,
        )

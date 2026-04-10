from __future__ import annotations

from sqlalchemy import Select, and_, select

from app.models import Language, Tag, TagTranslation
from app.repositories.base import BaseRepository
from app.repositories.projections import LocalizedTag


class TagRepository(BaseRepository[Tag]):
    def list_all(self, language_code: str | None = None) -> list[LocalizedTag]:
        statement = self._localized_statement(language_code).order_by(Tag.slug.asc())
        rows = self.session.execute(statement).all()
        return [self._to_projection(row) for row in rows]

    def get_by_slug(
        self,
        slug: str,
        language_code: str | None = None,
    ) -> LocalizedTag | None:
        statement = self._localized_statement(language_code).where(Tag.slug == slug)
        row = self.session.execute(statement).one_or_none()
        return None if row is None else self._to_projection(row)

    def _localized_statement(self, language_code: str | None) -> Select:
        target_language = language_code or "en"
        statement = select(Tag, TagTranslation.name, Language.code)
        return (
            statement.join(TagTranslation, TagTranslation.tag_id == Tag.id)
            .join(
                Language,
                and_(
                    Language.id == TagTranslation.language_id,
                    Language.code == target_language,
                ),
            )
        )

    @staticmethod
    def _to_projection(row) -> LocalizedTag:
        tag, display_name, language_code = row
        return LocalizedTag(
            id=tag.id,
            slug=tag.slug,
            is_active=tag.is_active,
            display_name=display_name or tag.slug,
            language_code=language_code,
        )

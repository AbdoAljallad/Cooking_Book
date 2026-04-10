from __future__ import annotations

from dataclasses import dataclass

import app.models  # noqa: F401
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from app.database.session import get_session_factory, session_scope
from app.models import (
    AppSetting,
    Category,
    CategoryTranslation,
    Language,
    Profile,
    Recipe,
    Tag,
    TagTranslation,
    Unit,
    UnitTranslation,
)
from app.seeds.data import (
    CATEGORIES,
    DEFAULT_APP_SETTING,
    DEFAULT_PROFILE,
    LANGUAGES,
    TAGS,
    UNITS,
)


@dataclass(slots=True)
class SeedSummary:
    languages: int
    profiles: int
    app_settings: int
    categories: int
    category_translations: int
    units: int
    unit_translations: int
    tags: int
    tag_translations: int
    recipes: int


def _get_existing(session: Session, statement: Select):
    return session.execute(statement).scalar_one_or_none()


def _count_rows(session: Session, model: type) -> int:
    return session.scalar(select(func.count()).select_from(model)) or 0


def _get_or_create_language(session: Session, payload: dict) -> Language:
    language = _get_existing(
        session,
        select(Language).where(Language.code == payload["code"]),
    )
    if language is None:
        language = Language(**payload)
        session.add(language)
        session.flush()
    else:
        language.name = payload["name"]
        language.native_name = payload["native_name"]
        language.is_rtl = payload["is_rtl"]
        language.is_active = payload["is_active"]
    return language


def _get_or_create_profile(session: Session) -> Profile:
    profile = _get_existing(
        session,
        select(Profile).where(Profile.email == DEFAULT_PROFILE["email"]),
    )
    if profile is None:
        profile = Profile(**DEFAULT_PROFILE)
        session.add(profile)
        session.flush()
    else:
        profile.display_name = DEFAULT_PROFILE["display_name"]
        profile.is_active = DEFAULT_PROFILE["is_active"]
    return profile


def _get_or_create_app_setting(
    session: Session,
    profile: Profile,
    languages_by_code: dict[str, Language],
) -> AppSetting:
    app_setting = _get_existing(
        session,
        select(AppSetting).where(AppSetting.profile_id == profile.id),
    )
    target_language = languages_by_code[DEFAULT_APP_SETTING["ui_language_code"]]

    if app_setting is None:
        app_setting = AppSetting(
            profile_id=profile.id,
            ui_language_id=target_language.id,
            theme_name=DEFAULT_APP_SETTING["theme_name"],
            layout_direction=DEFAULT_APP_SETTING["layout_direction"],
        )
        session.add(app_setting)
        session.flush()
    else:
        app_setting.ui_language_id = target_language.id
        app_setting.theme_name = DEFAULT_APP_SETTING["theme_name"]
        app_setting.layout_direction = DEFAULT_APP_SETTING["layout_direction"]
    return app_setting


def _sync_category_translation(
    session: Session,
    category: Category,
    language: Language,
    name: str,
) -> CategoryTranslation:
    translation = _get_existing(
        session,
        select(CategoryTranslation).where(
            CategoryTranslation.category_id == category.id,
            CategoryTranslation.language_id == language.id,
        ),
    )
    if translation is None:
        translation = CategoryTranslation(
            category_id=category.id,
            language_id=language.id,
            name=name,
        )
        session.add(translation)
        session.flush()
    else:
        translation.name = name
    return translation


def _sync_unit_translation(
    session: Session,
    unit: Unit,
    language: Language,
    payload: dict[str, str],
) -> UnitTranslation:
    translation = _get_existing(
        session,
        select(UnitTranslation).where(
            UnitTranslation.unit_id == unit.id,
            UnitTranslation.language_id == language.id,
        ),
    )
    if translation is None:
        translation = UnitTranslation(
            unit_id=unit.id,
            language_id=language.id,
            name=payload["name"],
            abbreviation=payload.get("abbreviation"),
        )
        session.add(translation)
        session.flush()
    else:
        translation.name = payload["name"]
        translation.abbreviation = payload.get("abbreviation")
    return translation


def _sync_tag_translation(
    session: Session,
    tag: Tag,
    language: Language,
    name: str,
) -> TagTranslation:
    translation = _get_existing(
        session,
        select(TagTranslation).where(
            TagTranslation.tag_id == tag.id,
            TagTranslation.language_id == language.id,
        ),
    )
    if translation is None:
        translation = TagTranslation(
            tag_id=tag.id,
            language_id=language.id,
            name=name,
        )
        session.add(translation)
        session.flush()
    else:
        translation.name = name
    return translation


def _seed_categories(session: Session, languages_by_code: dict[str, Language]) -> None:
    for item in CATEGORIES:
        category = _get_existing(
            session,
            select(Category).where(Category.slug == item["slug"]),
        )
        if category is None:
            category = Category(
                slug=item["slug"],
                sort_order=item["sort_order"],
                is_active=True,
            )
            session.add(category)
            session.flush()
        else:
            category.sort_order = item["sort_order"]
            category.is_active = True

        _sync_category_translation(session, category, languages_by_code["en"], item["en"])
        _sync_category_translation(session, category, languages_by_code["ar"], item["ar"])


def _seed_units(session: Session, languages_by_code: dict[str, Language]) -> None:
    for item in UNITS:
        unit = _get_existing(
            session,
            select(Unit).where(Unit.code == item["code"]),
        )
        if unit is None:
            unit = Unit(
                code=item["code"],
                symbol=item["symbol"],
                is_fractional=item["is_fractional"],
                is_active=True,
            )
            session.add(unit)
            session.flush()
        else:
            unit.symbol = item["symbol"]
            unit.is_fractional = item["is_fractional"]
            unit.is_active = True

        _sync_unit_translation(session, unit, languages_by_code["en"], item["en"])
        _sync_unit_translation(session, unit, languages_by_code["ar"], item["ar"])


def _seed_tags(session: Session, languages_by_code: dict[str, Language]) -> None:
    for item in TAGS:
        tag = _get_existing(
            session,
            select(Tag).where(Tag.slug == item["slug"]),
        )
        if tag is None:
            tag = Tag(slug=item["slug"], is_active=True)
            session.add(tag)
            session.flush()
        else:
            tag.is_active = True

        _sync_tag_translation(session, tag, languages_by_code["en"], item["en"])
        _sync_tag_translation(session, tag, languages_by_code["ar"], item["ar"])


def seed_reference_data(session: Session) -> SeedSummary:
    languages_by_code = {
        item["code"]: _get_or_create_language(session, item) for item in LANGUAGES
    }
    profile = _get_or_create_profile(session)
    _get_or_create_app_setting(session, profile, languages_by_code)
    _seed_categories(session, languages_by_code)
    _seed_units(session, languages_by_code)
    _seed_tags(session, languages_by_code)
    session.flush()

    return SeedSummary(
        languages=_count_rows(session, Language),
        profiles=_count_rows(session, Profile),
        app_settings=_count_rows(session, AppSetting),
        categories=_count_rows(session, Category),
        category_translations=_count_rows(session, CategoryTranslation),
        units=_count_rows(session, Unit),
        unit_translations=_count_rows(session, UnitTranslation),
        tags=_count_rows(session, Tag),
        tag_translations=_count_rows(session, TagTranslation),
        recipes=_count_rows(session, Recipe),
    )


def run_seed(session_factory: sessionmaker[Session] | None = None) -> SeedSummary:
    if session_factory is not None:
        session = session_factory()
        try:
            summary = seed_reference_data(session)
            session.commit()
            return summary
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    with session_scope() as session:
        return seed_reference_data(session)


def main() -> int:
    try:
        summary = run_seed(get_session_factory())
    except SQLAlchemyError as exc:
        print(f"Reference data seed failed: {exc}")
        return 1

    print("Reference data seeded successfully.")
    print(
        "languages={0.languages}, profiles={0.profiles}, app_settings={0.app_settings}, "
        "categories={0.categories}, category_translations={0.category_translations}, "
        "units={0.units}, unit_translations={0.unit_translations}, "
        "tags={0.tags}, tag_translations={0.tag_translations}, recipes={0.recipes}".format(summary)
    )
    return 0

from app.utils.i18n import direction_for_language, language_label, normalize_language_code, translate


def test_language_helpers_support_expected_languages() -> None:
    assert normalize_language_code("AR") == "ar"
    assert normalize_language_code("ru") == "ru"
    assert normalize_language_code("de") == "en"
    assert direction_for_language("ar") == "rtl"
    assert direction_for_language("en") == "ltr"
    assert language_label("ar")


def test_translate_uses_language_catalog_and_english_fallback() -> None:
    assert translate("en", "settings.save") == "Save Settings"
    assert translate("ar", "nav.settings") != "nav.settings"
    assert translate("ru", "home.category.all") != "home.category.all"
    assert translate("ru", "favorites.empty_description") != _english("favorites.empty_description")
    assert translate("ru", "add_recipe.metadata_subtitle") != _english("add_recipe.metadata_subtitle")
    assert translate("ru", "nonexistent.key") == "nonexistent.key"


def _english(key: str) -> str:
    return translate("en", key)

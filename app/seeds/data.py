from __future__ import annotations


LANGUAGES = [
    {
        "code": "en",
        "name": "English",
        "native_name": "English",
        "is_rtl": False,
        "is_active": True,
    },
    {
        "code": "ar",
        "name": "Arabic",
        "native_name": "العربية",
        "is_rtl": True,
        "is_active": True,
    },
    {
        "code": "ru",
        "name": "Russian",
        "native_name": "Русский",
        "is_rtl": False,
        "is_active": True,
    },
]

DEFAULT_PROFILE = {
    "display_name": "Local User",
    "email": "local@cookbook.app",
    "is_active": True,
}

DEFAULT_APP_SETTING = {
    "theme_name": "dark",
    "layout_direction": "ltr",
    "ui_language_code": "en",
}

CATEGORIES = [
    {"slug": "soups", "sort_order": 10, "en": "Soups", "ar": "شوربات", "ru": "Супы"},
    {"slug": "appetizers", "sort_order": 20, "en": "Appetizers", "ar": "مقبلات", "ru": "Закуски"},
    {"slug": "salads", "sort_order": 30, "en": "Salads", "ar": "سلطات", "ru": "Салаты"},
    {"slug": "main_dishes", "sort_order": 40, "en": "Main Dishes", "ar": "أطباق رئيسية", "ru": "Основные блюда"},
    {"slug": "rice_dishes", "sort_order": 50, "en": "Rice Dishes", "ar": "أطباق الأرز", "ru": "Блюда из риса"},
    {"slug": "meat", "sort_order": 60, "en": "Meat", "ar": "لحوم", "ru": "Мясо"},
    {"slug": "chicken", "sort_order": 70, "en": "Chicken", "ar": "دجاج", "ru": "Курица"},
    {"slug": "seafood", "sort_order": 80, "en": "Seafood", "ar": "مأكولات بحرية", "ru": "Морепродукты"},
    {"slug": "vegetarian", "sort_order": 90, "en": "Vegetarian", "ar": "نباتي", "ru": "Вегетарианское"},
    {"slug": "baked_goods", "sort_order": 100, "en": "Baked Goods", "ar": "مخبوزات", "ru": "Выпечка"},
    {"slug": "desserts", "sort_order": 110, "en": "Desserts", "ar": "حلويات", "ru": "Десерты"},
    {"slug": "drinks", "sort_order": 120, "en": "Drinks", "ar": "مشروبات", "ru": "Напитки"},
    {"slug": "sauces", "sort_order": 130, "en": "Sauces", "ar": "صلصات", "ru": "Соусы"},
    {"slug": "pickles", "sort_order": 140, "en": "Pickles", "ar": "مخللات", "ru": "Соленья"},
]

UNITS = [
    {"code": "gram", "symbol": "g", "is_fractional": True, "en": {"name": "Gram", "abbreviation": "g"}, "ar": {"name": "جرام", "abbreviation": "جم"}, "ru": {"name": "Грамм", "abbreviation": "г"}},
    {"code": "kilogram", "symbol": "kg", "is_fractional": True, "en": {"name": "Kilogram", "abbreviation": "kg"}, "ar": {"name": "كيلوجرام", "abbreviation": "كجم"}, "ru": {"name": "Килограмм", "abbreviation": "кг"}},
    {"code": "milliliter", "symbol": "ml", "is_fractional": True, "en": {"name": "Milliliter", "abbreviation": "ml"}, "ar": {"name": "ملليلتر", "abbreviation": "مل"}, "ru": {"name": "Миллилитр", "abbreviation": "мл"}},
    {"code": "liter", "symbol": "l", "is_fractional": True, "en": {"name": "Liter", "abbreviation": "l"}, "ar": {"name": "لتر", "abbreviation": "ل"}, "ru": {"name": "Литр", "abbreviation": "л"}},
    {"code": "cup", "symbol": "cup", "is_fractional": True, "en": {"name": "Cup", "abbreviation": "cup"}, "ar": {"name": "كوب", "abbreviation": "كوب"}, "ru": {"name": "Чашка", "abbreviation": "чаш."}},
    {"code": "tablespoon", "symbol": "tbsp", "is_fractional": True, "en": {"name": "Tablespoon", "abbreviation": "tbsp"}, "ar": {"name": "ملعقة كبيرة", "abbreviation": "ك"}, "ru": {"name": "Столовая ложка", "abbreviation": "ст. л."}},
    {"code": "teaspoon", "symbol": "tsp", "is_fractional": True, "en": {"name": "Teaspoon", "abbreviation": "tsp"}, "ar": {"name": "ملعقة صغيرة", "abbreviation": "ص"}, "ru": {"name": "Чайная ложка", "abbreviation": "ч. л."}},
    {"code": "piece", "symbol": "pc", "is_fractional": False, "en": {"name": "Piece", "abbreviation": "pc"}, "ar": {"name": "قطعة", "abbreviation": "قطعة"}, "ru": {"name": "Штука", "abbreviation": "шт."}},
]

TAGS = [
    {"slug": "quick", "en": "Quick", "ar": "سريع", "ru": "Быстро"},
    {"slug": "spicy", "en": "Spicy", "ar": "حار", "ru": "Острое"},
    {"slug": "healthy", "en": "Healthy", "ar": "صحي", "ru": "Полезное"},
    {"slug": "traditional", "en": "Traditional", "ar": "تقليدي", "ru": "Традиционное"},
    {"slug": "vegetarian", "en": "Vegetarian", "ar": "نباتي", "ru": "Вегетарианское"},
    {"slug": "family_favorite", "en": "Family Favorite", "ar": "مفضل للعائلة", "ru": "Любимое в семье"},
    {"slug": "baked", "en": "Baked", "ar": "مخبوز", "ru": "Запечённое"},
    {"slug": "grilled", "en": "Grilled", "ar": "مشوي", "ru": "На гриле"},
]

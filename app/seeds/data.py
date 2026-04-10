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
    {"slug": "soups", "sort_order": 10, "en": "Soups", "ar": "شوربات"},
    {"slug": "appetizers", "sort_order": 20, "en": "Appetizers", "ar": "مقبلات"},
    {"slug": "salads", "sort_order": 30, "en": "Salads", "ar": "سلطات"},
    {"slug": "main_dishes", "sort_order": 40, "en": "Main Dishes", "ar": "أطباق رئيسية"},
    {"slug": "rice_dishes", "sort_order": 50, "en": "Rice Dishes", "ar": "أطباق الأرز"},
    {"slug": "meat", "sort_order": 60, "en": "Meat", "ar": "لحوم"},
    {"slug": "chicken", "sort_order": 70, "en": "Chicken", "ar": "دجاج"},
    {"slug": "seafood", "sort_order": 80, "en": "Seafood", "ar": "مأكولات بحرية"},
    {"slug": "vegetarian", "sort_order": 90, "en": "Vegetarian", "ar": "نباتي"},
    {"slug": "baked_goods", "sort_order": 100, "en": "Baked Goods", "ar": "مخبوزات"},
    {"slug": "desserts", "sort_order": 110, "en": "Desserts", "ar": "حلويات"},
    {"slug": "drinks", "sort_order": 120, "en": "Drinks", "ar": "مشروبات"},
    {"slug": "sauces", "sort_order": 130, "en": "Sauces", "ar": "صلصات"},
    {"slug": "pickles", "sort_order": 140, "en": "Pickles", "ar": "مخللات"},
]

UNITS = [
    {
        "code": "gram",
        "symbol": "g",
        "is_fractional": True,
        "en": {"name": "Gram", "abbreviation": "g"},
        "ar": {"name": "جرام", "abbreviation": "جم"},
    },
    {
        "code": "kilogram",
        "symbol": "kg",
        "is_fractional": True,
        "en": {"name": "Kilogram", "abbreviation": "kg"},
        "ar": {"name": "كيلوجرام", "abbreviation": "كجم"},
    },
    {
        "code": "milliliter",
        "symbol": "ml",
        "is_fractional": True,
        "en": {"name": "Milliliter", "abbreviation": "ml"},
        "ar": {"name": "ملليلتر", "abbreviation": "مل"},
    },
    {
        "code": "liter",
        "symbol": "l",
        "is_fractional": True,
        "en": {"name": "Liter", "abbreviation": "l"},
        "ar": {"name": "لتر", "abbreviation": "ل"},
    },
    {
        "code": "cup",
        "symbol": "cup",
        "is_fractional": True,
        "en": {"name": "Cup", "abbreviation": "cup"},
        "ar": {"name": "كوب", "abbreviation": "كوب"},
    },
    {
        "code": "tablespoon",
        "symbol": "tbsp",
        "is_fractional": True,
        "en": {"name": "Tablespoon", "abbreviation": "tbsp"},
        "ar": {"name": "ملعقة كبيرة", "abbreviation": "ك"},
    },
    {
        "code": "teaspoon",
        "symbol": "tsp",
        "is_fractional": True,
        "en": {"name": "Teaspoon", "abbreviation": "tsp"},
        "ar": {"name": "ملعقة صغيرة", "abbreviation": "ص"},
    },
    {
        "code": "piece",
        "symbol": "pc",
        "is_fractional": False,
        "en": {"name": "Piece", "abbreviation": "pc"},
        "ar": {"name": "قطعة", "abbreviation": "قطعة"},
    },
]

TAGS = [
    {"slug": "quick", "en": "Quick", "ar": "سريع"},
    {"slug": "spicy", "en": "Spicy", "ar": "حار"},
    {"slug": "healthy", "en": "Healthy", "ar": "صحي"},
    {"slug": "traditional", "en": "Traditional", "ar": "تقليدي"},
    {"slug": "vegetarian", "en": "Vegetarian", "ar": "نباتي"},
    {"slug": "family_favorite", "en": "Family Favorite", "ar": "مفضل للعائلة"},
    {"slug": "baked", "en": "Baked", "ar": "مخبوز"},
    {"slug": "grilled", "en": "Grilled", "ar": "مشوي"},
]

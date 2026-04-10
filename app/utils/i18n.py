"""Helpers for language metadata and lightweight UI localization."""

from __future__ import annotations


RTL_LANGUAGE_CODES = {"ar"}
SUPPORTED_LANGUAGE_CODES = ("en", "ar", "ru")

_LANGUAGE_NATIVE_NAMES = {"en": "English", "ar": "العربية", "ru": "Русский"}

_TRANSLATIONS = {
    "en": {
        "search.search": "Search",
        "search.clear": "Clear",
        "image.placeholder": "No Image",
        "image.choose": "Choose Image",
        "image.paste": "Paste from Clipboard",
        "image.clear": "Clear Image",
        "image.drop_here": "Drop image here",
        "image.no_image_selected": "No image selected",
        "image.hint": "Choose a file, paste an image, or drag and drop it here. The app stores a managed copy automatically after save.",
        "image.error.clipboard_empty": "Clipboard does not currently contain an image.",
        "image.error.unsupported_file": "The selected file is not a supported image.",
        "image.error.invalid_image": "The provided image could not be read.",
        "image.error.save_failed": "The image could not be stored in the managed recipe images folder.",
    },
    "ar": {
        "search.search": "بحث",
        "search.clear": "مسح",
        "image.placeholder": "No Image",
        "image.choose": "اختيار صورة",
        "image.paste": "لصق من الحافظة",
        "image.clear": "إزالة الصورة",
        "image.drop_here": "أسقط الصورة هنا",
        "image.no_image_selected": "لم يتم اختيار صورة",
        "image.hint": "اختر ملفًا، أو الصق صورة، أو اسحبها وأفلتها هنا. سيحفظ التطبيق نسخة مُدارة تلقائيًا بعد الحفظ.",
        "image.error.clipboard_empty": "لا تحتوي الحافظة حاليًا على صورة.",
        "image.error.unsupported_file": "الملف المحدد ليس صورة مدعومة.",
        "image.error.invalid_image": "تعذر قراءة الصورة المُدخلة.",
        "image.error.save_failed": "تعذر حفظ الصورة داخل مجلد الصور المُدار من التطبيق.",
    },
    "ru": {
        "search.search": "Поиск",
        "search.clear": "Очистить",
        "image.placeholder": "No Image",
        "image.choose": "Выбрать изображение",
        "image.paste": "Вставить из буфера",
        "image.clear": "Очистить изображение",
        "image.drop_here": "Перетащите изображение сюда",
        "image.no_image_selected": "Изображение не выбрано",
        "image.hint": "Выберите файл, вставьте изображение или перетащите его сюда. После сохранения приложение автоматически создаст управляемую копию.",
        "image.error.clipboard_empty": "В буфере обмена сейчас нет изображения.",
        "image.error.unsupported_file": "Выбранный файл не является поддерживаемым изображением.",
        "image.error.invalid_image": "Не удалось прочитать предоставленное изображение.",
        "image.error.save_failed": "Не удалось сохранить изображение в управляемую папку приложения.",
    },
}


def is_rtl_language(language_code: str, is_rtl_hint: bool | None = None) -> bool:
    if is_rtl_hint is not None:
        return is_rtl_hint
    return language_code.lower() in RTL_LANGUAGE_CODES


def direction_for_language(language_code: str, is_rtl_hint: bool | None = None) -> str:
    return "rtl" if is_rtl_language(language_code, is_rtl_hint) else "ltr"


def normalize_language_code(language_code: str | None) -> str:
    code = (language_code or "en").lower()
    return code if code in SUPPORTED_LANGUAGE_CODES else "en"


def translate(language_code: str | None, key: str, **kwargs: object) -> str:
    normalized = normalize_language_code(language_code)
    template = _TRANSLATIONS.get(normalized, {}).get(key) or _TRANSLATIONS["en"].get(key) or key
    try:
        return template.format(**kwargs)
    except Exception:
        return template


def language_label(language_code: str | None) -> str:
    normalized = normalize_language_code(language_code)
    labels = {
        "en": {"en": "English", "ar": "Arabic", "ru": "Russian"},
        "ar": {"en": "الإنجليزية", "ar": "العربية", "ru": "الروسية"},
        "ru": {"en": "Английский", "ar": "Арабский", "ru": "Русский"},
    }
    return labels[normalized][normalized]


def localized_native_language_name(language_code: str | None) -> str:
    return _LANGUAGE_NATIVE_NAMES.get(normalize_language_code(language_code), "English")

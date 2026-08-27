"""
PurgeKit v3.0 — Language Manager
MIT License — TeamExyKings
"""

import os
import json

LANG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "lang")

LANGUAGES = {
    "en": "English",
    "ta": "Tamil — தமிழ்",
    "hi": "Hindi — हिन्दी",
    "te": "Telugu — తెలుగు",
    "kn": "Kannada — ಕನ್ನಡ",
    "ml": "Malayalam — മലയാളം",
    "mr": "Marathi — मराठी",
    "bn": "Bengali — বাংলা",
    "gu": "Gujarati — ગુજરાતી",
    "pa": "Punjabi — ਪੰਜਾਬੀ",
    "ur": "Urdu — اردو",
    "es": "Spanish — Español",
    "fr": "French — Français",
    "de": "German — Deutsch",
    "it": "Italian — Italiano",
    "pt": "Portuguese — Português",
    "ru": "Russian — Русский",
    "zh": "Chinese — 中文",
    "ja": "Japanese — 日本語",
    "ko": "Korean — 한국어",
    "ar": "Arabic — العربية",
    "tr": "Turkish — Türkçe",
    "nl": "Dutch — Nederlands",
    "pl": "Polish — Polski",
    "vi": "Vietnamese — Tiếng Việt",
    "th": "Thai — ภาษาไทย",
    "id": "Indonesian — Bahasa Indonesia",
    "ms": "Malay — Bahasa Melayu",
    "sw": "Swahili — Kiswahili",
}

_cache = {}

def load_lang(code: str) -> dict:
    if code in _cache:
        return _cache[code]
    path = os.path.join(LANG_DIR, f"{code}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        _cache[code] = data
        return data
    except Exception:
        # fallback to English
        if code != "en":
            return load_lang("en")
        return {}

def t(lang_data: dict, key: str, **kwargs) -> str:
    """Translate a key, with optional format kwargs."""
    val = lang_data.get(key, key)
    try:
        return val.format(**kwargs) if kwargs else val
    except Exception:
        return val

import re
import unicodedata


def clean_text(value: str | None) -> str:
    return " ".join((value or "").strip().split())


def normalize_text(value: str | None) -> str:
    cleaned = clean_text(value).lower()
    return "".join(
        char
        for char in unicodedata.normalize("NFD", cleaned)
        if unicodedata.category(char) != "Mn"
    )


def normalize_grade_key(value: str | None) -> str:
    normalized = normalize_text(value)
    return re.sub(r"[^a-z0-9]", "", normalized)


def normalize_person_name(value: str | None) -> str:
    normalized = normalize_text(value)
    return re.sub(r"[^a-z0-9]", "", normalized)


WEBCOLEGIOS_GRADE_ALIASES = {
    "parvulos": "P\u00e1rvulos",
    "prejardin": "Prejard\u00edn",
    "jardin": "Jard\u00edn",
    "transicion": "Transici\u00f3n",
    "jardindetransicion": "Jard\u00edn de Transici\u00f3n",
    "septimo": "S\u00e9ptimo",
    "decimo": "D\u00e9cimo",
}

INVALID_GRADE_KEYS = {"", "na"}


def normalize_grade_name(value: str | None) -> str:
    cleaned = clean_text(value)
    if not cleaned:
        return ""

    key = normalize_grade_key(cleaned)
    if key in INVALID_GRADE_KEYS:
        return ""

    mapped = WEBCOLEGIOS_GRADE_ALIASES.get(key)
    if mapped:
        return mapped

    normalized_words = re.sub(r"[-_]+", " ", cleaned)
    normalized_words = re.sub(r"[^A-Za-z0-9\u00c0-\u017f\s]", "", normalized_words)
    return " ".join(word.capitalize() for word in normalized_words.split())


def map_webcolegios_grade_to_local(value: str | None) -> str:
    return normalize_grade_name(value)


def normalize_document(value: str | None) -> str:
    return "".join(char for char in (value or "") if char.isdigit()).strip()


def truncate(value: str | None, max_length: int) -> str:
    return clean_text(value)[:max_length]

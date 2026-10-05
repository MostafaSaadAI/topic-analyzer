import re

from rapidfuzz import fuzz

_AR_DIACRITICS = re.compile(r"[\u064B-\u0652\u0640]")
_AR_LETTERS = re.compile(r"[\u0600-\u06FF]")
_LATIN_LETTERS = re.compile(r"[A-Za-z]")


def clean_text(text):
    if not text or not isinstance(text, str):
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"[^\w\s\u0600-\u06FF]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_arabic(text):
    text = _AR_DIACRITICS.sub("", text)
    text = re.sub(r"[إأآا]", "ا", text)
    text = text.replace("ى", "ي").replace("ة", "ه")
    return text


def detect_language(text):
    if not text:
        return "unknown"
    ar = len(_AR_LETTERS.findall(text))
    en = len(_LATIN_LETTERS.findall(text))
    if ar == 0 and en == 0:
        return "unknown"
    return "ar" if ar >= en else "en"


def remove_duplicates(df, threshold=88):
    if df.empty:
        return df

    df = df.drop_duplicates(subset="url").reset_index(drop=True)

    kept_idx, kept_titles = [], []
    for i, title in enumerate(df["title"].fillna("")):
        norm = normalize_arabic(clean_text(title)).lower()
        if not norm:
            continue
        is_dup = any(fuzz.token_set_ratio(norm, k) >= threshold for k in kept_titles)
        if not is_dup:
            kept_idx.append(i)
            kept_titles.append(norm)

    return df.iloc[kept_idx].reset_index(drop=True)

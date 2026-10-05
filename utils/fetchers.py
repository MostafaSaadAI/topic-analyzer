from datetime import date

import feedparser
import pandas as pd
import requests

from config import RSS_FEEDS
from utils.preprocessing import clean_text, detect_language

COLUMNS = ["url", "title", "description", "source", "published_at", "language"]


def fetch_newsapi(query, from_date, to_date, language, sort_by, page_size, api_key):
    params = {
        "q": query,
        "from": from_date.isoformat(),
        "to": to_date.isoformat(),
        "sortBy": sort_by,
        "pageSize": page_size,
        "apiKey": api_key,
    }
    if language in ("ar", "en"):
        params["language"] = language

    r = requests.get("https://newsapi.org/v2/everything", params=params, timeout=15)
    data = r.json()

    if r.status_code != 200:
        raise RuntimeError(f"NewsAPI {r.status_code}: {data.get('message', 'unknown error')}")

    rows = []
    for a in data.get("articles", []):
        title = clean_text(a.get("title") or "")
        if not title or not a.get("url"):
            continue
        rows.append(
            {
                "url": a["url"],
                "title": title,
                "description": clean_text(a.get("description") or ""),
                "source": (a.get("source") or {}).get("name", ""),
                "published_at": a.get("publishedAt", ""),
                "language": language if language in ("ar", "en") else detect_language(title),
            }
        )
    return pd.DataFrame(rows, columns=COLUMNS)


def fetch_rss(query):
    q = query.lower()
    rows = []
    for name, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
        except Exception:
            continue
        for e in feed.entries:
            title = clean_text(e.get("title", ""))
            desc = clean_text(e.get("summary", ""))
            if q not in f"{title} {desc}".lower():
                continue
            published = e.get("published", "") or e.get("updated", "")
            rows.append(
                {
                    "url": e.get("link", ""),
                    "title": title,
                    "description": desc,
                    "source": name,
                    "published_at": pd.to_datetime(published, errors="coerce", utc=True).isoformat()
                    if published
                    else date.today().isoformat(),
                    "language": detect_language(title),
                }
            )
    df = pd.DataFrame(rows, columns=COLUMNS)
    return df[df["url"] != ""]

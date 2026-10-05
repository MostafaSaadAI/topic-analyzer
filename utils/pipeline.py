from datetime import date, timedelta

import pandas as pd

from config import API_KEY, DEDUP_THRESHOLD, FREE_PLAN_MAX_DAYS_BACK
from utils.analysis import analyze
from utils.database import existing_urls, save_articles
from utils.fetchers import fetch_newsapi, fetch_rss
from utils.preprocessing import remove_duplicates


def collect_and_store(query, language="all", use_newsapi=True, use_rss=True,
                      sort_by="publishedAt", page_size=100):
    frames, warnings = [], []

    if use_newsapi:
        if not API_KEY:
            warnings.append("NEWSAPI_KEY is missing in .env")
        else:
            try:
                today = date.today()
                frames.append(
                    fetch_newsapi(
                        query, today - timedelta(days=FREE_PLAN_MAX_DAYS_BACK), today,
                        language, sort_by, page_size, API_KEY,
                    )
                )
            except Exception as e:
                warnings.append(str(e))

    if use_rss:
        frames.append(fetch_rss(query))

    frames = [f for f in frames if not f.empty]
    if not frames:
        return 0, warnings

    df = pd.concat(frames, ignore_index=True)
    df = remove_duplicates(df, DEDUP_THRESHOLD)
    df = df[~df["url"].isin(existing_urls())].reset_index(drop=True)
    if df.empty:
        return 0, warnings

    texts = (df["title"] + ". " + df["description"].str[:200]).tolist()
    res = analyze(texts)
    df["sentiment_label"] = [r["label"] for r in res]
    df["confidence"] = [r["confidence"] for r in res]
    df["sentiment_score"] = [r["score"] for r in res]

    return save_articles(df), warnings

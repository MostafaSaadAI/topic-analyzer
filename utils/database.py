import os
import sqlite3

import pandas as pd

from config import DB_PATH


def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS articles (
            url TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            source TEXT,
            published_at TEXT,
            language TEXT,
            sentiment_label TEXT,
            confidence REAL,
            sentiment_score REAL
        )
        """
    )
    return conn


def existing_urls():
    conn = get_conn()
    try:
        return {r[0] for r in conn.execute("SELECT url FROM articles")}
    finally:
        conn.close()


def save_articles(df):
    if df.empty:
        return 0
    cols = [
        "url", "title", "description", "source", "published_at",
        "language", "sentiment_label", "confidence", "sentiment_score",
    ]
    conn = get_conn()
    try:
        before = conn.total_changes
        conn.executemany(
            f"INSERT OR IGNORE INTO articles ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
            df[cols].values.tolist(),
        )
        conn.commit()
        return conn.total_changes - before
    finally:
        conn.close()


def load_articles(query, start, end, language="all"):
    sql = """
        SELECT * FROM articles
        WHERE (title LIKE ? OR description LIKE ?)
          AND date(published_at) BETWEEN ? AND ?
    """
    like = f"%{query}%"
    params = [like, like, start.isoformat(), end.isoformat()]
    if language in ("ar", "en"):
        sql += " AND language = ?"
        params.append(language)

    conn = get_conn()
    try:
        df = pd.read_sql_query(sql, conn, params=params)
    finally:
        conn.close()

    if not df.empty:
        df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce", utc=True)
        df = df.dropna(subset=["published_at"])
        df["date"] = df["published_at"].dt.date
    return df

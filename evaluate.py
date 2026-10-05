import argparse

import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, f1_score

from utils.analysis import analyze
from utils.database import get_conn
from utils.preprocessing import detect_language

LABELS = ["negative", "neutral", "positive"]


def export_sample(n=300):
    conn = get_conn()
    df = pd.read_sql_query("SELECT title, description FROM articles", conn)
    conn.close()
    df = df.sample(min(n, len(df)), random_state=42)
    df["text"] = df["title"]
    df["label"] = ""
    df[["text", "label"]].to_csv("data/to_label.csv", index=False, encoding="utf-8-sig")
    print(f"Exported {len(df)} titles to data/to_label.csv")


def vader_predict(texts):
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    try:
        nltk.data.find("sentiment/vader_lexicon.zip")
    except LookupError:
        nltk.download("vader_lexicon")
    sia = SentimentIntensityAnalyzer()
    out = []
    for t in texts:
        c = sia.polarity_scores(t)["compound"]
        out.append("positive" if c > 0.05 else "negative" if c < -0.05 else "neutral")
    return out


def report(name, y_true, y_pred):
    print(f"\n===== {name} =====")
    print("Macro-F1:", round(f1_score(y_true, y_pred, average="macro", labels=LABELS), 3))
    print(classification_report(y_true, y_pred, labels=LABELS, zero_division=0))
    print("Confusion matrix (rows=true, cols=pred), order:", LABELS)
    print(confusion_matrix(y_true, y_pred, labels=LABELS))


def evaluate():
    df = pd.read_csv("data/labeled_sample.csv").dropna(subset=["label"])
    df["label"] = df["label"].str.strip().str.lower()
    df["lang"] = df["text"].apply(detect_language)
    print(f"Labeled sample size: {len(df)} | {df['lang'].value_counts().to_dict()}")

    df["transformer"] = [r["label"] for r in analyze(df["text"].tolist())]
    df["vader"] = vader_predict(df["text"].tolist())

    for lang in ["en", "ar"]:
        sub = df[df["lang"] == lang]
        if len(sub) < 10:
            continue
        report(f"VADER ({lang})", sub["label"], sub["vader"])
        report(f"Transformer ({lang})", sub["label"], sub["transformer"])

    errors = df[df["label"] != df["transformer"]]
    errors.to_csv("data/errors.csv", index=False, encoding="utf-8-sig")
    print(f"\nSaved {len(errors)} errors to data/errors.csv")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--export", action="store_true")
    args = p.parse_args()
    export_sample() if args.export else evaluate()

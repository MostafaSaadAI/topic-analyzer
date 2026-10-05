import streamlit as st
from transformers import pipeline

from config import SENTIMENT_MODEL


@st.cache_resource(show_spinner="Loading sentiment model (first time only)...")
def load_model():
    return pipeline(
        "sentiment-analysis",
        model=SENTIMENT_MODEL,
        top_k=None,
        truncation=True,
        max_length=128,
    )


def analyze(texts, batch_size=8):
    texts = [t if t else "." for t in texts]
    if not texts:
        return []

    outputs = load_model()(texts, batch_size=batch_size)

    results = []
    for out in outputs:
        probs = {o["label"].lower(): o["score"] for o in out}
        label = max(probs, key=probs.get)
        results.append(
            {
                "label": label,
                "confidence": round(probs[label], 4),
                "score": round(probs.get("positive", 0) - probs.get("negative", 0), 4),
            }
        )
    return results


LABEL_EN = {"positive": "Positive", "neutral": "Neutral", "negative": "Negative"}

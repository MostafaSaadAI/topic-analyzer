import plotly.express as px

from utils.analysis import LABEL_EN

COLORS = {"Positive": "#2ecc71", "Negative": "#e74c3c", "Neutral": "#95a5a6"}


def _with_label(df):
    df = df.copy()
    df["Sentiment"] = df["sentiment_label"].map(LABEL_EN)
    return df


def distribution_chart(df):
    c = _with_label(df)["Sentiment"].value_counts().reset_index()
    c.columns = ["Sentiment", "Count"]
    return px.pie(c, names="Sentiment", values="Count", color="Sentiment",
                  color_discrete_map=COLORS, title="Sentiment Distribution")


def volume_chart(df):
    v = df.groupby("date").size().reset_index(name="Articles")
    return px.bar(v, x="date", y="Articles", title="Articles per Day (Volume)")


def trend_chart(df, window=3):
    d = df.groupby("date").agg(avg=("sentiment_score", "mean"), n=("url", "count")).reset_index()
    d["Moving average"] = d["avg"].rolling(window, min_periods=1).mean()
    fig = px.scatter(
        d, x="date", y="avg", size="n",
        title=f"Sentiment Trend ({window}-day moving average, dot size = number of articles)",
        labels={"avg": "Average sentiment score", "date": "Date"},
    )
    fig.add_scatter(x=d["date"], y=d["Moving average"], mode="lines", name="Moving average")
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    return fig


def source_chart(df, min_articles=5):
    s = df.groupby("source").agg(avg=("sentiment_score", "mean"), n=("url", "count")).reset_index()
    s = s[s["n"] >= min_articles].sort_values("avg")
    if s.empty:
        return None
    return px.bar(
        s, x="avg", y="source", orientation="h", text="n",
        title=f"Average Sentiment by Source (sources with {min_articles}+ articles)",
        labels={"avg": "Average sentiment score", "source": "Source"},
    )

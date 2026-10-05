from datetime import date, timedelta

import pandas as pd
import streamlit as st

from utils.analysis import LABEL_EN
from utils.database import load_articles
from utils.keywords import top_terms
from utils.pipeline import collect_and_store
from utils.visualization import distribution_chart, source_chart, trend_chart, volume_chart

st.set_page_config(page_title="Topic Analyzer", page_icon="📊", layout="wide")
st.title("📊 Topic Analyzer Dashboard")

with st.sidebar:
    st.header("1) Collect new articles")
    query = st.text_input("Topic", "Artificial Intelligence")
    language = st.selectbox(
        "Language", ["all", "ar", "en"],
        format_func=lambda x: {"all": "All", "ar": "Arabic", "en": "English"}[x],
    )
    use_newsapi = st.checkbox("NewsAPI", True)
    use_rss = st.checkbox("RSS feeds", True)

    if st.button("🔄 Collect & Analyze", type="primary"):
        with st.spinner("Collecting and analyzing..."):
            added, warns = collect_and_store(query, language, use_newsapi, use_rss)
        for w in warns:
            st.warning(w)
        st.success(f"Added {added} new articles to the database")

    st.divider()
    st.header("2) Analysis filters")
    start = st.date_input("From", date.today() - timedelta(days=29))
    end = st.date_input("To", date.today())
    min_conf = st.slider("Minimum model confidence", 0.0, 1.0, 0.0, 0.05)

df = load_articles(query, start, end, language)
if not df.empty:
    df = df[df["confidence"] >= min_conf]

if df.empty:
    st.info("No data for these filters. Click 'Collect & Analyze' first, or widen the date range.")
    st.stop()

st.caption(
    f"⚠️ Analysis is based on headlines plus a short description. Sample size N = {len(df)} articles. "
    "Smaller samples give less reliable results."
)

counts = df["sentiment_label"].value_counts()
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Articles", len(df))
m2.metric("Positive 😀", int(counts.get("positive", 0)))
m3.metric("Negative 😟", int(counts.get("negative", 0)))
m4.metric("Neutral 😐", int(counts.get("neutral", 0)))
m5.metric("Avg. confidence", f"{df['confidence'].mean():.2f}")

c1, c2 = st.columns(2)
c1.plotly_chart(distribution_chart(df), use_container_width=True)
c2.plotly_chart(volume_chart(df), use_container_width=True)
st.plotly_chart(trend_chart(df), use_container_width=True)

src = source_chart(df)
if src is not None:
    st.plotly_chart(src, use_container_width=True)

st.subheader("🔑 Top keywords and phrases")
uni, bi = top_terms((df["title"] + " " + df["description"].fillna("")).tolist())
k1, k2 = st.columns(2)
with k1:
    st.markdown("**Single words**")
    if uni:
        st.bar_chart(pd.DataFrame(uni, columns=["Word", "Count"]).set_index("Word"))
with k2:
    st.markdown("**Two-word phrases**")
    if bi:
        st.bar_chart(pd.DataFrame(bi, columns=["Phrase", "Count"]).set_index("Phrase"))

st.subheader("📑 Articles")
table = df.assign(Sentiment=df["sentiment_label"].map(LABEL_EN))[
    ["title", "source", "published_at", "Sentiment", "confidence", "sentiment_score", "url"]
].rename(columns={
    "title": "Title", "source": "Source", "published_at": "Published",
    "confidence": "Confidence", "sentiment_score": "Score", "url": "Link",
})
st.dataframe(table, use_container_width=True, column_config={"Link": st.column_config.LinkColumn()})

st.download_button(
    "⬇️ Download CSV", table.to_csv(index=False).encode("utf-8-sig"),
    file_name=f"{query}_analysis.csv", mime="text/csv",
)

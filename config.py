import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NEWSAPI_KEY")

DB_PATH = "data/news.db"

SENTIMENT_MODEL = "cardiffnlp/twitter-xlm-roberta-base-sentiment"

FREE_PLAN_MAX_DAYS_BACK = 29

RSS_FEEDS = {
    "BBC Arabic": "https://feeds.bbci.co.uk/arabic/rss.xml",
    "BBC World": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "BBC Technology": "http://feeds.bbci.co.uk/news/technology/rss.xml",
    "BBC Business": "http://feeds.bbci.co.uk/news/business/rss.xml",
    "Al Jazeera EN": "https://www.aljazeera.com/xml/rss/all.xml",
    "TechCrunch": "https://techcrunch.com/feed/",
    "The Verge": "https://www.theverge.com/rss/index.xml",
}

DEDUP_THRESHOLD = 88

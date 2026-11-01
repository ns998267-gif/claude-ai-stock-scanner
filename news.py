import feedparser
import pandas as pd
from urllib.parse import quote

QUERIES = [
    "Indian stock market NSE stocks earnings results",
    "India stocks block deal order win regulatory news",
    "Nifty stocks breakout market news India"
]

def fetch_news(limit=30):
    rows, seen = [], set()
    for query in QUERIES:
        url = "https://news.google.com/rss/search?q=" + quote(query) + "&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(url)
        for entry in feed.entries:
            link = entry.get("link", "")
            title = entry.get("title", "")
            if link and title and link not in seen:
                seen.add(link)
                rows.append({
                    "title": title,
                    "source": entry.get("source", {}).get("title", "Google News RSS"),
                    "published": entry.get("published", "Time unavailable"),
                    "link": link
                })
    return pd.DataFrame(rows[:limit], columns=["title","source","published","link"])

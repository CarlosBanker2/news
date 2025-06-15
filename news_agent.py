import streamlit as st
from duckduckgo_search import DDGS
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GNEWS_KEY = os.getenv("GNEWS_KEY")

# Streamlit setup
st.set_page_config(page_title="📰 News Lookup", page_icon="🗞️", layout="wide")
st.title("🗞️ News Lookup")
st.markdown("Get news articles from multiple sources.")

# Input section
topic = st.text_input("Enter a topic to search:")
sources = ["DuckDuckGo", "BBC", "Reuters", "Al Jazeera"]
selected_sources = st.multiselect("Select sources:", sources, default=sources)

# Helper function to get image from HTML
def extract_image_from_html(html):
    try:
        soup = BeautifulSoup(html, "html.parser")
        img = soup.find("img")
        if img and img.get("src"):
            return img["src"]
    except:
        pass
    return "https://via.placeholder.com/400x200"

# Start search
if st.button("🔍 Search") and topic:
    st.info("Fetching news articles...")
    all_news = []
    errors = {}

    # GNews section
    featured = []
    try:
        url = f"https://gnews.io/api/v4/search?q={topic}&lang=en&max=5&token={GNEWS_KEY}"
        gnews_data = requests.get(url).json()
        for article in gnews_data.get("articles", []):
            featured.append({
                "title": article["title"],
                "url": article["url"],
                "image": article.get("image", "https://via.placeholder.com/400x200"),
                "source": article["source"]["name"],
                "published": article["publishedAt"]
            })
    except Exception as e:
        errors["GNews"] = str(e)

    # DuckDuckGo section
    if "DuckDuckGo" in selected_sources:
        try:
            with DDGS() as ddgs:
                results = ddgs.text(topic, max_results=30)
                for r in results:
                    all_news.append({
                        "title": r.get("title"),
                        "link": r.get("href"),
                        "body": r.get("body", ""),
                        "source": "DuckDuckGo",
                        "published": datetime.now()
                    })
        except Exception as e:
            errors["DuckDuckGo"] = str(e)

    # RSS Feeds section
    rss_sources = {
        "BBC": "http://feeds.bbci.co.uk/news/rss.xml",
        "Reuters": "http://feeds.reuters.com/reuters/topNews",
        "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml"
    }

    for name, feed_url in rss_sources.items():
        if name in selected_sources:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:20]:
                    all_news.append({
                        "title": entry.title,
                        "link": entry.link,
                        "body": entry.get("summary", ""),
                        "source": name,
                        "published": datetime(*entry.published_parsed[:6]) if entry.get("published_parsed") else datetime.now()
                    })
            except Exception as e:
                errors[name] = str(e)

    # Sort news
    all_news = sorted(all_news, key=lambda x: x.get("published", datetime.min), reverse=True)

    # Featured
    st.subheader("🌟 Featured News")
    for f in featured:
        st.markdown(f"**[{f['title']}]({f['url']})**")
        st.image(f["image"], use_container_width=True)
        st.caption(f"{f['source']} | {f['published'][:10]}")
        st.markdown("---")

    # Results
    st.subheader("📰 News Results")
    if not all_news:
        st.warning("No news found.")
    else:
        page_size = 10
        total_pages = max(1, len(all_news) // page_size + (1 if len(all_news) % page_size else 0))
        page = st.number_input("Page", 1, total_pages, 1)
        start = (page - 1) * page_size
        end = start + page_size
        for item in all_news[start:end]:
            img_url = extract_image_from_html(item.get("body", "")) if item["source"] != "DuckDuckGo" else "https://via.placeholder.com/400x200"
            pub_date = item["published"].strftime("%Y-%m-%d %H:%M") if isinstance(item["published"], datetime) else item["published"]
            st.markdown(f"### [{item['title']}]({item['link']})")
            st.caption(f"{item['source']} | {pub_date}")
            st.image(img_url, use_container_width=True)
            st.write(item["body"])
            st.markdown("---")

    # Errors
    if errors:
        st.subheader("⚠️ Errors")
        for source, msg in errors.items():
            st.warning(f"{source}: {msg}")

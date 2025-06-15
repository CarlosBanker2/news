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
HF_TOKEN = os.getenv("HF_TOKEN")
GNEWS_KEY = os.getenv("GNEWS_KEY")

# Setup Streamlit UI
st.set_page_config(page_title="📰 News Lookup", page_icon="🗞️", layout="wide")

# Apply Daily Maverick Inspired Styling
st.markdown("""
    <style>
    html, body {
        background-color: #f8f8f8;
        color: #111;
        font-family: 'Georgia', serif;
    }
    .st-emotion-cache-1v0mbdj, .st-emotion-cache-13k62yr {
        background: white;
        border: 1px solid #ddd;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .stImage > img {
        border-radius: 5px;
    }
    .stButton > button {
        background-color: #333;
        color: white;
        border: none;
        padding: 0.5em 1em;
        border-radius: 4px;
    }
    .stButton > button:hover {
        background-color: #222;
    }
    .category-nav {
        display: flex;
        gap: 1rem;
        margin-bottom: 1rem;
        flex-wrap: wrap;
    }
    .category-button {
        padding: 0.3em 0.6em;
        border: 1px solid #ccc;
        border-radius: 4px;
        background-color: #eee;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🗞️ News Lookup")
st.markdown("A multi-source AI-powered news summarizer with filtering and pagination.")

# Category Navigation
categories = ["Politics", "Business", "Technology", "Health", "World", "Environment", "Science"]
st.markdown('<div class="category-nav">' + ''.join([f'<div class="category-button">{cat}</div>' for cat in categories]) + '</div>', unsafe_allow_html=True)

# Initialize API status tracker
if "rate_limits" not in st.session_state:
    st.session_state.rate_limits = {
        "DuckDuckGo": "✅ Available",
        "RSS": "✅ Available",
        "GNews": "✅ Available"
    }

# Source toggle
st.sidebar.subheader("News Source Settings")
use_ddg = st.sidebar.checkbox("Enable DuckDuckGo", value=True)
use_rss = st.sidebar.checkbox("Enable RSS Feeds", value=True)
use_gnews = st.sidebar.checkbox("Enable GNews (Featured)", value=True)

# API Status Info
with st.sidebar.expander("⚙️ API Rate Limit Status"):
    for key, status in st.session_state.rate_limits.items():
        st.write(f"{key}: {status}")

# Summarizer
headers = {"Authorization": f"Bearer {HF_TOKEN}"}
HF_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

def summarize(text):
    payload = {"inputs": text}
    res = requests.post(HF_API_URL, headers=headers, json=payload)
    if res.status_code == 200:
        return res.json()[0]['summary_text']
    return f"❌ Error: {res.status_code}"

# Data sources
RSS_FEEDS = [
    ("BBC", "http://feeds.bbci.co.uk/news/rss.xml"),
    ("Reuters", "http://feeds.reuters.com/reuters/topNews"),
    ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml"),
]

AVAILABLE_SOURCES = ["DuckDuckGo", "BBC", "Reuters", "Al Jazeera"]

def fetch_og_image(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                return og_image["content"]
    except:
        pass
    return "https://via.placeholder.com/400x200?text=No+Image"

def get_duckduckgo_news(topic):
    try:
        with DDGS() as ddg:
            results = ddg.text(f"{topic} news", max_results=20)
            return [{
                "source": "DuckDuckGo",
                "title": r["title"],
                "url": r["href"],
                "content": r["body"],
                "image": fetch_og_image(r["href"]),
                "published": datetime.now()
            } for r in results]
    except Exception as e:
        st.session_state.rate_limits["DuckDuckGo"] = f"⚠️ {e}"
        return []

def get_rss_news():
    entries = []
    for name, url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            published_dt = datetime(*entry.published_parsed[:6]) if hasattr(entry, "published_parsed") else datetime.min
            image = fetch_og_image(entry.link)
            entries.append({
                "source": name,
                "title": entry.title,
                "url": entry.link,
                "content": getattr(entry, "summary", ""),
                "image": image,
                "published": published_dt
            })
    return entries

def get_gnews_news(topic):
    if not GNEWS_KEY:
        return []
    url = "https://gnews.io/api/v4/search"
    params = {"q": topic, "token": GNEWS_KEY, "sortby": "publishedAt"}
    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        articles = res.json().get("articles", [])
        return [{
            "source": a["source"]["name"],
            "title": a["title"],
            "url": a["url"],
            "content": a.get("description") or a.get("content", ""),
            "image": a.get("image") or fetch_og_image(a["url"]),
            "published": datetime.fromisoformat(a.get("publishedAt").replace("Z", "+00:00")) if a.get("publishedAt") else datetime.min
        } for a in articles if a.get("title") and a.get("url")]
    except Exception as e:
        st.session_state.rate_limits["GNews"] = f"⚠️ {e}"
        return []

# Setup columns
col1, col2 = st.columns([3, 1])

# Input and Search Logic
with col1:
    if "search_topic" not in st.session_state:
        st.session_state.search_topic = "climate change"
    if "news_index" not in st.session_state:
        st.session_state.news_index = 0

    topic_input = st.text_input("Enter a news topic:", value=st.session_state.search_topic)
    selected_sources = st.multiselect("Filter by source:", AVAILABLE_SOURCES, default=AVAILABLE_SOURCES)

    if st.button("🔎 Look Up News") or topic_input != st.session_state.search_topic:
        st.session_state.search_topic = topic_input
        st.session_state.news_index = 0

        all_news = []
        if use_gnews:
            st.session_state.featured_news = get_gnews_news(topic_input)
        else:
            st.session_state.featured_news = []

        if use_ddg:
            all_news += get_duckduckgo_news(topic_input)
        if use_rss:
            all_news += get_rss_news()

        all_news = sorted([n for n in all_news if n["source"] in selected_sources], key=lambda x: x.get("published", datetime.min), reverse=True)

        st.session_state.results = all_news[:50]

# Results tab
with col1:
    if "results" in st.session_state and st.session_state.results:
        st.subheader("📄 Results")
        news = st.session_state.results
        idx = st.session_state.news_index
        end_idx = min(idx + 10, len(news))

        for i in range(idx, end_idx):
            article = news[i]
            with st.expander(f"{i+1}. {article['title']} [{article['source']}]"):
                image_url = article.get("image") or "https://via.placeholder.com/400x200?text=No+Image"
                st.image(image_url, use_container_width=True)
                st.markdown(f"**URL:** [{article['url']}]({article['url']})")
                st.markdown(f"**Original:** {article['content'][:500]}...")
                st.markdown("**Summary:**")
                st.markdown(summarize(article['content']))

        if end_idx < len(news):
            if st.button("🔽 Show 10 More"):
                st.session_state.news_index += 10

# Right sidebar - Featured / Related
with col2:
    st.subheader("🟨 Featured (GNews)")
    if "featured_news" in st.session_state and st.session_state.featured_news:
        for art in st.session_state.featured_news:
            image_url = art.get("image") or "https://via.placeholder.com/400x200?text=No+Image"
            st.image(image_url, use_container_width=True)
            st.markdown(f"**[{art['title']}]({art['url']})**\n\n*{art['source']}*", unsafe_allow_html=True)
    else:
        st.info("No featured articles yet.")

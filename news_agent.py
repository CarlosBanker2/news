import streamlit as st
from duckduckgo_search import DDGS
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
import os
from dotenv import load_dotenv

# Load API keys from .env
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
GNEWS_KEY = os.getenv("GNEWS_KEY")

# Page setup with modern styling
st.set_page_config(
    page_title="NewsHub Pro",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600;700&display=swap');
    
    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Main container */
    .main-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #f0f2f6;
    }
    
    .main-title {
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .main-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        color: #64748b;
        font-weight: 400;
        margin-bottom: 0;
    }
    
    /* Search section */
    .search-section {
        background: #ffffff;
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #e2e8f0;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        background: #ffffff;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1.1rem;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        color: white;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Multiselect styling */
    .stMultiSelect > div > div {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        font-family: 'Inter', sans-serif;
    }
    
    /* News card styling */
    .news-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .news-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }
    
    .news-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .news-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.4rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.5rem;
        line-height: 1.4;
    }
    
    .news-title a {
        color: inherit;
        text-decoration: none;
        transition: color 0.3s ease;
    }
    
    .news-title a:hover {
        color: #667eea;
    }
    
    .news-meta {
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        color: #64748b;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .news-source {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 500;
        font-size: 0.8rem;
    }
    
    .news-content {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        line-height: 1.6;
        color: #475569;
        margin-bottom: 1rem;
    }
    
    /* Featured section */
    .featured-section {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .featured-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.8rem;
        font-weight: 600;
        color: #7c2d12;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .featured-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Pagination */
    .pagination-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 1rem;
        margin: 2rem 0;
        padding: 1rem;
        background: #f8fafc;
        border-radius: 12px;
    }
    
    /* Sidebar styling */
    .sidebar-section {
        background: #ffffff;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #e2e8f0;
    }
    
    .sidebar-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.3rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #f0f2f6;
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-color: #667eea !important;
    }
    
    /* Image styling */
    .news-image {
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Stats cards */
    .stats-container {
        display: flex;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        flex: 1;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
    }
    
    .stat-number {
        font-family: 'Inter', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5rem;
        }
        
        .main-container {
            margin: 0.5rem;
            padding: 1rem;
        }
        
        .search-section {
            padding: 1rem;
        }
        
        .stats-container {
            flex-direction: column;
        }
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-container">
    <div class="main-header">
        <h1 class="main-title">NewsHub Pro</h1>
        <p class="main-subtitle">Professional news aggregation and analysis platform</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Search section
with st.container():
    st.markdown('<div class="search-section">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        topic = st.text_input(
            "Search News Topic",
            placeholder="Enter keywords, company names, or topics...",
            help="Search across multiple news sources for comprehensive coverage"
        )
    
    with col2:
        search_button = st.button("🔍 Search News", use_container_width=True)
    
    # Source selection
    available_sources = ["DuckDuckGo", "BBC", "Reuters", "Al Jazeera"]
    selected_sources = st.multiselect(
        "Select News Sources",
        available_sources,
        default=available_sources,
        help="Choose which news sources to include in your search"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

# Helper functions
def extract_image_from_html(html):
    try:
        soup = BeautifulSoup(html, "html.parser")
        img = soup.find("img")
        if img and img.get("src"):
            return img["src"]
    except Exception:
        pass
    return "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=400&h=200&fit=crop"

def format_date(date_obj):
    if isinstance(date_obj, datetime):
        return date_obj.strftime('%B %d, %Y at %I:%M %p')
    return str(date_obj)[:19] if str(date_obj) else "Unknown date"

# Search execution
if search_button and topic:
    with st.spinner("🔍 Searching news sources..."):
        all_news = []
        rate_limits = {}
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # --- GNews API (Featured Section) ---
        featured = []
        status_text.text("Fetching featured articles...")
        progress_bar.progress(20)
        
        try:
            if GNEWS_KEY:
                gnews_url = f"https://gnews.io/api/v4/search?q={topic}&lang=en&max=5&token={GNEWS_KEY}"
                gnews_data = requests.get(gnews_url, timeout=10).json()
                if gnews_data.get("articles"):
                    for item in gnews_data["articles"]:
                        featured.append({
                            "title": item.get("title"),
                            "url": item.get("url"),
                            "image": item.get("image") or "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=400&h=200&fit=crop",
                            "source": item.get("source", {}).get("name", "GNews"),
                            "published": item.get("publishedAt", datetime.now().isoformat()),
                            "description": item.get("description", "")
                        })
        except Exception as e:
            rate_limits["GNews"] = f"Featured articles unavailable: {str(e)}"

        # --- DuckDuckGo Search ---
        if "DuckDuckGo" in selected_sources:
            status_text.text("Searching DuckDuckGo...")
            progress_bar.progress(40)
            try:
                with DDGS() as ddgs:
                    results = ddgs.text(topic, max_results=20)
                    for r in results:
                        all_news.append({
                            "title": r.get("title"),
                            "link": r.get("href"),
                            "body": r.get("body", "No description available."),
                            "source": "DuckDuckGo",
                            "published": datetime.now()
                        })
            except Exception as e:
                rate_limits["DuckDuckGo"] = f"Search failed: {str(e)}"

        # --- RSS Feeds ---
        rss_feeds = {
            "BBC": "http://feeds.bbci.co.uk/news/rss.xml",
            "Reuters": "http://feeds.reuters.com/reuters/topNews",
            "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml"
        }

        progress_step = 60 / len([s for s in selected_sources if s in rss_feeds])
        current_progress = 40

        for name, url in rss_feeds.items():
            if name in selected_sources:
                status_text.text(f"Fetching {name} articles...")
                current_progress += progress_step
                progress_bar.progress(min(int(current_progress), 90))
                
                try:
                    feed = feedparser.parse(url)
                    for entry in feed.entries[:15]:
                        all_news.append({
                            "title": entry.get("title"),
                            "link": entry.get("link"),
                            "body": entry.get("summary", "No summary available."),
                            "source": name,
                            "published": datetime(*entry.published_parsed[:6]) if entry.get("published_parsed") else datetime.now()
                        })
                except Exception as e:
                    rate_limits[name] = f"RSS feed error: {str(e)}"

        progress_bar.progress(100)
        status_text.text("Processing results...")
        
        # Sort articles newest first
        all_news = sorted(all_news, key=lambda x: x.get("published", datetime.min), reverse=True)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()

        # Statistics
        if all_news or featured:
            st.markdown(f"""
            <div class="stats-container">
                <div class="stat-card">
                    <div class="stat-number">{len(all_news)}</div>
                    <div class="stat-label">News Articles</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(featured)}</div>
                    <div class="stat-label">Featured Stories</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(selected_sources)}</div>
                    <div class="stat-label">Sources</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Layout
        col1, col2 = st.columns([2.5, 1])

        # --- Main News Results ---
        with col1:
            st.markdown("## 📰 Latest News")
            
            if not all_news:
                st.markdown("""
                <div class="news-card" style="text-align: center; padding: 3rem;">
                    <h3 style="color: #64748b; margin-bottom: 1rem;">No articles found</h3>
                    <p style="color: #94a3b8;">Try adjusting your search terms or selecting different sources.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Pagination
                page_size = 8
                total_pages = max(1, (len(all_news) - 1) // page_size + 1)
                
                col_page1, col_page2, col_page3 = st.columns([1, 2, 1])
                with col_page2:
                    page = st.number_input(
                        f"Page (1-{total_pages})",
                        min_value=1,
                        max_value=total_pages,
                        value=1,
                        help=f"Showing {len(all_news)} total articles"
                    )
                
                start = (page - 1) * page_size
                end = start + page_size

                for i, item in enumerate(all_news[start:end]):
                    image_url = extract_image_from_html(item["body"]) if item["source"] != "DuckDuckGo" else "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=600&h=300&fit=crop"
                    pub_str = format_date(item["published"])
                    
                    st.markdown(f"""
                    <div class="news-card">
                        <div class="news-title">
                            <a href="{item['link']}" target="_blank">{item['title']}</a>
                        </div>
                        <div class="news-meta">
                            <span class="news-source">{item['source']}</span>
                            <span>📅 {pub_str}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.image(image_url, use_container_width=True, caption=f"Source: {item['source']}")
                    
                    st.markdown(f"""
                    <div class="news-content">
                        {item['body'][:300]}{'...' if len(item['body']) > 300 else ''}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("---")

        # --- Featured Section ---
        with col2:
            st.markdown("""
            <div class="featured-section">
                <h3 class="featured-title">⭐ Featured Stories</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if not featured:
                st.info("💡 Featured stories will appear here when available")
            else:
                for item in featured:
                    st.markdown(f"""
                    <div class="featured-card">
                        <h4 style="margin-bottom: 0.5rem; font-family: 'Playfair Display', serif;">
                            <a href="{item['url']}" target="_blank" style="color: #1e293b; text-decoration: none;">
                                {item['title'][:80]}{'...' if len(item['title']) > 80 else ''}
                            </a>
                        </h4>
                        <p style="font-size: 0.8rem; color: #64748b; margin-bottom: 0.5rem;">
                            {item['source']} • {item['published'][:10]}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if item.get('image'):
                        st.image(item['image'], use_container_width=True)
                    
                    if item.get('description'):
                        st.markdown(f"<p style='font-size: 0.9rem; color: #475569; margin-bottom: 1rem;'>{item['description'][:150]}{'...' if len(item.get('description', '')) > 150 else ''}</p>", unsafe_allow_html=True)
                    
                    st.markdown("---")

        # Error reporting
        if rate_limits:
            st.markdown("### ⚠️ Source Status")
            for source, error in rate_limits.items():
                st.warning(f"**{source}**: {error}")

# Sidebar with additional options
with st.sidebar:
    st.markdown("""
    <div class="sidebar-section">
        <h3 class="sidebar-title">⚙️ Settings</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("**Search Preferences**")
    max_results = st.slider("Max results per source", 5, 50, 20)
    show_images = st.checkbox("Show article images", value=True)
    
    st.markdown("**Display Options**")
    articles_per_page = st.selectbox("Articles per page", [5, 8, 10, 15], index=1)
    
    st.markdown("---")
    st.markdown("**About NewsHub Pro**")
    st.markdown("""
    Professional news aggregation platform designed for journalists, researchers, and news enthusiasts.
    
    **Features:**
    - Multi-source aggregation
    - Real-time search
    - Professional layout
    - Mobile responsive
    """)
    
    st.markdown("---")
    st.markdown("*Built with ❤️ for news professionals*")
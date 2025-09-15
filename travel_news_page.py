# pages/travel_news_page.py
import streamlit as st
from agents.fetch_travel_news import fetch_travel_news, get_travel_news_categories
from datetime import datetime
from urllib.parse import urlparse
from email.utils import parsedate_to_datetime

def _is_valid_url(url: str) -> bool:
    if not url:
        return False
    try:
        p = urlparse(url)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False

def _format_pub(pub: str) -> str:
    if not pub:
        return ""
    pub_str = str(pub).strip()
    try:
        if pub_str.endswith("Z"):
            dt = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
            return dt.strftime("%b %d, %Y")
        dt = datetime.fromisoformat(pub_str)
        return dt.strftime("%b %d, %Y")
    except Exception:
        pass
    try:
        dt = parsedate_to_datetime(pub_str)
        return dt.strftime("%b %d, %Y")
    except Exception:
        pass
    if "T" in pub_str:
        return pub_str.split("T")[0]
    return pub_str[:30] + ("..." if len(pub_str) > 30 else "")

def _get_travel_score(title, description):
    """Calculate a travel relevance score for sorting."""
    travel_keywords = [
        "travel", "tourism", "tourist", "vacation", "trip", "visit", 
        "destination", "guide", "attractions", "hotel", "flight"
    ]
    
    text = f"{title or ''} {description or ''}".lower()
    score = sum(1 for keyword in travel_keywords if keyword in text)
    return score

@st.cache_data(ttl=300)  # Reduced TTL for more fresh content
def _get_articles_cached(destination: str, max_results: int = 6, category: str = None, include_blogs: bool = True):
    try:
        return fetch_travel_news(
            destination, 
            max_results=max_results, 
            category=category if category != "All Categories" else None,
            include_blogs=include_blogs
        )
    except Exception as e:
        print("fetch_travel_news error:", e)
        return []

def render():
    st.title("🌍 Travel News & Blogs")
    st.markdown("*Get the latest travel news, guides, and blog posts for your destination*")

    # Enhanced form with more options
    with st.form("news_form"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            dest = st.text_input(
                "Enter destination (city, country, or region)", 
                placeholder="e.g. Paris, Japan, Southeast Asia, Maldives"
            )
        
        with col2:
            categories = ["All Categories"] + get_travel_news_categories()
            category = st.selectbox("Category", categories)

        # Additional options
        col3, col4, col5 = st.columns(3)
        
        with col3:
            max_results = st.slider("Number of articles", min_value=3, max_value=15, value=8)
        
        with col4:
            include_blogs = st.checkbox("Include travel blogs", value=True, 
                                      help="Include content from popular travel blogs")
        
        with col5:
            sort_by_relevance = st.checkbox("Sort by travel relevance", value=True,
                                           help="Prioritize more travel-specific content")

        submitted = st.form_submit_button("🔍 Find Travel News", type="primary")

    if not submitted:
        # Show some helpful tips
        with st.expander("💡 Tips for better results"):
            st.markdown("""
            - **Be specific**: Try "Tokyo" instead of just "Japan" for city-specific news
            - **Use categories**: Select specific travel categories for focused results
            - **Include blogs**: Travel blogs often have more personal experiences and tips
            - **Try variations**: If no results, try the country name or nearby major city
            """)
        return

    if not dest or dest.strip() == "":
        st.error("Please enter a destination.")
        return

    destination = dest.strip()
    
    # Show search info
    search_info = f"🔍 Searching for: **{destination}**"
    if category != "All Categories":
        search_info += f" | Category: **{category}**"
    if include_blogs:
        search_info += " | Including travel blogs"
    
    st.info(search_info)

    with st.spinner(f"Fetching travel content for '{destination}'..."):
        articles = _get_articles_cached(
            destination, 
            max_results=max_results, 
            category=category,
            include_blogs=include_blogs
        )

    if not articles:
        st.warning("🔍 No travel content found for this destination.")
        
        with st.expander("Try these suggestions:"):
            st.markdown(f"""
            - Search for the **country** instead of the city (e.g., if you searched "Nice", try "France")
            - Try **nearby major cities** or regions
            - Use **English names** for destinations
            - Check spelling of the destination name
            - Try broader terms like "Southeast Asia" instead of specific small towns
            """)
        return

    # Sort articles by travel relevance if requested
    if sort_by_relevance:
        articles = sorted(articles, 
                         key=lambda x: _get_travel_score(x.get("title"), x.get("description")), 
                         reverse=True)

    st.success(f"✅ Found {len(articles)} travel-related articles")

    # Display articles in an enhanced format
    for i, art in enumerate(articles, 1):
        title = art.get("title") or "Untitled"
        desc = art.get("description") or ""
        url = art.get("url") or ""
        img = art.get("image") or ""
        src = art.get("source") or ""
        pub = art.get("publishedAt") or art.get("pubDate") or ""

        pub_str = _format_pub(pub)
        
        # Create a card-like container
        with st.container():
            # Article number and title
            cols = st.columns([1, 4])
            
            with cols[0]:
                if _is_valid_url(img):
                    try:
                        st.image(img, width=150)
                    except Exception:
                        st.image("https://via.placeholder.com/150x100/4CAF50/white?text=Travel", width=150)
                else:
                    st.image("https://via.placeholder.com/150x100/4CAF50/white?text=Travel", width=150)

            with cols[1]:
                # Article title with numbering
                if _is_valid_url(url):
                    st.markdown(f"### [{i}. {title}]({url})")
                else:
                    st.markdown(f"### {i}. {title}")
                
                # Source and date info with icons
                info_parts = []
                if src:
                    info_parts.append(f"📰 {src}")
                if pub_str:
                    info_parts.append(f"📅 {pub_str}")
                
                if info_parts:
                    st.caption(" • ".join(info_parts))
                
                # Description with better formatting
                if desc:
                    # Limit description length for better display
                    display_desc = desc[:300] + "..." if len(desc) > 300 else desc
                    st.write(display_desc)
                
                # Action buttons
                if _is_valid_url(url):
                    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 3])
                    with col_btn1:
                        st.markdown(f"[🔗 Read More]({url})")
                    with col_btn2:
                        st.markdown(f"[📤 Share]({url})")

            st.divider()

    # Footer with additional options
    with st.expander("🔄 Refresh or modify search"):
        col_refresh1, col_refresh2 = st.columns(2)
        
        with col_refresh1:
            if st.button("🔄 Refresh Results", help="Get fresh articles"):
                st.cache_data.clear()
                st.rerun()
        
        with col_refresh2:
            if st.button("📋 Export Results", help="Copy article titles and links"):
                export_text = f"Travel News for {destination}:\n\n"
                for i, art in enumerate(articles, 1):
                    title = art.get("title", "Untitled")
                    url = art.get("url", "")
                    export_text += f"{i}. {title}\n"
                    if url:
                        export_text += f"   {url}\n"
                    export_text += "\n"
                
                st.text_area("Copy this text:", value=export_text, height=200)
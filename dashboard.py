import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client, Client
import os
from datetime import datetime
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Page config
st.set_page_config(
    page_title="LivePulse v2.0 Enhanced",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Supabase connection
@st.cache_resource
def init_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    return create_client(url, key)

supabase = init_supabase()

# Custom CSS (same as before)
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .main-header h1 {
        font-size: 2.5rem;
        margin: 0;
        font-weight: 700;
    }
    .main-header p {
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    .success-banner {
        background: #d1fae5;
        color: #065f46;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        border-left: 4px solid #10b981;
    }
</style>
""", unsafe_allow_html=True)

# Load data from Supabase
@st.cache_data(ttl=600)
def load_data():
    try:
        response = supabase.table('articles').select('*').execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Sidebar Navigation
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/news.png", width=80)
    st.title("Navigation")
    
    page = st.radio(
        "Go to",
        ["📊 Dashboard", "⚙️ Settings", "ℹ️ About"],
        label_visibility="collapsed"
    )
    
    st.divider()
    dark_mode = st.checkbox("🌙 Dark Mode", value=False)
    auto_refresh = st.checkbox("🔄 Auto-Refresh", value=False)

# PAGE: Dashboard
if page == "📊 Dashboard":
    st.markdown("""
    <div class="main-header">
        <h1>📰 LivePulse v2.0 Enhanced</h1>
        <p>Real-Time News Intelligence Dashboard with Advanced AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    df = load_data()
    
    if df is not None and not df.empty:
        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.markdown(f"""
        <div class="success-banner">
            ✅ Data loaded successfully! Last updated: {last_updated}
        </div>
        """, unsafe_allow_html=True)
        
        # Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total Articles", len(df), delta=f"{len(df)} new")
        
        with col2:
            if 'sentiment' in df.columns:
                positive_pct = (df['sentiment'].value_counts(normalize=True).get('positive', 0) * 100)
                positive_count = len(df[df['sentiment']=='positive'])
                st.metric("😊 Positive Sentiment", f"{positive_pct:.1f}%", delta=f"{positive_count} articles")
        
        with col3:
            sources = df['source'].nunique() if 'source' in df.columns else 0
            st.metric("📰 News Sources", sources, delta="Active")
        
        with col4:
            topics = df['topic'].nunique() if 'topic' in df.columns else 0
            st.metric("🏷️ Topics Identified", topics, delta="Categories")
        
        st.divider()
        
        # Charts Row
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎭 Sentiment Distribution")
            if 'sentiment' in df.columns:
                sentiment_counts = df['sentiment'].value_counts()
                fig = px.pie(
                    values=sentiment_counts.values,
                    names=sentiment_counts.index,
                    color_discrete_sequence=['#ef4444', '#10b981'],
                    hole=0.4
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Top 10 News Sources")
            if 'source' in df.columns:
                source_counts = df['source'].value_counts().head(10)
                fig = px.bar(
                    x=source_counts.values,
                    y=source_counts.index,
                    orientation='h',
                    color=source_counts.values,
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(height=400, showlegend=False, yaxis_title="", xaxis_title="Articles")
                st.plotly_chart(fig, use_container_width=True)
        
        # Topic Distribution
        st.subheader("🏷️ Topic Distribution")
        if 'topic' in df.columns:
            topic_counts = df['topic'].value_counts().head(10)
            fig = px.bar(
                x=topic_counts.values,
                y=topic_counts.index,
                orientation='h',
                color=topic_counts.values,
                color_continuous_scale='Plasma'
            )
            fig.update_layout(height=500, showlegend=False, yaxis_title="Topic", xaxis_title="Number of Articles")
            st.plotly_chart(fig, use_container_width=True)
        
        # Trending Keywords
        st.subheader("☁️ Trending Keywords")
        col1, col2 = st.columns(2)
        
        if 'sentiment' in df.columns and 'title' in df.columns:
            with col1:
                st.write("**Positive News Keywords**")
                positive_text = ' '.join(df[df['sentiment']=='positive']['title'].dropna())
                if positive_text:
                    wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='Greens').generate(positive_text)
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis('off')
                    st.pyplot(fig)
            
            with col2:
                st.write("**Negative News Keywords**")
                negative_text = ' '.join(df[df['sentiment']=='negative']['title'].dropna())
                if negative_text:
                    wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='Reds').generate(negative_text)
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis('off')
                    st.pyplot(fig)
        
        # Articles Table
        st.subheader("📄 Recent Articles")
        display_cols = ['title', 'source', 'sentiment', 'topic', 'published_date']
        available_cols = [col for col in display_cols if col in df.columns]
        st.dataframe(df[available_cols].head(50), use_container_width=True)
        
    else:
        st.warning("⚠️ No data available. Scraper will run daily at 8 AM IST automatically.")

# PAGE: Settings
elif page == "⚙️ Settings":
    st.title("⚙️ Settings")
    st.subheader("🎨 Appearance")
    theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
    st.subheader("🔄 Data Refresh")
    st.info("Dashboard automatically refreshes every 10 minutes")
    st.info("Scraper runs daily at 8:00 AM IST via GitHub Actions")

# PAGE: About
elif page == "ℹ️ About":
    st.title("ℹ️ About LivePulse v2.0 Enhanced")
    st.markdown("""
    ### 📰 LivePulse News Analytics Dashboard
    
    **Version:** 2.0 Enhanced with Full Automation
    
    **Features:**
    - 🤖 Fully automated news scraping (Daily at 8 AM IST)
    - 📊 Real-time sentiment analysis
    - 🏷️ AI-powered topic categorization
    - 📈 Interactive data visualizations
    - ☁️ Word cloud generation
    - 🔄 Automatic data refresh
    - 📅 Date-wise tracking
    
    **Technology Stack:**
    - **Frontend:** Streamlit
    - **Database:** Supabase (PostgreSQL)
    - **Visualization:** Plotly, WordCloud, Matplotlib
    - **AI:** TextBlob, Custom NLP
    - **Automation:** GitHub Actions
    - **Deployment:** Streamlit Cloud
    
    **News Sources (15+):**
    - BBC, CNN, Reuters, The Guardian
    - Al Jazeera, India Today, Hindustan Times
    - Live Mint, Economic Times, News18
    - And more...
    
    ---
    
    **Developer:** Sonikratika
    **GitHub:** [livepulse-automated](https://github.com/sonikratika023-droid/livepulse-automated)
    **Portfolio:** Professional Data Analytics Project
    """)

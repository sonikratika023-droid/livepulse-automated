import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from supabase import create_client, Client
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Page config
st.set_page_config(
    page_title="LivePulse v2.0 Enhanced",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - FIXED WITH VISIBLE TEXT
st.markdown("""
<style>
    /* Light background */
    .stApp {
        background-color: #ffffff;
        color: #000000;
    }
    
    /* Colorful gradient header */
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        padding: 30px;
        margin-bottom: 10px;
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);
        border-radius: 15px;
        color: white;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    
    .subtitle {
        text-align: center;
        color: #6b7280;
        font-size: 1.2rem;
        margin-bottom: 30px;
    }
    
    /* Success message with light green */
    .success-banner {
        background-color: #d1fae5;
        border-left: 4px solid #10b981;
        padding: 15px 20px;
        border-radius: 8px;
        margin: 20px 0;
        color: #047857;
        font-weight: 500;
    }
    
    /* FIXED METRIC CARDS WITH VISIBLE TEXT */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        border: 1px solid #d1d5db;
    }
    
    /* Force black text on metrics */
    div[data-testid="metric-container"] label {
        color: #1f2937 !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
    }
    
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #111827 !important;
        font-size: 2rem !important;
        font-weight: bold !important;
    }
    
    div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
        color: #10b981 !important;
        font-weight: 500 !important;
    }
    
    /* Sidebar light theme */
    section[data-testid="stSidebar"] {
        background-color: #f9fafb;
        border-right: 1px solid #e5e7eb;
    }
    
    section[data-testid="stSidebar"] * {
        color: #1f2937;
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        padding: 12px;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(99, 102, 241, 0.3);
    }
    
    .stButton>button:hover {
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
        box-shadow: 0 4px 8px rgba(99, 102, 241, 0.4);
    }
    
    /* Tab styling for light theme */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f3f4f6;
        border-radius: 8px;
        color: #374151;
        padding: 12px 24px;
        font-weight: 500;
        border: 1px solid #e5e7eb;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
        color: white !important;
        border: none;
    }
    
    /* Subheaders - VISIBLE BLACK TEXT */
    h1, h2, h3, h4, h5, h6 {
        color: #111827 !important;
        font-weight: 600;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f9fafb;
        border-radius: 8px;
        color: #111827 !important;
    }
    
    /* All text should be visible */
    p, span, div {
        color: #374151;
    }
    
    /* File uploader text */
    .stFileUploader label {
        color: #111827 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Supabase
@st.cache_resource
def init_supabase():
    url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL"))
    key = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY"))
    if not url or not key:
        st.error("❌ Supabase credentials not found!")
        st.stop()
    return create_client(url, key)

supabase = init_supabase()

# Load data from Supabase
@st.cache_data(ttl=300)
def load_data():
    try:
        response = supabase.table('articles').select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            if 'published_date' in df.columns:
                df['published_date'] = pd.to_datetime(df['published_date'])
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Main app
def main():
    # Colorful gradient header
    st.markdown('<div class="main-header">📰 LivePulse v2.0 Enhanced</div>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Real-Time News Intelligence Dashboard with Advanced AI</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("📁 Upload Data")
        st.info("Upload your enhanced news CSV")
        
        uploaded_file = st.file_uploader("Drag and drop file here", type=['csv'], help="Limit 200MB per file • CSV")
        
        st.markdown("---")
        st.title("⚙️ Settings")
        
        dark_mode = st.checkbox("🌙 Dark Mode", value=False)
        
        st.markdown("---")
        
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.title("🔄 Auto-Refresh")
        auto_refresh = st.checkbox("Enable Auto-Refresh")
        
        st.markdown("---")
        st.title("📊 About")
        st.info("AI-powered news analytics dashboard with sentiment analysis.")
    
    # Load data
    df = load_data()
    
    if df.empty and uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.markdown('<div class="success-banner">✅ Data loaded successfully! Last updated: ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '</div>', unsafe_allow_html=True)
    elif not df.empty:
        st.markdown('<div class="success-banner">✅ Data loaded successfully! Last updated: ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '</div>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ No data available yet.")
        st.info("💡 Upload a CSV file or run the scraper.")
        return
    
    # Metrics row - WITH VISIBLE TEXT
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📰 Total Articles", len(df), delta=f"↑ {len(df)} new")
    
    with col2:
        positive_count = len(df[df['sentiment'] == 'Positive'])
        positive_pct = (positive_count / len(df) * 100) if len(df) > 0 else 0
        st.metric("😊 Positive Sentiment", f"{positive_pct:.1f}%", delta=f"↑ {positive_count} articles")
    
    with col3:
        sources = df['source'].nunique()
        st.metric("📡 News Sources", sources, delta="↑ Active")
    
    with col4:
        topics = df['topic'].nunique()
        st.metric("🏷️ Topics Identified", topics, delta="↑ Categories")
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Analytics", "☁️ Word Clouds", "📰 Articles"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Sentiment Distribution")
            sentiment_counts = df['sentiment'].value_counts()
            fig_pie = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                title="",
                color_discrete_map={'Positive': '#10b981', 'Negative': '#ef4444', 'Neutral': '#93c5fd'},
                hole=0.4
            )
            fig_pie.update_layout(
                paper_bgcolor='white',
                plot_bgcolor='white',
                font=dict(color='#111827', size=14),
                showlegend=True
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.subheader("📡 Top 10 News Sources")
            source_counts = df['source'].value_counts().head(10)
            fig_bar = px.bar(
                x=source_counts.values,
                y=source_counts.index,
                orientation='h',
                title="",
                color=source_counts.values,
                color_continuous_scale='Viridis'
            )
            fig_bar.update_layout(
                paper_bgcolor='white',
                plot_bgcolor='white',
                font=dict(color='#111827', size=12),
                xaxis_title="Number of Articles",
                yaxis_title="",
                showlegend=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    with tab2:
        if 'published_date' in df.columns:
            st.subheader("📈 Sentiment Trend Over Time")
            df_time = df.groupby([df['published_date'].dt.date, 'sentiment']).size().reset_index(name='count')
            fig_line = px.line(
                df_time,
                x='published_date',
                y='count',
                color='sentiment',
                title="",
                color_discrete_map={'Positive': '#10b981', 'Negative': '#ef4444', 'Neutral': '#93c5fd'}
            )
            fig_line.update_layout(
                paper_bgcolor='white',
                plot_bgcolor='white',
                font=dict(color='#111827')
            )
            st.plotly_chart(fig_line, use_container_width=True)
        
        st.subheader("🏷️ Topic Distribution")
        topic_counts = df['topic'].value_counts().head(10)
        fig_topic = px.bar(
            x=topic_counts.index,
            y=topic_counts.values,
            title="",
            color=topic_counts.values,
            color_continuous_scale='Plasma'
        )
        fig_topic.update_layout(
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(color='#111827')
        )
        st.plotly_chart(fig_topic, use_container_width=True)
    
    with tab3:
        st.subheader("☁️ Trending Keywords")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 😊 Positive News Keywords")
            positive_text = ' '.join(df[df['sentiment'] == 'Positive']['title'].dropna())
            if positive_text:
                wordcloud = WordCloud(
                    width=800, 
                    height=400, 
                    background_color='white',
                    colormap='Greens'
                ).generate(positive_text)
                fig, ax = plt.subplots(figsize=(10, 5), facecolor='white')
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
        
        with col2:
            st.markdown("### 😟 Negative News Keywords")
            negative_text = ' '.join(df[df['sentiment'] == 'Negative']['title'].dropna())
            if negative_text:
                wordcloud = WordCloud(
                    width=800, 
                    height=400, 
                    background_color='white',
                    colormap='Reds'
                ).generate(negative_text)
                fig, ax = plt.subplots(figsize=(10, 5), facecolor='white')
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
    
    with tab4:
        st.subheader("📰 Recent Articles")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            sentiment_filter = st.multiselect("Filter by Sentiment", options=df['sentiment'].unique(), default=df['sentiment'].unique())
        with col2:
            source_filter = st.multiselect("Filter by Source", options=df['source'].unique(), default=list(df['source'].unique())[:5])
        with col3:
            topic_filter = st.multiselect("Filter by Topic", options=df['topic'].unique(), default=df['topic'].unique())
        
        # Apply filters
        filtered_df = df[
            (df['sentiment'].isin(sentiment_filter)) &
            (df['source'].isin(source_filter)) &
            (df['topic'].isin(topic_filter))
        ]
        
        # Display articles
        for idx, row in filtered_df.head(20).iterrows():
            with st.expander(f"📄 {row['title']}"):
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"**Source:** {row['source']}")
                with col2:
                    sentiment_emoji = {'Positive': '🟢', 'Negative': '🔴', 'Neutral': '⚪'}
                    st.markdown(f"**Sentiment:** {sentiment_emoji.get(row['sentiment'], '')} {row['sentiment']}")
                with col3:
                    st.markdown(f"**Topic:** {row['topic']}")
                
                st.markdown(f"**Published:** {row.get('published_date', 'N/A')}")
                
                if 'url' in row and row['url']:
                    st.markdown(f"[🔗 Read Full Article]({row['url']})")

if __name__ == "__main__":
    main()

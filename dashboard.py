import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from supabase import create_client, Client
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import re

# Page config
st.set_page_config(
    page_title="LivePulse - News Analytics Dashboard",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        background-color: #667eea;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Supabase
@st.cache_resource
def init_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        st.error("❌ Supabase credentials not found! Please configure environment variables.")
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
    st.markdown('<h1 class="main-header">📰 LivePulse News Analytics</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("⚙️ Controls")
        
        # Theme toggle
        theme = st.radio("Theme", ["Dark", "Light"], index=0)
        if theme == "Light":
            st.markdown("""
            <style>
                .stApp {
                    background-color: white;
                    color: black;
                }
            </style>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Refresh button
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📊 About")
        st.info("Real-time news analytics dashboard powered by AI sentiment analysis.")
        
    # Load data
    df = load_data()
    
    if df.empty:
        st.warning("⚠️ No data available yet. The scraper will populate data automatically.")
        st.info("💡 The GitHub Actions workflow runs daily at 8 AM IST to scrape fresh news.")
        return
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📰 Total Articles", len(df))
    
    with col2:
        positive_count = len(df[df['sentiment'] == 'Positive'])
        st.metric("😊 Positive News", positive_count)
    
    with col3:
        negative_count = len(df[df['sentiment'] == 'Negative'])
        st.metric("😟 Negative News", negative_count)
    
    with col4:
        neutral_count = len(df[df['sentiment'] == 'Neutral'])
        st.metric("😐 Neutral News", neutral_count)
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Analytics", "☁️ Word Clouds", "📰 Articles"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Sentiment distribution pie chart
            sentiment_counts = df['sentiment'].value_counts()
            fig_pie = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                title="Sentiment Distribution",
                color_discrete_map={'Positive': '#00D9FF', 'Negative': '#FF4B4B', 'Neutral': '#A0A0A0'}
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Topic distribution
            topic_counts = df['topic'].value_counts().head(10)
            fig_bar = px.bar(
                x=topic_counts.values,
                y=topic_counts.index,
                orientation='h',
                title="Top 10 Topics",
                labels={'x': 'Number of Articles', 'y': 'Topic'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    with tab2:
        # Sentiment over time
        if 'published_date' in df.columns:
            df_time = df.groupby(['published_date', 'sentiment']).size().reset_index(name='count')
            fig_line = px.line(
                df_time,
                x='published_date',
                y='count',
                color='sentiment',
                title="Sentiment Trend Over Time",
                labels={'published_date': 'Date', 'count': 'Number of Articles'}
            )
            st.plotly_chart(fig_line, use_container_width=True)
        
        # Source analysis
        source_sentiment = df.groupby(['source', 'sentiment']).size().unstack(fill_value=0)
        fig_stacked = go.Figure(data=[
            go.Bar(name='Positive', x=source_sentiment.index, y=source_sentiment.get('Positive', 0)),
            go.Bar(name='Neutral', x=source_sentiment.index, y=source_sentiment.get('Neutral', 0)),
            go.Bar(name='Negative', x=source_sentiment.index, y=source_sentiment.get('Negative', 0))
        ])
        fig_stacked.update_layout(barmode='stack', title='Articles by Source and Sentiment')
        st.plotly_chart(fig_stacked, use_container_width=True)
    
    with tab3:
        st.subheader("☁️ Trending Keywords")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Positive News Keywords")
            positive_text = ' '.join(df[df['sentiment'] == 'Positive']['title'].dropna())
            if positive_text:
                wordcloud = WordCloud(width=800, height=400, background_color='white').generate(positive_text)
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
            else:
                st.info("No positive news available yet.")
        
        with col2:
            st.markdown("### Negative News Keywords")
            negative_text = ' '.join(df[df['sentiment'] == 'Negative']['title'].dropna())
            if negative_text:
                wordcloud = WordCloud(width=800, height=400, background_color='white').generate(negative_text)
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
            else:
                st.info("No negative news available yet.")
    
    with tab4:
        st.subheader("📰 Recent Articles")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            sentiment_filter = st.multiselect("Filter by Sentiment", options=df['sentiment'].unique(), default=df['sentiment'].unique())
        with col2:
            source_filter = st.multiselect("Filter by Source", options=df['source'].unique(), default=df['source'].unique())
        with col3:
            topic_filter = st.multiselect("Filter by Topic", options=df['topic'].unique(), default=df['topic'].unique())
        
        # Apply filters
        filtered_df = df[
            (df['sentiment'].isin(sentiment_filter)) &
            (df['source'].isin(source_filter)) &
            (df['topic'].isin(topic_filter))
        ]
        
        # Display articles
        for idx, row in filtered_df.iterrows():
            with st.expander(f"📄 {row['title']}"):
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"**Source:** {row['source']}")
                with col2:
                    sentiment_color = {'Positive': '🟢', 'Negative': '🔴', 'Neutral': '⚪'}
                    st.markdown(f"**Sentiment:** {sentiment_color.get(row['sentiment'], '')} {row['sentiment']}")
                with col3:
                    st.markdown(f"**Topic:** {row['topic']}")
                
                st.markdown(f"**Published:** {row.get('published_date', 'N/A')}")
                
                if 'url' in row and row['url']:
                    st.markdown(f"[🔗 Read Full Article]({row['url']})")

if __name__ == "__main__":
    main()

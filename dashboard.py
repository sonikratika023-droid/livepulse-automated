"""
LivePulse - Real-Time News Intelligence Dashboard
Cloud Version with Supabase Integration
Author: Kratika Soni
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime
import os
from supabase import create_client

# ========================================
# PAGE CONFIGURATION
# ========================================
st.set_page_config(
    page_title="LivePulse v2.0 Enhanced",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================
# CUSTOM CSS - ENHANCED STYLING
# ========================================
def load_css():
    st.markdown("""
    <style>
    /* Main container */
    .main {
        padding: 2rem;
    }

    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }

    /* Sentiment badges */
    .sentiment-positive {
        background: #10b981;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: bold;
    }

    .sentiment-negative {
        background: #ef4444;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: bold;
    }

    .sentiment-neutral {
        background: #6b7280;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: bold;
    }

    /* Animate on load */
    .stApp {
        animation: fadeIn 0.5s ease-in;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    </style>
    """, unsafe_allow_html=True)

load_css()

# ========================================
# SUPABASE INTEGRATION
# ========================================
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL"))
        key = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY"))
        if url and key:
            return create_client(url, key)
        return None
    except:
        return None

supabase = init_supabase()

@st.cache_data(ttl=300)
def load_data_from_supabase():
    if supabase:
        try:
            response = supabase.table('articles').select("*").execute()
            if response.data:
                df = pd.DataFrame(response.data)
                if 'published_date' in df.columns:
                    df['published_date'] = pd.to_datetime(df['published_date'])
                return df
        except Exception as e:
            st.sidebar.error(f"Supabase error: {e}")
    return pd.DataFrame()

# ========================================
# HEADER
# ========================================
st.markdown("""
<div class="main-header">
    <h1>📰 LivePulse v2.0 Enhanced</h1>
    <p style='font-size: 1.2rem; margin-top: 0.5rem;'>
        Real-Time News Intelligence Dashboard with Advanced AI
    </p>
</div>
""", unsafe_allow_html=True)

# ========================================
# SIDEBAR - FILE UPLOAD & SETTINGS
# ========================================
with st.sidebar:
    st.header("📁 Upload Data")
    uploaded_file = st.file_uploader(
        "Upload CSV (optional)",
        type=['csv'],
        help="Upload CSV file or use Supabase data"
    )

    st.markdown("---")

    # Settings
    st.header("⚙️ Settings")
    dark_mode = st.checkbox("🌙 Dark Mode", value=False)

    st.markdown("---")
    
    # Refresh button
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.header("📊 About")
    st.info("""
    **LivePulse v2.0 Enhanced**

    ✨ Features:
    - 20+ news sources
    - AI sentiment analysis
    - Topic clustering
    - Real-time updates
    - Advanced visualizations
    """)

# ========================================
# LOAD DATA
# ========================================
df = load_data_from_supabase()

if df.empty and uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

# ========================================
# MAIN CONTENT
# ========================================
if not df.empty:
    # Display last updated time
    st.success(f"✅ Data loaded successfully! Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # ========================================
    # KEY METRICS ROW
    # ========================================
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="📰 Total Articles",
            value=len(df),
            delta=f"{len(df)} new"
        )

    with col2:
        positive_pct = (len(df[df['sentiment'] == 'Positive']) / len(df)) * 100
        st.metric(
            label="😊 Positive Sentiment",
            value=f"{positive_pct:.1f}%",
            delta=f"{len(df[df['sentiment'] == 'Positive'])} articles"
        )

    with col3:
        st.metric(
            label="📡 News Sources",
            value=df['source'].nunique(),
            delta="Active"
        )

    with col4:
        st.metric(
            label="🏷️ Topics Identified",
            value=df['topic'].nunique(),
            delta="Categories"
        )

    st.markdown("---")

    # ========================================
    # VISUALIZATIONS - TWO COLUMNS
    # ========================================
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("🎭 Sentiment Distribution")
        sentiment_counts = df['sentiment'].value_counts()

        fig_sentiment = px.pie(
            values=sentiment_counts.values,
            names=sentiment_counts.index,
            color=sentiment_counts.index,
            color_discrete_map={
                'Positive': '#10b981',
                'Negative': '#ef4444',
                'Neutral': '#6b7280'
            },
            hole=0.4
        )
        fig_sentiment.update_traces(textinfo='percent+label')
        fig_sentiment.update_layout(height=400)
        st.plotly_chart(fig_sentiment, use_container_width=True)

    with col_right:
        st.subheader("📊 Top 10 News Sources")
        source_counts = df['source'].value_counts().head(10)

        fig_sources = px.bar(
            x=source_counts.values,
            y=source_counts.index,
            orientation='h',
            color=source_counts.values,
            color_continuous_scale='Viridis'
        )
        fig_sources.update_layout(
            xaxis_title="Number of Articles",
            yaxis_title="Source",
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig_sources, use_container_width=True)

    st.markdown("---")

    # ========================================
    # TOPIC ANALYSIS
    # ========================================
    st.subheader("🏷️ Topic Distribution")

    topic_counts = df['topic'].value_counts().head(10)

    fig_topics = px.bar(
        x=topic_counts.index,
        y=topic_counts.values,
        color=topic_counts.values,
        color_continuous_scale='Plasma',
        labels={'x': 'Topic', 'y': 'Number of Articles'}
    )
    fig_topics.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_topics, use_container_width=True)

    st.markdown("---")

    # ========================================
    # WORD CLOUD
    # ========================================
    st.subheader("☁️ Trending Keywords")

    col_wc1, col_wc2 = st.columns(2)

    with col_wc1:
        st.write("**Positive News Keywords**")
        positive_text = ' '.join(df[df['sentiment'] == 'Positive']['title'].dropna())
        if positive_text:
            wordcloud_pos = WordCloud(
                width=400,
                height=300,
                background_color='white',
                colormap='Greens'
            ).generate(positive_text)

            fig_wc_pos, ax = plt.subplots(figsize=(6, 4))
            ax.imshow(wordcloud_pos, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig_wc_pos)

    with col_wc2:
        st.write("**Negative News Keywords**")
        negative_text = ' '.join(df[df['sentiment'] == 'Negative']['title'].dropna())
        if negative_text:
            wordcloud_neg = WordCloud(
                width=400,
                height=300,
                background_color='white',
                colormap='Reds'
            ).generate(negative_text)

            fig_wc_neg, ax = plt.subplots(figsize=(6, 4))
            ax.imshow(wordcloud_neg, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig_wc_neg)

    st.markdown("---")

    # ========================================
    # DATA TABLE WITH SEARCH
    # ========================================
    st.subheader("🔍 Search & Filter Articles")

    col_search1, col_search2, col_search3 = st.columns(3)

    with col_search1:
        search_term = st.text_input("🔎 Search by keyword", "")

    with col_search2:
        filter_sentiment = st.multiselect(
            "Filter by sentiment",
            options=df['sentiment'].unique(),
            default=df['sentiment'].unique()
        )

    with col_search3:
        filter_source = st.multiselect(
            "Filter by source",
            options=sorted(df['source'].unique()),
            default=[]
        )

    # Apply filters
    filtered_df = df.copy()

    if search_term:
        filtered_df = filtered_df[
            filtered_df['title'].str.contains(search_term, case=False, na=False) |
            filtered_df['description'].str.contains(search_term, case=False, na=False)
        ]

    if filter_sentiment:
        filtered_df = filtered_df[filtered_df['sentiment'].isin(filter_sentiment)]

    if filter_source:
        filtered_df = filtered_df[filtered_df['source'].isin(filter_source)]

    st.write(f"**Showing {len(filtered_df)} of {len(df)} articles**")

    # ========================================
    # ARTICLE READER - EXPANDABLE CARDS
    # ========================================
    st.write(f"**Showing top {min(50, len(filtered_df))} articles**")

    # Add view mode toggle
    view_mode = st.radio(
        "View Mode:",
        options=["📋 Table View", "📄 Article Cards"],
        horizontal=True
    )

    if view_mode == "📋 Table View":
        # Table view
        display_cols = ['source', 'published_date', 'title', 'sentiment', 'topic']
        available_cols = [col for col in display_cols if col in filtered_df.columns]
        display_df = filtered_df[available_cols].head(50)
        st.dataframe(display_df, use_container_width=True, height=400)

    else:
        # Article Cards View with FULL READING EXPERIENCE
        st.markdown("---")

        for idx, row in filtered_df.head(50).iterrows():
            # Sentiment color
            if row['sentiment'] == 'Positive':
                sentiment_color = '#10b981'
                emoji = '😊'
            elif row['sentiment'] == 'Negative':
                sentiment_color = '#ef4444'
                emoji = '😟'
            else:
                sentiment_color = '#6b7280'
                emoji = '😐'

            # Create expandable article card
            with st.expander(f"{emoji} **{row['title']}**", expanded=False):
                col_a, col_b = st.columns([3, 1])

                with col_a:
                    st.markdown(f"**📰 Source:** {row['source']}")
                    st.markdown(f"**📅 Published:** {row.get('published_date', 'N/A')}")
                    st.markdown(f"**🏷️ Topic:** {row['topic']}")

                    # Show description/summary
                    st.markdown("**📝 Summary:**")
                    description = row.get('description', 'No description available.')
                    st.write(description[:500] + '...' if len(description) > 500 else description)

                    # Read full article button
                    if 'url' in row and row['url']:
                        st.markdown(f"**[🔗 Read Full Article →]({row['url']})**", unsafe_allow_html=True)

                with col_b:
                    # Sentiment badge
                    sentiment_score = row.get('sentiment_score', 0)
                    st.markdown(f"""
                    <div style='background: {sentiment_color}; color: white; padding: 1rem;
                    border-radius: 10px; text-align: center;'>
                        <h3 style='margin: 0; color: white;'>{emoji}</h3>
                        <p style='margin: 0; color: white; font-weight: bold;'>{row['sentiment']}</p>
                        <p style='margin: 0; color: white; font-size: 0.9rem;'>
                            Score: {sentiment_score:.2f}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("---")


else:
    # No file uploaded
    st.info("👈 Please upload your enhanced news CSV file from the sidebar or wait for Supabase data!")

    st.markdown("### 📖 How to use:")
    st.markdown("""
    1. **Data loads automatically** from Supabase
    2. **Or upload CSV** manually from sidebar
    3. **Explore** the interactive dashboard!
    4. **Run scraper** to get fresh data
    """)

# ========================================
# FOOTER
# ========================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6b7280; padding: 2rem;'>
    <p><strong>LivePulse v2.0 Enhanced</strong> | Built with Python, Streamlit & AI</p>
    <p> <b>Kratika Soni</b> |  Data Analytics Student |  sonikratika023@gmail.com</p>
</div>
""", unsafe_allow_html=True)


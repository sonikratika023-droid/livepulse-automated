import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from supabase import create_client
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="LivePulse v2.0",
    page_icon="📰",
    layout="wide"
)

# SIMPLE CSS - NO CONFLICTS
st.markdown("""
<style>
    .stApp { background-color: #ffffff !important; }
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        padding: 30px;
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);
        border-radius: 15px;
        color: white !important;
    }
    div[data-testid="stMetricValue"] { color: #111827 !important; font-size: 2rem !important; }
    div[data-testid="stMetricLabel"] { color: #111827 !important; }
    h1, h2, h3 { color: #111827 !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def init_supabase():
    url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL"))
    key = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY"))
    if not url or not key:
        st.error("❌ Supabase credentials not found!")
        st.stop()
    return create_client(url, key)

supabase = init_supabase()

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
        st.error(f"Error: {e}")
        return pd.DataFrame()

def main():
    st.markdown('<div class="main-header">📰 LivePulse v2.0</div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.title("📁 Upload Data")
        uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
        st.markdown("---")
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()
    
    df = load_data()
    
    if df.empty and uploaded_file:
        df = pd.read_csv(uploaded_file)
    
    if df.empty:
        st.warning("No data")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📰 Articles", len(df))
    with col2:
        pos = len(df[df['sentiment'] == 'Positive'])
        st.metric("😊 Positive", f"{pos/len(df)*100:.1f}%")
    with col3:
        st.metric("📡 Sources", df['source'].nunique())
    with col4:
        st.metric("🏷️ Topics", df['topic'].nunique())
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Analytics", "☁️ Words", "📰 Articles"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Sentiment")
            fig = px.pie(df, names='sentiment', hole=0.4)
            fig.update_layout(paper_bgcolor='white', font=dict(color='black'))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Top Sources")
            top = df['source'].value_counts().head(10)
            fig = px.bar(x=top.values, y=top.index, orientation='h')
            fig.update_layout(paper_bgcolor='white', font=dict(color='black'))
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        if 'published_date' in df.columns:
            st.subheader("Trend")
            df_time = df.groupby([df['published_date'].dt.date, 'sentiment']).size().reset_index(name='count')
            fig = px.line(df_time, x='published_date', y='count', color='sentiment')
            fig.update_layout(paper_bgcolor='white', font=dict(color='black'))
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Positive")
            text = ' '.join(df[df['sentiment']=='Positive']['title'].dropna())
            if text:
                wc = WordCloud(width=800, height=400, background_color='white').generate(text)
                fig, ax = plt.subplots(facecolor='white')
                ax.imshow(wc)
                ax.axis('off')
                st.pyplot(fig)
        
        with col2:
            st.markdown("### Negative")
            text = ' '.join(df[df['sentiment']=='Negative']['title'].dropna())
            if text:
                wc = WordCloud(width=800, height=400, background_color='white').generate(text)
                fig, ax = plt.subplots(facecolor='white')
                ax.imshow(wc)
                ax.axis('off')
                st.pyplot(fig)
    
    with tab4:
        st.subheader("Articles")
        for idx, row in df.head(20).iterrows():
            with st.expander(f"📄 {row['title']}"):
                st.markdown(f"**Source:** {row['source']}")
                st.markdown(f"**Sentiment:** {row['sentiment']}")
                if 'url' in row and row['url']:
                    st.markdown(f"[🔗 Read]({row['url']})")

if __name__ == "__main__":
    main()

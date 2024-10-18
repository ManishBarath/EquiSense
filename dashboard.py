import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import scraper
import numpy as np
from collections import Counter
import time

st.set_page_config(
    page_title="FinBERT Sentiment Analysis Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .sentiment-positive {
        color: #28a745;
        font-weight: bold;
    }
    .sentiment-negative {
        color: #dc3545;
        font-weight: bold;
    }
    .sentiment-neutral {
        color: #ffc107;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model():
    """Load the FinBERT model and tokenizer"""
    model_path = "./finbert_model"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    model.eval()
    return tokenizer, model

@st.cache_data
def get_scraped_data():
    """Scrape news data"""
    return scraper.scrape_all()

def predict_sentiment_single(text, tokenizer, model):
    """Predict sentiment for a single text"""
    labels = ["negative", "neutral", "positive"]
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        pred_label = labels[torch.argmax(probs)]
        confidence = torch.max(probs).item()
    
    return pred_label, confidence, probs[0].numpy()

def predict_sentiment_batch(headlines, tokenizer, model):
    """Predict sentiment for multiple headlines"""
    labels = ["negative", "neutral", "positive"]
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, headline in enumerate(headlines):
        inputs = tokenizer(headline, return_tensors="pt", truncation=True, padding=True, max_length=512)
        
        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            pred_label = labels[torch.argmax(probs)]
            confidence = torch.max(probs).item()
        
        results.append({
            "headline": headline,
            "sentiment": pred_label,
            "confidence": confidence,
            "negative_prob": probs[0][0].item(),
            "neutral_prob": probs[0][1].item(),
            "positive_prob": probs[0][2].item()
        })
        
        # Update progress
        progress = (i + 1) / len(headlines)
        progress_bar.progress(progress)
        status_text.text(f"Processing headline {i + 1} of {len(headlines)}")
    
    progress_bar.empty()
    status_text.empty()
    
    return results

def main():
    # Header
    st.markdown('<h1 class="main-header">📈 FinBERT Sentiment Analysis Dashboard</h1>', unsafe_allow_html=True)
    
    # Load model
    with st.spinner("Loading FinBERT model..."):
        tokenizer, model = load_model()
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", ["Single Prediction", "Batch Analysis", "News Scraping", "Model Info"])
    
    if page == "Single Prediction":
        single_prediction_page(tokenizer, model)
    elif page == "Batch Analysis":
        batch_analysis_page(tokenizer, model)
    elif page == "News Scraping":
        news_scraping_page(tokenizer, model)
    elif page == "Model Info":
        model_info_page()

def single_prediction_page(tokenizer, model):
    st.header("🔍 Single Text Sentiment Prediction")
    
    # Text input
    text_input = st.text_area(
        "Enter a financial headline or text:",
        placeholder="e.g., 'Apple reports record quarterly earnings beating analyst expectations'",
        height=100
    )
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        predict_button = st.button("Predict Sentiment", type="primary")
    
    if predict_button and text_input:
        with st.spinner("Analyzing sentiment..."):
            sentiment, confidence, probs = predict_sentiment_single(text_input, tokenizer, model)
        
        # Display results
        st.subheader("Results")
        
        # Sentiment with colored text
        sentiment_class = f"sentiment-{sentiment.lower()}"
        st.markdown(f'**Predicted Sentiment:** <span class="{sentiment_class}">{sentiment.upper()}</span>', unsafe_allow_html=True)
        st.markdown(f'**Confidence:** {confidence:.3f}')
        
        # Probability distribution chart
        fig = go.Figure(data=[
            go.Bar(x=['Negative', 'Neutral', 'Positive'], 
                   y=probs,
                   marker_color=['#dc3545', '#ffc107', '#28a745'])
        ])
        fig.update_layout(
            title="Sentiment Probability Distribution",
            xaxis_title="Sentiment",
            yaxis_title="Probability",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    elif predict_button and not text_input:
        st.warning("Please enter some text to analyze.")

def batch_analysis_page(tokenizer, model):
    st.header("📊 Batch Sentiment Analysis")
    
    # Text area for multiple headlines
    st.subheader("Enter Multiple Headlines")
    batch_text = st.text_area(
        "Enter headlines (one per line):",
        placeholder="Company A reports strong earnings\nMarket volatility increases\nNew regulations announced",
        height=150
    )
    
    # File upload option
    st.subheader("Or Upload a CSV File")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    headlines = []
    
    if batch_text:
        headlines = [line.strip() for line in batch_text.split('\n') if line.strip()]
    elif uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        if 'headline' in df.columns:
            headlines = df['headline'].tolist()
        elif 'text' in df.columns:
            headlines = df['text'].tolist()
        else:
            st.error("CSV file must have a 'headline' or 'text' column")
            return
    
    if headlines:
        st.write(f"Found {len(headlines)} headlines to analyze")
        
        if st.button("Analyze All Headlines", type="primary"):
            results = predict_sentiment_batch(headlines, tokenizer, model)
            
            # Convert to DataFrame
            df_results = pd.DataFrame(results)
            
            # Display summary metrics
            st.subheader("Summary Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            sentiment_counts = Counter(df_results['sentiment'])
            total_headlines = len(df_results)
            
            with col1:
                st.metric("Total Headlines", total_headlines)
            with col2:
                st.metric("Positive", sentiment_counts.get('positive', 0))
            with col3:
                st.metric("Neutral", sentiment_counts.get('neutral', 0))
            with col4:
                st.metric("Negative", sentiment_counts.get('negative', 0))
            
            # Sentiment distribution pie chart
            col1, col2 = st.columns(2)
            
            with col1:
                fig_pie = px.pie(
                    values=list(sentiment_counts.values()),
                    names=list(sentiment_counts.keys()),
                    title="Sentiment Distribution",
                    color_discrete_map={
                        'positive': '#28a745',
                        'neutral': '#ffc107',
                        'negative': '#dc3545'
                    }
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Average confidence by sentiment
                avg_confidence = df_results.groupby('sentiment')['confidence'].mean()
                fig_bar = px.bar(
                    x=avg_confidence.index,
                    y=avg_confidence.values,
                    title="Average Confidence by Sentiment",
                    color=avg_confidence.index,
                    color_discrete_map={
                        'positive': '#28a745',
                        'neutral': '#ffc107',
                        'negative': '#dc3545'
                    }
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Detailed results table
            st.subheader("Detailed Results")
            
            # Add color coding to sentiment column
            def color_sentiment(val):
                if val == 'positive':
                    return 'background-color: #d4edda; color: #155724'
                elif val == 'negative':
                    return 'background-color: #f8d7da; color: #721c24'
                else:
                    return 'background-color: #fff3cd; color: #856404'
            
            styled_df = df_results.style.applymap(color_sentiment, subset=['sentiment'])
            st.dataframe(styled_df, use_container_width=True)
            
            # Download results
            csv = df_results.to_csv(index=False)
            st.download_button(
                label="Download Results as CSV",
                data=csv,
                file_name="sentiment_analysis_results.csv",
                mime="text/csv"
            )

def news_scraping_page(tokenizer, model):
    st.header("📰 Live News Sentiment Analysis")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        scrape_mode = st.selectbox(
            "Choose scraping mode:",
            ["Quick Scrape (3 sources)", "Full Scrape (8 sources)"],
            help="Quick scrape is faster but fewer headlines. Full scrape takes longer but more comprehensive."
        )
        
        if st.button("Scrape Latest News", type="primary"):
            with st.spinner("Scraping latest financial news..."):
                if "Quick" in scrape_mode:
                    scraped_headlines = scraper.scrape_quick()
                else:
                    scraped_headlines = scraper.scrape_all()
            
            if scraped_headlines:
                st.success(f"Successfully scraped {len(scraped_headlines)} headlines!")
                
                # Store in session state
                st.session_state.scraped_headlines = scraped_headlines
                st.session_state.scrape_timestamp = time.time()
            else:
                st.error("No headlines found. Please check your internet connection.")
    
    with col2:
        if st.button("Test Individual Sources", type="secondary"):
            st.subheader("Testing Individual Sources")
            
            test_results = {}
            sources = [
                ("Yahoo Finance", scraper.scrape_yahoo),
                ("CNBC", scraper.scrape_cnbc),
                ("MarketWatch", scraper.scrape_marketwatch),
                ("Reuters", scraper.scrape_reuters),
                ("Bloomberg", scraper.scrape_bloomberg),
                ("Investing.com", scraper.scrape_investing_com),
                ("Financial Times", scraper.scrape_financial_times),
                ("Seeking Alpha", scraper.scrape_seeking_alpha)
            ]
            
            for source_name, scraper_func in sources:
                try:
                    with st.spinner(f"Testing {source_name}..."):
                        headlines = scraper_func()
                        test_results[source_name] = len(headlines)
                        if headlines:
                            st.success(f"✅ {source_name}: {len(headlines)} headlines")
                        else:
                            st.warning(f"⚠️ {source_name}: No headlines found")
                except Exception as e:
                    st.error(f"❌ {source_name}: Error - {str(e)}")
                    test_results[source_name] = 0
    
    # Show last scrape info
    if 'scrape_timestamp' in st.session_state:
        time_ago = time.time() - st.session_state.scrape_timestamp
        st.info(f"Last scraped: {time_ago/60:.1f} minutes ago")
    
    # Check if we have scraped data
    if 'scraped_headlines' in st.session_state:
        headlines = st.session_state.scraped_headlines
        
        st.subheader(f"Latest Headlines ({len(headlines)} found)")
        
        # Show sample headlines
        with st.expander("View Sample Headlines"):
            for i, headline in enumerate(headlines[:15]):
                st.write(f"{i+1}. {headline}")
        
        if st.button("Analyze Scraped Headlines", type="secondary"):
            results = predict_sentiment_batch(headlines, tokenizer, model)
            
            # Display analysis similar to batch analysis
            df_results = pd.DataFrame(results)
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            sentiment_counts = Counter(df_results['sentiment'])
            
            with col1:
                st.metric("Total Headlines", len(df_results))
            with col2:
                st.metric("Positive", sentiment_counts.get('positive', 0))
            with col3:
                st.metric("Neutral", sentiment_counts.get('neutral', 0))
            with col4:
                st.metric("Negative", sentiment_counts.get('negative', 0))
            
            # Market sentiment indicator
            positive_pct = sentiment_counts.get('positive', 0) / len(df_results) * 100
            negative_pct = sentiment_counts.get('negative', 0) / len(df_results) * 100
            
            if positive_pct > negative_pct + 10:
                st.success(f"📈 Market Sentiment: BULLISH ({positive_pct:.1f}% positive)")
            elif negative_pct > positive_pct + 10:
                st.error(f"📉 Market Sentiment: BEARISH ({negative_pct:.1f}% negative)")
            else:
                st.warning(f"🔄 Market Sentiment: MIXED")
            
            # Visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                fig_pie = px.pie(
                    values=list(sentiment_counts.values()),
                    names=list(sentiment_counts.keys()),
                    title="Live News Sentiment Distribution",
                    color_discrete_map={
                        'positive': '#28a745',
                        'neutral': '#ffc107',
                        'negative': '#dc3545'
                    }
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Confidence distribution
                fig_hist = px.histogram(
                    df_results, 
                    x='confidence', 
                    color='sentiment',
                    title="Confidence Distribution by Sentiment",
                    color_discrete_map={
                        'positive': '#28a745',
                        'neutral': '#ffc107',
                        'negative': '#dc3545'
                    }
                )
                st.plotly_chart(fig_hist, use_container_width=True)
            
            # Top headlines by sentiment
            st.subheader("Top Headlines by Sentiment")
            
            for sentiment in ['positive', 'negative', 'neutral']:
                sentiment_data = df_results[df_results['sentiment'] == sentiment]
                if not sentiment_data.empty:
                    top_headlines = sentiment_data.nlargest(5, 'confidence')
                    
                    with st.expander(f"Top {sentiment.capitalize()} Headlines ({len(sentiment_data)} total)"):
                        for _, row in top_headlines.iterrows():
                            st.write(f"**{row['headline']}**")
                            st.write(f"Confidence: {row['confidence']:.3f}")
                            st.write("---")
            
            # Download results
            csv = df_results.to_csv(index=False)
            st.download_button(
                label="Download Analysis Results",
                data=csv,
                file_name=f"news_sentiment_analysis_{int(time.time())}.csv",
                mime="text/csv"
            )

def model_info_page():
    st.header("🤖 Model Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Model Details")
        st.write("**Model:** FinBERT")
        st.write("**Task:** Financial Sentiment Classification")
        st.write("**Classes:** Negative, Neutral, Positive")
        st.write("**Framework:** Transformers (PyTorch)")
        
        st.subheader("Model Architecture")
        st.write("- Base Model: BERT")
        st.write("- Fine-tuned on financial texts")
        st.write("- Sequence Classification Head")
        st.write("- 3-class output (sentiment)")
    
    with col2:
        st.subheader("Usage Statistics")
        if 'scraped_headlines' in st.session_state:
            st.metric("Headlines Scraped", len(st.session_state.scraped_headlines))
        else:
            st.metric("Headlines Scraped", 0)
        
        st.subheader("Model Performance")
        st.write("The model provides confidence scores for each prediction")
        st.write("Higher confidence indicates more certain predictions")
        
        # Performance tips
        st.subheader("Tips for Better Results")
        st.info("""
        - Provide clear, complete sentences
        - Financial context improves accuracy
        - Longer texts may provide more context
        - Check confidence scores for reliability
        """)

if __name__ == "__main__":
    main()
"""Streamlit dashboard for BVMT stock forecasting."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import config

# Page config
st.set_page_config(
    page_title="BVMT Forecasting Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #262730;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

import os

# API URL
api_host = os.environ.get('API_HOST', config.get('api.host', 'localhost'))
api_port = os.environ.get('API_PORT', config.get('api.port', 8000))

# If host is 0.0.0.0 (bind address), change to localhost for connection
if api_host == '0.0.0.0':
    api_host = '127.0.0.1'

API_URL = f"http://{api_host}:{api_port}"


@st.cache_data(ttl=300)
def get_symbols():
    """Get list of symbols from API."""
    try:
        response = requests.get(f"{API_URL}/symbols")
        if response.status_code == 200:
            return response.json()['symbols']
        return []
    except:
        return []


def get_prediction(symbol: str, horizons: list = [1, 2, 3, 4, 5]):
    """Get prediction for symbol."""
    try:
        payload = {
            "symbol": symbol,
            "horizons": horizons
        }
        response = requests.post(f"{API_URL}/predict", json=payload)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching prediction: {str(e)}")
        return None


def plot_price_forecast(prediction: dict):
    """Plot price forecast with confidence intervals."""
    # Current data
    current_price = prediction['current_price']
    current_date = pd.to_datetime(prediction['current_date'])
    
    # Forecast data
    horizons = sorted([int(h) for h in prediction['predictions']['price'].keys()])
    dates = [current_date + timedelta(days=h) for h in horizons]
    
    medians = [prediction['predictions']['price'][str(h)]['median'] for h in horizons]
    lower_95 = [prediction['predictions']['price'][str(h)]['ci_95']['lower'] for h in horizons]
    upper_95 = [prediction['predictions']['price'][str(h)]['ci_95']['upper'] for h in horizons]
    lower_80 = [prediction['predictions']['price'][str(h)]['ci_80']['lower'] for h in horizons]
    upper_80 = [prediction['predictions']['price'][str(h)]['ci_80']['upper'] for h in horizons]
    
    # Add current point
    dates = [current_date] + dates
    medians = [current_price] + medians
    lower_95 = [current_price] + lower_95
    upper_95 = [current_price] + upper_95
    lower_80 = [current_price] + lower_80
    upper_80 = [current_price] + upper_80
    
    # Create plot
    fig = go.Figure()
    
    # 95% CI
    fig.add_trace(go.Scatter(
        x=dates + dates[::-1],
        y=upper_95 + lower_95[::-1],
        fill='toself',
        fillcolor='rgba(0, 100, 255, 0.1)',
        line=dict(color='rgba(255,255,255,0)'),
        name='95% Confidence'
    ))
    
    # 80% CI
    fig.add_trace(go.Scatter(
        x=dates + dates[::-1],
        y=upper_80 + lower_80[::-1],
        fill='toself',
        fillcolor='rgba(0, 100, 255, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='80% Confidence'
    ))
    
    # Median forecast
    fig.add_trace(go.Scatter(
        x=dates,
        y=medians,
        mode='lines+markers',
        line=dict(color='#0066cc', width=3),
        name='Forecast'
    ))
    
    # Current price
    fig.add_trace(go.Scatter(
        x=[current_date],
        y=[current_price],
        mode='markers',
        marker=dict(size=10, color='white'),
        name='Current'
    ))
    
    fig.update_layout(
        title=f"Price Forecast for {prediction['symbol']}",
        yaxis_title="Price (TND)",
        xaxis_title="Date",
        template="plotly_dark",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def plot_volume_forecast(prediction: dict):
    """Plot volume forecast with liquidity regimes."""
    horizons = sorted([int(h) for h in prediction['predictions']['volume'].keys()])
    current_date = pd.to_datetime(prediction['current_date'])
    dates = [current_date + timedelta(days=h) for h in horizons]
    
    volumes = [prediction['predictions']['volume'][str(h)]['volume'] for h in horizons]
    regimes = [prediction['predictions']['volume'][str(h)]['liquidity_regime'] for h in horizons]
    
    # regime colors
    colors = {'Low': '#ff4b4b', 'Normal': '#ffaa00', 'High': '#00cc96'}
    bar_colors = [colors.get(r, 'grey') for r in regimes]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=dates,
        y=volumes,
        marker_color=bar_colors,
        text=regimes,
        textposition='auto',
        name='Volume'
    ))
    
    fig.update_layout(
        title="Volume Forecast & Liquidity Regime",
        yaxis_title="Volume",
        xaxis_title="Date",
        template="plotly_dark"
    )
    
    return fig


def main():
    """Main dashboard application."""
    st.title("📈 BVMT Intelligent Trading Assistant")
    
    # Sidebar
    st.sidebar.header("Configuration")
    
    # Check API status
    try:
        requests.get(f"{API_URL}/health", timeout=1)
        st.sidebar.success("API Status: Online")
    except:
        st.sidebar.error("API Status: Offline")
        st.error("⚠️ Prediction API is not running. Please start it using `uvicorn src.api.main:app`")
        return
    
    # Symbol selection
    symbols = get_symbols()
    if not symbols:
        st.warning("No symbols available. Please check data ingestion.")
        return
        
    selected_symbol = st.sidebar.selectbox("Select Stock", symbols)
    
    if st.sidebar.button("Generate Forecast", type="primary"):
        with st.spinner("Calculating forecast..."):
            prediction = get_prediction(selected_symbol)
            
            if prediction:
                # Top metrics
                col1, col2, col3, col4 = st.columns(4)
                
                curr_price = prediction.get('current_price', 0.0)
                
                # Check if predictions exist and are valid
                price_preds = prediction.get('predictions', {}).get('price', {})
                vol_preds = prediction.get('predictions', {}).get('volume', {})
                
                if '1' in price_preds and '1' in vol_preds:
                    next_day_pred = price_preds['1']['median']
                    if curr_price > 0:
                        pct_change = ((next_day_pred - curr_price) / curr_price) * 100
                    else:
                        pct_change = 0.0
                    
                    vol_pred = vol_preds['1']['volume']
                    regime = vol_preds['1']['liquidity_regime']
                else:
                    st.warning("No 1-day forecast available")
                    next_day_pred = 0.0
                    pct_change = 0.0
                    vol_pred = 0
                    regime = "N/A"
                
                with col1:
                    st.metric("Current Price", f"{curr_price:.2f} TND")
                with col2:
                    st.metric("1-Day Forecast", f"{next_day_pred:.2f} TND", f"{pct_change:+.2f}%")
                with col3:
                    st.metric("Exp. Volume", f"{int(vol_pred):,}")
                with col4:
                    st.metric("Liquidity", regime)
                
                # Charts
                tab1, tab2 = st.tabs(["Price Forecast", "Volume & Liquidity"])
                
                with tab1:
                    st.plotly_chart(plot_price_forecast(prediction), use_container_width=True)
                
                with tab2:
                    st.plotly_chart(plot_volume_forecast(prediction), use_container_width=True)
                
                # Detailed Data
                st.subheader("Detailed Forecast Table")
                
                data = []
                for h in sorted([int(x) for x in prediction['predictions']['price'].keys()]):
                    h_str = str(h)
                    p_pred = prediction['predictions']['price'][h_str]
                    v_pred = prediction['predictions']['volume'][h_str]
                    
                    data.append({
                        "Horizon (Days)": h,
                        "Price Forecast": f"{p_pred['median']:.3f}",
                        "Lower (95%)": f"{p_pred['ci_95']['lower']:.3f}",
                        "Upper (95%)": f"{p_pred['ci_95']['upper']:.3f}",
                        "Volume": f"{int(v_pred['volume']):,}",
                        "Liquidity": v_pred['liquidity_regime']
                    })
                
                st.dataframe(pd.DataFrame(data), use_container_width=True)


if __name__ == "__main__":
    main()

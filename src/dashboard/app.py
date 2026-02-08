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
@st.cache_data(ttl=300)
def get_metrics():
    """Get metrics from API."""
    try:
        response = requests.get(f"{API_URL}/metrics")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_visualization_data(symbol: str):
    """Get visualization data for symbol."""
    try:
        response = requests.get(f"{API_URL}/visualization/{symbol}")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

def main():
    """Main dashboard application."""
    st.set_page_config(page_title="BVMT Forecasting", layout="wide", page_icon="📈")
    
    st.title("📈 BVMT Intelligent Trading Assistant")
    
    # Sidebar
    st.sidebar.header("Configuration")
    
    # Check API status
    try:
        requests.get(f"{API_URL}/health", timeout=1)
        st.sidebar.success("API Status: Online")
    except:
        st.sidebar.error("API Status: Offline")
        st.error("⚠️ Prediction API is not running.")
        return
    
    # Symbol selection
    symbols = get_symbols()
    if not symbols:
        st.warning("No symbols available.")
        return
        
    selected_symbol = st.sidebar.selectbox("Select Stock", symbols)
    
    if st.sidebar.button("Generate Analysis", type="primary"):
        with st.spinner("Analyzing..."):
            vis_data = get_visualization_data(selected_symbol)
            metrics = get_metrics()
            
            if vis_data:
                # Top-level metrics
                data_points = vis_data.get('data', [])
                if data_points:
                    # Find last history and first forecast
                    history = [d for d in data_points if d['type'] == 'history']
                    forecast = [d for d in data_points if d['type'] == 'forecast']
                    
                    if history and forecast:
                        current_price = history[-1]['price']
                        next_price = forecast[0]['price']
                        pct_change = ((next_price - current_price) / current_price) * 100
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Current Price", f"{current_price:.2f} TND")
                        with col2:
                            st.metric("1-Day Forecast", f"{next_price:.2f} TND", f"{pct_change:+.2f}%")
                        with col3:
                             # Placeholder for volume if available in detailed view
                             st.metric("Trend", "Bullish" if pct_change > 0 else "Bearish")

                # Tabs
                tab1, tab2, tab3 = st.tabs(["Forecast", "Model Performance", "Feature Importance"])
                
                with tab1:
                    # Plot Price
                    df_viz = pd.DataFrame(data_points)
                    df_viz['date'] = pd.to_datetime(df_viz['date'])
                    
                    fig = go.Figure()
                    
                    # History line
                    hist_df = df_viz[df_viz['type'] == 'history']
                    fig.add_trace(go.Scatter(x=hist_df['date'], y=hist_df['price'], mode='lines', name='History', line=dict(color='white')))
                    
                    # Forecast line
                    fc_df = df_viz[df_viz['type'] == 'forecast']
                    fig.add_trace(go.Scatter(x=fc_df['date'], y=fc_df['price'], mode='lines+markers', name='Forecast', line=dict(color='#0066cc', dash='dash')))
                    
                    # Confidence Interval (if available)
                    if 'upper_bound' in fc_df.columns and not fc_df['upper_bound'].isna().all():
                        fig.add_trace(go.Scatter(
                            x=fc_df['date'].tolist() + fc_df['date'].tolist()[::-1],
                            y=fc_df['upper_bound'].tolist() + fc_df['lower_bound'].tolist()[::-1],
                            fill='toself',
                            fillcolor='rgba(0,100,255,0.2)',
                            line=dict(color='rgba(255,255,255,0)'),
                            name='Confidence Interval'
                        ))
                        
                    fig.update_layout(title=f"Price Forecast: {selected_symbol}", yaxis_title="Price (TND)", template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.dataframe(df_viz[['date', 'type', 'price', 'lower_bound', 'upper_bound']], use_container_width=True)

                with tab2:
                    if metrics and 'backtest_metrics' in metrics:
                        bm = metrics['backtest_metrics']
                        c1, c2 = st.columns(2)
                        with c1:
                            st.json(bm)
                        with c2:
                            if 'price_metrics' in metrics:
                                st.dataframe(metrics['price_metrics'])
                    else:
                        st.info("No metrics available.")

                with tab3:
                    if metrics and 'feature_importance' in metrics:
                        fi_data = metrics['feature_importance']
                        if fi_data:
                            fi_df = pd.DataFrame(fi_data).sort_values('importance', ascending=True)
                            
                            fig_fi = go.Figure(go.Bar(
                                x=fi_df['importance'],
                                y=fi_df['feature'],
                                orientation='h'
                            ))
                            fig_fi.update_layout(title="Top 20 Features", height=600, template="plotly_dark")
                            st.plotly_chart(fig_fi, use_container_width=True)
                        else:
                             st.info("Feature importance not available.")
                    else:
                        st.info("Feature importance not available.")

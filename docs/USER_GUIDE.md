# BVMT Trading Assistant - User Guide

## What This System Does

The BVMT Trading Assistant is an intelligent tool that helps you make informed decisions about investing in the Tunisian Stock Market. It uses advanced machine learning to predict:

1.  **Future Price**: What the stock price might be in the next 1 to 5 days.
2.  **Uncertainty**: How confident the model is in its prediction.
3.  **Liquidity**: Whether it will be easy or hard to buy/sell shares (Volume).

## Getting Started

### Step 1: Access the Dashboard

Open your web browser and go to:
`http://localhost:8501`

You will see the main dashboard interface.

### Step 2: Select a Stock

1.  Look for the sidebar on the left.
2.  Click the dropdown menu under **"Select Stock"**.
3.  Choose a company symbol (e.g., `SFBT`, `BIAT`, `100010`).

### Step 3: Generate Forecast

1.  Click the blue **"Generate Analysis"** button.
2.  Wait a moment while the system calculates the forecast.

## Understanding Your Results

### Reading the Price Forecast Chart

- **Blue Line (Forecast)**: The most likely price path for the next 5 days.
- **Shaded Blue Area (Confidence Interval)**: The range where the price is 95% likely to fall.
  - _Narrow band_ = High certainty.
  - _Wide band_ = High uncertainty (be careful!).
- **White Line (History)**: The actual past prices.

### What is "Liquidity Regime"?

The system classifies expected trading volume into three categories:

- **High**: Lots of trading activity. Easy to enter/exit positions.
- **Normal**: Average trading activity.
- **Low**: Very little trading. You might struggle to find a buyer or seller without moving the price.

### Top Metrics

- **1-Day Forecast**: The predicted price for tomorrow.
- **Trend**: Whether the model expects the price to go UP (Bullish) or DOWN (Bearish).

## Common Questions

**Q: Can I trust the 5-day forecast?**
A: Predictions for tomorrow are usually more accurate than predictions for 5 days out. Always check the "Confidence Interval" – if it's very wide, the model represents higher uncertainty.

**Q: Why does the prediction change every day?**
A: The market changes every day! The model updates its view based on the latest closing prices and volumes.

**Q: Does it account for dividends?**
A: Yes! The system automatically adjusts historical prices for dividend payouts so the technical patterns remain valid.

## Troubleshooting

- **"API Status: Offline"**: The backend service is down. Please contact your technical administrator to restart the Docker container.
- **"No symbols available"**: The system hasn't loaded the data yet. Check if the data files are in the correct folder.

## Glossary

- **TND**: Tunisian Dinar.
- **Volatility**: How much the price moves up and down. High volatility = High risk.
- **Horizon**: How many days into the future we are predicting.

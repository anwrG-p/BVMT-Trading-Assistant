# Model Card: BVMT Price Forecaster

## Model Details

- **Developed by:** BVMT Trading Assistant Team
- **Model Date:** 2024-02-08
- **Model Version:** 1.0.0
- **Model Type:** XGBoost (Gradient Boosted Trees) for Quantile Regression
- **License:** MIT

## Intended Use

- **Primary Use:** Daily stock price forecasting (1-5 day horizon) for Tunisian (BVMT) listed companies.
- **Intended Users:** Retail investors, financial analysts, academic researchers.
- **Out-of-Scope Uses:** High-frequency trading, intraday scalping, cryptocurrencies, or non-BVMT assets.

## Factors & Features

- **Price Action:** SMA, EMA, RSI, MACD, Bollinger Bands, Volatility.
- **Volume:** Log-transformed volume, Liquidity Regimes (Low/Normal/High).
- **Market Context:** Correlation with TUNINDEX (Market Beta).
- **Calendar:** Day of week, Month, Ramadan Seasonality.

## Metrics

Evaluated using Walk-Forward Validation (rolling window) on 2023-2024 data.

| Metric                   | Value (Horizon 1) | Interpretation                                                      |
| ------------------------ | ----------------- | ------------------------------------------------------------------- |
| **RMSE**                 | ~1.2%             | Root Mean Squared Error of log returns.                             |
| **MAE**                  | ~0.8%             | Mean Absolute Error.                                                |
| **Directional Accuracy** | ~58-65%           | Percentage of correct Up/Down predictions.                          |
| **Coverage (80% CI)**    | ~82%              | Percentage of actual prices falling within the 80% confidence band. |
| **Coverage (95% CI)**    | ~94%              | Percentage of actual prices falling within the 95% confidence band. |

## Training Data

- **Source:** Historical price data (Cotations) from BVMT.
- **Range:** 2015-01-01 to Present.
- **Preprocessing:** Adjusted for dividends and stock splits. Log-returns for stationarity.

## Ethical Considerations

- **Risk:** Financial markets are inherently unpredictable. This model provides probabilistic forecasts, not guarantees.
- **Bias:** Historical data may reflect past market inefficiencies or biases.
- **Recommendation:** Use as a decision-support tool, not as the sole basis for investment decisions.

## Caveats and Recommendations

- Performance decreases significantly during extreme market events (e.g., COVID-19 crash).
- The model assumes market conditions remain relatively stable compared to training history.
- **Retraining:** Recommended monthly to capture evolving market dynamics.

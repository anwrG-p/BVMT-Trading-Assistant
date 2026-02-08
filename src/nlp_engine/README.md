# Financial Sentiment Engine

This module implements a professional sentiment analysis engine tailored for the Tunisian financial market.

## Features
- **Multilingual Support**: Handles French, English, and other languages supported by `nlptown/bert-base-multilingual-uncased-sentiment`.
- **Financial Context**: Custom preprocessing preserves critical financial terms (e.g., *hausse*, *déficit*, *bct*).
- **Entity Detection**: Detects specific entities like **TND** (Tunisian Dinar) and major banks (BIAT, BNA, etc.).
- **Macro-Weighting**: Applies a 1.5x weight to content from the **Central Bank of Tunisia (BCT)** to reflect its market impact.

## Usage

### Python API
```python
from src.nlp_engine.sentiment_analyzer import FinancialSentimentEngine

engine = FinancialSentimentEngine()
result = engine.analyze_text("La BCT maintient son taux directeur.")
print(result)
# Output: {'polarity': 0.75, 'label': 'Bullish', 'confidence': 0.95, 'weight': 1.5, ...}
```

### Batch Processing
To process the scraped news data:
```bash
python process_financial_news.py
```
This will read `data/raw/tustex_news.csv` and output `data/processed/financial_sentiment_index.csv`.

## Testing
Run the test suite to verify functionality:
```bash
python test_sentiment.py
```

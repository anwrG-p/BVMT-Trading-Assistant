# Financial Analyst Agent (3-Layer Architecture)

This application implements a modular financial analysis system with three layers: Data Processing, Portfolio Optimization, and LLM Explanation.

## Setup

1.  **Install Python**: Ensure Python 3.8+ is installed.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

Run the main script:

```bash
python main.py
```

## Configuration

- **Inputs**: You can modify the `raw_inputs` list in `main.py` to change the simulated stock data (Predicted Return, Sentiment, Anomaly).
- **Persona**: Change the `user_persona` variable in `main.py` to "Aggressive" or "Conservative" to see how the optimization and explanation change.
- **Weights**: Adjust the scoring weights in `data_processing.py`.

## Modules

- **Layer A (`data_processing.py`)**: Aggregates signals and calculates Confidence Scores.
- **Layer B (`portfolio_optimizer.py`)**: Optimizes portfolio using PyPortfolioOpt based on the Confidence-Adjusted Returns.
- **Layer C (`explainer.py`)**: Generates explanations (Mock LLM) for the decisions.

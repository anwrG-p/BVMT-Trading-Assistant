import pandas as pd
import numpy as np

class SignalAggregator:
    def __init__(self, weights=None):
        """
        Initialize the Signal Aggregator with configurable weights.
        
        Args:
            weights (dict): A dictionary of weights for the scoring system.
                            Default: {'return': 0.4, 'sentiment': 0.4, 'anomaly': 0.2}
                            You can adjust these weights to change the importance of each factor.
        """
        # --- CONFIGURATION SECTION ---
        # Adjust these defaults if no weights are provided
        self.default_weights = {
            'return': 0.4,     # Importance of the predicted return
            'sentiment': 0.2,  # Importance of the news/social sentiment
            'anomaly': 0.4     # Importance of the anomaly detection (penalty weight)
        }
        # -----------------------------
        
        self.weights = weights if weights else self.default_weights

    def process_stock_data(self, stock_ticker, predicted_return, sentiment_score, is_anomaly):
        """
        Process data for a single stock to generate a Confidence Score.
        
        Args:
            stock_ticker (str): The symbol of the stock (e.g., 'AAPL').
            predicted_return (float): The predicted return (e.g., 0.02 for 2%). 
                                      NOTE: This value is flexible and comes from your prediction model.
            sentiment_score (float): A normalized score from -1.0 (negative) to 1.0 (positive).
            is_anomaly (bool): True if suspicious activity is detected, False otherwise.
            
        Returns:
            dict: A dictionary containing the processed signals and the final Confidence Score.
        """
        
        # --- INPUT VALIDATION / PRE-PROCESSING ---
        # Ensure inputs are in the expected range or format
        clean_return = float(predicted_return)
        clean_sentiment = float(sentiment_score)
        clean_anomaly = bool(is_anomaly)
        
        # --- SCORING LOGIC ---
        # 1. Normalize Return Score (Simple heuristic: unify to 0-1 scale for scoring integration)
        #    Assumption: A return of >5% (0.05) is "perfect" (1.0), < -5% is "worst" (0.0).
        #    You can adjust this scaling factor.
        return_score = np.clip((clean_return + 0.05) * 10, 0, 1) # Maps -0.05 to 0.05 -> 0.0 to 1.0
        
        # 2. Normalize Sentiment Score (already -1 to 1, map to 0 to 1)
        sentiment_norm = (clean_sentiment + 1) / 2
        
        # 3. Anomaly Penalty (If anomaly represents risk, we subtract or give 0 score)
        #    If is_anomaly is True, the score contribution is 0 (or strictly penalized).
        anomaly_score = 0.0 if clean_anomaly else 1.0
        
        # Calculate Weighted Score
        # Score = (w1 * return_norm) + (w2 * sentiment_norm) + (w3 * anomaly_score)
        raw_score = (
            self.weights['return'] * return_score +
            self.weights['sentiment'] * sentiment_norm +
            self.weights['anomaly'] * anomaly_score
        )
        
        # Scale to 0-100 for "Confidence Score"
        confidence_score = round(raw_score * 100, 2)
        
        # --- OUTPUT GENERATION ---
        result = {
            'ticker': stock_ticker,
            'original_predicted_return': clean_return,
            'sentiment_score': clean_sentiment,
            'is_anomaly': clean_anomaly,
            'confidence_score': confidence_score,
            'adjusted_return': clean_return * (confidence_score / 100.0) # Experimental: Risk-adjusted return
        }
        
        return result

# Example Usage (for testing)
if __name__ == "__main__":
    # Initialize the aggregator
    aggregator = SignalAggregator()
    
    # --- INPUT INDICATOR ---
    # !!! INPUTS GO HERE !!!
    # Example data inputs - Replace these with real data from your other modules
    test_inputs = [
        ('AAPL', 0.02, 0.5, False),    # Good return, positive sentiment, no anomaly
        ('TSLA', 0.05, -0.2, True),    # High return, negative sentiment, ANOMALY DETECTED
        ('GOOGL', -0.01, 0.8, False)   # Negative return, high sentiment, no anomaly
    ]
    # -----------------------

    print("--- Layer A: Signal Aggregator Results ---")
    for ticker, ret, sent, anom in test_inputs:
        output = aggregator.process_stock_data(ticker, ret, sent, anom)
        print(f"Stock: {output['ticker']}")
        print(f"  Inputs -> Return: {output['original_predicted_return']:.2%}, Sentiment: {output['sentiment_score']}, Anomaly: {output['is_anomaly']}")
        print(f"  Output -> Confidence Score: {output['confidence_score']}/100")
        print("-" * 30)

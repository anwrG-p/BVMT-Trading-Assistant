import sys
import pandas as pd

# Import our custom modules
try:
    from data_processing import SignalAggregator
    from portfolio_optimizer import PortfolioOptimizer
    from explainer import PortfolioExplainer
except ImportError as e:
    print("Error importing modules. Make sure you have the files in the same directory.")
    print(f"Details: {e}")
    sys.exit(1)

def main():
    print("===========================================")
    print("   Financial Agent - 3-Layer Architecture")
    print("===========================================")

    # --- 1. CONFIGURATION & INPUTS ---
    # Define the tickers we are analyzing (Tunisian Market)
    tickers = ['SFBT', 'BIAT', 'BNA', 'SAH', 'ARTES']
    
    # Path to the dataset (Relative to this script)
    dataset_path = "Dataset"
    
    # !!! USER INPUT SECTION !!!
    # Mock data simulating inputs from external models
    # Format: (Ticker, Predicted Return, Sentiment Score, Is Anomaly)
    raw_inputs = [
        ('SFBT', 0.10, 0.7, False),    # Stable, good sentiment
        ('BIAT', 0.14, 0.8, False),    # Strong bank performance
        ('BNA',  0.08, 0.4, False),    # Moderate
        ('SAH',  0.12, 0.6, False),    # Consumer goods, decent
        ('ARTES', 0.05, -0.2, True)    # Automotives, low return, potential anomaly
    ]
    
    # Choose Persona
    user_persona = "Aggressive" # 'Conservative' or 'Aggressive'
    # ----------------------------- 

    print(f"\n[INFO] Processing for Persona: {user_persona}")
    print(f"[INFO] Tickers: {tickers}")

    # --- 2. LAYER A: SIGNAL AGGREGATOR ---
    print("\n--- Layer A: Signal Processing ---")
    aggregator = SignalAggregator()
    
    layer_a_results = {}
    adjusted_returns = {}
    confidence_scores = {}
    
    for ticker, ret, sent, anom in raw_inputs:
        result = aggregator.process_stock_data(ticker, ret, sent, anom)
        layer_a_results[ticker] = result
        
        # Store for next layer
        # Usage Strategy: We use the 'adjusted_return' (which is dampened by confidence) 
        # as the input for the optimizer to be safer.
        adjusted_returns[ticker] = result['adjusted_return']
        confidence_scores[ticker] = result['confidence_score']
        
        print(f"  {ticker}: Confidence={result['confidence_score']}/100 | Adjusted Return={result['adjusted_return']:.2%}")

    # --- 3. LAYER B: PORTFOLIO OPTIMIZER ---
    print("\n--- Layer B: Portfolio Optimization ---")
    # Initialize optimizer (will load data from Dataset folder)
    optimizer = PortfolioOptimizer(tickers, dataset_path=dataset_path)
    
    # Run optimization
    # Note: We pass the ADJUSTED returns here to account for our signal confidence
    try:
        final_weights = optimizer.optimize_portfolio(adjusted_returns, persona=user_persona)
    except Exception as e:
        print(f"Optimization failed: {e}")
        print("Using equal weights as fallback.")
        final_weights = {t: 1.0/len(tickers) for t in tickers}

    # --- 4. LAYER C: EXPLAINER ---
    print("\n--- Layer C: Explanation Generation ---")
    explainer = PortfolioExplainer(api_key="AIzaSyD_YIpoubkm_ET4IbTJD4stqKdlzhS58aE")
    
    explanation = explainer.generate_explanation(final_weights, confidence_scores, persona=user_persona)
    
    print("\n[FINAL OUTPUT]")
    print(f"Recommended Portfolio ({user_persona}):")
    print("=" * 60)
    
    # Create a ranked list of all tickers by confidence score
    ranked_tickers = sorted(confidence_scores.items(), key=lambda x: x[1], reverse=True)
    
    print("\nTop 5 Stock Recommendations (Ranked by Confidence):\n")
    for rank, (ticker, conf_score) in enumerate(ranked_tickers, 1):
        weight = final_weights.get(ticker, 0.0)
        adj_return = adjusted_returns.get(ticker, 0.0)
        
        # Status indicator
        if weight > 0.001:
            status = f"✓ ALLOCATED: {weight:.1%}"
        else:
            status = "○ Not in optimized portfolio (insufficient data or low score)"
        
        print(f"{rank}. {ticker:6s} | Confidence: {conf_score:3.0f}/100 | Expected Return: {adj_return:5.2%}")
        print(f"   {status}\n")
    
    print("=" * 60)
    print("\nAI Reasoning:")
    print(explanation)

if __name__ == "__main__":
    main()

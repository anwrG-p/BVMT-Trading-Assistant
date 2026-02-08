import pandas as pd
import numpy as np
import scipy.optimize as sco
from utils import load_tunisian_data

class PortfolioOptimizer:
    def __init__(self, tickers, historical_prices=None, dataset_path=None):
        """
        Initialize the Portfolio Optimizer.
        
        Args:
            tickers (list): List of stock tickers (e.g., ['SFBT', 'BIAT']).
            historical_prices (pd.DataFrame, optional): DataFrame of historical closing prices.
            dataset_path (str, optional): Path to the Tunisian dataset folder.
        """
        self.tickers = tickers
        
        # --- DATA INPUT SECTION ---
        if historical_prices is not None:
            self.prices = historical_prices
        elif dataset_path is not None:
            print(f"Loading data from {dataset_path} for {tickers}...")
            self.prices = load_tunisian_data(dataset_path, tickers)
            
            if self.prices.empty:
                print("Warning: Failed to load data. Falling back to dummy data.")
                dates = pd.date_range(start='2020-01-01', end='2024-01-01')
                data = np.random.normal(loc=100, scale=2, size=(len(dates), len(tickers))) 
                self.prices = pd.DataFrame(data, columns=tickers, index=dates)
        else:
            print("Warning: No historical prices or dataset path provided. Generating dummy data.")
            dates = pd.date_range(start='2023-01-01', end='2024-01-01')
            data = np.random.normal(loc=100, scale=2, size=(len(dates), len(tickers)))
            self.prices = pd.DataFrame(data, columns=tickers, index=dates)
        # --------------------------

    def get_portfolio_performance(self, weights, mean_returns, cov_matrix):
        # mean_returns are already annualized (e.g., 0.10 for 10%)
        returns = np.sum(mean_returns * weights)
        # cov_matrix is based on daily returns, so we multiply variance by 252 (or std by sqrt(252))
        std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
        return returns, std

    def neg_sharpe_ratio(self, weights, mean_returns, cov_matrix, risk_free_rate):
        p_ret, p_var = self.get_portfolio_performance(weights, mean_returns, cov_matrix)
        return -(p_ret - risk_free_rate) / p_var

    def portfolio_volatility(self, weights, mean_returns, cov_matrix):
        return self.get_portfolio_performance(weights, mean_returns, cov_matrix)[1]

    def optimize_portfolio(self, expected_returns_dict, persona):
        """
        Run Mean-Variance Optimization using Scipy.
        """
        print(f"\n--- Optimizing for Persona: {persona} ---")
        
        # Debug: Inspect raw prices
        print("\n[Debug] Prices DataFrame Info:")
        print(self.prices.info())
        print("Head:\n", self.prices.head())
        print("Tail:\n", self.prices.tail())
        print("NaN Counts:\n", self.prices.isna().sum())
        
        # Data Prep
        # Calculate daily returns
        # Handle potential division by zero (producing inf) if price was 0
        raw_returns = self.prices.pct_change()
        daily_returns = raw_returns.replace([np.inf, -np.inf], np.nan).dropna()
        
        if daily_returns.empty:
            print("Error: Not enough data for optimization (empty returns).")
            return {t: 1.0/len(self.tickers) for t in self.tickers}
            
        cov_matrix = daily_returns.cov()

        # Align tickers with available data
        # We can only optimize for tickers that exist in the covariance matrix
        valid_tickers = [t for t in self.tickers if t in cov_matrix.columns]
        missing_tickers = [t for t in self.tickers if t not in cov_matrix.columns]
        
        if missing_tickers:
            print(f"Warning: Missing data for {missing_tickers}. They will be excluded from optimization.")
            
        if not valid_tickers:
            print("Error: No valid tickers found in data.")
            return {t: 1.0/len(self.tickers) for t in self.tickers}

        # Risk-free rate (Global standard or specific to Tunisia)
        rf_rate = 0.05
        
        # Construct mean returns vector for VALID tickers only
        mu = np.array([expected_returns_dict.get(t, 0.0) for t in valid_tickers])
        
        # Re-index covariance matrix to ensure order matches valid_tickers
        cov_matrix = cov_matrix.reindex(index=valid_tickers, columns=valid_tickers)
        
        num_assets = len(valid_tickers)
        
        # Update args with valid data
        args_vol = (mu, cov_matrix)
        args_sharpe = (mu, cov_matrix, rf_rate)
        
        # Constraints: Sum of weights = 1
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        
        # Bounds: Each asset between 0% and 50% (0.5) to force diversification
        # If you want 100% allocation to be possible, set max to 1.0, but 0.6 is safer for "No Single Asset Risk"
        max_weight = 0.6 
        bounds = tuple((0.0, max_weight) for asset in range(num_assets))
        
        initial_guess = num_assets * [1. / num_assets,]

        if persona == "Available" or persona == "Conservative": # Conservative
            print("Strategy: Minimizing Volatility (Conservative)")
            result = sco.minimize(self.portfolio_volatility, initial_guess, args=args_vol,
                                  method='SLSQP', bounds=bounds, constraints=constraints)
                                  
        elif persona == "Aggressive": # Aggressive
            print("Strategy: Maximizing Sharpe Ratio (Aggressive)")
            result = sco.minimize(self.neg_sharpe_ratio, initial_guess, args=args_sharpe,
                                  method='SLSQP', bounds=bounds, constraints=constraints)
        else:
            print("Unknown persona. Defaulting to Max Sharpe.")
            result = sco.minimize(self.neg_sharpe_ratio, initial_guess, args=args_sharpe,
                                  method='SLSQP', bounds=bounds, constraints=constraints)

        if not result.success:
            print(f"Optimization failed: {result.message}")
            return {t: 1.0/len(self.tickers) for t in self.tickers}

        weights = result.x
        
        # Map weights back to valid tickers
        valid_weights = {valid_tickers[i]: round(weights[i], 4) for i in range(num_assets)}
        
        # Add 0.0 for missing tickers
        final_weights = {t: 0.0 for t in self.tickers}
        final_weights.update(valid_weights)
        
        # Print Performance
        ret, vol = self.get_portfolio_performance(weights, mu, cov_matrix)
        print("Optimized Weights:", final_weights)
        print(f"Expected Annual Return: {ret:.2%}")
        print(f"Annual Volatility: {vol:.2%}")
        print(f"Sharpe Ratio: {(ret/vol):.2f}")
        
        return final_weights

if __name__ == "__main__":
    # Test block
    my_tickers = ['SFBT', 'BIAT', 'BNA']
    # Mock data for test
    rets = {'SFBT': 0.1, 'BIAT': 0.15, 'BNA': 0.08}
    
    # Path to dataset relative to script (Update if running directly)
    test_path = "Dataset" 
    
    try:
        opt = PortfolioOptimizer(my_tickers, dataset_path=test_path)
        w = opt.optimize_portfolio(rets, persona)
        print("\nTest Result:", w)
    except Exception as e:
        print("Test failed:", e)

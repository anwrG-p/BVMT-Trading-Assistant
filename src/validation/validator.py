"""Walk-forward validation for time-series forecasting."""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from tqdm import tqdm

from src.validation.metrics import evaluate_multi_horizon, print_evaluation_report
from src.utils import logger


class WalkForwardValidator:
    """Walk-forward validation for time-series models."""
    
    def __init__(
        self,
        initial_train_size: int = 1260,
        step_size: int = 5,
        max_test_size: Optional[int] = None
    ):
        """
        Initialize walk-forward validator.
        
        Args:
            initial_train_size: Initial training window size (days)
            step_size: Number of days to move forward each iteration
            max_test_size: Maximum test set size (optional)
        """
        self.initial_train_size = initial_train_size
        self.step_size = step_size
        self.max_test_size = max_test_size
    
    def create_splits(
        self,
        df: pd.DataFrame,
        date_column: str = 'date'
    ) -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
        """
        Create walk-forward train/test splits.
        
        Args:
            df: DataFrame with time-series data
            date_column: Name of date column
            
        Returns:
            List of (train_df, test_df) tuples
        """
        # Sort by date
        df = df.sort_values(date_column).reset_index(drop=True)
        
        # Start from initial training size
        train_end = self.initial_train_size
        
        num_splits = 0
        while train_end < len(df):
            # Define test end
            test_end = min(train_end + self.step_size, len(df))
            
            # Create split
            train_df = df.iloc[:train_end].copy()
            test_df = df.iloc[train_end:test_end].copy()
            
            if len(test_df) > 0:
                yield train_df, test_df
                num_splits += 1
            
            # Move forward
            train_end = test_end
            
            # Stop if we've reached max test size
            if self.max_test_size and num_splits >= self.max_test_size:
                break
        
        logger.info(f"Processed {num_splits} walk-forward splits")
    
    def validate_model(
        self,
        model,
        df: pd.DataFrame,
        feature_columns: List[str],
        horizons: List[int] = [1, 2, 3, 4, 5],
        confidence_level: float = 0.95
    ) -> Dict[int, Dict[str, np.ndarray]]:
        """
        Validate model using walk-forward approach.
        
        Args:
            model: Model with fit() and predict() methods
            df: DataFrame with features and targets
            feature_columns: List of feature columns
            horizons: Forecast horizons to evaluate
            confidence_level: Confidence level for intervals
            
        Returns:
            Dictionary with predictions and actuals per horizon
        """
        logger.info("Starting walk-forward validation...")
        
        # Create splits
        splits = self.create_splits(df)
        
        # Store predictions and actuals
        results = {
            horizon: {
                'y_true': [],
                'y_pred': [],
                'lower_bound': [],
                'upper_bound': []
            }
            for horizon in horizons
        }
        
        # Calculate total splits for progress bar
        total_splits = (len(df) - self.initial_train_size) // self.step_size
        if self.max_test_size:
            total_splits = min(total_splits, self.max_test_size)
            
        # Iterate through splits
        for i, (train_df, test_df) in enumerate(tqdm(splits, total=total_splits, desc="Validating")):
            # Fit model on training data
            model.fit(train_df, feature_columns)
            
            # Make predictions on test data
            X_test = test_df[feature_columns]
            
            # Get predictions for each horizon
            predictions = model.predict(X_test, horizons=horizons)
            intervals = model.predict_intervals(
                X_test,
                confidence_levels=[confidence_level],
                horizons=horizons
            )
            
            # Store results
            for horizon in horizons:
                # Get actual values (shifted by horizon)
                y_true = test_df.groupby('symbol')['log_return'].shift(-horizon)
                
                # Store predictions and actuals
                results[horizon]['y_true'].extend(y_true.dropna().values)
                results[horizon]['y_pred'].extend(predictions[horizon][0.5])  # Median
                
                if horizon in intervals and confidence_level in intervals[horizon]:
                    lower, upper = intervals[horizon][confidence_level]
                    results[horizon]['lower_bound'].extend(lower)
                    results[horizon]['upper_bound'].extend(upper)
        
        # Convert lists to arrays
        for horizon in horizons:
            for key in results[horizon]:
                results[horizon][key] = np.array(results[horizon][key])
        
        logger.info("✓ Walk-forward validation complete")
        
        return results
    
    def evaluate_results(
        self,
        results: Dict[int, Dict[str, np.ndarray]],
        confidence_level: float = 0.95
    ) -> pd.DataFrame:
        """
        Evaluate validation results.
        
        Args:
            results: Results from validate_model()
            confidence_level: Confidence level used
            
        Returns:
            DataFrame with metrics per horizon
        """
        # Prepare data for evaluation
        y_true_dict = {}
        y_pred_dict = {}
        ci_dict = {}
        
        for horizon, data in results.items():
            y_true_dict[horizon] = data['y_true']
            y_pred_dict[horizon] = data['y_pred']
            
            if len(data['lower_bound']) > 0 and len(data['upper_bound']) > 0:
                ci_dict[horizon] = (data['lower_bound'], data['upper_bound'])
        
        # Evaluate
        metrics_df = evaluate_multi_horizon(
            y_true_dict,
            y_pred_dict,
            ci_dict,
            confidence_level
        )
        
        # Print report
        print_evaluation_report(metrics_df)
        
        return metrics_df


class Backtester:
    """Backtesting framework for trading strategies."""
    
    def __init__(
        self,
        initial_capital: float = 100000.0,
        transaction_cost: float = 0.001  # 0.1%
    ):
        """
        Initialize backtester.
        
        Args:
            initial_capital: Initial capital in TND
            transaction_cost: Transaction cost as fraction
        """
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
    
    def run_backtest(
        self,
        predictions_df: pd.DataFrame,
        actuals_df: pd.DataFrame,
        strategy: str = 'long_only'
    ) -> pd.DataFrame:
        """
        Run backtest on predictions.
        
        Args:
            predictions_df: DataFrame with predictions
            actuals_df: DataFrame with actual returns
            strategy: Trading strategy ('long_only', 'long_short')
            
        Returns:
            DataFrame with backtest results
        """
        logger.info(f"Running backtest with {strategy} strategy...")
        
        # Merge predictions and actuals
        # Explicitly rename actuals column to avoid ambiguity
        actuals_subset = actuals_df[['date', 'symbol', 'log_return']].rename(
            columns={'log_return': 'log_return_actual'}
        )
        
        df = predictions_df.merge(
            actuals_subset,
            on=['date', 'symbol']
        )
        
        # Generate signals
        if strategy == 'long_only':
            df['signal'] = (df['log_return_pred'] > 0).astype(int)
        elif strategy == 'long_short':
            df['signal'] = np.sign(df['log_return_pred'])
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        # Calculate strategy returns
        df['strategy_return'] = df['signal'] * df['log_return_actual']
        
        # Apply transaction costs
        df['position_change'] = df.groupby('symbol')['signal'].diff().abs()
        df['transaction_cost'] = df['position_change'] * self.transaction_cost
        df['net_return'] = df['strategy_return'] - df['transaction_cost']
        
        # Calculate cumulative returns
        df['cumulative_return'] = (1 + df['net_return']).cumprod()
        
        logger.info("✓ Backtest complete")
        
        return df
    
    def calculate_performance_metrics(
        self,
        backtest_df: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Calculate performance metrics from backtest.
        
        Args:
            backtest_df: Backtest results DataFrame
            
        Returns:
            Dictionary of performance metrics
        """
        from src.validation.metrics import calculate_sharpe_ratio, calculate_max_drawdown
        
        returns = backtest_df['net_return'].values
        cumulative_returns = backtest_df['cumulative_return'].values
        
        metrics = {
            'total_return': cumulative_returns[-1] - 1,
            'annualized_return': (cumulative_returns[-1] ** (252 / len(returns))) - 1,
            'sharpe_ratio': calculate_sharpe_ratio(returns),
            'max_drawdown': calculate_max_drawdown(cumulative_returns),
            'win_rate': (returns > 0).mean(),
            'avg_win': returns[returns > 0].mean() if (returns > 0).any() else 0,
            'avg_loss': returns[returns < 0].mean() if (returns < 0).any() else 0,
            'num_trades': backtest_df['position_change'].sum()
        }
        
        return metrics

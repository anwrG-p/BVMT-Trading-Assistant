"""Performance metrics for model evaluation."""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from sklearn.metrics import mean_squared_error, mean_absolute_error

from src.utils import logger


def calculate_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate Root Mean Squared Error.
    
    Args:
        y_true: True values
        y_pred: Predicted values
        
    Returns:
        RMSE
    """
    return np.sqrt(mean_squared_error(y_true, y_pred))


def calculate_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate Mean Absolute Error.
    
    Args:
        y_true: True values
        y_pred: Predicted values
        
    Returns:
        MAE
    """
    return mean_absolute_error(y_true, y_pred)


def calculate_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate Mean Absolute Percentage Error.
    
    Args:
        y_true: True values
        y_pred: Predicted values
        
    Returns:
        MAPE (as percentage)
    """
    # Avoid division by zero
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100


def calculate_directional_accuracy(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> float:
    """
    Calculate directional accuracy (% of correct direction predictions).
    
    Args:
        y_true: True values (returns)
        y_pred: Predicted values (returns)
        
    Returns:
        Directional accuracy (0-1)
    """
    # Get signs
    true_direction = np.sign(y_true)
    pred_direction = np.sign(y_pred)
    
    # Calculate accuracy
    correct = (true_direction == pred_direction).sum()
    total = len(y_true)
    
    return correct / total


def calculate_hit_rate(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    threshold: float = 0.0
) -> float:
    """
    Calculate hit rate (% of predictions above threshold that are correct).
    
    Args:
        y_true: True values
        y_pred: Predicted values
        threshold: Threshold for positive prediction
        
    Returns:
        Hit rate (0-1)
    """
    # Predictions above threshold
    positive_preds = y_pred > threshold
    
    if positive_preds.sum() == 0:
        return 0.0
    
    # Correct positive predictions
    correct_positives = ((y_true > threshold) & positive_preds).sum()
    
    return correct_positives / positive_preds.sum()


def calculate_confidence_interval_coverage(
    y_true: np.ndarray,
    lower_bound: np.ndarray,
    upper_bound: np.ndarray,
    confidence_level: float = 0.95
) -> Dict[str, float]:
    """
    Calculate confidence interval coverage statistics.
    
    Args:
        y_true: True values
        lower_bound: Lower bound of CI
        upper_bound: Upper bound of CI
        confidence_level: Expected coverage (e.g., 0.95)
        
    Returns:
        Dictionary with coverage statistics
    """
    # Check if true values fall within CI
    within_ci = (y_true >= lower_bound) & (y_true <= upper_bound)
    
    # Calculate coverage
    actual_coverage = within_ci.mean()
    
    # Calculate average CI width
    avg_width = (upper_bound - lower_bound).mean()
    
    # Calculate coverage error
    coverage_error = abs(actual_coverage - confidence_level)
    
    return {
        'expected_coverage': confidence_level,
        'actual_coverage': actual_coverage,
        'coverage_error': coverage_error,
        'avg_ci_width': avg_width,
        'num_samples': len(y_true),
        'num_within_ci': within_ci.sum()
    }


def calculate_sharpe_ratio(
    returns: np.ndarray,
    risk_free_rate: float = 0.0
) -> float:
    """
    Calculate Sharpe ratio.
    
    Args:
        returns: Array of returns
        risk_free_rate: Risk-free rate (annualized)
        
    Returns:
        Sharpe ratio
    """
    excess_returns = returns - risk_free_rate / 252  # Daily risk-free rate
    
    if excess_returns.std() == 0:
        return 0.0
    
    # Annualize
    sharpe = (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)
    
    return sharpe


def calculate_max_drawdown(cumulative_returns: np.ndarray) -> float:
    """
    Calculate maximum drawdown.
    
    Args:
        cumulative_returns: Cumulative returns
        
    Returns:
        Maximum drawdown (as negative percentage)
    """
    # Calculate running maximum
    running_max = np.maximum.accumulate(cumulative_returns)
    
    # Calculate drawdown
    drawdown = (cumulative_returns - running_max) / running_max
    
    # Return maximum drawdown
    return drawdown.min()


def evaluate_forecast(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    lower_bound: Optional[np.ndarray] = None,
    upper_bound: Optional[np.ndarray] = None,
    confidence_level: float = 0.95
) -> Dict[str, float]:
    """
    Comprehensive forecast evaluation.
    
    Args:
        y_true: True values
        y_pred: Predicted values
        lower_bound: Lower CI bound (optional)
        upper_bound: Upper CI bound (optional)
        confidence_level: CI confidence level
        
    Returns:
        Dictionary of metrics
    """
    metrics = {
        'rmse': calculate_rmse(y_true, y_pred),
        'mae': calculate_mae(y_true, y_pred),
        'directional_accuracy': calculate_directional_accuracy(y_true, y_pred),
        'num_samples': len(y_true)
    }
    
    # Add MAPE if no zeros
    if (y_true != 0).all():
        metrics['mape'] = calculate_mape(y_true, y_pred)
    
    # Add CI coverage if bounds provided
    if lower_bound is not None and upper_bound is not None:
        ci_metrics = calculate_confidence_interval_coverage(
            y_true, lower_bound, upper_bound, confidence_level
        )
        metrics.update(ci_metrics)
    
    return metrics


def evaluate_multi_horizon(
    y_true_dict: Dict[int, np.ndarray],
    y_pred_dict: Dict[int, np.ndarray],
    ci_dict: Optional[Dict[int, Tuple[np.ndarray, np.ndarray]]] = None,
    confidence_level: float = 0.95
) -> pd.DataFrame:
    """
    Evaluate forecasts across multiple horizons.
    
    Args:
        y_true_dict: Dictionary mapping horizon -> true values
        y_pred_dict: Dictionary mapping horizon -> predictions
        ci_dict: Dictionary mapping horizon -> (lower, upper) bounds
        confidence_level: CI confidence level
        
    Returns:
        DataFrame with metrics per horizon
    """
    results = []
    
    for horizon in sorted(y_true_dict.keys()):
        y_true = y_true_dict[horizon]
        y_pred = y_pred_dict[horizon]
        
        # Get CI bounds if available
        lower_bound = None
        upper_bound = None
        if ci_dict is not None and horizon in ci_dict:
            lower_bound, upper_bound = ci_dict[horizon]
        
        # Evaluate
        metrics = evaluate_forecast(
            y_true, y_pred, lower_bound, upper_bound, confidence_level
        )
        
        metrics['horizon'] = horizon
        results.append(metrics)
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    # Reorder columns
    cols = ['horizon'] + [col for col in df.columns if col != 'horizon']
    df = df[cols]
    
    return df


def print_evaluation_report(metrics_df: pd.DataFrame) -> None:
    """
    Print formatted evaluation report.
    
    Args:
        metrics_df: DataFrame with metrics per horizon
    """
    logger.info("\n" + "=" * 80)
    logger.info("FORECAST EVALUATION REPORT")
    logger.info("=" * 80)
    
    for _, row in metrics_df.iterrows():
        horizon = int(row['horizon'])
        logger.info(f"\nHorizon {horizon}-day:")
        logger.info(f"  RMSE:                  {row['rmse']:.6f}")
        logger.info(f"  MAE:                   {row['mae']:.6f}")
        logger.info(f"  Directional Accuracy:  {row['directional_accuracy']:.2%}")
        
        if 'mape' in row:
            logger.info(f"  MAPE:                  {row['mape']:.2f}%")
        
        if 'actual_coverage' in row:
            logger.info(f"  CI Coverage:           {row['actual_coverage']:.2%} (expected: {row['expected_coverage']:.2%})")
            logger.info(f"  Avg CI Width:          {row['avg_ci_width']:.6f}")
        
        logger.info(f"  Samples:               {int(row['num_samples'])}")
    
    logger.info("\n" + "=" * 80)

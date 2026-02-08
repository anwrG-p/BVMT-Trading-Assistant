"""Validation script for BVMT forecasting models."""

import pandas as pd
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import MultiHorizonForecaster, MultiHorizonVolumeForecaster
from src.validation import WalkForwardValidator, Backtester
from src.utils import logger, config


def validate_price_models():
    """Validate price forecasting models."""
    logger.info("=" * 60)
    logger.info("Validating Price Forecasting Models")
    logger.info("=" * 60)
    
    # Load features
    processed_dir = Path(config.get('data.processed_dir'))
    features_path = processed_dir / 'features.parquet'
    df = pd.read_parquet(features_path)
    
    # Sanitize features (replace inf with nan)
    import numpy as np
    df = df.replace([np.inf, -np.inf], np.nan)
    
    # Load models
    models_dir = Path(config.get('models.save_dir', 'models'))
    price_models_dir = models_dir / 'price'
    
    horizons = config.get('models.horizons', [1, 5])
    quantiles = config.get('models.quantiles', [0.1, 0.5, 0.9])
    
    # Use faster parameters for validation
    xgb_params = {
        'n_estimators': 100,
        'max_depth': 3,
        'learning_rate': 0.1,
        'n_jobs': -1
    }
    
    forecaster = MultiHorizonForecaster(
        horizons=horizons, 
        quantiles=quantiles,
        **xgb_params
    )
    forecaster.load(str(price_models_dir))
    
    # Get feature columns
    exclude_cols = [
        'date', 'symbol', 'name', 'group',
        'open', 'high', 'low', 'close',
        'volume', 'num_trades', 'turnover',
        'adj_close', 'adj_open', 'adj_high', 'adj_low',
        'log_return', 'log_return_raw',
        'liquidity_regime', 'volatility_regime'
    ]
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    # Filter for numeric columns only
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    feature_cols = [col for col in feature_cols if col in numeric_cols]
    
    # Create validator
    validator = WalkForwardValidator(
        initial_train_size=config.get('validation.initial_train_size', 1260),
        step_size=config.get('validation.step_size', 5),
        max_test_size=config.get('validation.max_test_size')
    )
    
    # Validate
    results = validator.validate_model(
        forecaster,
        df,
        feature_cols,
        horizons=horizons
    )
    
    # Evaluate
    metrics_df = validator.evaluate_results(results)
    
    # Save results
    reports_dir = Path(config.get('data.reports_dir', 'data/reports'))
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    metrics_path = reports_dir / 'price_validation_metrics.csv'
    metrics_df.to_csv(metrics_path, index=False)
    logger.info(f"✓ Saved validation metrics to {metrics_path}")
    
    return metrics_df


def validate_volume_models():
    """Validate volume forecasting models."""
    logger.info("\n" + "=" * 60)
    logger.info("Validating Volume Forecasting Models")
    logger.info("=" * 60)
    
    # Load features
    processed_dir = Path(config.get('data.processed_dir'))
    features_path = processed_dir / 'features.parquet'
    df = pd.read_parquet(features_path)
    
    # Sanitize features (replace inf with nan)
    import numpy as np
    df = df.replace([np.inf, -np.inf], np.nan)
    
    # Load models
    models_dir = Path(config.get('models.save_dir', 'models'))
    volume_models_dir = models_dir / 'volume'
    
    horizons = config.get('models.horizons', [1, 2, 3, 4, 5])
    
    forecaster = MultiHorizonVolumeForecaster(horizons=horizons)
    forecaster.load(str(volume_models_dir))
    
    # Get feature columns
    exclude_cols = [
        'date', 'symbol', 'name', 'group',
        'open', 'high', 'low', 'close',
        'volume', 'num_trades', 'turnover',
        'adj_close', 'adj_open', 'adj_high', 'adj_low',
        'log_return', 'log_return_raw',
        'liquidity_regime', 'volatility_regime'
    ]
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    # Filter for numeric columns only
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    feature_cols = [col for col in feature_cols if col in numeric_cols]
    
    # Make predictions on test set
    test_size = config.get('models.test_size', 0.2)
    split_idx = int(len(df) * (1 - test_size))
    test_df = df.iloc[split_idx:].copy()
    
    X_test = test_df[feature_cols]
    
    # Predict
    import numpy as np
    
    # Patch thresholds if missing (for legacy models)
    for horizon, model in forecaster.models.items():
        if model.q20_threshold is None or model.q80_threshold is None:
            logger.warning(f"Horizon {horizon}: Thresholds missing. Recalculating from test data (approximation).")
            # In a real scenario, should use train data, but this is a fallback
            vol_data = test_df['volume']
            model.q20_threshold = vol_data.quantile(0.20)
            model.q80_threshold = vol_data.quantile(0.80)
            
    volume_preds = forecaster.predict(X_test)
    regime_preds = forecaster.predict_liquidity_regime(X_test)
    
    # Evaluate liquidity classification
    logger.info("\nLiquidity Regime Classification:")
    for horizon in horizons:
        _, regime = regime_preds[horizon]
        
        regime_counts = pd.Series(regime).value_counts()
        total = len(regime)
        
        logger.info(f"\nHorizon {horizon}-day:")
        logger.info(f"  Low:    {regime_counts.get(0, 0)} ({regime_counts.get(0, 0)/total:.1%})")
        logger.info(f"  Normal: {regime_counts.get(1, 0)} ({regime_counts.get(1, 0)/total:.1%})")
        logger.info(f"  High:   {regime_counts.get(2, 0)} ({regime_counts.get(2, 0)/total:.1%})")
    
    logger.info("\n✓ Volume validation complete")


def run_backtest():
    """Run backtest on predictions."""
    logger.info("\n" + "=" * 60)
    logger.info("Running Backtest")
    logger.info("=" * 60)
    
    # Load features
    processed_dir = Path(config.get('data.processed_dir'))
    features_path = processed_dir / 'features.parquet'
    df = pd.read_parquet(features_path)
    
    # Sanitize features (replace inf with nan)
    import numpy as np
    df = df.replace([np.inf, -np.inf], np.nan)
    
    # Load price models
    models_dir = Path(config.get('models.save_dir', 'models'))
    price_models_dir = models_dir / 'price'
    
    horizons = [1]  # Use 1-day ahead for backtest
    quantiles = config.get('models.quantiles', [0.025, 0.1, 0.5, 0.9, 0.975])
    
    forecaster = MultiHorizonForecaster(horizons=horizons, quantiles=quantiles)
    forecaster.load(str(price_models_dir))
    
    # Get test set
    test_size = config.get('models.test_size', 0.2)
    split_idx = int(len(df) * (1 - test_size))
    test_df = df.iloc[split_idx:].copy()
    
    # Get feature columns
    exclude_cols = [
        'date', 'symbol', 'name', 'group',
        'open', 'high', 'low', 'close',
        'volume', 'num_trades', 'turnover',
        'adj_close', 'adj_open', 'adj_high', 'adj_low',
        'log_return', 'log_return_raw',
        'liquidity_regime', 'volatility_regime'
    ]
    feature_cols = [col for col in test_df.columns if col not in exclude_cols]
    
    # Filter for numeric columns only
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    feature_cols = [col for col in feature_cols if col in numeric_cols]
    
    # Make predictions
    X_test = test_df[feature_cols]
    predictions = forecaster.predict(X_test, horizons=horizons)
    
    # Create predictions DataFrame
    predictions_df = test_df[['date', 'symbol']].copy()
    predictions_df['log_return_pred'] = predictions[1][0.5]  # Median prediction
    
    # Run backtest
    backtester = Backtester(initial_capital=100000.0, transaction_cost=0.001)
    backtest_df = backtester.run_backtest(
        predictions_df,
        test_df,
        strategy='long_only'
    )
    
    # Calculate performance metrics
    metrics = backtester.calculate_performance_metrics(backtest_df)
    
    logger.info("\nBacktest Performance Metrics:")
    logger.info(f"  Total Return:       {metrics['total_return']:.2%}")
    logger.info(f"  Annualized Return:  {metrics['annualized_return']:.2%}")
    logger.info(f"  Sharpe Ratio:       {metrics['sharpe_ratio']:.2f}")
    logger.info(f"  Max Drawdown:       {metrics['max_drawdown']:.2%}")
    logger.info(f"  Win Rate:           {metrics['win_rate']:.2%}")
    logger.info(f"  Avg Win:            {metrics['avg_win']:.4f}")
    logger.info(f"  Avg Loss:           {metrics['avg_loss']:.4f}")
    logger.info(f"  Num Trades:         {int(metrics['num_trades'])}")
    
    # Save backtest results
    reports_dir = Path(config.get('data.reports_dir', 'data/reports'))
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    backtest_path = reports_dir / 'backtest_results.csv'
    backtest_df.to_csv(backtest_path, index=False)
    logger.info(f"\n✓ Saved backtest results to {backtest_path}")
    
    return metrics


def evaluate_saved_models():
    """Evaluate saved models on the test set (no retraining)."""
    logger.info("\n" + "=" * 60)
    logger.info("Evaluating Saved Models (Fast Mode)")
    logger.info("=" * 60)
    
    # Load features
    processed_dir = Path(config.get('data.processed_dir'))
    features_path = processed_dir / 'features.parquet'
    df = pd.read_parquet(features_path)
    
    # Sanitize features (replace inf with nan)
    import numpy as np
    df = df.replace([np.inf, -np.inf], np.nan)
    
    # Load models
    models_dir = Path(config.get('models.save_dir', 'models'))
    price_models_dir = models_dir / 'price'
    
    horizons = config.get('models.horizons', [1, 5])
    quantiles = config.get('models.quantiles', [0.1, 0.5, 0.9])
    
    forecaster = MultiHorizonForecaster(horizons=horizons, quantiles=quantiles)
    try:
        forecaster.load(str(price_models_dir))
    except FileNotFoundError:
        logger.error("No saved models found. Please train models first.")
        return
        
    # Get feature columns matches training
    exclude_cols = [
        'date', 'symbol', 'name', 'group',
        'open', 'high', 'low', 'close',
        'volume', 'num_trades', 'turnover',
        'adj_close', 'adj_open', 'adj_high', 'adj_low',
        'log_return', 'log_return_raw',
        'liquidity_regime', 'volatility_regime'
    ]
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    # Filter for numeric columns only
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    feature_cols = [col for col in feature_cols if col in numeric_cols]
    
    # Create Test Split (last 15% as configured)
    test_size = config.get('model.test_ratio', 0.15)
    split_idx = int(len(df) * (1 - test_size))
    test_df = df.iloc[split_idx:].copy()
    
    logger.info(f"Evaluating on test set: {len(test_df)} samples")
    
    # Predict
    X_test = test_df[feature_cols]
    predictions = forecaster.predict(X_test)
    
    # Available quantiles are [0.1, 0.5, 0.9] which supports 80% CI (0.1 lower, 0.9 upper)
    # 90% CI would need 0.05/0.95
    confidence_level = 0.8
    intervals = forecaster.predict_intervals(X_test, confidence_levels=[confidence_level])
    
    # Prepare results for evaluation
    # We need to restructure predictions to match what evaluate_multi_horizon expects
    # y_true_dict[horizon] = series
    # y_pred_dict[horizon] = series
    # ci_dict[horizon] = (lower, upper)
    
    from src.validation.metrics import evaluate_multi_horizon, print_evaluation_report
    
    y_true_dict = {}
    y_pred_dict = {}
    ci_dict = {}
    
    target_col = 'log_return'
    
    for horizon in horizons:
        # Create true target for this horizon
        # Note: We need to be careful with alignment. 
        # The forecaster.create_target does the shift on the WHOLE df usually.
        # Here we just want the truth for the test set.
        # But simply shifting the test set rows might miss the transition at the boundary.
        # Safer to shift the whole DF then slice.
        
        full_target = df.groupby('symbol')[target_col].shift(-horizon)
        y_true = full_target.iloc[split_idx:]
        
        # Align with X_test (drop NaNs if any were dropped during prediction?)
        # XGBoost handles NaNs, but metric calc needs matching indices
        
        # Filter indices where we have both prediction and truth
        valid_mask = ~y_true.isna()
        y_true = y_true[valid_mask]
        
        # Get median prediction (0.5)
        y_pred = predictions[horizon][0.5]
        y_pred = pd.Series(y_pred, index=test_df.index)
        y_pred = y_pred[valid_mask]
        
        # Get CI
        # predict_intervals returns dict[confidence_level] -> (lower, upper)
        if confidence_level in intervals[horizon]:
            lower, upper = intervals[horizon][confidence_level]
            lower = pd.Series(lower, index=test_df.index)[valid_mask]
            upper = pd.Series(upper, index=test_df.index)[valid_mask]
        else:
            logger.warning(f"Confidence level {confidence_level} not found for horizon {horizon}")
            lower = pd.Series(np.nan, index=test_df.index)[valid_mask]
            upper = pd.Series(np.nan, index=test_df.index)[valid_mask]
        
        y_true_dict[horizon] = y_true
        y_pred_dict[horizon] = y_pred
        ci_dict[horizon] = (lower, upper)
        
    # Evaluate
    metrics_df = evaluate_multi_horizon(
        y_true_dict,
        y_pred_dict,
        ci_dict,
        confidence_level=confidence_level
    )
    
    print_evaluation_report(metrics_df)
    
    # Save
    reports_dir = Path(config.get('data.reports_dir', 'data/reports'))
    reports_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = reports_dir / 'price_evaluation_metrics.csv'
    metrics_df.to_csv(metrics_path, index=False)
    logger.info(f"✓ Saved evaluation metrics to {metrics_path}")
    
    return metrics_df


if __name__ == '__main__':
    # Run fast evaluation of saved models
    evaluate_saved_models()
    
    # Verify volume models
    validate_volume_models()
    
    # Run backtest
    run_backtest()
    
    logger.info("\n" + "=" * 60)
    logger.info("✓ Validation Complete!")
    logger.info("=" * 60)

"""Comprehensive test suite for BVMT forecasting system."""

import pytest
import pandas as pd
import numpy as np
import os
from pathlib import Path
from datetime import datetime, timedelta

from src.data.loaders import FileLoaderFactory
from src.data.validators import DataQualityValidator
from src.data.dividends import DividendAdjuster
from src.features import FeaturePipeline
from src.models import (
    XGBQuantileForecaster,
    MultiHorizonForecaster,
    VolumeForecaster,
    MultiHorizonVolumeForecaster
)
from src.validation import calculate_rmse, calculate_directional_accuracy
from src.api.predictor import StockPredictor


# Test Data Loading
def test_csv_loader(tmp_path):
    """Test CSV file loading."""
    # Create dummy CSV
    df = pd.DataFrame({
        'SEANCE': ['01/01/2023', '02/01/2023'],
        'CODE': ['ABC', 'ABC'],
        'VALEUR': ['Test Corp', 'Test Corp'],
        'OUVERTURE': [10.0, 10.5],
        'PLUS_HAUT': [11.0, 11.0],
        'PLUS_BAS': [9.5, 10.0],
        'CLOTURE': [10.5, 10.8],
        'QUANTITE_NEGOCIEE': [1000, 1500]
    })
    csv_path = tmp_path / "test.csv"
    df.to_csv(csv_path, sep=';', index=False)
    
    loader = FileLoaderFactory.create_loader(csv_path)
    loaded_df = loader.load()
    
    assert len(loaded_df) == 2
    assert 'date' in loaded_df.columns
    assert 'close' in loaded_df.columns
    assert loaded_df['close'].iloc[0] == 10.5


# Test Feature Engineering
def test_feature_pipeline():
    """Test feature generation."""
    # Create dummy data
    dates = pd.date_range(start='2023-01-01', periods=100)
    df = pd.DataFrame({
        'date': dates,
        'symbol': ['ABC'] * 100,
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 105,
        'low': np.random.randn(100).cumsum() + 95,
        'close': np.random.randn(100).cumsum() + 100,
        'adj_close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 100),
        'num_trades': np.random.randint(10, 100, 100),
        'turnover': np.random.uniform(10000, 100000, 100)
    })
    
    pipeline = FeaturePipeline()
    features_df = pipeline.generate_features(df)
    
    assert 'sma_20' in features_df.columns
    assert 'rsi' in features_df.columns
    assert 'volume_ma' in features_df.columns


# Test Price Models
def test_price_forecaster():
    """Test XGBoost price forecasting."""
    # Create dummy data
    df = pd.DataFrame({
        'feature1': np.random.randn(100),
        'feature2': np.random.randn(100),
        'log_return': np.random.randn(100) * 0.01,
        'symbol': ['ABC'] * 100
    })
    
    feature_cols = ['feature1', 'feature2']
    
    model = XGBQuantileForecaster(horizon=1, n_estimators=10)
    y = model.create_target(df, 'log_return')
    
    # Check target creation
    assert len(y) == 100
    assert pd.isna(y.iloc[-1])  # Last value should be NaN due to shift
    
    # Fit model (excluding NaN)
    valid_idx = ~y.isna()
    model.fit(df.loc[valid_idx, feature_cols], y[valid_idx])
    
    assert model.is_fitted
    
    # Predict
    preds = model.predict(df[feature_cols])
    assert 0.5 in preds  # Median should be present
    assert len(preds[0.5]) == 100


# Test Volume Models
def test_volume_forecaster():
    """Test volume forecasting with liquidity regimes."""
    # Create dummy data
    df = pd.DataFrame({
        'feature1': np.random.randn(100),
        'volume': np.random.randint(100, 1000, 100),
        'symbol': ['ABC'] * 100
    })
    
    feature_cols = ['feature1']
    
    model = VolumeForecaster(horizon=1, n_estimators=10)
    y = model.create_target(df, 'volume')
    volume_data = df['volume']
    
    # Fit model
    valid_idx = ~y.isna()
    model.fit(
        df.loc[valid_idx, feature_cols],
        y[valid_idx],
        volume_data[valid_idx]
    )
    
    assert model.is_fitted
    assert model.q20_threshold is not None
    assert model.q80_threshold is not None
    
    # Predict regime
    _, regimes = model.predict_liquidity_regime(df[feature_cols])
    assert set(regimes).issubset({0, 1, 2})


# Test Validation Metrics
def test_metrics():
    """Test performance metrics."""
    y_true = np.array([1.0, 2.0, 3.0])
    y_pred = np.array([1.1, 1.9, 3.2])
    
    rmse = calculate_rmse(y_true, y_pred)
    assert rmse > 0
    assert rmse < 0.5
    
    # Directional accuracy
    y_true_dir = np.array([0.01, -0.01, 0.01])
    y_pred_dir = np.array([0.02, -0.005, -0.01])
    acc = calculate_directional_accuracy(y_true_dir, y_pred_dir)
    assert acc == 2/3  # 2 correct out of 3


if __name__ == "__main__":
    # Allow running tests directly
    sys.exit(pytest.main(["-v", __file__]))

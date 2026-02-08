"""Stock predictor class for making predictions."""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime, timedelta

from src.models import MultiHorizonForecaster, MultiHorizonVolumeForecaster
from src.features import FeaturePipeline
from src.utils import logger, config


class StockPredictor:
    """Main predictor class for stock forecasting."""
    
    def __init__(self, models_dir: Optional[str] = None):
        """
        Initialize stock predictor.
        
        Args:
            models_dir: Directory containing trained models
        """
        if models_dir is None:
            models_dir = config.get('models.save_dir', 'models')
        
        self.models_dir = Path(models_dir)
        self.price_forecaster = None
        self.volume_forecaster = None
        self.feature_pipeline = FeaturePipeline()
        
        # Load models
        self._load_models()
    
    def _load_models(self):
        """Load trained models."""
        logger.info("Loading models...")
        
        # Load price models
        price_models_dir = self.models_dir / 'price'
        if price_models_dir.exists():
            horizons = config.get('models.horizons', [1, 2, 3, 4, 5])
            quantiles = config.get('models.quantiles', [0.025, 0.1, 0.5, 0.9, 0.975])
            
            self.price_forecaster = MultiHorizonForecaster(
                horizons=horizons,
                quantiles=quantiles
            )
            self.price_forecaster.load(str(price_models_dir))
            logger.info(f"✓ Loaded price models from {price_models_dir}")
        else:
            logger.warning(f"Price models not found: {price_models_dir}")
        
        # Load volume models
        volume_models_dir = self.models_dir / 'volume'
        if volume_models_dir.exists():
            horizons = config.get('models.horizons', [1, 2, 3, 4, 5])
            
            self.volume_forecaster = MultiHorizonVolumeForecaster(horizons=horizons)
            self.volume_forecaster.load(str(volume_models_dir))
            logger.info(f"✓ Loaded volume models from {volume_models_dir}")
        else:
            logger.warning(f"Volume models not found: {volume_models_dir}")
    async def refresh_data(self, symbol: str) -> pd.DataFrame:
        """
        Fetch latest data for symbol (Real-time Pipeline).
        
        Args:
            symbol: Stock symbol
            
        Returns:
            DataFrame with latest features
        """
        import yfinance as yf
        
        # Yahoo Finance symbols often need suffix (e.g. '.TN' for Tunisia?)
        # For now, let's try direct symbol or fallback
        yf_symbol = symbol
        if not symbol.endswith('.TN') and not symbol.endswith('.BVMT'):
             # Heuristic: try adding .TN if not present, though BVMT might not be on YF fully
             # If not on YF, we might need our internal scraper.
             # For this demo, let's assume we can get it or fallback to last known data.
             pass

        logger.info(f"Refreshing data for {symbol}...")
        
        # TODO: integrate with actual real-time scraper if available
        # For now, we simulate "real-time" by ensuring we have the latest processed data
        # In a real production system, this would call the scraper module
        
        # Reload features to get any updates
        processed_dir = Path(config.get('data.processed_dir'))
        features_path = processed_dir / 'features.parquet'
        if features_path.exists():
            return pd.read_parquet(features_path)
            
        raise FileNotFoundError("Features file not found")

    def get_visualization_data(
        self,
        symbol: str,
        current_data: pd.DataFrame,
        horizons: Optional[List[int]] = None
    ) -> Dict:
        """
        Get data for visualization (History + Forecast + CI).
        
        Args:
            symbol: Stock symbol
            current_data: Feature DataFrame
            horizons: Forecast horizons
            
        Returns:
            Dictionary for plotting
        """
        if horizons is None:
            horizons = config.get('models.horizons', [1, 2, 3, 4, 5])
            
        # Get history (last 30 days)
        symbol_data = current_data[current_data['symbol'] == symbol].copy()
        history = symbol_data.iloc[-30:][['date', 'close', 'high', 'low']].to_dict('records')
        
        # Get predictions
        preds = self.predict(symbol, current_data, horizons)
        
        current_date_str = preds['current_date']
        current_date = pd.to_datetime(current_date_str)
        
        forecast_data = []
        
        # Reconstruct forecast timeline
        # Start from current price/date
        forecast_data.append({
            'date': current_date_str,
            'price': preds['current_price'],
            'type': 'history',
            'lower_bound': None,
            'upper_bound': None
        })
        
        price_preds = preds['predictions']['price']
        
        for h in horizons:
            # Approximate date for horizon (trading days)
            # Simple business day offset
            future_date = current_date + pd.Timedelta(days=h) 
            # Ideally use a trading calendar
            
            p_data = price_preds[h]
            median_return = p_data['median'] # This is log return? No, wait.
            # predict() returns transformed values or raw?
            # MultiHorizonForecaster returns WHAT?
            # It returns the PREDICTION from the model.
            # The model predicts LOG RETURN usually (as per create_target).
            # So we need to convert back to price!
             
            # WAIT: predict() in predictor.py 
            # currently just returns the raw output of forecaster.predict()
            # which is log_return.
            # We need to convert it to price for the user/visualization.
            
            # Let's fix predict() to return Prices or Returns?
            # Usually API consumers want Price or % Change.
            # Let's assume predict() needs to convert log_return to price level.
            
            # For visualization, we definitely need Price Levels.
            
            # Convert log return to price: Price_t+h = Price_t * exp(log_return)
            current_price = preds['current_price']
            predicted_price = current_price * np.exp(median_return)
            
            # CI conversion
            # lower_ret = p_data['ci_80']['lower'] if available
            # We need to handle the dict structure carefully
            
            lower_price = None
            upper_price = None
            
            # Check for CI keys (depends on what predict() returned)
            if 'ci_80' in p_data:
                lower_ret = p_data['ci_80']['lower']
                upper_ret = p_data['ci_80']['upper']
                lower_price = current_price * np.exp(lower_ret)
                upper_price = current_price * np.exp(upper_ret)
            
            forecast_data.append({
                 'date': future_date.strftime('%Y-%m-%d'),
                 'price': predicted_price,
                 'type': 'forecast',
                 'lower_bound': lower_price,
                 'upper_bound': upper_price
            })
            
        return {
            "symbol": symbol,
            "data": forecast_data
        }

    def predict(
        self,
        symbol: str,
        current_data: pd.DataFrame,
        horizons: Optional[List[int]] = None
    ) -> Dict:
        """
        Make predictions for a stock.
        """
        if horizons is None:
            horizons = config.get('models.horizons', [1, 2, 3, 4, 5])
        
        # Filter for symbol
        symbol_data = current_data[current_data['symbol'] == symbol].copy()
        
        if len(symbol_data) == 0:
            raise ValueError(f"No data found for symbol: {symbol}")
        
        # Get latest row
        latest = symbol_data.iloc[-1]
        
        # Get feature columns matches training
        # We need to ensure we use the same columns as training
        # Ideally, forecaster.feature_names should be used if available
        
        # Heuristic for now: exclude known non-features
        exclude_cols = [
            'date', 'symbol', 'name', 'group',
            'open', 'high', 'low', 'close',
            'volume', 'num_trades', 'turnover',
            'adj_close', 'adj_open', 'adj_high', 'adj_low',
            'log_return', 'log_return_raw',
            'liquidity_regime', 'volatility_regime'
        ]
        feature_cols = [col for col in current_data.columns if col not in exclude_cols]
        # Ensure numeric
        feature_cols = [c for c in feature_cols if pd.api.types.is_numeric_dtype(current_data[c])]

        # Prepare features
        X = symbol_data[feature_cols].iloc[[-1]]  # Last row only
        
        # Price predictions
        price_predictions = {}
        if self.price_forecaster:
            # Raw predictions are log returns
            predictions = self.price_forecaster.predict(X, horizons=horizons)
            
            # Check available quantiles for CI
            # We want 80% (0.1, 0.9) and maybe 90% (0.05, 0.95) if available
            available_quantiles = self.price_forecaster.quantiles
            
            # Determine which CIs we can support
            cis_to_calc = []
            
            # Check for 80% CI (needs 0.1 and 0.9)
            if 0.1 in available_quantiles and 0.9 in available_quantiles:
                cis_to_calc.append(0.80)
            
            # Check for 90% CI (needs 0.05 and 0.95)
            if 0.05 in available_quantiles and 0.95 in available_quantiles:
                cis_to_calc.append(0.90)
                
            intervals = {}
            if cis_to_calc:
                 intervals = self.price_forecaster.predict_intervals(
                    X,
                    confidence_levels=cis_to_calc,
                    horizons=horizons
                )
            
            for horizon in horizons:
                pred_data = {
                    'median': float(predictions[horizon][0.5][0]) # Median log return
                }
                
                # Add CIs if calculated
                for conf in cis_to_calc:
                    key = f'ci_{int(conf*100)}'
                    if conf in intervals.get(horizon, {}):
                         pred_data[key] = {
                            'lower': float(intervals[horizon][conf][0][0]),
                            'upper': float(intervals[horizon][conf][1][0])
                        }
                
                price_predictions[horizon] = pred_data
        
        # Volume predictions
        volume_predictions = {}
        if self.volume_forecaster:
            regime_preds = self.volume_forecaster.predict_liquidity_regime(X, horizons=horizons)
            
            for horizon in horizons:
                volume, regime = regime_preds[horizon]
                
                # Get regime name safely
                regime_val = int(regime[0])
                regime_name = 'Unknown'
                if hasattr(self.volume_forecaster.models[horizon], 'get_regime_name'):
                    regime_name = self.volume_forecaster.models[horizon].get_regime_name(regime_val)
                
                volume_predictions[horizon] = {
                    'volume': float(volume[0]),
                    'liquidity_regime': regime_name
                }
        
        # Prepare result
        result = {
            'symbol': symbol,
            'name': latest.get('name', ''),
            'current_price': float(latest.get('close', 0)),
            'current_date': str(latest.get('date', '')),
            'predictions': {
                'price': price_predictions,
                'volume': volume_predictions
            }
        }
        
        return result

    def predict_batch(
        self,
        symbols: List[str],
        current_data: pd.DataFrame,
        horizons: Optional[List[int]] = None
    ) -> List[Dict]:
        """
        Make predictions for multiple stocks.
        """
        results = []
        
        for symbol in symbols:
            try:
                prediction = self.predict(symbol, current_data, horizons)
                results.append(prediction)
            except Exception as e:
                logger.error(f"Error predicting {symbol}: {str(e)}")
                results.append({
                    'symbol': symbol,
                    'error': str(e)
                })
        
        return results

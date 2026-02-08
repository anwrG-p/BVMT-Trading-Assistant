import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from src.utils import logger, config

class MockStockPredictor:
    """Mock predictor for when real models are missing."""
    
    def __init__(self, models_dir: Optional[str] = None):
        logger.warning("Initializing MockStockPredictor due to missing models")
        
    async def refresh_data(self, symbol: str) -> pd.DataFrame:
        logger.info(f"Mocking refresh data for {symbol}")
        # Return a dummy dataframe
        dates = pd.date_range(end=datetime.now(), periods=30)
        df = pd.DataFrame({
            'date': dates,
            'symbol': symbol,
            'close': np.random.uniform(10, 100, 30),
            'high': np.random.uniform(10, 100, 30),
            'low': np.random.uniform(10, 100, 30),
            'open': np.random.uniform(10, 100, 30),
            'volume': np.random.uniform(1000, 10000, 30),
            'name': [f"Mock {symbol}" for _ in range(30)]
        })
        return df

    def predict(self, symbol: str, current_data: pd.DataFrame, horizons: Optional[List[int]] = None) -> Dict:
        if horizons is None:
            horizons = [1, 2, 3, 4, 5]
            
        # Get latest close safely
        if not current_data.empty:
            current_price = float(current_data['close'].iloc[-1])
            current_date = str(current_data['date'].iloc[-1])
        else:
            current_price = 100.0
            current_date = str(datetime.now())
        
        price_predictions = {}
        volume_predictions = {}
        
        for h in horizons:
            # Mock price prediction (random small change)
            change = np.random.uniform(-0.02, 0.02)
            
            price_predictions[h] = {
                'median': np.log(1 + change), # log return
                'ci_80': {'lower': np.log(1 + change - 0.01), 'upper': np.log(1 + change + 0.01)},
                'ci_90': {'lower': np.log(1 + change - 0.02), 'upper': np.log(1 + change + 0.02)}
            }
            
            volume_predictions[h] = {
                'volume': 5000.0,
                'liquidity_regime': 'Normal'
            }
            
        return {
            'symbol': symbol,
            'name': f"Mock {symbol}",
            'current_price': current_price,
            'current_date': current_date,
            'predictions': {
                'price': price_predictions,
                'volume': volume_predictions
            }
        }

    def predict_batch(self, symbols: List[str], current_data: pd.DataFrame, horizons: Optional[List[int]] = None) -> List[Dict]:
        results = []
        for symbol in symbols:
            # Create a dummy DF for the symbol just to satisfy predict signature
            dummy_df = pd.DataFrame({
                'date': [datetime.now()], 
                'symbol': [symbol], 
                'close': [100.0],
                'name': [f"Mock {symbol}"]
            })
            results.append(self.predict(symbol, dummy_df, horizons))
        return results

    def get_visualization_data(self, symbol: str, current_data: pd.DataFrame, horizons: Optional[List[int]] = None) -> Dict:
        if horizons is None:
            horizons = [1, 2, 3, 4, 5]
            
        # Call predict to get simulated forecast
        preds = self.predict(symbol, current_data, horizons)
        current_price = preds['current_price']
        
        forecast_data = []
        # Add a few history points
        for i in range(5):
             forecast_data.append({
                'date': (datetime.now() - timedelta(days=5-i)).strftime('%Y-%m-%d'),
                'price': current_price * (1 - (0.01 * (5-i))),
                'type': 'history',
                'lower_bound': None,
                'upper_bound': None
            })
            
        # Add forecast points
        for i, h in enumerate(horizons):
             forecast_data.append({
                'date': (datetime.now() + timedelta(days=h)).strftime('%Y-%m-%d'),
                'price': current_price * (1 + (0.01 * (i+1))),
                'type': 'forecast',
                'lower_bound': current_price * (1 + (0.01 * (i+1)) - 0.05),
                'upper_bound': current_price * (1 + (0.01 * (i+1)) + 0.05)
            })
            
        return {
            "symbol": symbol,
            "data": forecast_data
        }

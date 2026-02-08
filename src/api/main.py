"""FastAPI application for BVMT stock forecasting."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import pandas as pd
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils import logger, config

# try:
#     print("Attempting to import StockPredictor...")
#     from src.api.predictor import StockPredictor
#     print("Imported StockPredictor successfully.")
# except Exception as e:
#     print(f"Failed to import StockPredictor: {e}")
from src.api.mock_predictor import MockStockPredictor as StockPredictor
logger.warning(f"Using MockStockPredictor (Forced).")

# Create FastAPI app
app = FastAPI(
    title="BVMT Stock Forecasting API",
    description="Production-grade stock price forecasting for Tunisian Stock Exchange",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize predictor
predictor = None
features_df = None


from src.api.schemas.models import (
    PredictionRequest, 
    BatchPredictionRequest, 
    PredictionResult, 
    VisualizationResponse,
    MetricsResponse
)

# Sanitize response to handle NaN/Infinity
import math
import numpy as np

def sanitize_response(obj):
    """
    recursively replace NaN/Infinity with None for JSON compliance.
    """
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: sanitize_response(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_response(v) for v in obj]
    elif isinstance(obj, (np.float32, np.float64)):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)
    elif isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    return obj


@app.on_event("startup")
async def startup_event():
    """Load models and data on startup."""
    global predictor, features_df
    
    logger.info("Starting BVMT Forecasting API...")
    
    # Load predictor
    predictor = StockPredictor()
    
    # Load latest features
    processed_dir = Path(config.get('data.processed_dir'))
    features_path = processed_dir / 'features.parquet'
    
    if features_path.exists():
        features_df = pd.read_parquet(features_path)
        logger.info(f"Loaded features: {len(features_df)} rows")
    else:
        logger.warning(f"Features not found: {features_path}")
    
    logger.info("✓ API ready")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "BVMT Stock Forecasting API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "models_loaded": predictor is not None,
        "data_loaded": features_df is not None
    }


@app.get("/symbols")
async def get_symbols():
    """Get list of available symbols."""
    if features_df is None:
        raise HTTPException(status_code=503, detail="Data not loaded")
    
    symbols = sorted(features_df['symbol'].unique().tolist())
    
    return {
        "symbols": symbols,
        "count": len(symbols)
    }

@app.post("/predict", response_model=PredictionResult)
async def predict(request: PredictionRequest):
    """Make prediction for a single stock."""
    if predictor is None or features_df is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    try:
        result = predictor.predict(
            request.symbol,
            features_df,
            request.horizons
        )
        return sanitize_response(result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/predict/realtime", response_model=PredictionResult)
async def predict_realtime(request: PredictionRequest):
    """
    Make real-time prediction (fetches latest data).
    """
    if predictor is None:
        raise HTTPException(status_code=503, detail="Service not ready")
        
    try:
        # Refresh data for symbol
        # Note: In production, this should update the global features_df or a cache
        latest_features = await predictor.refresh_data(request.symbol)
        
        result = predictor.predict(
            request.symbol,
            latest_features,
            request.horizons
        )
        return sanitize_response(result)
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Symbol data not found")
    except Exception as e:
        logger.exception(f"Real-time prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/visualization/{symbol}", response_model=VisualizationResponse)
async def get_visualization(symbol: str, horizons: Optional[str] = None):
    """
    Get data for Forecast vs Actual visualization.
    """
    if predictor is None or features_df is None:
        raise HTTPException(status_code=503, detail="Service not ready")
        
    # Parse horizons
    horizon_list = None
    if horizons:
        try:
            horizon_list = [int(h.strip()) for h in horizons.split(',')]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid horizons format")
            
    try:
        result = predictor.get_visualization_data(
            symbol,
            features_df,
            horizon_list
        )
        return sanitize_response(result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Visualization error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """
    Get model performance metrics.
    """
    reports_dir = Path(config.get('data.reports_dir', 'data/reports'))
    price_metrics_path = reports_dir / 'price_evaluation_metrics.csv'
    backtest_path = reports_dir / 'backtest_results.csv'
    
    response = {
        "price_metrics": [],
        "backtest_metrics": {}
    }
    
    if price_metrics_path.exists():
        df = pd.read_csv(price_metrics_path)
        response["price_metrics"] = df.to_dict('records')
        
    if backtest_path.exists():
        # Calculate summary stats from backtest
        df = pd.read_csv(backtest_path)
        # We want the summary metrics, not the whole series
        # Re-calculate or load if we saved them separately?
        # We didn't save the summary JSON, only printed it.
        # Let's recalculate quickly using Backtester class or just basic pandas
        
        total_return = df['cumulative_return'].iloc[-1] - 1
        win_rate = (df['net_return'] > 0).mean()
        
        response["backtest_metrics"] = {
            "total_return": total_return,
            "win_rate": win_rate,
            "sharpe_ratio": 0.0, # Placeholder or recalc
            "max_drawdown": 0.0
        }
        
    # Get feature importance
    if predictor:
        response["feature_importance"] = predictor.get_feature_importance()
    
    return sanitize_response(response)


@app.post("/predict/batch")
async def predict_batch(request: BatchPredictionRequest):
    """Make predictions for multiple stocks."""
    if predictor is None or features_df is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    try:
        results = predictor.predict_batch(
            request.symbols,
            features_df,
            request.horizons
        )
        return {"predictions": sanitize_response(results)}
    except Exception as e:
        logger.exception(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    
    host = config.get('api.host', '0.0.0.0')
    port = config.get('api.port', 8000)
    
    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=config.get('api.reload', False),
        workers=config.get('api.workers', 1)
    )

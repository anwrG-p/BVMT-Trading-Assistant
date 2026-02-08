from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union

class PredictionRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol to predict")
    horizons: Optional[List[int]] = Field(None, description="Forecast horizons in days (e.g. [1, 5])")

class BatchPredictionRequest(BaseModel):
    symbols: List[str] = Field(..., description="List of stock symbols")
    horizons: Optional[List[int]] = Field(None, description="Forecast horizons")

class ConfidenceInterval(BaseModel):
    lower: float
    upper: float

class PricePrediction(BaseModel):
    median: float
    ci_80: Optional[ConfidenceInterval] = None
    ci_95: Optional[ConfidenceInterval] = None

class VolumePrediction(BaseModel):
    volume: float
    liquidity_regime: str

class PredictionResult(BaseModel):
    symbol: str
    name: str
    current_price: float
    current_date: str
    predictions: Dict[str, Dict[int, Union[PricePrediction, VolumePrediction]]] 
    # Structure: predictions['price'][1] -> PricePrediction

class VisualizationDataPoint(BaseModel):
    date: str
    price: float
    type: str = Field(..., description="'history' or 'forecast'")
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None

class VisualizationResponse(BaseModel):
    symbol: str
    data: List[VisualizationDataPoint]

class MetricsResponse(BaseModel):
    price_metrics: List[Dict[str, Optional[Union[int, float]]]]
    backtest_metrics: Dict[str, Optional[Union[int, float]]]
    feature_importance: Optional[List[Dict[str, Union[str, float]]]] = None

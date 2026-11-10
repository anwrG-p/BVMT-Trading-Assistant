"""Pydantic schemas matching dashboard-frontend contracts."""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal

# --- Market Overview Schemas ---

class IndexData(BaseModel):
    name: str = "TUNINDEX"
    value: float
    change: float

class StockTicker(BaseModel):
    symbol: str
    price: float
    change: float

class MarketAlert(BaseModel):
    id: int
    symbol: str
    type: Literal["volume", "price", "news", "market"]
    description: str
    timestamp: str

class MarketOverviewResponse(BaseModel):
    index: IndexData
    gainers: List[StockTicker]
    losers: List[StockTicker]
    sentiment: float = Field(..., ge=0.0, le=1.0)
    recent_alerts: List[MarketAlert]
    marketVolume: Optional[float] = 1845000.0
    activeTraders: Optional[int] = 1240


# --- Stock Analysis Schemas ---

class PricePoint(BaseModel):
    date: str
    value: float
    forecast: Optional[bool] = False

class SentimentPoint(BaseModel):
    date: str
    score: float

class TechnicalIndicators(BaseModel):
    rsi: float
    macd: str

class Recommendation(BaseModel):
    action: Literal["ACHETER", "VENDRE", "CONSERVER"]
    confidence: float

class StockAnalysisResponse(BaseModel):
    symbol: str
    name: str
    price_history: List[PricePoint]
    sentiment_timeline: List[SentimentPoint]
    indicators: TechnicalIndicators
    recommendation: Recommendation


# --- Portfolio Schemas ---

class Position(BaseModel):
    symbol: str
    quantity: int
    buyPrice: float
    currentPrice: float
    pl: float

class AllocationItem(BaseModel):
    name: str
    value: float

class PerformancePoint(BaseModel):
    date: str
    value: float

class PortfolioResponse(BaseModel):
    capital: float
    roi: float
    positions: List[Position]
    allocation: List[AllocationItem]
    performance: List[PerformancePoint]
    suggestions: List[str]


# --- Alerts Schemas ---

class AlertDetail(BaseModel):
    id: int
    symbol: str
    type: str
    severity: Literal["High", "Medium", "Low"]
    timestamp: str
    status: Literal["Open", "Resolved"]

class AlertsResponse(BaseModel):
    alerts: List[AlertDetail]
    filters: List[str]


# --- Chatbot Schemas ---

class ChatMessageRequest(BaseModel):
    message: str
    symbol: Optional[str] = None

class ChatMessageResponse(BaseModel):
    reply: str
    timestamp: str

"""Stock analysis routes for historical prices, technical indicators, and forecasts."""

from fastapi import APIRouter, HTTPException
from src.api.schemas.frontend_models import StockAnalysisResponse
from src.api.data_service import BVMTDataService

router = APIRouter(prefix="/stock", tags=["Stock"])
data_service = BVMTDataService()

@router.get("/{symbol}", response_model=StockAnalysisResponse)
async def get_stock_analysis(symbol: str):
    """Retrieve detailed analysis for a stock, including historical prices, indicators, and forecast."""
    try:
        return data_service.get_stock_analysis(symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analysis for {symbol}: {str(e)}")

"""Market routes for BVMT index, gainers, losers, and sentiment."""

from fastapi import APIRouter
from src.api.schemas.frontend_models import MarketOverviewResponse
from src.api.data_service import BVMTDataService

router = APIRouter(prefix="/market", tags=["Market"])
data_service = BVMTDataService()

@router.get("/overview", response_model=MarketOverviewResponse)
async def get_market_overview():
    """Retrieve current market overview including Tunindex, top gainers, losers, and sentiment."""
    return data_service.get_market_overview()

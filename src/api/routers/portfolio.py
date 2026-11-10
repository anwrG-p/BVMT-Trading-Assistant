"""Portfolio management and optimization routes."""

from fastapi import APIRouter
from src.api.schemas.frontend_models import PortfolioResponse
from src.api.data_service import BVMTDataService

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])
data_service = BVMTDataService()

@router.get("", response_model=PortfolioResponse)
async def get_portfolio():
    """Retrieve portfolio metrics, positions, allocation, and rebalancing recommendations."""
    return data_service.get_portfolio()

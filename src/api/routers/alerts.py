"""Market alerts and notification routes."""

from fastapi import APIRouter
from src.api.schemas.frontend_models import AlertsResponse
from src.api.data_service import BVMTDataService

router = APIRouter(prefix="/alerts", tags=["Alerts"])
data_service = BVMTDataService()

@router.get("", response_model=AlertsResponse)
async def get_alerts():
    """Retrieve market alerts and available filters."""
    return data_service.get_alerts()

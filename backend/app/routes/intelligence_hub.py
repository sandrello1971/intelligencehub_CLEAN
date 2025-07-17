from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db

router = APIRouter(prefix="/intelligence-hub", tags=["Intelligence HUB"])

@router.get("/services")
async def get_available_services(db: Session = Depends(get_db)):
    """Lista servizi Intelligence HUB disponibili"""
    
    from app.services.intelligence_hub_service import IntelligenceHubService
    
    hub_service = IntelligenceHubService()
    services = await hub_service.get_available_services(db)
    
    return {
        "success": True,
        "data": services,
        "total": len(services)
    }

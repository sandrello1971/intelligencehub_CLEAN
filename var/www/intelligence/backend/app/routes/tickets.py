"""
Intelligence API - Tickets Routes  
API endpoints for ticket management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.modules.ticketing.services import TicketingService
from app.modules.ticketing.schemas import (
    TicketResponse, TicketUpdate, TicketListItem, 
    ServicesInput, BulkOperationResult
)

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket_detail(ticket_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific ticket"""
    service = TicketingService(db)
    ticket = service.get_ticket_detail(ticket_id)
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket non trovato")
    
    return ticket


@router.get("/", response_model=List[TicketListItem])
def list_tickets(
    priority: Optional[str] = Query(None, description="Filter by priority (alta/media/bassa)"),
    status: Optional[str] = Query(None, description="Filter by status"),
    customer_name: Optional[str] = Query(None, description="Filter by customer name"),
    db: Session = Depends(get_db)
):
    """List tickets with optional filtering"""
    service = TicketingService(db)
    
    # Build filters dict
    filters = {}
    if priority:
        filters["priority"] = priority
    if status:
        filters["status"] = status
    if customer_name:
        filters["customer_name"] = customer_name
    
    tickets = service.list_tickets(filters=filters)
    return tickets


@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket(ticket_id: int, ticket_update: TicketUpdate, db: Session = Depends(get_db)):
    """Update a ticket"""
    service = TicketingService(db)
    
    # TODO: Implement ticket update logic in service
    # For now, just return the ticket detail
    ticket = service.get_ticket_detail(ticket_id)
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket non trovato")
    
    return ticket


@router.post("/{ticket_id}/generate-all")
def generate_opportunities_from_ticket(
    ticket_id: int, 
    payload: ServicesInput, 
    db: Session = Depends(get_db)
):
    """Generate opportunities from ticket services"""
    service = TicketingService(db)
    ticket = service.get_ticket_detail(ticket_id)
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket non trovato")
    
    # This would integrate with the opportunities/CRM module
    
    return {
        "success": True,
        "ticket_id": ticket_id,
        "services": payload.services,
        "message": "Opportunities generation initiated"
    }


@router.post("/{ticket_id}/auto-generate-from-services")
def auto_generate_from_services(ticket_id: int, db: Session = Depends(get_db)):
    """Auto-generate sub-tickets from detected services"""
    service = TicketingService(db)
    ticket = service.get_ticket_detail(ticket_id)
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket non trovato")
    
    if not ticket.get("detected_services"):
        raise HTTPException(status_code=400, detail="Nessun servizio rilevato nel ticket")
    
    # TODO: Implement auto-generation logic
    # This would create new tickets based on detected services
    
    return {
        "status": "ok",
        "ticket_id": ticket_id,
        "detected_services": ticket["detected_services"],
        "message": "Auto-generation completed"
    }


@router.post("/{ticket_id}/generate-crm-opportunities")
def generate_crm_opportunities(ticket_id: int, db: Session = Depends(get_db)):
    """Generate CRM opportunities from closed ticket"""
    service = TicketingService(db)
    ticket = service.get_ticket_detail(ticket_id)
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket non trovato")
    
    # Check if ticket is I24 type
    if not ticket.get("ticket_code", "").startswith("TCK-I24"):
        raise HTTPException(status_code=400, detail="Ticket non valido per generazione opportunità")
    
    # Check if all tasks are closed
    tasks_stats = ticket.get("tasks_stats", {})
    if tasks_stats.get("pending", 0) > 0:
        raise HTTPException(status_code=400, detail="Tutti i task devono essere chiusi")
    
    # This would integrate with the CRM module
    
    return {
        "status": "ok",
        "ticket_id": ticket_id,
        "message": "CRM opportunities created"
    }


@router.post("/auto-close-completed", response_model=BulkOperationResult)
def auto_close_completed_tickets(db: Session = Depends(get_db)):
    """Batch operation to auto-close all completed tickets"""
    service = TicketingService(db)
    result = service.auto_close_completed_tickets()
    
    return result

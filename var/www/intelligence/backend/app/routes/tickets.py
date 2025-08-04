"""
Intelligence API - Tickets Routes  
API endpoints for ticket management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict

from app.core.database import get_db
from app.routes.auth import get_current_user_dep
from app.modules.ticketing.services import TicketingService
from app.modules.ticketing.schemas import (
    TaskResponse, TaskUpdate, TicketResponse, TicketUpdate, TicketListItem,
    ServicesInput, TicketFilters, TaskFilters, BulkOperationResult,
    CommercialCommessaRequest, CommercialCommessaResponse,
    OpportunityGenerationRequest, OpportunityGenerationResponse
)

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("/{ticket_id}", response_model=Dict)
def get_ticket_detail(ticket_id: str, db: Session = Depends(get_db)):
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


@router.patch("/{ticket_id}", response_model=Dict)
def update_ticket(ticket_id: str, ticket_update: TicketUpdate, db: Session = Depends(get_db)):
    """Update a ticket"""
    service = TicketingService(db)
    
    # Convertiamo i dati di update
    update_data = ticket_update.dict(exclude_unset=True)
    
    # Chiamiamo il servizio per aggiornare il ticket
    updated_ticket = service.update_ticket(ticket_id, update_data)
    
    if not updated_ticket:
        raise HTTPException(status_code=500, detail="Errore nell'aggiornamento del ticket")
    
    return updated_ticket
    
    


@router.post("/{ticket_id}/generate-all")
def generate_opportunities_from_ticket(
    ticket_id: str, 
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
def auto_generate_from_services(ticket_id: str, db: Session = Depends(get_db)):
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
def generate_crm_opportunities(ticket_id: str, db: Session = Depends(get_db)):
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

# ===== COMMERCIAL ENDPOINTS =====

@router.post("/commercial/create-commessa")
def create_commercial_commessa(
    request: CommercialCommessaRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep)
):
    """Crea una nuova commessa commerciale da kit"""
    
    service = TicketingService(db)
    
    # Usa l'ID dell'utente corrente se non specificato
    owner_id = request.owner_id or str(current_user.id)
    
    request_data = {
        "company_id": request.company_id,
        "kit_commerciale_id": request.kit_commerciale_id,
        "notes": request.notes
    }
    
    result = service.create_commercial_commessa(request_data, owner_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get("/commercial/hierarchy/{company_id}")
def get_commercial_hierarchy(
    company_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep)
):
    """Ottiene la gerarchia ticket per una azienda (per la vista ad albero)"""
    from app.models.company import Company
    from app.models.commesse import Commessa
    from app.models.ticket import Ticket
    
    # Trova l'azienda
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Azienda non trovata")
    
    # Trova commesse per questa azienda
    commesse = db.query(Commessa).filter(
        Commessa.client_id == company_id
    ).all()
    
    service = TicketingService(db)
    
    tickets_padre = []
    tickets_figli = []
    
    # Trova tutti i ticket per questa azienda
    tickets = db.query(Ticket).filter(
        Ticket.company_id == company_id
    ).all()
    
    for ticket in tickets:
        ticket_detail = service.get_ticket_detail(str(ticket.id))
        if ticket_detail and company:
            ticket_detail["company_name"] = company.nome
        
        if ticket_detail:
            # Logica per distinguere ticket padre da figli
            # Ticket padre: quelli con [COMMERCIALE] nel titolo o ticket_code con sigla di kit commerciale
            is_padre = False
            
            if "[COMMERCIALE]" in ticket.title:
                is_padre = True
            elif ticket.ticket_code:
                # Estrai sigla dal ticket_code (TCK-XXX-...)
                import re
                match = re.match(r'TCK-([A-Z]+)-', ticket.ticket_code)
                if match:
                    sigla = match.group(1)
                    
                    # Verifica se la sigla corrisponde a un articolo principale di kit commerciale
                    from sqlalchemy import text
                    kit_query = text("""
                        SELECT COUNT(*) FROM kit_commerciali k
                        JOIN articoli a ON k.articolo_principale_id = a.id
                        WHERE a.codice = :sigla AND k.attivo = true
                    """)
                    result = db.execute(kit_query, {"sigla": sigla}).fetchone()
                    is_padre = result[0] > 0 if result else False
            
            if is_padre:
                tickets_padre.append(ticket_detail)
            else:
                tickets_figli.append(ticket_detail)
    
    return {
        "cliente": company.nome,
        "company_id": company_id,
        "tickets_padre": tickets_padre,
        "tickets_figli": tickets_figli,
        "statistics": {
            "total_commesse": len(commesse),
            "total_tickets_padre": len(tickets_padre),
            "total_tickets_figli": len(tickets_figli)
        }
    }

@router.get("/tasks/{task_id}", response_model=Dict)
def get_task_detail_endpoint(task_id: str, db: Session = Depends(get_db)):
    """Get detailed information about a specific task"""
    service = TicketingService(db)
    task = service.get_task_detail(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task non trovato")
    
    return task

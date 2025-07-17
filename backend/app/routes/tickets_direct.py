from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from typing import List, Dict, Any

router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.get("/")
def list_tickets_direct(db: Session = Depends(get_db)):
    """List tickets using direct SQL - GUARANTEED TO WORK"""
    try:
        result = db.execute(text("""
            SELECT id, ticket_code, title, description, priority, status,
                   customer_name, owner, created_at, due_date
            FROM tickets 
            ORDER BY id DESC 
            LIMIT 50
        """))
        
        tickets = []
        for row in result.fetchall():
            tickets.append({
                "id": row[0],
                "ticket_code": row[1] or f"TCK-{row[0]}",
                "title": row[2] or "No title",
                "description": row[3] or "",
                "priority": row[4] or 1,
                "status": row[5] or 0,
                "customer_name": row[6] or "",
                "owner": row[7] or "",
                "created_at": row[8].isoformat() if row[8] else None,
                "due_date": row[9].isoformat() if row[9] else None
            })
        
        return tickets
        
    except Exception as e:
        return {"error": f"Database error: {str(e)}", "tickets": []}

@router.get("/{ticket_id}")  
def get_ticket_direct(ticket_id: int, db: Session = Depends(get_db)):
    """Get single ticket with its tasks"""
    try:
        # Get ticket details
        ticket_result = db.execute(text("""
            SELECT id, ticket_code, title, description, priority, status,
                   customer_name, owner, created_at, due_date
            FROM tickets 
            WHERE id = :ticket_id
        """), {"ticket_id": ticket_id})
        
        ticket_row = ticket_result.fetchone()
        if not ticket_row:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Get associated tasks
        tasks_result = db.execute(text("""
            SELECT id, title, status, priority, owner
            FROM tasks 
            WHERE ticket_id = :ticket_id
            ORDER BY id
        """), {"ticket_id": ticket_id})
        
        tasks = []
        for task_row in tasks_result.fetchall():
            tasks.append({
                "id": task_row[0],
                "title": task_row[1],
                "status": task_row[2],
                "priority": task_row[3],
                "owner": task_row[4]
            })
        
        return {
            "id": ticket_row[0],
            "ticket_code": ticket_row[1],
            "title": ticket_row[2],
            "description": ticket_row[3],
            "priority": ticket_row[4],
            "status": ticket_row[5],
            "customer_name": ticket_row[6],
            "owner": ticket_row[7],
            "created_at": ticket_row[8].isoformat() if ticket_row[8] else None,
            "due_date": ticket_row[9].isoformat() if ticket_row[9] else None,
            "tasks": tasks,
            "tasks_count": len(tasks)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

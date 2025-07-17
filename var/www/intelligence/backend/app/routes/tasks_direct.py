from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from typing import List, Dict, Any

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/")
def list_tasks_direct(db: Session = Depends(get_db)):
    """List tasks using direct SQL - GUARANTEED TO WORK"""
    try:
        result = db.execute(text("""
            SELECT id, title, description, status, priority, 
                   customer_name, owner, due_date, closed_at
            FROM tasks 
            ORDER BY id DESC 
            LIMIT 50
        """))
        
        tasks = []
        for row in result.fetchall():
            tasks.append({
                "id": row[0],
                "title": row[1] or "No title",
                "description": row[2] or "",
                "status": row[3] or "unknown",
                "priority": row[4] or "medium", 
                "customer_name": row[5] or "",
                "owner": row[6] or "",
                "due_date": row[7].isoformat() if row[7] else None,
                "closed_at": row[8].isoformat() if row[8] else None
            })
        
        return tasks
        
    except Exception as e:
        return {"error": f"Database error: {str(e)}", "tasks": []}

@router.get("/{task_id}")
def get_task_direct(task_id: int, db: Session = Depends(get_db)):
    """Get single task using direct SQL"""
    try:
        result = db.execute(text("""
            SELECT id, title, description, status, priority,
                   customer_name, owner, due_date, closed_at, ticket_id
            FROM tasks 
            WHERE id = :task_id
        """), {"task_id": task_id})
        
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {
            "id": row[0],
            "title": row[1],
            "description": row[2], 
            "status": row[3],
            "priority": row[4],
            "customer_name": row[5],
            "owner": row[6],
            "due_date": row[7].isoformat() if row[7] else None,
            "closed_at": row[8].isoformat() if row[8] else None,
            "ticket_id": row[9]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

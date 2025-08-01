#!/usr/bin/env python3
"""
Task Status Hooks - Sistema per rilevare e gestire i cambi di stato dei task
"""

import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("task_status_hooks")

def on_task_status_changed(db: Session, task_id: str, old_status: str, new_status: str, user_id: str = None):
    """
    Hook chiamato quando cambia lo stato di un task
    Aggiorna il CRM e controlla se il ticket può essere chiuso
    """
    try:
        logger.info(f"🔄 Hook task status: {task_id} - {old_status} → {new_status}")
        
        # Recupera info del task e ticket collegato
        task_query = text("""
            SELECT t.id, t.title, t.ticket_id, t.status,
                   tk.ticket_code, tk.activity_id,
                   a.crm_activity_id
            FROM tasks t
            JOIN tickets tk ON t.ticket_id = tk.id
            JOIN activities a ON tk.activity_id = a.id
            WHERE t.id = CAST(:task_id AS uuid)
        """)
        
        task_result = db.execute(task_query, {"task_id": task_id}).fetchone()
        
        if not task_result:
            logger.error(f"❌ Task {task_id} non trovato")
            return False
        
        task_name = task_result[1]
        ticket_id = task_result[2]
        ticket_code = task_result[4]
        activity_id = task_result[5]
        crm_activity_id = task_result[6]
        
        logger.info(f"📋 Task: {task_name} - Ticket: {ticket_code} - CRM: {crm_activity_id}")
        
        # Aggiorna CRM con cambio stato task
        if crm_activity_id:
            try:
                import sys
                sys.path.append('/var/www/intelligence/backend')
                from app.integrations.crm_incloud.crm_update import update_activity_task_status
                
                crm_success = update_activity_task_status(
                    crm_activity_id=str(crm_activity_id),
                    ticket_code=ticket_code,
                    task_name=task_name,
                    old_status=old_status,
                    new_status=new_status
                )
                
                if crm_success:
                    logger.info(f"✅ CRM aggiornato per task {task_name}")
                else:
                    logger.warning(f"⚠️ Aggiornamento CRM fallito per task {task_name}")
                    
            except Exception as e:
                logger.error(f"❌ Errore aggiornamento CRM: {e}")
        
        # Controlla se tutti i task del ticket sono completati
        if new_status == "completed":
            check_ticket_completion(db, ticket_id, crm_activity_id, ticket_code)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Errore hook task status: {e}")
        return False

def check_ticket_completion(db: Session, ticket_id: str, crm_activity_id: int, ticket_code: str):
    """
    Controlla se tutti i task del ticket sono completati
    """
    try:
        logger.info(f"🔍 Controllo completamento ticket {ticket_code}")
        
        # Conta task del ticket
        task_count_query = text("""
            SELECT 
                COUNT(*) as total_tasks,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_tasks,
                COUNT(CASE WHEN status NOT IN ('completed', 'cancelled') THEN 1 END) as pending_tasks
            FROM tasks 
            WHERE ticket_id = CAST(:ticket_id AS uuid)
        """)
        
        counts = db.execute(task_count_query, {"ticket_id": ticket_id}).fetchone()
        
        total_tasks = counts[0]
        completed_tasks = counts[1] 
        pending_tasks = counts[2]
        
        logger.info(f"📊 Task status - Totali: {total_tasks}, Completati: {completed_tasks}, Pendenti: {pending_tasks}")
        
        # Se tutti i task sono completati, chiudi il ticket
        if pending_tasks == 0 and completed_tasks > 0:
            logger.info(f"🎯 Tutti i task completati! Chiusura ticket {ticket_code}")
            
            # Aggiorna stato ticket
            update_ticket_query = text("""
                UPDATE tickets 
                SET status = 'completed', 
                    updated_at = :now
                WHERE id = CAST(:ticket_id AS uuid)
            """)
            
            db.execute(update_ticket_query, {
                "ticket_id": ticket_id,
                "now": datetime.utcnow()
            })
            
            # Aggiorna CRM con chiusura ticket
            if crm_activity_id:
                try:
                    import sys
                    sys.path.append('/var/www/intelligence/backend')
                    from app.integrations.crm_incloud.crm_update import update_activity_ticket_closed
                    
                    crm_success = update_activity_ticket_closed(
                        crm_activity_id=str(crm_activity_id),
                        ticket_code=ticket_code,
                        total_tasks=total_tasks,
                        completed_tasks=completed_tasks
                    )
                    
                    if crm_success:
                        logger.info(f"✅ CRM aggiornato - Ticket {ticket_code} chiuso")
                        logger.info(f"🚀 Avvio FASE 2 per ticket {ticket_code}")
                        
                except Exception as e:
                    logger.error(f"❌ Errore aggiornamento CRM chiusura: {e}")
            
            db.commit()
            logger.info(f"🎉 Ticket {ticket_code} chiuso con successo!")
            
        else:
            logger.info(f"📋 Ticket {ticket_code} ancora in corso - {pending_tasks} task pendenti")
        
    except Exception as e:
        logger.error(f"❌ Errore controllo completamento ticket: {e}")
        db.rollback()

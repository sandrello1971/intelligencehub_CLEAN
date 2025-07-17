# services/database_service.py
# Database Service per IntelliChat con query robuste - IntelligenceHUB

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service per query database intelligenti"""
    
    def __init__(self):
        self.query_cache = {}
    
    def get_stats(self, db: Session) -> Dict[str, Any]:
        """Recupera statistiche generali database"""
        try:
            stats = {}
            
            # Query base con error handling individuale
            queries = {
                "companies": "SELECT COUNT(*) FROM companies",
                "users": "SELECT COUNT(*) FROM users", 
                "activities": "SELECT COUNT(*) FROM activities",
                "opportunities": "SELECT COUNT(*) FROM opportunities",
                "tasks": "SELECT COUNT(*) FROM tasks",
                "tickets": "SELECT COUNT(*) FROM tickets",
                "contacts": "SELECT COUNT(*) FROM contacts",
                "milestones": "SELECT COUNT(*) FROM milestones"
            }
            
            for key, query in queries.items():
                try:
                    result = db.execute(text(query)).scalar()
                    stats[key] = result or 0
                except Exception as e:
                    logger.error(f"Errore query {key}: {e}")
                    stats[key] = 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Errore get_stats: {e}")
            return {}
    
    def get_recent_activities(self, db: Session, limit: int = 5) -> List[Dict[str, Any]]:
        """Recupera attività recenti"""
        try:
            sql = text("""
                SELECT id, title, customer_name, created_at
                FROM activities 
                ORDER BY created_at DESC
                LIMIT :limit
            """)
            
            result = db.execute(sql, {"limit": limit})
            return [dict(row) for row in result.fetchall()]
            
        except Exception as e:
            logger.error(f"Errore get_recent_activities: {e}")
            return []
    
    def search_companies(self, db: Session, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Cerca aziende per nome"""
        try:
            sql = text("""
                SELECT id, nome, partita_iva, sector, address
                FROM companies 
                WHERE nome ILIKE :query
                ORDER BY nome
                LIMIT :limit
            """)
            
            result = db.execute(sql, {"query": f"%{query}%", "limit": limit})
            return [dict(row) for row in result.fetchall()]
            
        except Exception as e:
            logger.error(f"Errore search_companies: {e}")
            return []
    
    def get_opportunities_stats(self, db: Session) -> Dict[str, Any]:
        """Statistiche opportunità"""
        try:
            stats = {}
            
            # Conteggio per stato
            sql = text("""
                SELECT stato, COUNT(*) as count
                FROM opportunities
                GROUP BY stato
                ORDER BY count DESC
            """)
            
            result = db.execute(sql)
            stats['by_status'] = {row.stato: row.count for row in result.fetchall()}
            
            # Valore totale
            sql = text("""
                SELECT SUM(CAST(ammontare AS DECIMAL)) as total_value
                FROM opportunities
                WHERE ammontare ~ '^[0-9]+(\.[0-9]+)?$'
            """)
            
            result = db.execute(sql).scalar()
            stats['total_value'] = float(result) if result else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Errore get_opportunities_stats: {e}")
            return {}
    
    def health_check(self) -> Dict[str, Any]:
        """Health check del servizio database"""
        return {
            "healthy": True,
            "cache_size": len(self.query_cache)
        }

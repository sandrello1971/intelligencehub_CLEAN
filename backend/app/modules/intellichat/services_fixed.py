# Sostituisci il metodo get_kpi_dashboard con questo fix
def get_kpi_dashboard(self) -> Dict[str, Any]:
    """Get comprehensive KPI dashboard data"""
    try:
        # Test database connection
        result = self.db.execute(text("SELECT current_database()"))
        row = result.fetchone()
        current_db = row[0] if row else "unknown"
        
        kpi_data = {}
        
        # Total tasks
        result = self.db.execute(text("SELECT COUNT(*) FROM tasks"))
        row = result.fetchone()
        kpi_data["total_tasks"] = row[0] if row else 0
        
        # Completed tasks  
        result = self.db.execute(text("SELECT COUNT(*) FROM tasks WHERE status = 'chiuso'"))
        row = result.fetchone()
        kpi_data["completed_tasks"] = row[0] if row else 0
        
        # Open tasks
        result = self.db.execute(text("SELECT COUNT(*) FROM tasks WHERE status = 'aperto'"))
        row = result.fetchone()
        kpi_data["open_tasks"] = row[0] if row else 0
        
        # Active users
        result = self.db.execute(text("SELECT COUNT(DISTINCT owner) FROM tasks WHERE status != 'chiuso'"))
        row = result.fetchone()
        kpi_data["active_users"] = row[0] if row else 0
        
        # Open tickets
        result = self.db.execute(text("SELECT COUNT(*) FROM tickets WHERE status = 0"))
        row = result.fetchone()
        kpi_data["open_tickets"] = row[0] if row else 0
        
        # Total tickets
        result = self.db.execute(text("SELECT COUNT(*) FROM tickets"))
        row = result.fetchone()
        kpi_data["total_tickets"] = row[0] if row else 0
        
        # Companies count
        result = self.db.execute(text("SELECT COUNT(*) FROM companies"))
        row = result.fetchone()
        kpi_data["companies_count"] = row[0] if row else 0
        
        # Task status breakdown
        result = self.db.execute(text("SELECT status, COUNT(*) FROM tasks GROUP BY status"))
        task_status_breakdown = {}
        for row in result.fetchall():
            if row and len(row) >= 2:
                task_status_breakdown[row[0]] = row[1]
        
        # Calculate completion rate
        total = kpi_data["total_tasks"]
        completed = kpi_data["completed_tasks"]
        completion_rate = round((completed / total * 100), 1) if total > 0 else 0
        
        return {
            "total_tasks": kpi_data["total_tasks"],
            "completed_tasks": kpi_data["completed_tasks"],
            "open_tasks": kpi_data["open_tasks"],
            "active_users": kpi_data["active_users"],
            "open_tickets": kpi_data["open_tickets"],
            "total_tickets": kpi_data["total_tickets"], 
            "companies_count": kpi_data["companies_count"],
            "completion_rate": completion_rate,
            "task_status_breakdown": task_status_breakdown,
            "database_name": current_db,
            "last_update": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "error": f"Errore nel recupero KPI: {str(e)}",
            "total_tasks": 0,
            "completed_tasks": 0,
            "open_tasks": 0,
            "active_users": 0,
            "open_tickets": 0,
            "total_tickets": 0,
            "companies_count": 0,
            "completion_rate": 0,
            "task_status_breakdown": {},
            "database_name": "error",
            "last_update": datetime.utcnow().isoformat()
        }

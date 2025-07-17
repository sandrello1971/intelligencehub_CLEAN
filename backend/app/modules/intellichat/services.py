"""
Intelligence AI Chat Module - Services
Core AI functionality for chat, task generation, and insights
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from uuid import UUID, uuid4

from openai import OpenAI
from sqlalchemy.orm import Session
from sqlalchemy import text, func

from app.models.task import Task
from app.models.ticket import Ticket
from app.models.company import Company
from app.models.users import User
from app.models.activity import Activity
from app.modules.ticketing.services import TicketingService


class IntelliChatService:
    """Core AI service for intelligent chat and task generation"""
    
    def __init__(self, db: Session):
        self.db = db
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
        self.ticketing_service = TicketingService(db)
        
        # Session context for conversation memory
        self.session_context = {}
    
    # ===== CHAT FUNCTIONALITY =====
    
    def process_chat_message(
        self, 
        session_id: Union[str, UUID], 
        message: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Process chat message with AI and return structured response"""
        
        # Get or create session context
        session_key = str(session_id)
        if session_key not in self.session_context:
            self.session_context[session_key] = {"history": [], "last_df": None}
        
        session = self.session_context[session_key]
        
        # Build prompt with business context
        full_prompt = self._build_business_prompt(message, context, session["history"])
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.2
            )
            
            reply = response.choices[0].message.content.strip()
            
            # Parse AI response for actions
            parsed_response = self._parse_ai_response(reply)
            
            # Execute actions if requested
            if parsed_response.get("actions") and context and context.get("auto_execute"):
                executed_actions = self._execute_ai_actions(parsed_response["actions"])
                parsed_response["executed_actions"] = executed_actions
            
            # Update session history
            session["history"].append({
                "question": message,
                "answer": reply,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Add usage information
            parsed_response["usage"] = {
                "tokens": response.usage.total_tokens if response.usage else 0,
                "cost": self._calculate_cost(response.usage) if response.usage else 0
            }
            
            return parsed_response
            
        except Exception as e:
            return {
                "response": f"Mi dispiace, si è verificato un errore: {str(e)}",
                "actions": [],
                "error": True,
                "error_details": str(e)
            }
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for AI context"""
        return """
Sei un assistente AI intelligente per la gestione aziendale. 

Il tuo compito è:
1. Aiutare gli utenti con la gestione di task, ticket e attività aziendali
2. Generare automaticamente task da descrizioni naturali
3. Fornire insight e analisi sui dati aziendali
4. Rispondere in italiano in modo professionale ma amichevole

Quando l'utente chiede di creare task o ticket, restituisci una risposta JSON con:
{
  "response": "Risposta naturale all'utente",
  "actions": [
    {
      "type": "create_task|create_ticket|update_task",
      "data": {...dati per l'azione...},
      "confidence": 0.0-1.0
    }
  ],
  "needs_approval": true/false
}

Per task/ticket, includi sempre:
- title (obbligatorio)
- description 
- priority ("alta", "media", "bassa")
- customer_name (se menzionato)
"""
    
    def _build_business_prompt(
        self, 
        message: str, 
        context: Optional[Dict], 
        history: List[Dict]
    ) -> str:
        """Build comprehensive prompt with business context"""
        
        prompt_parts = []
        
        # Add conversation history
        if history:
            prompt_parts.append("Conversazione precedente:")
            for item in history[-3:]:  # Last 3 exchanges
                prompt_parts.append(f"Utente: {item['question']}")
                prompt_parts.append(f"Assistente: {item['answer']}")
        
        # Add current context
        if context:
            if context.get("current_page"):
                prompt_parts.append(f"Pagina corrente: {context['current_page']}")
            if context.get("selected_company_id"):
                company = self._get_company_context(context["selected_company_id"])
                if company:
                    prompt_parts.append(f"Azienda selezionata: {company}")
        
        # Add current message
        prompt_parts.append(f"Richiesta attuale: {message}")
        
        return "\n".join(prompt_parts)
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response for structured actions"""
        
        # Try to extract JSON from response
        try:
            # Look for JSON blocks
            if "{" in response and "}" in response:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_str = response[start:end]
                parsed = json.loads(json_str)
                
                # Validate required fields
                if "response" in parsed:
                    return parsed
        except json.JSONDecodeError:
            pass
        
        # If no valid JSON, return simple response
        return {
            "response": response,
            "actions": [],
            "needs_approval": False
        }
    
    def _execute_ai_actions(self, actions: List[Dict]) -> List[Dict]:
        """Execute AI-suggested actions"""
        executed = []
        
        for action in actions:
            try:
                action_type = action.get("type")
                action_data = action.get("data", {})
                
                if action_type == "create_task":
                    result = self._create_task_from_ai(action_data)
                    executed.append({
                        "action": action_type,
                        "success": True,
                        "result": result
                    })
                
                elif action_type == "create_ticket":
                    result = self._create_ticket_from_ai(action_data)
                    executed.append({
                        "action": action_type,
                        "success": True,
                        "result": result
                    })
                
                else:
                    executed.append({
                        "action": action_type,
                        "success": False,
                        "error": "Action type not supported"
                    })
                    
            except Exception as e:
                executed.append({
                    "action": action_type,
                    "success": False,
                    "error": str(e)
                })
        
        return executed
    
    def _create_task_from_ai(self, task_data: Dict) -> Dict:
        """Create task from AI-generated data"""
        # This would integrate with the ticketing service
        # For now, return simulation
        return {
            "task_id": "simulated_123",
            "title": task_data.get("title"),
            "description": task_data.get("description"),
            "message": "Task would be created here"
        }
    
    def _create_ticket_from_ai(self, ticket_data: Dict) -> Dict:
        """Create ticket from AI-generated data"""
        # This would integrate with the ticketing service
        return {
            "ticket_id": "simulated_456", 
            "ticket_code": f"TCK-AI-{datetime.now().strftime('%Y%m%d')}-001",
            "title": ticket_data.get("title"),
            "message": "Ticket would be created here"
        }
    
    # ===== BUSINESS INTELLIGENCE =====
    
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

        """Generate AI-powered business insights"""
        try:
            # Get data for analysis
            dashboard_data = self.get_kpi_dashboard()
            
            # Use AI to generate insights
            insight_prompt = f"""
Analizza questi dati aziendali e fornisci 3-5 insight utili:

Dati KPI:
- Task totali: {dashboard_data['total_tasks']}
- Task completati: {dashboard_data['completed_tasks']}
- Task aperti: {dashboard_data['open_tasks']}
- Tasso completamento: {dashboard_data['completion_rate']}%
- Ticket aperti: {dashboard_data['open_tickets']}
- Utenti attivi: {dashboard_data['active_users']}
- Aziende: {dashboard_data['companies_count']}

Fornisci insights in formato JSON:
{{
  "insights": [
    {{
      "title": "Titolo insight",
      "description": "Descrizione dettagliata",
      "type": "positive|warning|neutral",
      "priority": "high|medium|low",
      "suggested_action": "Azione suggerita"
    }}
  ]
}}
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Sei un consulente business che analizza KPI aziendali."},
                    {"role": "user", "content": insight_prompt}
                ],
                temperature=0.3
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content.strip()
            try:
                insights_data = json.loads(ai_response)
                return insights_data.get("insights", [])
            except json.JSONDecodeError:
                return [{
                    "title": "Analisi AI",
                    "description": ai_response,
                    "type": "neutral",
                    "priority": "medium",
                    "suggested_action": "Continua il monitoraggio"
                }]
                
        except Exception as e:
            return [{
                "title": "Errore Analisi",
                "description": f"Impossibile generare insights: {str(e)}",
                "type": "warning",
                "priority": "low",
                "suggested_action": "Verifica configurazione AI"
            }]
    
    # ===== UTILITY METHODS =====
    
    def _get_company_context(self, company_id: int) -> Optional[str]:
        """Get company context for AI prompts"""
        try:
            company = self.db.query(Company).filter(Company.id == company_id).first()
            if company:
                return f"{company.nome} (ID: {company.id})"
        except:
            pass
        return None
    
    def _calculate_cost(self, usage) -> float:
        """Calculate API cost based on token usage"""
        if not usage:
            return 0.0
        
        # GPT-4 pricing (approximate)
        cost_per_1k_tokens = 0.06 if "gpt-4" in self.model else 0.002
        return (usage.total_tokens / 1000) * cost_per_1k_tokens
    
    def clear_session_context(self, session_id: Union[str, UUID]) -> bool:
        """Clear session conversation history"""
        session_key = str(session_id)
        if session_key in self.session_context:
            del self.session_context[session_key]
            return True
        return False

    def generate_ai_insights(self, timeframe: str = "last_30_days") -> List[Dict]:
        """Generate AI-powered business insights"""
        try:
            # Get data for analysis
            dashboard_data = self.get_kpi_dashboard()
            
            # Use AI to generate insights
            insight_prompt = f"""
Analizza questi dati aziendali e fornisci 3-5 insight utili:

Dati KPI:
- Task totali: {dashboard_data['total_tasks']}
- Task completati: {dashboard_data['completed_tasks']}
- Task aperti: {dashboard_data['open_tasks']}
- Tasso completamento: {dashboard_data['completion_rate']}%
- Ticket aperti: {dashboard_data['open_tickets']}
- Utenti attivi: {dashboard_data['active_users']}
- Aziende: {dashboard_data['companies_count']}

Fornisci insights in formato JSON:
{{
  "insights": [
    {{
      "title": "Titolo insight",
      "description": "Descrizione dettagliata",
      "type": "positive|warning|neutral",
      "priority": "high|medium|low",
      "suggested_action": "Azione suggerita"
    }}
  ]
}}
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Sei un consulente business che analizza KPI aziendali."},
                    {"role": "user", "content": insight_prompt}
                ],
                temperature=0.3
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content.strip()
            try:
                insights_data = json.loads(ai_response)
                return insights_data.get("insights", [])
            except json.JSONDecodeError:
                return [{
                    "title": "Analisi AI",
                    "description": ai_response,
                    "type": "neutral",
                    "priority": "medium",
                    "suggested_action": "Continua il monitoraggio"
                }]
                
        except Exception as e:
            return [{
                "title": "Errore Analisi",
                "description": f"Impossibile generare insights: {str(e)}",
                "type": "warning",
                "priority": "low",
                "suggested_action": "Verifica configurazione AI"
            }]

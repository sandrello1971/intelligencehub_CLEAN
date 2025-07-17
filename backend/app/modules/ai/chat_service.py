"""
IntelliChat Service - Core AI Chat Engine
"""
from openai import AsyncOpenAI
from typing import Dict, Any, Optional, List
import json
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.config import settings

logger = logging.getLogger(__name__)

class IntelliChatService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        
        self.system_prompt = """
        Sei IntelliChat, l'assistente AI della piattaforma Intelligence per PMI italiane.
        
        Puoi aiutare con:
        - Gestione dati aziendali e contatti
        - Creazione e organizzazione attività e progetti  
        - Analisi business e insights
        - Integrazione con CRM e sistemi esterni
        
        Rispondi sempre in italiano, sii professionale ma cordiale.
        Se l'utente chiede di creare task o modificare dati, suggerisci le azioni ma chiedi conferma.
        """
    
    async def process_message(self, 
                            message: str,
                            user_id: int,
                            db: Session,
                            company_id: Optional[int] = None) -> Dict[str, Any]:
        """Processa messaggio utente e genera risposta AI"""
        
        try:
            # Prepara messaggi per OpenAI
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": message}
            ]
            
            # Chiamata OpenAI
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=2000,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            return {
                "response": ai_response,
                "conversation_id": f"conv_{user_id}_{int(datetime.utcnow().timestamp())}",
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Errore in process_message: {str(e)}")
            return {
                "error": "Errore nel processamento del messaggio",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

# Instance globale del servizio
chat_service = IntelliChatService()

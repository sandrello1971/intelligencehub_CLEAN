# services/ai_service.py
# AI Service per IntelliChat con database integration - IntelligenceHUB

import openai
import os
import asyncio
from typing import Dict, Any, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

class AIService:
    """Service per integrazione AI/OpenAI con database context"""
    
    def __init__(self):
        # Configura OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.has_openai = bool(openai.api_key)
        if not self.has_openai:
            logger.warning("OPENAI_API_KEY non configurata - usando fallback intelligente")
    
    async def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
        model: str = "gpt-3.5-turbo"
    ) -> Dict[str, Any]:
        """
        Genera risposta AI usando OpenAI o fallback intelligente
        """
        try:
            # Fallback intelligente con context database
            if not self.has_openai:
                return self._generate_fallback_response(prompt, context)
            
            # Prepara messages per OpenAI
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Aggiungi context se disponibile
            if context:
                messages.append({"role": "system", "content": f"Context: {context}"})
            
            messages.append({"role": "user", "content": prompt})
            
            # Chiamata OpenAI
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return {
                "response": response.choices[0].message.content.strip(),
                "model": model,
                "usage": response.usage
            }
            
        except Exception as e:
            logger.error(f"Errore OpenAI: {e}")
            return self._generate_fallback_response(prompt, context)
    
    def _generate_fallback_response(self, prompt: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Genera risposta fallback intelligente basata su context
        """
        prompt_lower = prompt.lower()
        
        # Parsing intelligente del context per statistiche
        if context:
            stats_response = self._parse_stats_from_context(context, prompt_lower)
            if stats_response:
                return {
                    "response": stats_response,
                    "model": "intelligent-fallback",
                    "usage": {"total_tokens": 0}
                }
        
        # Risposte predefinite per query comuni
        if any(keyword in prompt_lower for keyword in ['quante', 'numero', 'count', 'statistiche']):
            if context:
                return {
                    "response": f"Basandomi sui dati disponibili nel sistema:\n\n{context}\n\nQueste sono le statistiche principali di Intelligence Platform.",
                    "model": "database-stats",
                    "usage": {"total_tokens": 0}
                }
        
        # Risposta generica
        return {
            "response": f"Ho ricevuto la tua richiesta: '{prompt}'. Il sistema sta elaborando le informazioni disponibili per fornirti una risposta accurata.",
            "model": "fallback",
            "usage": {"total_tokens": 0}
        }
    
    def _parse_stats_from_context(self, context: str, prompt: str) -> Optional[str]:
        """
        Parsing intelligente del context per estrarre statistiche
        """
        lines = context.split('\n')
        stats = {}
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                stats[key.strip()] = value.strip()
        
        if not stats:
            return None
        
        # Genera risposta basata sul tipo di domanda
        if 'aziende' in prompt:
            companies = stats.get('Numero aziende nel database', 'N/A')
            return f"📊 Nel database di Intelligence Platform ci sono attualmente **{companies} aziende** registrate."
        
        elif 'statistiche' in prompt or 'completa' in prompt:
            response_parts = ["📊 **Statistiche Complete di Intelligence Platform:**\n"]
            
            if 'Numero aziende nel database' in stats:
                response_parts.append(f"🏢 **Aziende**: {stats['Numero aziende nel database']}")
            if 'Numero utenti nel database' in stats:
                response_parts.append(f"👥 **Utenti**: {stats['Numero utenti nel database']}")
            if 'Numero attività nel database' in stats:
                response_parts.append(f"⚡ **Attività**: {stats['Numero attività nel database']}")
            if 'Numero opportunità nel database' in stats:
                response_parts.append(f"💼 **Opportunità**: {stats['Numero opportunità nel database']}")
            
            response_parts.append(f"\n✨ Sistema completamente operativo con gestione intelligente dei dati aziendali!")
            return "\n".join(response_parts)
        
        return None
    
    def health_check(self) -> Dict[str, Any]:
        """Health check del servizio AI"""
        return {
            "healthy": True,
            "has_openai": self.has_openai,
            "model": "gpt-3.5-turbo" if self.has_openai else "intelligent-fallback"
        }

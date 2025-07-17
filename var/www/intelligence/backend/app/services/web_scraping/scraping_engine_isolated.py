"""
Scraping Engine Isolato - Intelligence Platform
Versione sicura che usa webscraping_final_working.py
"""
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class SafeScrapingEngine:
    def __init__(self):
        self.initialized = False
        self._initialize()
    
    def _initialize(self):
        """Inizializzazione sicura del motore"""
        try:
            # Import del modulo che sappiamo funzionare
            from app.services.web_scraping.webscraping_final_working import webscraping_final_working
            self.scraper = webscraping_final_working
            self.initialized = True
            logger.info("✅ SafeScrapingEngine inizializzato")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione: {e}")
            self.initialized = False
    
    async def scrape_url_safe(self, url: str) -> Dict[str, Any]:
        """Scraping sicuro con fallback"""
        if not self.initialized:
            logger.warning("⚠️ Engine non inizializzato, uso fallback")
            return self._fallback_scrape(url)
        
        try:
            logger.info(f"🌐 Inizio scraping: {url}")
            
            # Usa il webscraping funzionante
            result = await self.scraper.scrape_website(url)
            
            if result and result.get("content"):
                logger.info(f"✅ Scraping completato: {len(result['content'])} caratteri")
                return {
                    "success": True,
                    "url": url,
                    "content": result["content"],
                    "title": result.get("title", ""),
                    "metadata": result.get("metadata", {}),
                    "scraped_at": datetime.utcnow().isoformat()
                }
            else:
                logger.warning(f"⚠️ Contenuto vuoto per {url}")
                return self._fallback_scrape(url)
                
        except Exception as e:
            logger.error(f"❌ Errore scraping {url}: {e}")
            return self._fallback_scrape(url)
    
    def _fallback_scrape(self, url: str) -> Dict[str, Any]:
        """Fallback quando il scraping principale fallisce"""
        return {
            "success": False,
            "url": url,
            "content": f"Contenuto non disponibile per {url}",
            "title": "Scraping non riuscito",
            "metadata": {"error": "fallback_used"},
            "scraped_at": datetime.utcnow().isoformat()
        }
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Status del motore"""
        return {
            "initialized": self.initialized,
            "engine_version": "1.0-safe",
            "last_check": datetime.utcnow().isoformat()
        }

# Istanza globale
safe_engine = SafeScrapingEngine()

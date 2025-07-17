"""
🌐 WebScraping Wrapper Final - Con Adapter Intelligence Engine
Versione finale che usa adapter per engine originale + fallback bulletproof
"""

import logging
import asyncio
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class WebScrapingEngineWrapperFinal:
    """
    Wrapper finale che usa adapter per engine originale
    """
    
    def __init__(self):
        self.adapter = None
        self.fallback_engine = None
        self._initialize_engines()
    
    def _initialize_engines(self):
        """Inizializza adapter e fallback"""
        try:
            from .scraping_adapter import scraping_adapter
            self.adapter = scraping_adapter
            logger.info("✅ Scraping Adapter caricato")
        except Exception as e:
            logger.warning(f"⚠️ Adapter non disponibile: {e}")
            self.adapter = None
        
        # Fallback sempre disponibile
        from .webscraping_wrapper_bulletproof import BulletproofScrapingEngine
        self.fallback_engine = BulletproofScrapingEngine()
        logger.info("✅ Fallback engine pronto")
    
    async def scrape_website(self, url: str) -> Dict[str, Any]:
        """
        Scrape con adapter intelligence engine + fallback
        """
        # Prova adapter per engine originale
        if self.adapter:
            try:
                logger.info(f"🔧 Tentativo con Intelligence Engine Adapter: {url}")
                result = await self.adapter.scrape_website(url)
                
                if result and result.get('content'):
                    logger.info(f"✅ Intelligence Engine Adapter successo: {url}")
                    return result
                else:
                    logger.warning(f"⚠️ Adapter: risultato vuoto per {url}")
                    
            except Exception as e:
                logger.error(f"❌ Adapter fallito per {url}: {e}")
        
        # Fallback engine
        logger.info(f"🔄 Usando fallback engine per: {url}")
        try:
            result = await self.fallback_engine.scrape_website(url)
            if result:
                logger.info(f"✅ Fallback successo: {url}")
                return result
        except Exception as e:
            logger.error(f"❌ Anche fallback fallito per {url}: {e}")
        
        # Fallback finale
        return {
            "title": f"Contenuto non accessibile",
            "content": f"Non è stato possibile estrarre contenuto da {url}",
            "url": url,
            "confidence_score": 0.1,
            "extraction_method": "final_fallback"
        }

# Istanza globale
webscraping_engine_wrapper_final = WebScrapingEngineWrapperFinal()

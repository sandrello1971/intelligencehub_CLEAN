"""
🔧 Scraping Adapter - Converte URL string in ScrapedWebsiteModel
Risolve il problema 'str' object has no attribute 'id'
"""

import logging
from urllib.parse import urlparse
from typing import Dict, Any, Optional
from models.scraped_data import ScrapedWebsiteModel
from scraping_engine import IntelligenceWebScrapingEngine

logger = logging.getLogger(__name__)

class ScrapingAdapter:
    """
    Adapter che permette di usare l'engine originale con URL string
    """
    
    def __init__(self):
        self.engine = IntelligenceWebScrapingEngine()
        self._next_id = 1
    
    def _url_to_model(self, url: str) -> ScrapedWebsiteModel:
        """Converte URL string in ScrapedWebsiteModel"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Crea modello con dati minimi richiesti
        model = ScrapedWebsiteModel(
            url=url,
            domain=domain,
            title="",  # Sarà estratto durante scraping
            description="",
            respect_robots_txt=True,
            max_depth=1,
            follow_external_links=False
        )
        
        # Imposta ID temporaneo (evita errore 'None')
        model.id = self._next_id
        self._next_id += 1
        
        return model
    
    async def scrape_website(self, url: str) -> Dict[str, Any]:
        """
        Scrape website usando URL string - compatibile con wrapper
        """
        try:
            logger.info(f"🔧 Adapter: Convertendo URL {url} in modello")
            
            # Converti URL in modello
            website_model = self._url_to_model(url)
            
            logger.info(f"✅ Modello creato: ID={website_model.id}, Domain={website_model.domain}")
            
            # Usa engine originale
            result = await self.engine.scrape_website(website_model)
            
            if result and result.get('content_extracted'):
                # Trasforma in formato compatibile con wrapper
                content_items = result.get('content_extracted', [])
                if content_items:
                    first_content = content_items[0]
                    return {
                        "title": first_content.get('title', 'Documento Web'),
                        "content": first_content.get('content', ''),
                        "url": url,
                        "confidence_score": first_content.get('confidence_score', 0.8),
                        "extraction_method": "intelligence_engine_adapter",
                        "pages_scraped": result.get('pages_scraped', 0),
                        "original_result": result
                    }
            
            # Se nessun contenuto estratto ma nessun errore
            logger.warning(f"⚠️ Engine ha funzionato ma nessun contenuto per {url}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Adapter error per {url}: {e}")
            return None

# Istanza globale
scraping_adapter = ScrapingAdapter()

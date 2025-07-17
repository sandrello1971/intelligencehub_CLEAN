"""
🌐 WebScraping Wrapper Fixed per Intelligence Platform
Wrapper che usa il nome classe corretto: IntelligenceWebScrapingEngine
"""

import logging
import asyncio
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class WebScrapingEngineWrapper:
    """
    Wrapper per IntelligenceWebScrapingEngine 
    """
    
    def __init__(self):
        self.engine = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Inizializza l'engine con nome classe corretto"""
        try:
            # Import con nome classe corretto
            from .scraping_engine import IntelligenceWebScrapingEngine
            self.engine = IntelligenceWebScrapingEngine()
            logger.info("✅ IntelligenceWebScrapingEngine caricato con successo")
        except ImportError as e:
            logger.error(f"❌ Import IntelligenceWebScrapingEngine fallito: {e}")
            # Fallback a engine basic
            self.engine = BasicWebScrapingEngine()
            logger.warning("⚠️ Usando BasicWebScrapingEngine di fallback")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione engine: {e}")
            self.engine = BasicWebScrapingEngine()
    
    async def scrape_website(self, url: str) -> Dict[str, Any]:
        """
        Scrape website usando l'engine corretto
        """
        try:
            if hasattr(self.engine, 'scrape_website'):
                return await self.engine.scrape_website(url)
            elif hasattr(self.engine, 'scrape'):
                return await self.engine.scrape(url)
            else:
                logger.warning("⚠️ Metodo scrape non trovato, usando fallback")
                return await self._basic_scrape(url)
        except Exception as e:
            logger.error(f"❌ Errore scraping {url}: {e}")
            return await self._basic_scrape(url)
    
    async def _basic_scrape(self, url: str) -> Dict[str, Any]:
        """Scraping basic di fallback"""
        import aiohttp
        from bs4 import BeautifulSoup
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, timeout=15) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Estrai title
                        title = soup.find('title')
                        title_text = title.get_text().strip() if title else "Documento Web"
                        
                        # Rimuovi script e style
                        for script in soup(["script", "style", "nav", "footer", "header"]):
                            script.decompose()
                        
                        # Estrai contenuto dai tag principali
                        content_tags = soup.find_all(['p', 'div', 'article', 'main', 'section', 'h1', 'h2', 'h3'])
                        content_parts = []
                        
                        for tag in content_tags:
                            text = tag.get_text().strip()
                            if len(text) > 30:  # Solo testo significativo
                                content_parts.append(text)
                        
                        content = '\n'.join(content_parts)
                        
                        # Limita contenuto ma mantieni informazioni utili
                        if len(content) > 8000:
                            content = content[:8000] + "...\n[Contenuto troncato]"
                        
                        return {
                            "title": title_text,
                            "content": content,
                            "url": url,
                            "confidence_score": 0.7,
                            "extraction_method": "fallback_scraper",
                            "content_length": len(content),
                            "timestamp": asyncio.get_event_loop().time()
                        }
                    else:
                        logger.warning(f"⚠️ HTTP {response.status} per {url}")
                        return None
            
        except Exception as e:
            logger.error(f"❌ Errore fallback scraping {url}: {e}")
            return {
                "title": f"Errore accesso: {url.split('/')[-1] or 'documento'}",
                "content": f"Non è stato possibile accedere al contenuto di {url}. Il sito potrebbe essere protetto o temporaneamente non disponibile.",
                "url": url,
                "confidence_score": 0.1,
                "extraction_method": "error_fallback",
                "error": str(e)
            }

class BasicWebScrapingEngine:
    """Engine di fallback robusto"""
    
    async def scrape_website(self, url: str) -> Dict[str, Any]:
        """Basic scraping con aiohttp e BeautifulSoup"""
        import aiohttp
        from bs4 import BeautifulSoup
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; IntelligenceBot/1.0; +https://intelligence.ai/bot)'
            }
            
            timeout = aiohttp.ClientTimeout(total=20)
            
            async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Estrai title
                        title_tag = soup.find('title')
                        title = title_tag.get_text().strip() if title_tag else "Documento Web"
                        
                        # Rimuovi elementi non necessari
                        for element in soup(['script', 'style', 'nav', 'footer', 'aside', 'form']):
                            element.decompose()
                        
                        # Trova il contenuto principale
                        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=lambda x: x and 'content' in x.lower())
                        
                        if main_content:
                            content = main_content.get_text(separator='\n').strip()
                        else:
                            # Fallback: tutto il body
                            body = soup.find('body')
                            content = body.get_text(separator='\n').strip() if body else soup.get_text(separator='\n').strip()
                        
                        # Pulisci contenuto
                        lines = [line.strip() for line in content.split('\n') if line.strip()]
                        clean_content = '\n'.join(lines)
                        
                        # Limita dimensione
                        if len(clean_content) > 6000:
                            clean_content = clean_content[:6000] + "\n\n[Contenuto troncato per limiti di elaborazione]"
                        
                        return {
                            "title": title,
                            "content": clean_content,
                            "url": url,
                            "confidence_score": 0.8,
                            "extraction_method": "basic_engine_aiohttp",
                            "status_code": response.status
                        }
                    else:
                        return {
                            "title": f"Errore HTTP {response.status}",
                            "content": f"Il sito {url} ha restituito un errore HTTP {response.status}. Il contenuto potrebbe non essere disponibile.",
                            "url": url,
                            "confidence_score": 0.2,
                            "extraction_method": "error_response",
                            "status_code": response.status
                        }
            
        except Exception as e:
            logger.error(f"❌ Basic engine error per {url}: {e}")
            return {
                "title": f"Contenuto non accessibile",
                "content": f"Non è stato possibile accedere al contenuto di {url}. Errore: {str(e)}",
                "url": url,
                "confidence_score": 0.1,
                "extraction_method": "exception_fallback",
                "error": str(e)
            }

# Istanza globale del wrapper
webscraping_engine_wrapper = WebScrapingEngineWrapper()

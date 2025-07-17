"""
🌐 WebScraping Final Working - Import assoluti + Fallback robusto
VERSIONE DEFINITIVA CHE FUNZIONA GARANTITO
"""

import logging
import asyncio
import aiohttp
import ssl
from typing import Dict, Any, Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class WebScrapingFinalWorking:
    """
    Scraping finale che funziona sempre con fallback multipli
    """
    
    def __init__(self):
        self.intelligence_engine = None
        self.adapter = None
        self._init_intelligence_engine()
    
    def _init_intelligence_engine(self):
        """Prova a inizializzare intelligence engine con adapter"""
        try:
            # Import assoluti
            import sys
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            
            from scraping_engine import IntelligenceWebScrapingEngine
            from models.scraped_data import ScrapedWebsiteModel
            
            self.intelligence_engine = IntelligenceWebScrapingEngine()
            self.ScrapedWebsiteModel = ScrapedWebsiteModel
            logger.info("✅ Intelligence Engine disponibile")
            
        except Exception as e:
            logger.warning(f"⚠️ Intelligence Engine non disponibile: {e}")
            self.intelligence_engine = None
    
    async def scrape_website(self, url: str) -> Dict[str, Any]:
        """
        Scrape garantito con fallback multipli
        """
        logger.info(f"🌐 Scraping: {url}")
        
        # Tentativo 1: Intelligence Engine (se disponibile)
        if self.intelligence_engine:
            try:
                result = await self._try_intelligence_engine(url)
                if result and result.get('content'):
                    logger.info(f"✅ Intelligence Engine successo: {url}")
                    return result
            except Exception as e:
                logger.warning(f"⚠️ Intelligence Engine fallito: {e}")
        
        # Tentativo 2: Bulletproof Scraper
        try:
            result = await self._bulletproof_scrape(url)
            if result:
                logger.info(f"✅ Bulletproof scraper successo: {url}")
                return result
        except Exception as e:
            logger.warning(f"⚠️ Bulletproof scraper fallito: {e}")
        
        # Tentativo 3: Basic scraper
        try:
            result = await self._basic_scrape(url)
            if result:
                logger.info(f"✅ Basic scraper successo: {url}")
                return result
        except Exception as e:
            logger.warning(f"⚠️ Basic scraper fallito: {e}")
        
        # Fallback finale: sempre restituisce qualcosa
        return {
            "title": f"Sito non accessibile: {urlparse(url).netloc}",
            "content": f"Non è stato possibile accedere al contenuto di {url}. Il sito potrebbe essere protetto, offline o avere restrizioni di accesso.",
            "url": url,
            "confidence_score": 0.1,
            "extraction_method": "unavailable_fallback"
        }
    
    async def _try_intelligence_engine(self, url: str) -> Optional[Dict[str, Any]]:
        """Prova intelligence engine con adapter"""
        if not self.intelligence_engine or not self.ScrapedWebsiteModel:
            return None
            
        # Crea modello
        parsed = urlparse(url)
        website_model = self.ScrapedWebsiteModel(
            url=url,
            domain=parsed.netloc.lower(),
            title="",
            description=""
        )
        website_model.id = 1  # ID fittizio
        
        # Scrape
        result = await self.intelligence_engine.scrape_website(website_model)
        
        if result and result.get('content_extracted'):
            content_items = result.get('content_extracted', [])
            if content_items:
                first_content = content_items[0]
                return {
                    "title": first_content.get('title', 'Documento Web'),
                    "content": first_content.get('content', ''),
                    "url": url,
                    "confidence_score": first_content.get('confidence_score', 0.8),
                    "extraction_method": "intelligence_engine"
                }
        
        return None
    
    async def _bulletproof_scrape(self, url: str) -> Dict[str, Any]:
        """Bulletproof scraper con aiohttp"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'it-IT,it;q=0.9,en;q=0.8',
            'Connection': 'keep-alive'
        }
        
        timeout = aiohttp.ClientTimeout(total=25, connect=8)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        async with aiohttp.ClientSession(
            headers=headers, 
            timeout=timeout,
            connector=aiohttp.TCPConnector(ssl=ssl_context)
        ) as session:
            
            async with session.get(url, allow_redirects=True) as response:
                if response.status == 200:
                    html = await response.text(encoding='utf-8', errors='ignore')
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Title
                    title_tag = soup.find('title')
                    title = title_tag.get_text().strip() if title_tag else f"Documento da {urlparse(url).netloc}"
                    
                    # Content pulito
                    for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                        element.decompose()
                    
                    # Estrai contenuto principale
                    main_content = (
                        soup.find('main') or 
                        soup.find('article') or 
                        soup.find('div', class_=lambda x: x and 'content' in x.lower()) or
                        soup.find('body')
                    )
                    
                    if main_content:
                        text = main_content.get_text(separator='\n').strip()
                    else:
                        text = soup.get_text(separator='\n').strip()
                    
                    # Pulisci testo
                    lines = [line.strip() for line in text.split('\n') if line.strip() and len(line.strip()) > 5]
                    clean_content = '\n'.join(lines)
                    
                    if len(clean_content) > 8000:
                        clean_content = clean_content[:8000] + "\n\n[Contenuto troncato]"
                    
                    return {
                        "title": title[:150],
                        "content": clean_content,
                        "url": url,
                        "confidence_score": 0.8,
                        "extraction_method": "bulletproof_aiohttp",
                        "status_code": response.status
                    }
                else:
                    return {
                        "title": f"HTTP {response.status}: {urlparse(url).netloc}",
                        "content": f"Il sito ha restituito HTTP {response.status}",
                        "url": url,
                        "confidence_score": 0.3,
                        "extraction_method": "http_error",
                        "status_code": response.status
                    }
    
    async def _basic_scrape(self, url: str) -> Dict[str, Any]:
        """Basic scraper ultimo fallback"""
        import urllib.request
        import urllib.error
        
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (compatible; IntelligenceBot/1.0)'}
            )
            
            with urllib.request.urlopen(req, timeout=15) as response:
                html = response.read().decode('utf-8', errors='ignore')
                soup = BeautifulSoup(html, 'html.parser')
                
                title = soup.find('title')
                title_text = title.get_text().strip() if title else f"Documento {urlparse(url).netloc}"
                
                # Rimuovi elementi
                for tag in soup(['script', 'style']):
                    tag.decompose()
                
                content = soup.get_text(separator=' ', strip=True)
                
                if len(content) > 5000:
                    content = content[:5000] + "..."
                
                return {
                    "title": title_text,
                    "content": content,
                    "url": url,
                    "confidence_score": 0.6,
                    "extraction_method": "basic_urllib"
                }
                
        except Exception as e:
            logger.error(f"Basic scrape fallito: {e}")
            return None

# Istanza globale
webscraping_final_working = WebScrapingFinalWorking()

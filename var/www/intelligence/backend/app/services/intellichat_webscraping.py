"""
🧠 Intellichat Web Scraping Integration Service
Servizio indipendente per integrare web scraping nell'intellichat
"""

import re
import logging
from typing import List, Dict, Any, Optional
import aiohttp
import asyncio

logger = logging.getLogger(__name__)

class IntellichatWebScrapingService:
    """
    Servizio per gestire richieste di web scraping dall'intellichat
    """
    
    def __init__(self):
        self.base_url = "http://localhost:8000"  # URL dell'API interna
        self.url_patterns = [
            r'https?://[^\s<>"]+',
            r'www\.[^\s<>"]+',
        ]
        
    def extract_urls_from_message(self, message: str) -> List[str]:
        """Estrae URL dal messaggio dell'utente"""
        urls = []
        for pattern in self.url_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            urls.extend(matches)
        
        # Normalizza URL
        normalized_urls = []
        for url in urls:
            if not url.startswith(('http://', 'https://')):
                if url.startswith('www.'):
                    url = 'https://' + url
                else:
                    url = 'https://' + url
            normalized_urls.append(url)
            
        return list(set(normalized_urls))
    
    def detect_scraping_intent(self, message: str) -> bool:
        """Rileva se l'utente vuole scrappare contenuti"""
        scraping_keywords = [
            'scrappa', 'scrape', 'estrai', 'analizza sito', 
            'leggi sito', 'importa da', 'carica da web',
            'aggiungi sito', 'scarica contenuto', 'scraping'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in scraping_keywords)
    
    async def process_scraping_request(self, message: str, user_id: str = None) -> Dict[str, Any]:
        """
        Processa richiesta di scraping dall'intellichat
        """
        try:
            urls = self.extract_urls_from_message(message)
            has_scraping_intent = self.detect_scraping_intent(message)
            
            if not urls:
                return {
                    "type": "no_urls",
                    "message": "Non ho rilevato URL nel tuo messaggio."
                }
            
            if has_scraping_intent:
                # Esegui scraping
                return await self._execute_scraping(urls)
            else:
                # Suggerisci scraping
                return {
                    "type": "suggestion",
                    "urls": urls,
                    "message": f"Ho rilevato {len(urls)} URL. Vuoi che li aggiunga alla knowledge base per poter rispondere alle tue domande utilizzando anche questi contenuti?"
                }
                
        except Exception as e:
            logger.error(f"Errore processing scraping request: {str(e)}")
            return {
                "type": "error",
                "message": f"Si è verificato un errore nell'elaborazione della richiesta: {str(e)}"
            }
    
    async def _execute_scraping(self, urls: List[str]) -> Dict[str, Any]:
        """Esegue lo scraping degli URL"""
        try:
            results = []
            
            for url in urls:
                try:
                    # Simula chiamata all'API interna (in produzione useresti aiohttp)
                    from services.web_scraping.scraping_engine import WebScrapingEngine
                    from services.web_scraping.knowledge_base_integration_corrected import KnowledgeBaseIntegration
                    
                    scraping_engine = WebScrapingEngine()
                    kb_integration = KnowledgeBaseIntegration()
                    
                    # Scrape content
                    scraped_data = await scraping_engine.scrape_website(url)
                    
                    if scraped_data:
                        # Integra con knowledge base
                        knowledge_doc_id = await kb_integration.create_knowledge_document_from_scraped(
                            scraped_data=scraped_data,
                            url=url
                        )
                        
                        results.append({
                            "url": url,
                            "success": True,
                            "knowledge_document_id": str(knowledge_doc_id),
                            "title": scraped_data.get("title", "Senza titolo")
                        })
                    else:
                        results.append({
                            "url": url,
                            "success": False,
                            "error": "Contenuto non estratto"
                        })
                        
                except Exception as e:
                    results.append({
                        "url": url,
                        "success": False,
                        "error": str(e)
                    })
            
            successful = len([r for r in results if r["success"]])
            total = len(results)
            
            if successful > 0:
                return {
                    "type": "success",
                    "results": results,
                    "message": f"✅ Ho aggiunto {successful}/{total} siti alla knowledge base. Ora posso utilizzare questi contenuti per rispondere alle tue domande!"
                }
            else:
                return {
                    "type": "partial_failure",
                    "results": results,
                    "message": f"❌ Non sono riuscito a processare nessuno dei {total} URL forniti."
                }
                
        except Exception as e:
            logger.error(f"Errore execute scraping: {str(e)}")
            return {
                "type": "error",
                "message": f"Errore durante il processamento degli URL: {str(e)}"
            }

# Istanza globale del servizio
webscraping_service = IntellichatWebScrapingService()

async def handle_webscraping_in_chat(message: str, user_id: str = None) -> Dict[str, Any]:
    """
    Funzione helper per integrare web scraping nell'intellichat
    Da chiamare dal route intellichat esistente
    """
    return await webscraping_service.process_scraping_request(message, user_id)

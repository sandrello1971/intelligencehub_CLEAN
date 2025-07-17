"""
🧠 Intellichat Web Scraping Integration Service - FIXED DEFINITIVO
Versione che usa webscraping_final_working GARANTITO
"""

import re
import logging
from typing import List, Dict, Any, Optional
import asyncio

logger = logging.getLogger(__name__)

class IntellichatWebScrapingServiceFixed:
    """
    Servizio finale per web scraping dall'intellichat - FIXED
    """
    
    def __init__(self):
        self.url_patterns = [
            r'https?://[^\s<>"]+',
            r'www\.[^\s<>"]+(?:\.[a-zA-Z]{2,})',
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
            'aggiungi sito', 'scarica contenuto', 'scraping',
            'leggi il contenuto', 'aggiungi alla knowledge'
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
                    "message": "Non ho rilevato URL nel tuo messaggio.",
                    "has_webscraping": False
                }
            
            if has_scraping_intent:
                # Esegui scraping
                return await self._execute_scraping(urls, user_id)
            else:
                # Suggerisci scraping
                return {
                    "type": "suggestion",
                    "urls": urls,
                    "has_webscraping": True,
                    "message": f"Ho rilevato {len(urls)} URL nel tuo messaggio:\n" + 
                              "\n".join([f"• {url}" for url in urls]) +
                              f"\n\nVuoi che li aggiunga alla knowledge base? Potrò utilizzare questi contenuti per rispondere alle tue domande future."
                }
                
        except Exception as e:
            logger.error(f"Errore processing scraping request: {str(e)}")
            return {
                "type": "error",
                "message": f"Si è verificato un errore nell'elaborazione della richiesta: {str(e)}",
                "has_webscraping": False
            }
    
    async def _execute_scraping(self, urls: List[str], user_id: str = None) -> Dict[str, Any]:
        """Esegue lo scraping degli URL usando webscraping_final_working"""
        try:
            # Import DIRETTO del modulo funzionante
            from services.web_scraping.webscraping_final_working import webscraping_final_working
            from services.web_scraping.knowledge_base_integration_isolated import kb_integration_fixed
            
            results = []
            
            for url in urls:
                try:
                    logger.info(f"🌐 Scraping URL: {url}")
                    
                    # Scrape content usando webscraping_final_working
                    scraped_data = await webscraping_final_working.scrape_website(url)
                    
                    if scraped_data and scraped_data.get("content") and len(scraped_data.get("content", "")) > 50:
                        # Integra con knowledge base
                        knowledge_doc_id = await kb_integration_fixed.create_knowledge_document_from_scraped(
                            scraped_data=scraped_data,
                            url=url,
                            user_id=user_id
                        )
                        
                        results.append({
                            "url": url,
                            "success": True,
                            "knowledge_document_id": str(knowledge_doc_id),
                            "title": scraped_data.get("title", "Senza titolo"),
                            "content_length": len(scraped_data.get("content", "")),
                            "extraction_method": scraped_data.get("extraction_method", "unknown")
                        })
                        
                        logger.info(f"✅ URL {url} scrappato e aggiunto alla knowledge base")
                    else:
                        results.append({
                            "url": url,
                            "success": False,
                            "error": "Contenuto non estratto, troppo corto o non accessibile"
                        })
                        
                except Exception as e:
                    logger.error(f"❌ Errore scraping {url}: {str(e)}")
                    results.append({
                        "url": url,
                        "success": False,
                        "error": str(e)
                    })
            
            successful = len([r for r in results if r["success"]])
            total = len(results)
            
            if successful > 0:
                successful_titles = [r["title"] for r in results if r["success"]]
                return {
                    "type": "success",
                    "results": results,
                    "has_webscraping": True,
                    "message": f"✅ Perfetto! Ho aggiunto {successful}/{total} siti alla knowledge base:\n" +
                              "\n".join([f"• {title}" for title in successful_titles]) +
                              f"\n\nOra posso utilizzare questi contenuti per rispondere alle tue domande!"
                }
            else:
                return {
                    "type": "failure",
                    "results": results,
                    "has_webscraping": True,
                    "message": f"❌ Non sono riuscito a processare nessuno dei {total} URL forniti. I siti potrebbero essere protetti o non accessibili."
                }
                
        except Exception as e:
            logger.error(f"Errore execute scraping: {str(e)}")
            return {
                "type": "error",
                "message": f"Errore durante il processamento degli URL: {str(e)}",
                "has_webscraping": False
            }

# Istanza globale del servizio
webscraping_service_fixed = IntellichatWebScrapingServiceFixed()

async def handle_webscraping_in_chat_final(message: str, user_id: str = None) -> Dict[str, Any]:
    """
    Funzione helper FIXED per integrare web scraping nell'intellichat
    """
    return await webscraping_service_fixed.process_scraping_request(message, user_id)

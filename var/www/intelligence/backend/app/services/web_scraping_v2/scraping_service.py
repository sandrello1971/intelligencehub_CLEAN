import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import hashlib
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ScrapingService:
    """Servizio dedicato solo al scraping HTML"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.timeout = 30
    
    def scrape_url(self, url: str) -> Dict:
        """
        Scrape URL e restituisce dati puliti
        Returns: {success: bool, data: dict, error: str}
        """
        try:
            logger.info(f"Starting scraping: {url}")
            
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return {"success": False, "error": "Invalid URL format"}
            
            # HTTP Request
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract data
            title = self._extract_title(soup)
            content = self._extract_clean_content(soup)
            domain = parsed_url.netloc
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            return {
                "success": True,
                "data": {
                    "url": url,
                    "domain": domain,
                    "title": title,
                    "content": content,
                    "content_hash": content_hash,
                    "raw_html": response.text
                },
                "error": None
            }
            
        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            return {"success": False, "error": f"Request failed: {str(e)}"}
        except Exception as e:
            logger.error(f"Scraping failed for {url}: {e}")
            return {"success": False, "error": f"Scraping failed: {str(e)}"}
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Estrai title dalla pagina"""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        # Fallback to h1
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()
        
        return "No title found"
    
    def _extract_clean_content(self, soup: BeautifulSoup) -> str:
        """Estrai contenuto pulito per vettorizzazione"""
        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "header", "footer", "aside", "noscript"]):
            element.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = ' '.join(chunk for chunk in chunks if chunk)
        
        return clean_text

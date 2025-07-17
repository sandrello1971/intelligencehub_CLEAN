import asyncio
import logging
import hashlib
import re
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from datetime import datetime
import aiohttp
import json

from playwright.async_api import async_playwright, Browser, Page
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from app.services.web_scraping.models.scraped_data import (
    ScrapedWebsiteModel,
    ScrapedContentModel,
    ScrapedContactModel,
    ScrapedCompanyModel,
    ContentType,
    ScrapingStatus
)

logger = logging.getLogger(__name__)

class IntelligenceWebScrapingEngine:
    """
    🕷️ Intelligence Web Scraping Engine
    
    Features:
    - Respectful scraping con robots.txt
    - JavaScript support via Playwright
    - Intelligent content extraction
    - Rate limiting automatico
    - Error handling robusto
    """
    
    def __init__(self, 
                 rate_limit_delay: float = 2.0,
                 max_concurrent: int = 3,
                 timeout: int = 30):
        
        self.rate_limit_delay = rate_limit_delay
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.ua = UserAgent()
        
        # Semaforo per limitare richieste concorrenti
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # Contatori per statistiche
        self.stats = {
            'pages_scraped': 0,
            'content_extracted': 0,
            'contacts_found': 0,
            'companies_found': 0,
            'errors': 0
        }
    
    async def __aenter__(self):
        """Inizializza risorse asincrone"""
        try:
            # Avvia Playwright
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--disable-gpu',
                    '--window-size=1920x1080',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            # Crea sessione HTTP
            connector = aiohttp.TCPConnector(limit=10, ssl=False)
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'User-Agent': self.ua.random,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
            )
            
            logger.info("Intelligence WebScrapingEngine initialized successfully")
            return self
            
        except Exception as e:
            logger.error(f"Failed to initialize WebScrapingEngine: {str(e)}")
            raise
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Pulisce risorse"""
        if self.session:
            await self.session.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
            
        logger.info("Intelligence WebScrapingEngine closed")
    
    async def scrape_website(self, website: ScrapedWebsiteModel) -> Dict[str, Any]:
        """
        Scraping principale di un sito web
        
        Args:
            website: Modello del sito da scrapare
            
        Returns:
            Dict con risultati scraping
        """
        results = {
            'website_id': website.id,
            'url': str(website.url),
            'status': ScrapingStatus.RUNNING,
            'started_at': datetime.now(),
            'pages_scraped': 0,
            'content_extracted': [],
            'contacts_found': [],
            'companies_found': [],
            'errors': []
        }
        
        try:
            # Verifica robots.txt se richiesto
            if website.respect_robots_txt:
                if not await self._check_robots_txt(str(website.url)):
                    results['status'] = ScrapingStatus.FAILED
                    results['errors'].append("Scraping not allowed by robots.txt")
                    return results
            
            # Usa semaforo per limitare richieste concorrenti
            async with self.semaphore:
                # Delay per rate limiting
                await asyncio.sleep(self.rate_limit_delay)
                
                # Scraping con Playwright
                page_content = await self._scrape_page_with_playwright(str(website.url))
                
                if page_content:
                    results['pages_scraped'] = 1
                    self.stats['pages_scraped'] += 1
                    
                    # Estrai contenuti
                    content_results = await self._extract_all_content(
                        page_content, str(website.url), website.id
                    )
                    
                    results['content_extracted'] = content_results.get('content', [])
                    results['contacts_found'] = content_results.get('contacts', [])
                    results['companies_found'] = content_results.get('companies', [])
                    
                    # Aggiorna statistiche
                    self.stats['content_extracted'] += len(results['content_extracted'])
                    self.stats['contacts_found'] += len(results['contacts_found'])
                    self.stats['companies_found'] += len(results['companies_found'])
                
                results['status'] = ScrapingStatus.COMPLETED
                results['completed_at'] = datetime.now()
                
        except Exception as e:
            logger.error(f"Scraping failed for {website.url}: {str(e)}")
            results['status'] = ScrapingStatus.FAILED
            results['errors'].append(f"Scraping error: {str(e)}")
            results['completed_at'] = datetime.now()
            self.stats['errors'] += 1
        
        return results
    
    async def _scrape_page_with_playwright(self, url: str) -> Optional[str]:
        """Scraping con Playwright per supporto JavaScript"""
        try:
            page = await self.browser.new_page()
            
            # Imposta user agent random
            await page.set_extra_http_headers({
                'User-Agent': self.ua.random
            })
            
            # Naviga alla pagina
            await page.goto(url, wait_until='networkidle', timeout=self.timeout * 1000)
            
            # Attendi caricamento completo
            await asyncio.sleep(2)
            
            # Ottieni contenuto
            content = await page.content()
            
            await page.close()
            return content
            
        except Exception as e:
            logger.error(f"Playwright scraping failed for {url}: {str(e)}")
            return None
    
    async def _check_robots_txt(self, url: str) -> bool:
        """Verifica robots.txt"""
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            async with self.session.get(robots_url) as response:
                if response.status == 200:
                    robots_content = await response.text()
                    
                    # Parsing semplificato robots.txt
                    lines = robots_content.split('\n')
                    current_user_agent = None
                    
                    for line in lines:
                        line = line.strip()
                        if line.startswith('User-agent:'):
                            current_user_agent = line.split(':', 1)[1].strip()
                        elif line.startswith('Disallow:') and current_user_agent in ['*', 'IntelligenceBot']:
                            disallow_path = line.split(':', 1)[1].strip()
                            if disallow_path == '/':
                                logger.info(f"Scraping disallowed by robots.txt for {url}")
                                return False
                    
            return True
            
        except Exception as e:
            logger.warning(f"Could not check robots.txt for {url}: {str(e)}")
            return True  # Se non possiamo verificare, assumiamo permesso
    
    async def _extract_all_content(self, html_content: str, url: str, website_id: int) -> Dict[str, List]:
        """Estrae tutti i tipi di contenuto da una pagina"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        results = {
            'content': [],
            'contacts': [],
            'companies': []
        }
        
        # Estrai informazioni aziendali
        company_info = await self._extract_company_info(soup, url, website_id)
        if company_info:
            results['companies'].append(company_info)
            
            # Crea anche un content record per l'azienda
            company_content = ScrapedContentModel(
                website_id=website_id,
                page_url=url,
                page_title=self._extract_page_title(soup),
                content_type=ContentType.COMPANY_INFO,
                content_hash=self._generate_content_hash(company_info.model_dump_json()),
                cleaned_text=self._extract_clean_text(soup),
                structured_data=company_info.model_dump(),
                extraction_method="playwright",
                confidence_score=company_info.confidence_score,
                scraped_at=datetime.now()
            )
            results['content'].append(company_content)
        
        # Estrai contatti
        contacts = await self._extract_contacts(soup, url, website_id)
        results['contacts'].extend(contacts)
        
        # Crea content records per i contatti
        for contact in contacts:
            contact_content = ScrapedContentModel(
                website_id=website_id,
                page_url=url,
                page_title=self._extract_page_title(soup),
                content_type=ContentType.CONTACT_INFO,
                content_hash=self._generate_content_hash(contact.model_dump_json()),
                cleaned_text=f"{contact.full_name} - {contact.email} - {contact.position}",
                structured_data=contact.model_dump(),
                extraction_method="playwright",
                confidence_score=contact.confidence_score,
                scraped_at=datetime.now()
            )
            results['content'].append(contact_content)
        
        return results
    
    async def _extract_company_info(self, soup: BeautifulSoup, url: str, website_id: int) -> Optional[ScrapedCompanyModel]:
        """Estrae informazioni aziendali"""
        company_data = {}
        
        # Nome azienda (strategie multiple)
        company_name = self._extract_company_name(soup)
        if not company_name:
            return None
        
        company_data['company_name'] = company_name
        
        # Descrizione
        description = self._extract_company_description(soup)
        if description:
            company_data['description'] = description
        
        # Contatti
        email = self._extract_company_email(soup)
        if email:
            company_data['email'] = email
        
        phone = self._extract_company_phone(soup)
        if phone:
            company_data['phone'] = phone
        
        # Indirizzo
        address = self._extract_company_address(soup)
        if address:
            company_data.update(address)
        
        # Website
        company_data['website'] = url
        
        # Calcola confidence score
        confidence = self._calculate_company_confidence(company_data)
        company_data['confidence_score'] = confidence
        
        # Calcola completezza dati
        completeness = self._calculate_data_completeness(company_data, [
            'company_name', 'description', 'email', 'phone', 'address_city'
        ])
        company_data['data_completeness'] = completeness
        
        if confidence > 0.3:  # Soglia minima
            return ScrapedCompanyModel(
                scraped_content_id=0,  # Sarà impostato dal caller
                extracted_at=datetime.now(),
                **company_data
            )
        
        return None
    
    def _extract_company_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Estrae nome azienda"""
        # Strategie multiple per nome azienda
        selectors = [
            'h1',
            'title',
            '.company-name',
            '#company-name',
            '[itemprop="name"]',
            '.logo img[alt]',
            '.brand',
            '.site-title'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                if element.name == 'img':
                    text = element.get('alt', '').strip()
                elif element.name == 'title':
                    text = element.get_text().strip()
                    # Pulisci titolo pagina
                    text = text.split('|')[0].split('-')[0].strip()
                else:
                    text = element.get_text().strip()
                
                if text and len(text) > 2 and len(text) < 100:
                    return text
        
        return None
    
    def _extract_company_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Estrae descrizione azienda"""
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '').strip()
        
        # Sezioni about/chi siamo
        selectors = [
            '.about', '#about', '.company-description',
            '.chi-siamo', '.about-us', '.company-info'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text().strip()
                if len(text) > 50:
                    return text[:500]  # Limita lunghezza
        
        return None
    
    def _extract_company_email(self, soup: BeautifulSoup) -> Optional[str]:
        """Estrae email aziendale"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        # Cerca in tutto il testo
        emails = re.findall(email_pattern, soup.get_text())
        
        # Filtra email valide (evita quelle generiche)
        valid_emails = []
        for email in emails:
            if not any(generic in email.lower() for generic in ['example', 'test', 'dummy', 'noreply']):
                valid_emails.append(email)
        
        return valid_emails[0] if valid_emails else None
    
    def _extract_company_phone(self, soup: BeautifulSoup) -> Optional[str]:
        """Estrae telefono aziendale"""
        # Pattern telefono italiano
        phone_patterns = [
            r'\+39\s?\d{2,3}[\s.-]?\d{3,4}[\s.-]?\d{3,4}',
            r'0\d{1,3}[\s.-]?\d{3,4}[\s.-]?\d{3,4}',
            r'\d{3}[\s.-]?\d{3}[\s.-]?\d{4}'
        ]
        
        text = soup.get_text()
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0]
        
        return None
    
    def _extract_company_address(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Estrae indirizzo aziendale"""
        address_data = {}
        
        # Cerca sezioni indirizzo
        selectors = [
            '.address', '.indirizzo', '.contact-info',
            '[itemprop="address"]', '.location'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text().strip()
                
                # Parsing semplificato indirizzo
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                if lines:
                    address_data['address_street'] = lines[0]
                    
                    # Cerca CAP e città
                    for line in lines:
                        if re.search(r'\d{5}', line):  # CAP
                            parts = line.split()
                            for i, part in enumerate(parts):
                                if re.match(r'\d{5}', part):
                                    address_data['address_zip'] = part
                                    if i + 1 < len(parts):
                                        address_data['address_city'] = ' '.join(parts[i+1:])
                                    break
                break
        
        return address_data
    
    async def _extract_contacts(self, soup: BeautifulSoup, url: str, website_id: int) -> List[ScrapedContactModel]:
        """Estrae contatti dalla pagina"""
        contacts = []
        
        # Cerca sezioni team/contatti
        contact_sections = soup.find_all(['div', 'section'], class_=lambda x: x and any(
            keyword in x.lower() for keyword in ['team', 'staff', 'contact', 'chi-siamo', 'about']
        ))
        
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        for section in contact_sections:
            # Trova email nella sezione
            emails = re.findall(email_pattern, section.get_text())
            
            for email in emails:
                contact_data = {'email': email}
                
                # Cerca nome associato
                name = self._find_name_near_email(section, email)
                if name:
                    contact_data['full_name'] = name
                    parts = name.split()
                    if len(parts) >= 2:
                        contact_data['first_name'] = parts[0]
                        contact_data['last_name'] = ' '.join(parts[1:])
                
                # Cerca posizione
                position = self._find_position_near_email(section, email)
                if position:
                    contact_data['position'] = position
                
                # Calcola confidence
                confidence = self._calculate_contact_confidence(contact_data)
                contact_data['confidence_score'] = confidence
                
                if confidence > 0.4:  # Soglia minima
                    contact = ScrapedContactModel(
                        scraped_content_id=0,  # Sarà impostato dal caller
                        extracted_at=datetime.now(),
                        **contact_data
                    )
                    contacts.append(contact)
        
        return contacts[:5]  # Limita a 5 contatti per pagina
    
    def _find_name_near_email(self, section: BeautifulSoup, email: str) -> Optional[str]:
        """Trova nome vicino all'email"""
        # Cerca nel testo circostante
        text = section.get_text()
        email_pos = text.find(email)
        
        if email_pos > 0:
            # Testo prima dell'email
            before_text = text[:email_pos].strip()
            words = before_text.split()
            
            # Cerca parole che sembrano nomi (iniziano con maiuscola)
            potential_names = []
            for word in words[-10:]:  # Ultime 10 parole
                if word.istitle() and len(word) > 2:
                    potential_names.append(word)
            
            if len(potential_names) >= 2:
                return ' '.join(potential_names[-2:])
        
        return None
    
    def _find_position_near_email(self, section: BeautifulSoup, email: str) -> Optional[str]:
        """Trova posizione vicino all'email"""
        # Parole chiave posizioni
        position_keywords = [
            'ceo', 'cto', 'cmo', 'direttore', 'manager', 'responsabile',
            'coordinatore', 'amministratore', 'presidente', 'vicepresidente',
            'founder', 'co-founder', 'partner', 'senior', 'junior', 'lead'
        ]
        
        text = section.get_text().lower()
        for keyword in position_keywords:
            if keyword in text:
                # Estrai contesto intorno alla parola
                start = max(0, text.find(keyword) - 50)
                end = min(len(text), text.find(keyword) + 50)
                context = text[start:end]
                
                # Estrai la posizione
                words = context.split()
                for i, word in enumerate(words):
                    if keyword in word:
                        # Prendi 2-3 parole intorno
                        position_words = words[max(0, i-1):i+3]
                        position = ' '.join(position_words).strip()
                        return position.title()
        
        return None
    
    def _calculate_company_confidence(self, company_data: Dict[str, Any]) -> float:
        """Calcola confidence score per azienda"""
        score = 0.0
        
        # Peso per ogni campo
        weights = {
            'company_name': 0.3,
            'description': 0.2,
            'email': 0.2,
            'phone': 0.15,
            'address_city': 0.15
        }
        
        for field, weight in weights.items():
            if field in company_data and company_data[field]:
                score += weight
        
        return min(score, 1.0)
    
    def _calculate_contact_confidence(self, contact_data: Dict[str, Any]) -> float:
        """Calcola confidence score per contatto"""
        score = 0.0
        
        # Peso per ogni campo
        weights = {
            'email': 0.4,
            'full_name': 0.3,
            'position': 0.2,
            'phone': 0.1
        }
        
        for field, weight in weights.items():
            if field in contact_data and contact_data[field]:
                score += weight
        
        return min(score, 1.0)
    
    def _calculate_data_completeness(self, data: Dict[str, Any], required_fields: List[str]) -> float:
        """Calcola completezza dati"""
        filled_fields = sum(1 for field in required_fields if field in data and data[field])
        return filled_fields / len(required_fields) if required_fields else 0.0
    
    def _extract_page_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Estrae titolo pagina"""
        title = soup.find('title')
        return title.get_text().strip() if title else None
    
    def _extract_clean_text(self, soup: BeautifulSoup) -> str:
        """Estrae testo pulito dalla pagina"""
        # Rimuovi script e style
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Ottieni testo pulito
        text = soup.get_text()
        
        # Pulisci spazi multipli
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:2000]  # Limita lunghezza
    
    def _generate_content_hash(self, content: str) -> str:
        """Genera hash per contenuto"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_stats(self) -> Dict[str, int]:
        """Ottieni statistiche scraping"""
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset statistiche"""
        self.stats = {
            'pages_scraped': 0,
            'content_extracted': 0,
            'contacts_found': 0,
            'companies_found': 0,
            'errors': 0
        }

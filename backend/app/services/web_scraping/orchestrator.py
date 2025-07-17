"""
🎭 Web Scraping Orchestrator
Coordina scraping, processing e RAG integration
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from models.scraped_data import ScrapedWebsiteModel, ScrapingJobModel, ScrapingStatus
from scraping_engine import IntelligenceWebScrapingEngine
from rag_integration import WebScrapingRAGIntegration

logger = logging.getLogger(__name__)

class WebScrapingOrchestrator:
    """
    🎭 Orchestratore completo per web scraping
    
    Coordina:
    - Scraping engine
    - RAG integration
    - Database persistence
    - Error handling
    """
    
    def __init__(self):
        self.scraping_engine = None
        self.rag_integration = WebScrapingRAGIntegration()
        
        # Configurazione
        self.auto_rag_processing = True
        self.max_concurrent_jobs = 5
        
        # Statistiche globali
        self.global_stats = {
            'jobs_executed': 0,
            'websites_scraped': 0,
            'content_processed': 0,
            'rag_integrated': 0,
            'errors': 0
        }
    
    async def execute_scraping_job(self, website: ScrapedWebsiteModel) -> Dict[str, Any]:
        """
        Esegue job completo di scraping
        
        Args:
            website: Sito web da scrapare
            
        Returns:
            Dict con risultati completi
        """
        job_result = {
            'job_id': f"job_{website.id}_{int(datetime.now().timestamp())}",
            'website_id': website.id,
            'status': ScrapingStatus.RUNNING,
            'started_at': datetime.now(),
            'scraping_results': None,
            'rag_results': None,
            'errors': []
        }
        
        try:
            # Fase 1: Web Scraping
            logger.info(f"Starting scraping for website {website.id}: {website.url}")
            
            async with IntelligenceWebScrapingEngine() as engine:
                self.scraping_engine = engine
                scraping_results = await engine.scrape_website(website)
                
                job_result['scraping_results'] = scraping_results
                
                if scraping_results['status'] == ScrapingStatus.COMPLETED:
                    # Fase 2: RAG Integration (se abilitata)
                    if self.auto_rag_processing and scraping_results['content_extracted']:
                        logger.info(f"Starting RAG integration for {len(scraping_results['content_extracted'])} contents")
                        
                        rag_results = await self.rag_integration.bulk_process_scraped_content(
                            scraping_results['content_extracted']
                        )
                        
                        job_result['rag_results'] = rag_results
                        
                        if rag_results['successful'] > 0:
                            self.global_stats['rag_integrated'] += rag_results['successful']
                
                # Aggiorna statistiche
                self.global_stats['jobs_executed'] += 1
                self.global_stats['websites_scraped'] += 1
                self.global_stats['content_processed'] += len(scraping_results.get('content_extracted', []))
                
                job_result['status'] = ScrapingStatus.COMPLETED
                job_result['completed_at'] = datetime.now()
                
        except Exception as e:
            logger.error(f"Job execution failed for website {website.id}: {str(e)}")
            job_result['status'] = ScrapingStatus.FAILED
            job_result['errors'].append(f"Job execution error: {str(e)}")
            job_result['completed_at'] = datetime.now()
            self.global_stats['errors'] += 1
        
        return job_result
    
    async def execute_bulk_scraping(self, websites: List[ScrapedWebsiteModel]) -> Dict[str, Any]:
        """
        Esegue scraping bulk con concorrenza controllata
        
        Args:
            websites: Lista siti web da scrapare
            
        Returns:
            Dict con risultati bulk
        """
        bulk_result = {
            'total_websites': len(websites),
            'completed': 0,
            'failed': 0,
            'individual_results': [],
            'started_at': datetime.now(),
            'global_stats': {}
        }
        
        # Limita concorrenza
        semaphore = asyncio.Semaphore(self.max_concurrent_jobs)
        
        async def process_website(website):
            async with semaphore:
                return await self.execute_scraping_job(website)
        
        # Esegui jobs in parallelo
        tasks = [process_website(website) for website in websites]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Processa risultati
        for result in results:
            if isinstance(result, Exception):
                bulk_result['failed'] += 1
                bulk_result['individual_results'].append({
                    'status': 'failed',
                    'error': str(result)
                })
            else:
                bulk_result['individual_results'].append(result)
                if result['status'] == ScrapingStatus.COMPLETED:
                    bulk_result['completed'] += 1
                else:
                    bulk_result['failed'] += 1
        
        bulk_result['completed_at'] = datetime.now()
        bulk_result['global_stats'] = self.get_global_stats()
        
        return bulk_result
    
    def get_global_stats(self) -> Dict[str, int]:
        """Ottieni statistiche globali"""
        return self.global_stats.copy()
    
    def reset_global_stats(self):
        """Reset statistiche globali"""
        self.global_stats = {
            'jobs_executed': 0,
            'websites_scraped': 0,
            'content_processed': 0,
            'rag_integrated': 0,
            'errors': 0
        }
    
    def configure_rag_processing(self, enabled: bool):
        """Configura processing RAG automatico"""
        self.auto_rag_processing = enabled
    
    def configure_concurrency(self, max_concurrent: int):
        """Configura massima concorrenza"""
        self.max_concurrent_jobs = max_concurrent

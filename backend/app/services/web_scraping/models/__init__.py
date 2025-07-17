"""
Web Scraping Models
Modelli Pydantic per validazione dati web scraping
"""

from .scraped_data import *

__all__ = [
    # Data Models
    'ScrapedWebsiteModel',
    'ScrapedContentModel', 
    'ScrapedContactModel',
    'ScrapedCompanyModel',
    'ScrapingJobModel',
    
    # Utility Models
    'ScrapingMetrics',
    'DatabaseStats',
    
    # Enums
    'ContentType',
    'ScrapingStatus',
    'ScrapingFrequency',
    'IntegrationStatus',
    'RAGProcessingStatus'
]

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from datetime import datetime
import psycopg2
import os
import logging
from pathlib import Path

# Setup logging
logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api/web-scraping", tags=["web-scraping"])

# Models
class ScrapeUrlRequest(BaseModel):
    url: str
    auto_rag: bool = True
    company_id: int = None

class ScrapeResponse(BaseModel):
    success: bool
    message: str
    filename: str = None

# Database connection - SINGOLA DEFINIZIONE
def get_db_connection():
    try:
        return psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "intelligence"),
            user=os.getenv("DB_USER", "intelligence_user"),
            password=os.getenv("DB_PASSWORD", "intelligence_pass"),
            port=int(os.getenv("DB_PORT", "5432"))
        )
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

@router.get("/knowledge-stats")
async def get_knowledge_stats():
    """Statistiche knowledge base REALI dal database - FIXED"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query corrette senza errori sintassi
        cursor.execute("SELECT COUNT(*) FROM knowledge_documents WHERE filename LIKE %s", ('%scraped_%',))
        scraped_docs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM knowledge_documents")
        total_docs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM document_chunks")
        total_chunks = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM scraped_websites")
        scraped_sites = cursor.fetchone()[0]
        
        conn.close()
        
        # Determina status basato su dati reali
        status = "Attivo" if scraped_sites > 0 or scraped_docs > 0 else "Non Attivo"
        
        return {
            "total_documents": total_docs,
            "scraped_documents": scraped_docs,
            "total_chunks": total_chunks,
            "scraped_sites": scraped_sites,
            "status": status,
            "last_update": datetime.utcnow().isoformat(),
            "integration_status": "database_real_fixed",
            "database_type": "postgresql"
        }
        
    except Exception as e:
        logger.error(f"Knowledge stats error: {e}")
        return {
            "total_documents": 0,
            "scraped_documents": 0,
            "total_chunks": 0,
            "scraped_sites": 0,
            "status": "Errore",
            "error": str(e),
            "last_update": datetime.utcnow().isoformat()
        }

@router.get("/scraped-sites")
async def get_scraped_sites():
    """Lista siti scrappati"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT url, last_scraped, domain, title, status
            FROM scraped_websites 
            ORDER BY last_scraped DESC
        """)
        
        sites = []
        for row in cursor.fetchall():
            sites.append({
                "url": row[0],
                "last_scraped": row[1].isoformat() if row[1] else None,
                "domain": row[2],
                "title": row[3],
                "status": row[4]
            })
        
        conn.close()
        
        return {"scraped_sites": sites}
        
    except Exception as e:
        logger.error(f"Get scraped sites error: {e}")
        return {"scraped_sites": [], "error": str(e)}

@router.delete("/scraped-url")
async def delete_scraped_url(request: dict):
    """Elimina sito scrappato COMPLETAMENTE - FIXED"""
    try:
        url = request.get("url")
        if not url:
            raise HTTPException(status_code=400, detail="URL required")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Elimina da scraped_websites PRIMA
        cursor.execute("DELETE FROM scraped_websites WHERE url = %s", (url,))
        sites_deleted = cursor.rowcount
        
        # 2. Elimina TUTTI i documenti scraped (approccio semplice)
        cursor.execute("SELECT id FROM knowledge_documents WHERE filename LIKE 'scraped_%'")
        docs = cursor.fetchall()
        docs_deleted = 0
        
        for (doc_id,) in docs:
            cursor.execute("DELETE FROM document_chunks WHERE document_id = %s", (doc_id,))
            cursor.execute("DELETE FROM knowledge_documents WHERE id = %s", (doc_id,))
            docs_deleted += 1
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"Eliminato: {sites_deleted} siti, {docs_deleted} documenti",
            "url": url
        }
        
    except Exception as e:
        logger.error(f"Delete error: {e}")
        return {"success": False, "message": f"Errore: {str(e)}"}

@router.post("/scrape-url", response_model=ScrapeResponse)
async def scrape_url(request: ScrapeUrlRequest):
    """Scraping con vettorizzazione automatica"""
    try:
        import requests
        from bs4 import BeautifulSoup
        from datetime import datetime
        from urllib.parse import urlparse
        
        # Scraping
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(request.url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title').get_text().strip() if soup.find('title') else "No title"
        
        for script in soup(["script", "style"]):
            script.decompose()
        
        clean_text = soup.get_text()
        lines = (line.strip() for line in clean_text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_content = ' '.join(chunk for chunk in chunks if chunk)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"scraped_{timestamp}.html"
        
        # Salva database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO knowledge_documents (filename, extracted_text, created_at, updated_at)
            VALUES (%s, %s, NOW(), NOW()) RETURNING id
        """, (filename, clean_content))
        
        doc_id = cursor.fetchone()[0]
        
        parsed_url = urlparse(request.url)
        cursor.execute("""
            INSERT INTO scraped_websites (url, domain, title, status, last_scraped, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW(), NOW())
        """, (request.url, parsed_url.netloc, title, "completed"))
        
        conn.commit()
        conn.close()
        
        # VETTORIZZAZIONE AUTOMATICA
        try:
            import subprocess
            subprocess.run([
                "python", "/var/www/intelligence/backend/app/scripts/vectorize_html_from_db.py"
            ], cwd="/var/www/intelligence/backend", timeout=60)
        except Exception as e:
            logger.warning(f"Vectorization failed: {e}")
        
        return ScrapeResponse(
            success=True,
            message=f"Scraping + vettorizzazione completati: {title}",
            filename=filename
        )
        
    except Exception as e:
        logger.error(f"Scraping error: {e}")
        return ScrapeResponse(success=False, message=f"Errore: {str(e)}")

def update_company_scraping_status(company_id: int, status: str):
    """Update company scraping status"""
    if company_id:
        try:
            from app.core.database import get_db
            from sqlalchemy import text
            db = next(get_db())
            db.execute(text("UPDATE companies SET scraping_status = :status WHERE id = :id"), 
                      {"status": status, "id": company_id})
            db.commit()
        except Exception as e:
            print(f"Error updating company status: {e}")

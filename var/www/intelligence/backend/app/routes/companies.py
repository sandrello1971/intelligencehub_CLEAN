"""
Intelligence Platform - Companies API Routes
Complete CRUD operations for companies management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, desc
from app.core.database import get_db
from app.schemas.companies import CompanyResponse, CompanyUpdate, CompanySearchResponse
from typing import Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/companies", tags=["Companies"])

@router.get("/", response_model=CompanySearchResponse)
async def list_companies(
    search: Optional[str] = Query(None, description="Search in name, settore"),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    is_partner: Optional[bool] = Query(None, description="Filter by partner status"),
    partner_category: Optional[str] = Query(None, description="Filter by partner category"),
    settore: Optional[str] = Query(None, description="Filter by sector"),
    db: Session = Depends(get_db)
):
    """List companies with advanced search and filters"""
    try:
        # Base query
        base_query = """
            SELECT id, codice, name, partita_iva, codice_fiscale, indirizzo, 
                   citta, cap, provincia, regione, stato, settore, numero_dipendenti,
                   data_acquisizione, note, sito_web, email, telefono, score,
                   zona_commerciale, sales_persons, created_at,
                   is_partner, is_supplier, partner_category, partner_description,
                   partner_expertise, partner_rating, partner_status,
                   last_scraped_at, scraping_status, ai_analysis_summary
            FROM companies 
            WHERE 1=1
        """
        
        params = {}
        conditions = []
        
        # Search condition
        if search:
            conditions.append("(LOWER(name) LIKE :search OR LOWER(settore) LIKE :search)")
            params["search"] = f"%{search.lower()}%"
        
        # Filter conditions
        if is_partner is not None:
            conditions.append("is_partner = :is_partner")
            params["is_partner"] = is_partner
            
        if partner_category:
            conditions.append("partner_category = :partner_category")
            params["partner_category"] = partner_category
            
        if settore:
            conditions.append("LOWER(settore) = :settore")
            params["settore"] = settore.lower()
        
        # Add conditions to query
        if conditions:
            base_query += " AND " + " AND ".join(conditions)
        
        # Add ordering and pagination
        query = base_query + " ORDER BY name LIMIT :limit OFFSET :offset"
        params.update({"limit": limit, "offset": offset})
        
        # Execute main query
        result = db.execute(text(query), params)
        companies = result.fetchall()
        
        # Count queries for statistics
        count_query = "SELECT COUNT(*) as total FROM companies"
        partners_query = "SELECT COUNT(*) as count FROM companies WHERE is_partner = true"
        suppliers_query = "SELECT COUNT(*) as count FROM companies WHERE is_supplier = true"
        scraped_query = "SELECT COUNT(*) as count FROM companies WHERE scraping_status = 'completed'"
        
        total_result = db.execute(text(count_query))
        partners_result = db.execute(text(partners_query))
        suppliers_result = db.execute(text(suppliers_query))
        scraped_result = db.execute(text(scraped_query))
        
        return CompanySearchResponse(
            companies=[
                CompanyResponse(
                    id=comp.id,
                    codice=comp.codice,
                    name=comp.name,
                    partita_iva=comp.partita_iva,
                    codice_fiscale=comp.codice_fiscale,
                    indirizzo=comp.indirizzo,
                    citta=comp.citta,
                    cap=comp.cap,
                    provincia=comp.provincia,
                    regione=comp.regione,
                    stato=comp.stato,
                    settore=comp.settore,
                    numero_dipendenti=comp.numero_dipendenti,
                    data_acquisizione=comp.data_acquisizione,
                    note=comp.note,
                    sito_web=comp.sito_web,
                    email=comp.email,
                    telefono=comp.telefono,
                    score=comp.score,
                    zona_commerciale=comp.zona_commerciale,
                    sales_persons=comp.sales_persons,
                    created_at=comp.created_at,
                    is_partner=comp.is_partner or False,
                    is_supplier=comp.is_supplier or False,
                    partner_category=comp.partner_category,
                    partner_description=comp.partner_description,
                    partner_expertise=comp.partner_expertise or [],
                    partner_rating=comp.partner_rating or 0.0,
                    partner_status=comp.partner_status or "active",
                    last_scraped_at=comp.last_scraped_at,
                    scraping_status=comp.scraping_status or "pending",
                    ai_analysis_summary=comp.ai_analysis_summary
                )
                for comp in companies
            ],
            total=total_result.fetchone().total,
            partners_count=partners_result.fetchone().count,
            suppliers_count=suppliers_result.fetchone().count,
            scraped_count=scraped_result.fetchone().count
        )
        
    except Exception as e:
        logger.error(f"Error listing companies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/search")
async def search_companies_autocomplete(
    q: str = Query(..., description="Search query", min_length=2),
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db)
):
    """Search companies for autocomplete"""
    try:
        query = """
        SELECT id, name, partita_iva, settore
        FROM companies 
        WHERE LOWER(name) LIKE LOWER(:search)
        ORDER BY name
        LIMIT :limit
        """
        
        result = db.execute(text(query), {
            "search": f"%{q}%",
            "limit": limit
        }).fetchall()
        
        companies = []
        for row in result:
            companies.append({
                "id": row[0],
                "name": row[1], 
                "partita_iva": row[2],
                "settore": row[3]
            })
        
        return {"companies": companies}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: int, db: Session = Depends(get_db)):
    """Get single company by ID"""
    try:
        query = """
            SELECT id, codice, name, partita_iva, codice_fiscale, indirizzo, 
                   citta, cap, provincia, regione, stato, settore, numero_dipendenti,
                   data_acquisizione, note, sito_web, email, telefono, score,
                   zona_commerciale, sales_persons, created_at,
                   is_partner, is_supplier, partner_category, partner_description,
                   partner_expertise, partner_rating, partner_status,
                   last_scraped_at, scraping_status, ai_analysis_summary
            FROM companies 
            WHERE id = :id
        """
        
        result = db.execute(text(query), {"id": company_id})
        company = result.fetchone()
        
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        return CompanyResponse(
            id=company.id,
            codice=company.codice,
            name=company.name,
            partita_iva=company.partita_iva,
            codice_fiscale=company.codice_fiscale,
            indirizzo=company.indirizzo,
            citta=company.citta,
            cap=company.cap,
            provincia=company.provincia,
            regione=company.regione,
            stato=company.stato,
            settore=company.settore,
            numero_dipendenti=company.numero_dipendenti,
            data_acquisizione=company.data_acquisizione,
            note=company.note,
            sito_web=company.sito_web,
            email=company.email,
            telefono=company.telefono,
            score=company.score,
            zona_commerciale=company.zona_commerciale,
            sales_persons=company.sales_persons,
            created_at=company.created_at,
            is_partner=company.is_partner or False,
            is_supplier=company.is_supplier or False,
            partner_category=company.partner_category,
            partner_description=company.partner_description,
            partner_expertise=company.partner_expertise or [],
            partner_rating=company.partner_rating or 0.0,
            partner_status=company.partner_status or "active",
            last_scraped_at=company.last_scraped_at,
            scraping_status=company.scraping_status or "pending",
            ai_analysis_summary=company.ai_analysis_summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting company {company_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int, 
    company_data: CompanyUpdate, 
    db: Session = Depends(get_db)
):
    """Update company"""
    try:
        # Check if exists
        check_query = "SELECT id FROM companies WHERE id = :id"
        result = db.execute(text(check_query), {"id": company_id})
        if not result.fetchone():
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Build update query dynamically
        update_fields = []
        params = {"id": company_id}
        
        # Map Pydantic model to database fields
        field_mapping = {
            "name": "name",
            "partita_iva": "partita_iva",
            "codice_fiscale": "codice_fiscale",
            "indirizzo": "indirizzo",
            "citta": "citta",
            "provincia": "provincia",
            "regione": "regione",
            "settore": "settore",
            "numero_dipendenti": "numero_dipendenti",
            "sito_web": "sito_web",
            "email": "email",
            "telefono": "telefono",
            "note": "note",
            "is_partner": "is_partner",
            "is_supplier": "is_supplier",
            "partner_category": "partner_category",
            "partner_description": "partner_description",
            "partner_expertise": "partner_expertise",
            "partner_rating": "partner_rating",
            "partner_status": "partner_status"
        }
        
        # Only update fields that are provided (not None)
        for pydantic_field, db_field in field_mapping.items():
            value = getattr(company_data, pydantic_field, None)
            if value is not None:
                update_fields.append(f"{db_field} = :{pydantic_field}")
                params[pydantic_field] = value
        
        if update_fields:
            query = f"UPDATE companies SET {', '.join(update_fields)} WHERE id = :id"
            db.execute(text(query), params)
            db.commit()
            
            # Return updated company
            return await get_company(company_id, db)
        else:
            # No fields to update, return current company
            return await get_company(company_id, db)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating company {company_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/overview")
async def get_companies_stats(db: Session = Depends(get_db)):
    """Get companies statistics overview"""
    try:
        stats_query = """
            SELECT 
                COUNT(*) as total_companies,
                COUNT(CASE WHEN is_partner = true THEN 1 END) as partners_count,
                COUNT(CASE WHEN is_supplier = true THEN 1 END) as suppliers_count,
                COUNT(CASE WHEN scraping_status = 'completed' THEN 1 END) as scraped_count,
                COUNT(CASE WHEN partner_rating > 0 THEN 1 END) as rated_partners,
                AVG(partner_rating) as avg_partner_rating,
                COUNT(DISTINCT settore) as sectors_count
            FROM companies
        """
        
        result = db.execute(text(stats_query))
        stats = result.fetchone()
        
        return {
            "total_companies": stats.total_companies,
            "partners_count": stats.partners_count,
            "suppliers_count": stats.suppliers_count,
            "scraped_count": stats.scraped_count,
            "rated_partners": stats.rated_partners,
            "avg_partner_rating": float(stats.avg_partner_rating or 0),
            "sectors_count": stats.sectors_count
        }
        
    except Exception as e:
        logger.error(f"Error getting companies stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



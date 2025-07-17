"""
Enhanced IntelliChat API with RAG + Partner Search Integration
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
import logging
import json
import re
from datetime import datetime

from app.db.session import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/intellichat", tags=["intellichat"])

@router.post("/chat")
async def chat_with_rag(
    request: dict,
    db: Session = Depends(get_db)
):
    """Enhanced chat with RAG + Partner Search + Company Database"""
    
    message = request.get("message", "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    logger.info(f"IntelliChat query: {message}")
    
    # Analyze message intent
    intent = analyze_message_intent(message)
    
    response_parts = []
    
    # 1. Partner/Company Search
    if intent["is_partner_search"] or intent["is_company_search"]:
        companies_result = await search_companies_for_query(message, intent, db)
        if companies_result:
            response_parts.append(companies_result)
    
    # 2. RAG Knowledge Base Search
    if intent["needs_rag"]:
        rag_result = await search_knowledge_base(message, db)
        if rag_result:
            response_parts.append(rag_result)
    
    # 3. General AI Response if no specific results
    if not response_parts:
        general_response = generate_general_response(message, intent)
        response_parts.append(general_response)
    
    # Combine responses
    final_response = combine_responses(response_parts, intent)
    
    return {
        "response": final_response,
        "intent": intent,
        "timestamp": datetime.now().isoformat()
    }

def analyze_message_intent(message: str) -> Dict[str, Any]:
    """Analyze message to understand user intent"""
    
    message_lower = message.lower()
    
    # Partner search keywords
    partner_keywords = ["partner", "partner che", "qualcuno che", "azienda che", "chi si occupa", "fornitori", "cerco"]
    company_keywords = ["azienda", "aziende", "ditta", "società", "impresa"]
    
    # Service/technology keywords
    tech_keywords = {
        "ai": ["ai", "artificial intelligence", "intelligenza artificiale", "machine learning", "ml"],
        "cloud": ["cloud", "aws", "azure", "google cloud", "infrastruttura"],
        "security": ["security", "sicurezza", "cybersecurity", "protezione"],
        "software": ["software", "sviluppo", "programmazione", "app", "applicazioni"],
        "web": ["web", "sito", "website", "frontend", "backend"],
        "marketing": ["marketing", "pubblicità", "social", "seo"],
        "design": ["design", "grafica", "ui", "ux", "creativi"]
    }
    
    # Detect intent
    is_partner_search = any(kw in message_lower for kw in partner_keywords)
    is_company_search = any(kw in message_lower for kw in company_keywords)
    
    # Detect technology/service category
    detected_categories = []
    for category, keywords in tech_keywords.items():
        if any(kw in message_lower for kw in keywords):
            detected_categories.append(category)
    
    return {
        "is_partner_search": is_partner_search,
        "is_company_search": is_company_search,
        "needs_rag": True,  # Always try RAG for additional context
        "detected_categories": detected_categories,
        "original_query": message
    }

async def search_companies_for_query(message: str, intent: Dict, db: Session) -> str:
    """Search companies/partners based on query intent"""
    
    try:
        # Build search parameters
        filters = []
        params = {}
        
        # Add partner/supplier filter if looking for partners
        if intent["is_partner_search"]:
            filters.append("(is_partner = true OR is_supplier = true)")
        
        # Add category filters
        if intent["detected_categories"]:
            category_conditions = []
            for i, category in enumerate(intent["detected_categories"]):
                category_map = {
                    "ai": "AI",
                    "cloud": "Cloud",
                    "security": "Security",
                    "software": "Software",
                    "web": "Software",
                    "marketing": "Marketing",
                    "design": "Design"
                }
                
                mapped_category = category_map.get(category, category)
                param_name = f"category_{i}"
                category_conditions.append(f"(partner_category ILIKE :{param_name} OR settore ILIKE :{param_name} OR partner_description ILIKE :{param_name})")
                params[param_name] = f"%{mapped_category}%"
            
            if category_conditions:
                filters.append(f"({' OR '.join(category_conditions)})")
        else:
            # General search in all text fields
            filters.append("""(
                name ILIKE :search OR 
                settore ILIKE :search OR 
                partner_description ILIKE :search OR
                partner_category ILIKE :search
            )""")
            params["search"] = f"%{intent['original_query']}%"
        
        # Build final query
        where_clause = " AND ".join(filters) if filters else "1=1"
        
        query = f"""
        SELECT 
            name, settore, partner_category, partner_description,
            partner_rating, sito_web, citta, regione,
            is_partner, is_supplier, email, telefono
        FROM companies 
        WHERE {where_clause}
        ORDER BY 
            (CASE WHEN is_partner THEN 2 WHEN is_supplier THEN 1 ELSE 0 END) DESC,
            COALESCE(partner_rating, 0) DESC,
            name
        LIMIT 8
        """
        
        with db.connection() as conn:
            result = conn.execute(text(query), params)
            companies = [dict(row._mapping) for row in result]
        
        if not companies:
            return "❌ Non ho trovato aziende che corrispondono ai criteri richiesti nel nostro database."
        
        # Format response
        response = f"🔍 **Ho trovato {len(companies)} aziende** che potrebbero interessarti:\n\n"
        
        for i, company in enumerate(companies, 1):
            status = "🤝 Partner" if company["is_partner"] else "📦 Fornitore" if company["is_supplier"] else "🏢 Azienda"
            
            response += f"**{i}. {company['name']}** {status}\n"
            
            if company["partner_category"]:
                response += f"   🏷️ **Categoria**: {company['partner_category']}\n"
            elif company["settore"]:
                response += f"   🎯 **Settore**: {company['settore']}\n"
            
            if company["partner_description"]:
                desc = company["partner_description"][:100]
                response += f"   📝 **Servizi**: {desc}{'...' if len(company['partner_description']) > 100 else ''}\n"
            
            if company["citta"]:
                response += f"   📍 **Città**: {company['citta']}\n"
            
            if company["sito_web"]:
                response += f"   🌐 **Sito**: {company['sito_web']}\n"
            
            if company["email"]:
                response += f"   📧 **Email**: {company['email']}\n"
            
            response += "\n"
        
        return response
        
    except Exception as e:
        logger.error(f"Error searching companies: {e}")
        return f"❌ Errore durante la ricerca aziende: {str(e)}"

async def search_knowledge_base(message: str, db: Session) -> str:
    """Search in RAG knowledge base"""
    
    try:
        # Check if we have knowledge documents
        query = """
        SELECT COUNT(*) as doc_count
        FROM knowledge_documents 
        """
        
        with db.connection() as conn:
            result = conn.execute(text(query))
            doc_count = result.scalar() or 0
        
        if doc_count == 0:
            return "📚 La knowledge base è vuota. Carica documenti in 'Document RAG' per abilitare la ricerca."
        
        return f"📖 **Knowledge Base**: {doc_count} documenti disponibili per la ricerca RAG (integrazione in corso)."
        
    except Exception as e:
        logger.error(f"Error in RAG search: {e}")
        return f"❌ Errore nella ricerca RAG: {str(e)}"

def generate_general_response(message: str, intent: Dict) -> str:
    """Generate general AI response"""
    
    suggestions = [
        "🔍 'Cerco partner che si occupano di AI'",
        "🏢 'Abbiamo fornitori di servizi cloud?'", 
        "👥 'Chi lavora con cybersecurity?'",
        "📱 'Aziende di sviluppo software a Milano?'"
    ]
    
    return f"🤖 Ho ricevuto: '{message}'\n\n💡 **Suggerimenti**:\n" + "\n".join(f"• {s}" for s in suggestions)

def combine_responses(response_parts: List[str], intent: Dict) -> str:
    """Combine multiple response parts into final response"""
    
    if len(response_parts) == 1:
        return response_parts[0]
    
    return "\n\n---\n\n".join(response_parts)

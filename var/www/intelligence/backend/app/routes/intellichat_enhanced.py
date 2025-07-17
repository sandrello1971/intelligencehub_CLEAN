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
    
    # Save conversation
    await save_conversation(message, final_response, intent, db)
    
    return {
        "response": final_response,
        "intent": intent,
        "timestamp": datetime.now().isoformat()
    }

def analyze_message_intent(message: str) -> Dict[str, Any]:
    """Analyze message to understand user intent"""
    
    message_lower = message.lower()
    
    # Partner search keywords
    partner_keywords = ["partner", "partner che", "qualcuno che", "azienda che", "chi si occupa", "fornitori"]
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
    
    # Location detection
    location_match = re.search(r'\b(milano|roma|torino|napoli|bologna|firenze|venezia|lombardia|lazio|piemonte)\b', message_lower)
    detected_location = location_match.group(1) if location_match else None
    
    return {
        "is_partner_search": is_partner_search,
        "is_company_search": is_company_search,
        "needs_rag": not (is_partner_search or is_company_search),
        "detected_categories": detected_categories,
        "detected_location": detected_location,
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
                    "ai": "AI/Machine Learning",
                    "cloud": "Cloud Computing", 
                    "security": "Cybersecurity",
                    "software": "Software Development",
                    "web": "Software Development",
                    "marketing": "Marketing",
                    "design": "Design"
                }
                
                mapped_category = category_map.get(category, category.title())
                param_name = f"category_{i}"
                category_conditions.append(f"partner_category ILIKE :{param_name}")
                params[param_name] = f"%{mapped_category}%"
            
            if category_conditions:
                filters.append(f"({' OR '.join(category_conditions)})")
        
        # Add location filter
        if intent["detected_location"]:
            filters.append("(citta ILIKE :location OR regione ILIKE :location)")
            params["location"] = f"%{intent['detected_location']}%"
        
        # Add general search
        search_terms = intent["original_query"]
        filters.append("""(
            name ILIKE :search OR 
            settore ILIKE :search OR 
            partner_description ILIKE :search OR
            partner_category ILIKE :search
        )""")
        params["search"] = f"%{search_terms}%"
        
        # Build final query
        where_clause = " AND ".join(filters)
        
        query = f"""
        SELECT 
            name, settore, partner_category, partner_description,
            partner_rating, sito_web, citta, regione,
            is_partner, is_supplier, partner_expertise
        FROM companies 
        WHERE {where_clause}
        ORDER BY 
            (CASE WHEN is_partner THEN 2 WHEN is_supplier THEN 1 ELSE 0 END) DESC,
            partner_rating DESC,
            name
        LIMIT 10
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
            
            if company["settore"]:
                response += f"   🎯 **Settore**: {company['settore']}\n"
            
            if company["partner_description"]:
                desc = company["partner_description"][:150]
                response += f"   📝 **Servizi**: {desc}{'...' if len(company['partner_description']) > 150 else ''}\n"
            
            if company["citta"] or company["regione"]:
                location = f"{company['citta'] or ''}, {company['regione'] or ''}".strip(', ')
                response += f"   📍 **Località**: {location}\n"
            
            if company["partner_rating"] and company["partner_rating"] > 0:
                stars = "⭐" * int(company["partner_rating"])
                response += f"   {stars} **Rating**: {company['partner_rating']}/5\n"
            
            if company["sito_web"]:
                response += f"   🌐 **Sito**: {company['sito_web']}\n"
            
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
        WHERE content IS NOT NULL
        """
        
        with db.connection() as conn:
            result = conn.execute(text(query))
            doc_count = result.scalar()
        
        if doc_count == 0:
            return "📚 La knowledge base è attualmente vuota. Carica alcuni documenti per abilitare la ricerca RAG."
        
        # TODO: Implement actual RAG search with vector similarity
        # For now, simulate RAG response
        return f"📖 **Ricerca nella Knowledge Base** (simulazione con {doc_count} documenti):\n\nLa ricerca RAG per '{message}' è in fase di implementazione. Il sistema ha accesso a {doc_count} documenti caricati."
        
    except Exception as e:
        logger.error(f"Error in RAG search: {e}")
        return f"❌ Errore nella ricerca RAG: {str(e)}"

def generate_general_response(message: str, intent: Dict) -> str:
    """Generate general AI response"""
    
    if intent["is_partner_search"]:
        return "🤖 Per cercare partner o fornitori, prova a essere più specifico. Ad esempio: 'Cerco un partner che si occupa di AI' o 'Abbiamo fornitori di servizi cloud?'"
    
    return f"🤖 Ho ricevuto la tua domanda: '{message}'. Al momento posso aiutarti con:\n\n• 🔍 **Ricerca Partner**: 'Cerco partner che si occupano di AI/Cloud/Security'\n• 🏢 **Ricerca Aziende**: Informazioni su aziende nel database\n• 📚 **Knowledge Base**: Ricerca nei documenti caricati\n\nCosa ti interessa di più?"

def combine_responses(response_parts: List[str], intent: Dict) -> str:
    """Combine multiple response parts into final response"""
    
    if len(response_parts) == 1:
        return response_parts[0]
    
    combined = "🤖 **IntelliChat - Risposta Completa**\n\n"
    combined += "\n\n---\n\n".join(response_parts)
    
    return combined

async def save_conversation(message: str, response: str, intent: Dict, db: Session):
    """Save conversation to database"""
    
    try:
        query = """
        INSERT INTO ai_conversations (user_message, ai_response, intent_data, created_at)
        VALUES (:message, :response, :intent, NOW())
        """
        
        with db.connection() as conn:
            conn.execute(text(query), {
                "message": message,
                "response": response,
                "intent": json.dumps(intent)
            })
            conn.commit()
            
    except Exception as e:
        logger.error(f"Error saving conversation: {e}")

# services/business_card_service.py
# Servizio per elaborazione biglietti da visita - IntelligenceHUB

import logging
import uuid
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from PIL import Image
import pytesseract
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.business_card import BusinessCard

logger = logging.getLogger(__name__)

class BusinessCardService:
    """Servizio per elaborazione biglietti da visita"""
    
    def __init__(self):
        self.confidence_threshold = 0.7
        
    def process_business_card(self, db: Session, image_path: str, filename: str) -> BusinessCard:
        """
        Elabora biglietto da visita completo
        """
        try:
            # Crea record nel database
            card_id = str(uuid.uuid4())
            business_card = BusinessCard(
                id=card_id,
                filename=filename,
                original_filename=filename,
                status="processing"
            )
            db.add(business_card)
            db.commit()
            
            # Estrai testo da immagine
            extracted_text = self._extract_text_from_image(image_path)
            
            # Analizza testo estratto
            parsed_data = self._parse_business_card_text(extracted_text)
            
            # Calcola confidence score
            confidence = self._calculate_confidence_score(parsed_data)
            
            # Aggiorna record
            business_card.extracted_data = {
                "raw_text": extracted_text,
                "parsed_data": parsed_data
            }
            business_card.confidence_score = confidence
            business_card.nome = parsed_data.get("nome")
            business_card.cognome = parsed_data.get("cognome")
            business_card.azienda = parsed_data.get("azienda")
            business_card.posizione = parsed_data.get("posizione")
            business_card.email = parsed_data.get("email")
            business_card.telefono = parsed_data.get("telefono")
            business_card.indirizzo = parsed_data.get("indirizzo")
            business_card.status = "completed"
            business_card.processed_at = datetime.now()
            
            # Cerca match con aziende esistenti
            company_match = self._find_company_match(db, parsed_data.get("azienda"))
            if company_match:
                business_card.company_id = company_match
            
            db.commit()
            
            logger.info(f"Business card {card_id} elaborato con confidence {confidence:.2f}")
            return business_card
            
        except Exception as e:
            logger.error(f"Errore elaborazione business card: {e}")
            if 'business_card' in locals():
                business_card.status = "error"
                business_card.processing_error = str(e)
                db.commit()
            raise
    
    def _extract_text_from_image(self, image_path: str) -> str:
        """
        Estrai testo da immagine usando OCR
        """
        try:
            # Usa pytesseract per OCR
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang='ita+eng')
            return text.strip()
            
        except Exception as e:
            logger.error(f"Errore estrazione testo: {e}")
            return ""
    
    def _parse_business_card_text(self, text: str) -> Dict[str, Any]:
        """
        Parsing intelligente del testo estratto
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        parsed = {}
        
        # Regex patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'[\+]?[(]?[\d\s\-\(\)]{10,}'
        
        # Trova email
        email_match = re.search(email_pattern, text, re.IGNORECASE)
        if email_match:
            parsed['email'] = email_match.group()
        
        # Trova telefono
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            parsed['telefono'] = phone_match.group().strip()
        
        # Logica per nome/cognome (prime righe spesso contengono nome)
        if lines:
            # Prima linea spesso è nome
            first_line = lines[0]
            words = first_line.split()
            if len(words) >= 2:
                parsed['nome'] = words[0]
                parsed['cognome'] = ' '.join(words[1:])
            elif len(words) == 1:
                parsed['nome'] = words[0]
        
        # Cerca posizione/ruolo
        position_keywords = ['manager', 'director', 'ceo', 'cto', 'responsabile', 'direttore']
        for line in lines:
            if any(keyword in line.lower() for keyword in position_keywords):
                parsed['posizione'] = line
                break
        
        # Cerca azienda (spesso dopo il nome)
        if len(lines) >= 2:
            # Prova seconda linea come azienda
            second_line = lines[1]
            if not any(keyword in second_line.lower() for keyword in ['via', 'street', 'phone', 'tel']):
                parsed['azienda'] = second_line
        
        # Cerca indirizzo
        address_keywords = ['via', 'street', 'piazza', 'viale', 'corso']
        for line in lines:
            if any(keyword in line.lower() for keyword in address_keywords):
                parsed['indirizzo'] = line
                break
        
        return parsed
    
    def _calculate_confidence_score(self, parsed_data: Dict[str, Any]) -> float:
        """
        Calcola confidence score basato sui dati estratti
        """
        score = 0.0
        max_score = 0.0
        
        # Punteggi per campi importanti
        field_weights = {
            'nome': 0.2,
            'cognome': 0.2,
            'azienda': 0.2,
            'email': 0.2,
            'telefono': 0.1,
            'posizione': 0.1
        }
        
        for field, weight in field_weights.items():
            max_score += weight
            if field in parsed_data and parsed_data[field]:
                score += weight
        
        return score / max_score if max_score > 0 else 0.0
    
    def _find_company_match(self, db: Session, company_name: Optional[str]) -> Optional[int]:
        """
        Cerca match con aziende esistenti
        """
        if not company_name:
            return None
        
        try:
            sql = text("""
                SELECT id FROM companies 
                WHERE LOWER(nome) = LOWER(:company_name)
                OR LOWER(nome) LIKE LOWER(:company_like)
                LIMIT 1
            """)
            
            result = db.execute(sql, {
                "company_name": company_name,
                "company_like": f"%{company_name}%"
            }).fetchone()
            
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"Errore ricerca azienda: {e}")
            return None
    
    def create_contact_from_card(self, db: Session, card_id: str) -> Optional[int]:
        """
        Crea contatto da business card
        """
        try:
            # Recupera business card
            card = db.query(BusinessCard).filter(BusinessCard.id == card_id).first()
            if not card:
                return None
            
            # Crea contatto
            sql = text("""
                INSERT INTO contacts (nome, cognome, azienda, posizione, email, telefono, business_card_id)
                VALUES (:nome, :cognome, :azienda, :posizione, :email, :telefono, :card_id)
                RETURNING id
            """)
            
            result = db.execute(sql, {
                "nome": card.nome,
                "cognome": card.cognome,
                "azienda": card.azienda,
                "posizione": card.posizione,
                "email": card.email,
                "telefono": card.telefono,
                "card_id": card_id
            }).fetchone()
            
            if result:
                contact_id = result[0]
                card.contact_id = contact_id
                db.commit()
                return contact_id
            
            return None
            
        except Exception as e:
            logger.error(f"Errore creazione contatto: {e}")
            return None
    
    def get_business_cards(self, db: Session, limit: int = 50) -> List[BusinessCard]:
        """
        Recupera lista business cards
        """
        return db.query(BusinessCard).order_by(BusinessCard.created_at.desc()).limit(limit).all()
    
    def get_business_card_stats(self, db: Session) -> Dict[str, Any]:
        """
        Statistiche business cards
        """
        try:
            stats = {}
            
            # Conteggio totale
            total = db.query(BusinessCard).count()
            stats['total'] = total
            
            # Per status
            status_counts = db.execute(text("""
                SELECT status, COUNT(*) as count
                FROM business_cards
                GROUP BY status
            """)).fetchall()
            
            stats['by_status'] = {row.status: row.count for row in status_counts}
            
            # Confidence score medio
            avg_confidence = db.execute(text("""
                SELECT AVG(confidence_score) as avg_confidence
                FROM business_cards
                WHERE status = 'completed'
            """)).scalar()
            
            stats['avg_confidence'] = float(avg_confidence) if avg_confidence else 0.0
            
            return stats
            
        except Exception as e:
            logger.error(f"Errore statistiche business cards: {e}")
            return {}
    
    def health_check(self) -> Dict[str, Any]:
        """Health check del servizio"""
        return {
            "healthy": True,
            "confidence_threshold": self.confidence_threshold,
            "service": "BusinessCardService"
        }

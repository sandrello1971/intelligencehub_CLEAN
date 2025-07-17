# routes/business_cards.py
# API endpoints per Business Cards - IntelligenceHUB

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import os
import uuid
from datetime import datetime

from app.database import get_db
from app.schemas.business_card import (
   BusinessCardResponse, 
   BusinessCardUpload,
   BusinessCardListResponse,
   BusinessCardStats
)
from app.services.business_card_service import BusinessCardService
from app.models.business_card import BusinessCard

router = APIRouter(prefix="/business-cards", tags=["Business Cards"])

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inizializza servizio
bc_service = BusinessCardService()

# Directory per upload
UPLOAD_DIR = "/var/www/intelligence/backend/uploads/business_cards"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=BusinessCardResponse)
async def upload_business_card(
   file: UploadFile = File(...),
   db: Session = Depends(get_db)
):
   """
   Upload e elaborazione business card
   """
   try:
       # Valida file
       if not file.content_type.startswith('image/'):
           raise HTTPException(
               status_code=400,
               detail="File deve essere un'immagine"
           )
       
       # Genera nome file unico
       file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
       unique_filename = f"{uuid.uuid4()}.{file_extension}"
       file_path = os.path.join(UPLOAD_DIR, unique_filename)
       
       # Salva file
       with open(file_path, "wb") as f:
           content = await file.read()
           f.write(content)
       
       # Elabora business card
       business_card = bc_service.process_business_card(
           db=db,
           image_path=file_path,
           filename=unique_filename
       )
       
       logger.info(f"Business card {business_card.id} elaborata con successo")
       return business_card
       
   except Exception as e:
       logger.error(f"Errore upload business card: {e}")
       raise HTTPException(
           status_code=500,
           detail=f"Errore durante l'elaborazione: {str(e)}"
       )

@router.get("/", response_model=BusinessCardListResponse)
async def get_business_cards(
   limit: int = 50,
   db: Session = Depends(get_db)
):
   """
   Recupera lista business cards
   """
   try:
       business_cards = bc_service.get_business_cards(db, limit=limit)
       stats = bc_service.get_business_card_stats(db)
       
       return BusinessCardListResponse(
           business_cards=business_cards,
           total=len(business_cards),
           stats=BusinessCardStats(**stats)
       )
       
   except Exception as e:
       logger.error(f"Errore recupero business cards: {e}")
       raise HTTPException(
           status_code=500,
           detail="Errore durante il recupero dati"
       )

@router.get("/{card_id}", response_model=BusinessCardResponse)
async def get_business_card(
   card_id: str,
   db: Session = Depends(get_db)
):
   """
   Recupera business card per ID
   """
   try:
       business_card = db.query(BusinessCard).filter(BusinessCard.id == card_id).first()
       
       if not business_card:
           raise HTTPException(
               status_code=404,
               detail="Business card non trovata"
           )
       
       return business_card
       
   except HTTPException:
       raise
   except Exception as e:
       logger.error(f"Errore recupero business card {card_id}: {e}")
       raise HTTPException(
           status_code=500,
           detail="Errore durante il recupero"
       )

@router.post("/{card_id}/create-contact")
async def create_contact_from_card(
   card_id: str,
   db: Session = Depends(get_db)
):
   """
   Crea contatto da business card
   """
   try:
       contact_id = bc_service.create_contact_from_card(db, card_id)
       
       if not contact_id:
           raise HTTPException(
               status_code=400,
               detail="Impossibile creare contatto"
           )
       
       return {
           "message": "Contatto creato con successo",
           "contact_id": contact_id,
           "card_id": card_id
       }
       
   except HTTPException:
       raise
   except Exception as e:
       logger.error(f"Errore creazione contatto da card {card_id}: {e}")
       raise HTTPException(
           status_code=500,
           detail="Errore durante la creazione contatto"
       )

@router.get("/stats/overview")
async def get_business_card_stats(db: Session = Depends(get_db)):
   """
   Statistiche business cards
   """
   try:
       stats = bc_service.get_business_card_stats(db)
       return {
           "stats": stats,
           "timestamp": datetime.now().isoformat()
       }
       
   except Exception as e:
       logger.error(f"Errore statistiche business cards: {e}")
       raise HTTPException(
           status_code=500,
           detail="Errore durante il recupero statistiche"
       )

@router.delete("/{card_id}")
async def delete_business_card(
   card_id: str,
   db: Session = Depends(get_db)
):
   """
   Elimina business card
   """
   try:
       business_card = db.query(BusinessCard).filter(BusinessCard.id == card_id).first()
       
       if not business_card:
           raise HTTPException(
               status_code=404,
               detail="Business card non trovata"
           )
       
       # Elimina file se esiste
       if business_card.filename:
           file_path = os.path.join(UPLOAD_DIR, business_card.filename)
           if os.path.exists(file_path):
               os.remove(file_path)
       
       # Elimina da database
       db.delete(business_card)
       db.commit()
       
       return {"message": "Business card eliminata con successo"}
       
   except HTTPException:
       raise
   except Exception as e:
       logger.error(f"Errore eliminazione business card {card_id}: {e}")
       raise HTTPException(
           status_code=500,
           detail="Errore durante l'eliminazione"
       )

@router.get("/health/check")
async def health_check():
   """Health check business cards module"""
   return {
       "status": "healthy",
       "service": "BusinessCards",
       "service_health": bc_service.health_check(),
       "upload_dir": UPLOAD_DIR,
       "timestamp": datetime.now().isoformat()
   }

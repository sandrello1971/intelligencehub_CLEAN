# IntelliVoice 2.0 - Endpoint /record migliorato
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from openai import OpenAI
import os
import tempfile
import shutil
import json
import mimetypes
import subprocess
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.routes.auth import get_current_user_dep as get_current_user
from app.models.kit_commerciali import KitCommerciale

router = APIRouter(prefix="/api/v1/intellivoice", tags=["IntelliVoice 2.0"])

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo")

class RecordResponse(BaseModel):
    success: bool
    transcript: str
    analysis: dict
    timestamp: str

@router.post("/record", response_model=RecordResponse)
async def record_voice(
    audio: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """🎙️ IntelliVoice 2.0: Registrazione e analisi completa"""
    try:
        # 1. GESTIONE FILE AUDIO
        content_type = audio.content_type or "application/octet-stream"
        extension = mimetypes.guess_extension(content_type) or ".webm"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp_in:
            shutil.copyfileobj(audio.file, tmp_in)
            input_path = tmp_in.name

        output_path = input_path.replace(extension, ".mp3")
        
        try:
            # 2. CONVERSIONE AUDIO
            subprocess.run(
                ["ffmpeg", "-i", input_path, "-ar", "16000", output_path],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # 3. TRASCRIZIONE WHISPER
            with open(output_path, "rb") as f:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f
                )
            
            # 4. ANALISI AI
            analysis = await analyze_transcript_simple(transcript.text, db)
            
            return RecordResponse(
                success=True,
                transcript=transcript.text,
                analysis=analysis,
                timestamp=datetime.now().isoformat()
            )
            
        finally:
            # CLEANUP FILES
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)
                
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Errore conversione audio")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore trascrizione: {str(e)}")

async def analyze_transcript_simple(transcript: str, db: Session) -> dict:
    """Analisi AI semplificata del transcript"""
    try:
        # Lista kit commerciali
        kits = db.query(KitCommerciale).filter(
            KitCommerciale.attivo == True
        ).all()
        kits_list = "\n".join([f"- {kit.nome}" for kit in kits])
        
        # Prompt AI semplice
        prompt = f"""
Analizza questo transcript e estrai:

TRANSCRIPT: "{transcript}"

KIT COMMERCIALI DISPONIBILI:
{kits_list}

Rispondi in JSON:
{{
    "azienda_menzionata": "nome azienda se presente",
    "kit_rilevanti": ["kit1", "kit2"],
    "note_principali": "riassunto contenuto"
}}
"""

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Rispondi sempre in JSON valido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse JSON
        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "").strip()
        
        return json.loads(content)
        
    except Exception as e:
        print(f"[ERROR] Analisi fallita: {e}")
        return {
            "azienda_menzionata": "Non rilevata",
            "kit_rilevanti": [],
            "note_principali": transcript[:200] + "..." if len(transcript) > 200 else transcript
        }

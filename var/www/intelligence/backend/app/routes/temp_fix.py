# Query corretta per articoli disponibili
@router.get("/articoli-disponibili")
async def get_articoli_disponibili(db: Session = Depends(get_db)):
    """Lista tutti gli articoli disponibili per aggiungere ai kit"""
    try:
        query = """
        SELECT 
            id, 
            nome, 
            codice, 
            descrizione, 
            tipo_prodotto,
            attivo
        FROM articoli 
        WHERE attivo = true 
        ORDER BY codice
        """
        
        result = db.execute(text(query))
        articoli_data = []
        
        for row in result:
            articoli_data.append({
                "id": row.id,
                "codice": row.codice,
                "nome": row.nome,
                "descrizione": row.descrizione,
                "tipo_prodotto": row.tipo_prodotto,
                "attivo": row.attivo
            })
        
        return {
            "success": True,
            "count": len(articoli_data),
            "articoli": articoli_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore: {str(e)}")

@router.get("/articoli-compositi")
async def get_articoli_compositi(db: Session = Depends(get_db)):
    """Lista articoli compositi per articolo principale"""
    try:
        query = """
        SELECT 
            id, 
            nome, 
            codice, 
            descrizione
        FROM articoli 
        WHERE tipo_prodotto = 'composito' AND attivo = true 
        ORDER BY codice
        """
        
        result = db.execute(text(query))
        compositi_data = []
        
        for row in result:
            compositi_data.append({
                "id": row.id,
                "codice": row.codice,
                "nome": row.nome,
                "descrizione": row.descrizione
            })
        
        return {
            "success": True,
            "count": len(compositi_data),
            "articoli_compositi": compositi_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore: {str(e)}")

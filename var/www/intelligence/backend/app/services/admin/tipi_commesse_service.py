# services/admin/tipi_commesse_service.py
# Business Logic Service per Tipi Commesse - IntelligenceHUB

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text
from typing import List, Optional, Dict, Any
import csv
import io
from datetime import datetime
import uuid

from app.models.tipi_commesse import TipoCommessa as TipoCommessaModel
from app.schemas.admin import TipoCommessa, TipoCommessaCreate, TipoCommessaUpdate

class TipiCommesseService:
    """
    Service class per gestione business logic Tipi Commesse
    """
    
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[TipoCommessa]:
        """
        Recupera tutti i tipi commesse attivi
        """
        try:
            query = self.db.query(TipoCommessaModel).filter(
                TipoCommessaModel.is_active == True
            ).order_by(TipoCommessaModel.nome)
            
            return [TipoCommessa.from_orm(item) for item in query.all()]
        except Exception as e:
            raise Exception(f"Errore recupero tipi commesse: {str(e)}")

    def get_paginated(
        self, 
        page: int = 1, 
        per_page: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Recupera tipi commesse con paginazione e filtri
        """
        try:
            query = self.db.query(TipoCommessaModel)
            
            # Applica filtri
            if search:
                search_filter = or_(
                    TipoCommessaModel.nome.ilike(f"%{search}%"),
                    TipoCommessaModel.codice.ilike(f"%{search}%"),
                    TipoCommessaModel.descrizione.ilike(f"%{search}%")
                )
                query = query.filter(search_filter)
            
            if is_active is not None:
                query = query.filter(TipoCommessaModel.is_active == is_active)
            
            # Conta totale
            total = query.count()
            
            # Applica paginazione
            offset = (page - 1) * per_page
            items = query.order_by(TipoCommessaModel.nome).offset(offset).limit(per_page).all()
            
            # Calcola pagine totali
            total_pages = (total + per_page - 1) // per_page
            
            return {
                "data": [TipoCommessa.from_orm(item) for item in items],
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        except Exception as e:
            raise Exception(f"Errore recupero paginato: {str(e)}")

    def get_by_id(self, tipo_commessa_id: str) -> Optional[TipoCommessa]:
        """
        Recupera tipo commessa per ID
        """
        try:
            item = self.db.query(TipoCommessaModel).filter(
                TipoCommessaModel.id == tipo_commessa_id
            ).first()
            
            if item:
                return TipoCommessa.from_orm(item)
            return None
        except Exception as e:
            raise Exception(f"Errore recupero tipo commessa {tipo_commessa_id}: {str(e)}")

    def get_by_code(self, codice: str) -> Optional[TipoCommessa]:
        """
        Recupera tipo commessa per codice
        """
        try:
            item = self.db.query(TipoCommessaModel).filter(
                TipoCommessaModel.codice == codice.upper()
            ).first()
            
            if item:
                return TipoCommessa.from_orm(item)
            return None
        except Exception as e:
            raise Exception(f"Errore recupero tipo commessa con codice {codice}: {str(e)}")

    def create(self, tipo_commessa_data: TipoCommessaCreate, user_id: str) -> TipoCommessa:
        """
        Crea nuovo tipo commessa
        """
        try:
            # Verifica codice univoco
            existing = self.get_by_code(tipo_commessa_data.codice)
            if existing:
                raise ValueError(f"Codice {tipo_commessa_data.codice} già esistente")
            
            # Crea nuovo record
            db_item = TipoCommessaModel(
                id=str(uuid.uuid4()),
                nome=tipo_commessa_data.nome.strip(),
                codice=tipo_commessa_data.codice.upper().strip(),
                descrizione=tipo_commessa_data.descrizione.strip() if tipo_commessa_data.descrizione else None,
                sla_default_hours=tipo_commessa_data.sla_default_hours,
                is_active=tipo_commessa_data.is_active if tipo_commessa_data.is_active is not None else True,
                created_by=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(db_item)
            self.db.commit()
            self.db.refresh(db_item)
            
            return TipoCommessa.from_orm(db_item)
        except ValueError:
            raise
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Errore creazione tipo commessa: {str(e)}")

    def update(self, tipo_commessa_id: str, tipo_commessa_data: TipoCommessaUpdate, user_id: str) -> TipoCommessa:
        """
        Aggiorna tipo commessa esistente
        """
        try:
            db_item = self.db.query(TipoCommessaModel).filter(
                TipoCommessaModel.id == tipo_commessa_id
            ).first()
            
            if not db_item:
                raise ValueError(f"Tipo commessa {tipo_commessa_id} non trovato")
            
            # Verifica codice univoco se modificato
            if tipo_commessa_data.codice and tipo_commessa_data.codice.upper() != db_item.codice:
                existing = self.get_by_code(tipo_commessa_data.codice)
                if existing and existing.id != tipo_commessa_id:
                    raise ValueError(f"Codice {tipo_commessa_data.codice} già esistente")
            
            # Aggiorna campi
            update_data = tipo_commessa_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if field == 'codice' and value:
                    setattr(db_item, field, value.upper().strip())
                elif field == 'nome' and value:
                    setattr(db_item, field, value.strip())
                elif field == 'descrizione':
                    setattr(db_item, field, value.strip() if value else None)
                else:
                    setattr(db_item, field, value)
            
            db_item.updated_by = user_id
            db_item.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(db_item)
            
            return TipoCommessa.from_orm(db_item)
        except ValueError:
            raise
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Errore aggiornamento tipo commessa: {str(e)}")

    def delete(self, tipo_commessa_id: str) -> bool:
        """
        Elimina tipo commessa
        """
        try:
            # Verifica che non sia in uso
            if self.is_in_use(tipo_commessa_id):
                raise ValueError("Impossibile eliminare: tipo commessa in uso")
            
            db_item = self.db.query(TipoCommessaModel).filter(
                TipoCommessaModel.id == tipo_commessa_id
            ).first()
            
            if not db_item:
                raise ValueError(f"Tipo commessa {tipo_commessa_id} non trovato")
            
            self.db.delete(db_item)
            self.db.commit()
            
            return True
        except ValueError:
            raise
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Errore eliminazione tipo commessa: {str(e)}")

    def toggle_active(self, tipo_commessa_id: str, is_active: bool, user_id: str) -> TipoCommessa:
        """
        Attiva/disattiva tipo commessa
        """
        try:
            db_item = self.db.query(TipoCommessaModel).filter(
                TipoCommessaModel.id == tipo_commessa_id
            ).first()
            
            if not db_item:
                raise ValueError(f"Tipo commessa {tipo_commessa_id} non trovato")
            
            db_item.is_active = is_active
            db_item.updated_by = user_id
            db_item.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(db_item)
            
            return TipoCommessa.from_orm(db_item)
        except ValueError:
            raise
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Errore toggle attivazione: {str(e)}")

    def duplicate(self, tipo_commessa_id: str, new_name: Optional[str], user_id: str) -> TipoCommessa:
        """
        Duplica tipo commessa esistente
        """
        try:
            original = self.db.query(TipoCommessaModel).filter(
                TipoCommessaModel.id == tipo_commessa_id
            ).first()
            
            if not original:
                raise ValueError(f"Tipo commessa {tipo_commessa_id} non trovato")
            
            # Genera nuovo nome e codice
            nome = new_name if new_name else f"{original.nome} (Copia)"
            codice = f"{original.codice}_COPY"
            
            # Assicura codice univoco
            counter = 1
            while self.get_by_code(codice):
                codice = f"{original.codice}_COPY{counter}"
                counter += 1
            
            # Crea duplicato
            duplicate_data = TipoCommessaCreate(
                nome=nome,
                codice=codice,
                descrizione=original.descrizione,
                sla_default_hours=original.sla_default_hours,
                is_active=False  # Nuovo duplicato inattivo per sicurezza
            )
            
            return self.create(duplicate_data, user_id)
        except ValueError:
            raise
        except Exception as e:
            raise Exception(f"Errore duplicazione tipo commessa: {str(e)}")

    def check_code_availability(self, codice: str, exclude_id: Optional[str] = None) -> bool:
        """
        Verifica disponibilità codice
        """
        try:
            query = self.db.query(TipoCommessaModel).filter(
                TipoCommessaModel.codice == codice.upper()
            )
            
            if exclude_id:
                query = query.filter(TipoCommessaModel.id != exclude_id)
            
            existing = query.first()
            return existing is None
        except Exception as e:
            raise Exception(f"Errore verifica codice: {str(e)}")

    def is_in_use(self, tipo_commessa_id: str) -> bool:
        """
        Verifica se tipo commessa è in uso
        """
        try:
            # Verifica in milestones
            milestone_count = self.db.execute(text("""
                SELECT COUNT(*) FROM milestones 
                WHERE tipo_commessa_id = :tipo_commessa_id
            """), {"tipo_commessa_id": tipo_commessa_id}).scalar()
            
            # Verifica in opportunities  
                SELECT COUNT(*) FROM opportunities 
                WHERE tipo_commessa_id = :tipo_commessa_id
            """), {"tipo_commessa_id": tipo_commessa_id}).scalar()
            
        except Exception as e:
            raise Exception(f"Errore verifica utilizzo: {str(e)}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Recupera statistiche tipi commesse
        """
        try:
            total = self.db.query(TipoCommessaModel).count()
            active = self.db.query(TipoCommessaModel).filter(TipoCommessaModel.is_active == True).count()
            inactive = total - active
            
            # Tipi più utilizzati (se tabelle esistono)
            most_used_query = self.db.execute(text("""
                SELECT tc.id, tc.nome, tc.codice, 
                FROM sub_types tc
                LEFT JOIN (
                    SELECT tipo_commessa_id, COUNT(*) as milestone_count
                    FROM milestones 
                    GROUP BY tipo_commessa_id
                ) m ON tc.id = m.tipo_commessa_id
                LEFT JOIN (
                    FROM opportunities
                    GROUP BY tipo_commessa_id
                ) o ON tc.id = o.tipo_commessa_id
                WHERE tc.is_active = true
                ORDER BY usage_count DESC
                LIMIT 5
            """)).fetchall()
            
            most_used = [
                {
                    "id": row[0],
                    "nome": row[1], 
                    "codice": row[2],
                    "usage_count": row[3]
                }
                for row in most_used_query
            ]
            
            return {
                "total": total,
                "active": active,
                "inactive": inactive,
                "most_used": most_used
            }
        except Exception as e:
            raise Exception(f"Errore recupero statistiche: {str(e)}")

    def export_to_csv(self) -> str:
        """
        Esporta tipi commesse in formato CSV
        """
        try:
            items = self.db.query(TipoCommessaModel).order_by(TipoCommessaModel.nome).all()
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow([
                'ID', 'Nome', 'Codice', 'Descrizione', 
                'SLA Default (ore)', 'Attivo', 'Creato il'
            ])
            
            # Dati
            for item in items:
                writer.writerow([
                    item.id,
                    item.nome,
                    item.codice,
                    item.descrizione or '',
                    item.sla_default_hours,
                    'Sì' if item.is_active else 'No',
                    item.created_at.strftime('%Y-%m-%d %H:%M:%S') if item.created_at else ''
                ])
            
            return output.getvalue()
        except Exception as e:
            raise Exception(f"Errore esportazione CSV: {str(e)}")

    def import_from_csv(self, csv_data: str, user_id: str) -> Dict[str, Any]:
        """
        Importa tipi commesse da CSV
        """
        try:
            reader = csv.DictReader(io.StringIO(csv_data))
            imported = 0
            errors = []
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Validazione dati richiesti
                    if not row.get('Nome') or not row.get('Codice'):
                        errors.append(f"Riga {row_num}: Nome e Codice sono obbligatori")
                        continue
                    
                    # Prepara dati
                    tipo_commessa_data = TipoCommessaCreate(
                        nome=row['Nome'].strip(),
                        codice=row['Codice'].strip().upper(),
                        descrizione=row.get('Descrizione', '').strip() or None,
                        sla_default_hours=int(row.get('SLA Default (ore)', 48)),
                        is_active=row.get('Attivo', 'Sì').lower() in ['sì', 'si', 'yes', 'true', '1']
                    )
                    
                    # Verifica codice univoco
                    if not self.check_code_availability(tipo_commessa_data.codice):
                        errors.append(f"Riga {row_num}: Codice {tipo_commessa_data.codice} già esistente")
                        continue
                    
                    # Crea record
                    self.create(tipo_commessa_data, user_id)
                    imported += 1
                    
                except ValueError as e:
                    errors.append(f"Riga {row_num}: {str(e)}")
                except Exception as e:
                    errors.append(f"Riga {row_num}: Errore imprevisto - {str(e)}")
            
            return {
                "imported": imported,
                "errors": errors
            }
        except Exception as e:
            raise Exception(f"Errore importazione CSV: {str(e)}")

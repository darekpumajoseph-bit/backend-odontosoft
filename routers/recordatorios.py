from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db

router = APIRouter(prefix="/recordatorios", tags=["Recordatorios"])

@router.get("/", response_model=List[schemas.RecordatorioOut])
def get_recordatorios(db: Session = Depends(get_db)):
    return db.query(models.Recordatorio).all()

@router.get("/cita/{cita_id}", response_model=List[schemas.RecordatorioOut])
def get_recordatorios_por_cita(cita_id: int, db: Session = Depends(get_db)):
    return db.query(models.Recordatorio).filter(
        models.Recordatorio.id_cita == cita_id
    ).all()

@router.post("/", response_model=schemas.RecordatorioOut, status_code=201)
def create_recordatorio(data: schemas.RecordatorioCreate, db: Session = Depends(get_db)):
    nuevo = models.Recordatorio(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/{id}", response_model=schemas.RecordatorioOut)
def update_recordatorio(id: int, data: schemas.RecordatorioCreate, db: Session = Depends(get_db)):
    r = db.query(models.Recordatorio).filter(models.Recordatorio.id_recordatorio == id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Recordatorio no encontrado")
    for k, v in data.model_dump().items():
        setattr(r, k, v)
    db.commit()
    db.refresh(r)
    return r

@router.delete("/{id}")
def delete_recordatorio(id: int, db: Session = Depends(get_db)):
    r = db.query(models.Recordatorio).filter(models.Recordatorio.id_recordatorio == id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Recordatorio no encontrado")
    db.delete(r)
    db.commit()
    return {"mensaje": "Recordatorio eliminado correctamente"}
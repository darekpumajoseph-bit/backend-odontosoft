from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db

router = APIRouter(prefix="/historias-clinicas", tags=["Historias Clínicas"])

@router.get("/", response_model=List[schemas.HistoriaClinicaOut])
def get_historias(db: Session = Depends(get_db)):
    return db.query(models.HistoriaClinica).all()

@router.get("/paciente/{paciente_id}", response_model=List[schemas.HistoriaClinicaOut])
def get_historias_por_paciente(paciente_id: int, db: Session = Depends(get_db)):
    return db.query(models.HistoriaClinica).filter(
        models.HistoriaClinica.id_paciente == paciente_id
    ).all()

@router.get("/{id}", response_model=schemas.HistoriaClinicaOut)
def get_historia(id: int, db: Session = Depends(get_db)):
    h = db.query(models.HistoriaClinica).filter(models.HistoriaClinica.id_historia == id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Historia clínica no encontrada")
    return h

@router.post("/", response_model=schemas.HistoriaClinicaOut, status_code=201)
def create_historia(data: schemas.HistoriaClinicaCreate, db: Session = Depends(get_db)):
    nuevo = models.HistoriaClinica(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/{id}", response_model=schemas.HistoriaClinicaOut)
def update_historia(id: int, data: schemas.HistoriaClinicaCreate, db: Session = Depends(get_db)):
    h = db.query(models.HistoriaClinica).filter(models.HistoriaClinica.id_historia == id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Historia clínica no encontrada")
    for k, v in data.model_dump().items():
        setattr(h, k, v)
    db.commit()
    db.refresh(h)
    return h

@router.delete("/{id}")
def delete_historia(id: int, db: Session = Depends(get_db)):
    h = db.query(models.HistoriaClinica).filter(models.HistoriaClinica.id_historia == id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Historia clínica no encontrada")
    db.delete(h)
    db.commit()
    return {"mensaje": "Historia clínica eliminada correctamente"}
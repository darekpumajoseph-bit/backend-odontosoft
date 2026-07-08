from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db

router = APIRouter(prefix="/pagos", tags=["Pagos"])

@router.get("/", response_model=List[schemas.PagoOut])
def get_pagos(db: Session = Depends(get_db)):
    return db.query(models.Pago).all()

@router.get("/cita/{cita_id}", response_model=List[schemas.PagoOut])
def get_pagos_por_cita(cita_id: int, db: Session = Depends(get_db)):
    return db.query(models.Pago).filter(models.Pago.id_cita == cita_id).all()

@router.post("/", response_model=schemas.PagoOut, status_code=201)
def create_pago(data: schemas.PagoCreate, db: Session = Depends(get_db)):
    nuevo = models.Pago(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/{id}", response_model=schemas.PagoOut)
def update_pago(id: int, data: schemas.PagoCreate, db: Session = Depends(get_db)):
    p = db.query(models.Pago).filter(models.Pago.id_pago == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    for k, v in data.model_dump().items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return p

@router.delete("/{id}")
def delete_pago(id: int, db: Session = Depends(get_db)):
    p = db.query(models.Pago).filter(models.Pago.id_pago == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    db.delete(p)
    db.commit()
    return {"mensaje": "Pago eliminado correctamente"}
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import get_db

router = APIRouter(prefix="/servicios", tags=["Servicios"])

@router.get("/", response_model=List[schemas.ServicioOut])
def get_servicios(db: Session = Depends(get_db)):
    return db.query(models.Servicio).all()

@router.get("/{id}", response_model=schemas.ServicioOut)
def get_servicio(id: int, db: Session = Depends(get_db)):
    s = db.query(models.Servicio).filter(models.Servicio.id == id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return s

@router.get("/paciente/{paciente_id}", response_model=List[schemas.ServicioOut])
def get_servicios_por_paciente(paciente_id: int, db: Session = Depends(get_db)):
    return db.query(models.Servicio).filter(models.Servicio.paciente_id == paciente_id).all()

@router.post("/", response_model=schemas.ServicioOut, status_code=201)
def create_servicio(data: schemas.ServicioCreate, db: Session = Depends(get_db)):
    nuevo = models.Servicio(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/{id}", response_model=schemas.ServicioOut)
def update_servicio(id: int, data: schemas.ServicioUpdate, db: Session = Depends(get_db)):
    s = db.query(models.Servicio).filter(models.Servicio.id == id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(s, key, value)
    
    db.commit()
    db.refresh(s)
    return s

@router.delete("/{id}")
def delete_servicio(id: int, db: Session = Depends(get_db)):
    s = db.query(models.Servicio).filter(models.Servicio.id == id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    db.delete(s)
    db.commit()
    return {"mensaje": "Servicio eliminado correctamente"}
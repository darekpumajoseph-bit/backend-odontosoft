from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db

router = APIRouter(prefix="/consultorios", tags=["Consultorios"])

@router.get("/", response_model=List[schemas.ConsultorioOut])
def get_consultorios(db: Session = Depends(get_db)):
    return db.query(models.Consultorio).all()

@router.get("/{id}", response_model=schemas.ConsultorioOut)
def get_consultorio(id: int, db: Session = Depends(get_db)):
    c = db.query(models.Consultorio).filter(models.Consultorio.id_consultorio == id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Consultorio no encontrado")
    return c

@router.post("/", response_model=schemas.ConsultorioOut, status_code=201)
def create_consultorio(data: schemas.ConsultorioCreate, db: Session = Depends(get_db)):
    nuevo = models.Consultorio(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/{id}", response_model=schemas.ConsultorioOut)
def update_consultorio(id: int, data: schemas.ConsultorioCreate, db: Session = Depends(get_db)):
    c = db.query(models.Consultorio).filter(models.Consultorio.id_consultorio == id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Consultorio no encontrado")
    for k, v in data.model_dump().items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return c

@router.delete("/{id}")
def delete_consultorio(id: int, db: Session = Depends(get_db)):
    c = db.query(models.Consultorio).filter(models.Consultorio.id_consultorio == id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Consultorio no encontrado")
    db.delete(c)
    db.commit()
    return {"mensaje": "Consultorio eliminado correctamente"}
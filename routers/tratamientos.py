# routers/tratamientos.py - CRUD completo de tratamientos (SIN id_cita)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import get_db

router = APIRouter(prefix="/tratamientos", tags=["Tratamientos"])


@router.get("/", response_model=List[schemas.TratamientoOut])
def get_tratamientos(db: Session = Depends(get_db)):
    """Obtener todos los tratamientos del catálogo"""
    return db.query(models.Tratamiento).all()


@router.get("/{id}", response_model=schemas.TratamientoOut)
def get_tratamiento(id: int, db: Session = Depends(get_db)):
    """Obtener un tratamiento por ID"""
    tratamiento = db.query(models.Tratamiento).filter(models.Tratamiento.id_tratamiento == id).first()
    if not tratamiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tratamiento no encontrado"
        )
    return tratamiento


@router.post("/", response_model=schemas.TratamientoOut, status_code=status.HTTP_201_CREATED)
def create_tratamiento(data: schemas.TratamientoCreate, db: Session = Depends(get_db)):
    """
    Crear un nuevo tratamiento en el catálogo.
    Ya no recibe id_cita. La asociación con citas se hace en el endpoint de citas.
    """
    nuevo = models.Tratamiento(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/{id}", response_model=schemas.TratamientoOut)
def update_tratamiento(id: int, data: schemas.TratamientoUpdate, db: Session = Depends(get_db)):
    """
    Actualizar un tratamiento existente en el catálogo.
    Ya no recibe id_cita.
    """
    tratamiento = db.query(models.Tratamiento).filter(models.Tratamiento.id_tratamiento == id).first()
    if not tratamiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tratamiento no encontrado"
        )
    
    update_data = data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(tratamiento, key, value)
    
    db.commit()
    db.refresh(tratamiento)
    return tratamiento


@router.delete("/{id}")
def delete_tratamiento(id: int, db: Session = Depends(get_db)):
    """Eliminar un tratamiento del catálogo"""
    tratamiento = db.query(models.Tratamiento).filter(models.Tratamiento.id_tratamiento == id).first()
    if not tratamiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tratamiento no encontrado"
        )
    
    db.delete(tratamiento)
    db.commit()
    return {"mensaje": "Tratamiento eliminado correctamente", "id_tratamiento": id}
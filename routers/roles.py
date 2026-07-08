from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import get_db

router = APIRouter(prefix="/roles", tags=["Roles"])

@router.get("/", response_model=List[schemas.RolOut])
def get_roles(db: Session = Depends(get_db)):
    return db.query(models.Rol).all()

@router.get("/{id}", response_model=schemas.RolOut)
def get_rol(id: int, db: Session = Depends(get_db)):
    rol = db.query(models.Rol).filter(models.Rol.id == id).first()
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return rol

@router.post("/", response_model=schemas.RolOut, status_code=201)
def create_rol(data: schemas.RolCreate, db: Session = Depends(get_db)):
    nuevo = models.Rol(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/{id}", response_model=schemas.RolOut)
def update_rol(id: int, data: schemas.RolUpdate, db: Session = Depends(get_db)):
    rol = db.query(models.Rol).filter(models.Rol.id == id).first()
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(rol, key, value)
    
    db.commit()
    db.refresh(rol)
    return rol

@router.delete("/{id}")
def delete_rol(id: int, db: Session = Depends(get_db)):
    rol = db.query(models.Rol).filter(models.Rol.id == id).first()
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    db.delete(rol)
    db.commit()
    return {"mensaje": "Rol eliminado correctamente"}
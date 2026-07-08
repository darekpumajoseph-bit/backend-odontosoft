from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import get_db

router = APIRouter(prefix="/proveedores", tags=["Proveedores"])

@router.get("/", response_model=List[schemas.ProveedorOut])
def get_proveedores(db: Session = Depends(get_db)):
    return db.query(models.Proveedor).all()

@router.get("/{id}", response_model=schemas.ProveedorOut)
def get_proveedor(id: int, db: Session = Depends(get_db)):
    p = db.query(models.Proveedor).filter(models.Proveedor.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return p

@router.post("/", response_model=schemas.ProveedorOut, status_code=201)
def create_proveedor(data: schemas.ProveedorCreate, db: Session = Depends(get_db)):
    nuevo = models.Proveedor(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/{id}", response_model=schemas.ProveedorOut)
def update_proveedor(id: int, data: schemas.ProveedorUpdate, db: Session = Depends(get_db)):
    p = db.query(models.Proveedor).filter(models.Proveedor.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(p, key, value)
    
    db.commit()
    db.refresh(p)
    return p

@router.delete("/{id}")
def delete_proveedor(id: int, db: Session = Depends(get_db)):
    p = db.query(models.Proveedor).filter(models.Proveedor.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    db.delete(p)
    db.commit()
    return {"mensaje": "Proveedor eliminado correctamente"}
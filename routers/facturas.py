from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db

router = APIRouter(prefix="/facturas", tags=["Facturas"])

@router.get("/", response_model=List[schemas.FacturaOut])
def get_facturas(db: Session = Depends(get_db)):
    return db.query(models.Factura).all()

@router.get("/{id}", response_model=schemas.FacturaOut)
def get_factura(id: int, db: Session = Depends(get_db)):
    f = db.query(models.Factura).filter(models.Factura.id_factura == id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return f

@router.post("/", response_model=schemas.FacturaOut, status_code=201)
def create_factura(data: schemas.FacturaCreate, db: Session = Depends(get_db)):
    nuevo = models.Factura(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/{id}", response_model=schemas.FacturaOut)
def update_factura(id: int, data: schemas.FacturaCreate, db: Session = Depends(get_db)):
    f = db.query(models.Factura).filter(models.Factura.id_factura == id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    for k, v in data.model_dump().items():
        setattr(f, k, v)
    db.commit()
    db.refresh(f)
    return f

@router.delete("/{id}")
def delete_factura(id: int, db: Session = Depends(get_db)):
    f = db.query(models.Factura).filter(models.Factura.id_factura == id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    db.delete(f)
    db.commit()
    return {"mensaje": "Factura eliminada correctamente"}
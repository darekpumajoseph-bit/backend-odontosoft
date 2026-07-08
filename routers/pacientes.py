# routers/pacientes.py - CRUD completo de pacientes

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import get_db

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


@router.get("/", response_model=List[schemas.PacienteOut])
def get_pacientes(db: Session = Depends(get_db)):

    pacientes = (
        db.query(models.Paciente)
        .join(models.Paciente.usuarios)
        .filter(
            models.Usuario.rol == "Paciente",
            models.Usuario.estado == "Activo"
        )
        .all()
    )

    return pacientes

@router.get("/{id}", response_model=schemas.PacienteOut)
def get_paciente(id: int, db: Session = Depends(get_db)):
    """Obtener un paciente por ID"""
    paciente = db.query(models.Paciente).filter(models.Paciente.id_paciente == id).first()
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado"
        )
    return paciente


@router.get("/documento/{documento}", response_model=schemas.PacienteOut)
def get_paciente_by_documento(documento: str, db: Session = Depends(get_db)):
    """Obtener un paciente por número de documento"""
    paciente = db.query(models.Paciente).filter(models.Paciente.documento == documento).first()
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado"
        )
    return paciente


@router.post("/", response_model=schemas.PacienteOut, status_code=status.HTTP_201_CREATED)
def create_paciente(data: schemas.PacienteCreate, db: Session = Depends(get_db)):
    """Crear un nuevo paciente"""
    if db.query(models.Paciente).filter(models.Paciente.documento == data.documento).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Documento ya registrado"
        )
    nuevo = models.Paciente(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/{id}", response_model=schemas.PacienteOut)
def update_paciente(id: int, data: schemas.PacienteUpdate, db: Session = Depends(get_db)):
    """Actualizar un paciente existente"""
    paciente = db.query(models.Paciente).filter(models.Paciente.id_paciente == id).first()
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado"
        )
    
    update_data = data.model_dump(exclude_unset=True)
    
    # Verificar que el documento no esté en uso por otro paciente
    if "documento" in update_data:
        otro = db.query(models.Paciente).filter(
            models.Paciente.documento == update_data["documento"],
            models.Paciente.id_paciente != id
        ).first()
        if otro:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Documento ya registrado por otro paciente"
            )
    
    for key, value in update_data.items():
        setattr(paciente, key, value)
    
    db.commit()
    db.refresh(paciente)
    return paciente


@router.delete("/{id}")
def delete_paciente(id: int, db: Session = Depends(get_db)):
    """Eliminar un paciente"""
    paciente = db.query(models.Paciente).filter(models.Paciente.id_paciente == id).first()
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado"
        )
    db.delete(paciente)
    db.commit()
    return {"mensaje": "Paciente eliminado correctamente", "id_paciente": id}
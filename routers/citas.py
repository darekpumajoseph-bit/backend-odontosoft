# routers/citas.py - CRUD completo de citas con endpoints de tratamientos

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from typing import List

import models
import schemas
from database import get_db

router = APIRouter(prefix="/citas", tags=["Citas"])


# ============================================================
# OBTENER TODAS LAS CITAS
# ============================================================
@router.get("/", response_model=List[schemas.CitaOut])
def get_citas(db: Session = Depends(get_db)):
    citas = (
        db.query(models.Cita)
        .options(selectinload(models.Cita.tratamientos))
        .all()
    )
    return citas


# ============================================================
# OBTENER UNA CITA
# ============================================================
@router.get("/{id}", response_model=schemas.CitaOut)
def get_cita(id: int, db: Session = Depends(get_db)):
    cita = (
        db.query(models.Cita)
        .options(selectinload(models.Cita.tratamientos))
        .filter(models.Cita.id_cita == id)
        .first()
    )

    if not cita:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada"
        )
    return cita


# ============================================================
# CITAS POR PACIENTE
# ============================================================
@router.get("/paciente/{paciente_id}", response_model=List[schemas.CitaOut])
def get_citas_por_paciente(paciente_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Cita)
        .options(selectinload(models.Cita.tratamientos))
        .filter(models.Cita.id_paciente == paciente_id)
        .all()
    )


# ============================================================
# CITAS POR ODONTÓLOGO
# ============================================================
@router.get("/odontologo/{odontologo_id}", response_model=List[schemas.CitaOut])
def get_citas_por_odontologo(odontologo_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Cita)
        .options(selectinload(models.Cita.tratamientos))
        .filter(models.Cita.id_odontologo == odontologo_id)
        .all()
    )


# ============================================================
# CITAS POR CONSULTORIO
# ============================================================
@router.get("/consultorio/{consultorio_id}", response_model=List[schemas.CitaOut])
def get_citas_por_consultorio(consultorio_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Cita)
        .options(selectinload(models.Cita.tratamientos))
        .filter(models.Cita.id_consultorio == consultorio_id)
        .all()
    )


# ============================================================
# CREAR CITA
# ============================================================
@router.post("/", response_model=schemas.CitaOut, status_code=status.HTTP_201_CREATED)
def create_cita(data: schemas.CitaCreate, db: Session = Depends(get_db)):
    # Validar paciente
    paciente = db.query(models.Paciente).filter(models.Paciente.id_paciente == data.id_paciente).first()
    if not paciente:
        raise HTTPException(status_code=400, detail="El paciente no existe")

    # Validar odontólogo
    odontologo = db.query(models.Odontologo).filter(models.Odontologo.id_odontologo == data.id_odontologo).first()
    if not odontologo:
        raise HTTPException(status_code=400, detail="El odontólogo no existe")

    # Validar consultorio
    consultorio = db.query(models.Consultorio).filter(models.Consultorio.id_consultorio == data.id_consultorio).first()
    if not consultorio:
        raise HTTPException(status_code=400, detail="El consultorio no existe")

    nueva = models.Cita(**data.model_dump())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    return (
        db.query(models.Cita)
        .options(selectinload(models.Cita.tratamientos))
        .filter(models.Cita.id_cita == nueva.id_cita)
        .first()
    )


# ============================================================
# ACTUALIZAR CITA
# ============================================================
@router.put("/{id}", response_model=schemas.CitaOut)
def update_cita(id: int, data: schemas.CitaUpdate, db: Session = Depends(get_db)):
    cita = (
        db.query(models.Cita)
        .options(selectinload(models.Cita.tratamientos))
        .filter(models.Cita.id_cita == id)
        .first()
    )

    if not cita:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada"
        )

    update_data = data.model_dump(exclude_unset=True)

    # Validar paciente
    if "id_paciente" in update_data:
        paciente = db.query(models.Paciente).filter(models.Paciente.id_paciente == update_data["id_paciente"]).first()
        if not paciente:
            raise HTTPException(status_code=400, detail="El paciente no existe")

    # Validar odontólogo
    if "id_odontologo" in update_data:
        odontologo = db.query(models.Odontologo).filter(models.Odontologo.id_odontologo == update_data["id_odontologo"]).first()
        if not odontologo:
            raise HTTPException(status_code=400, detail="El odontólogo no existe")

    # Validar consultorio
    if "id_consultorio" in update_data:
        consultorio = db.query(models.Consultorio).filter(models.Consultorio.id_consultorio == update_data["id_consultorio"]).first()
        if not consultorio:
            raise HTTPException(status_code=400, detail="El consultorio no existe")

    # Actualizar campos
    for key, value in update_data.items():
        setattr(cita, key, value)

    db.commit()

    return (
        db.query(models.Cita)
        .options(selectinload(models.Cita.tratamientos))
        .filter(models.Cita.id_cita == id)
        .first()
    )


# ============================================================
# ELIMINAR CITA
# ============================================================
@router.delete("/{id}")
def delete_cita(id: int, db: Session = Depends(get_db)):
    cita = db.query(models.Cita).filter(models.Cita.id_cita == id).first()
    if not cita:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada"
        )

    db.delete(cita)
    db.commit()
    return {"mensaje": "Cita eliminada correctamente", "id_cita": id}


# ============================================================
# OBTENER TRATAMIENTOS DE UNA CITA
# ============================================================
@router.get("/{cita_id}/tratamientos", response_model=List[schemas.TratamientoOut])
def get_tratamientos_de_cita(cita_id: int, db: Session = Depends(get_db)):
    cita = db.query(models.Cita).filter(models.Cita.id_cita == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    return cita.tratamientos


# ============================================================
# ASOCIAR TRATAMIENTO A UNA CITA (POST)
# ============================================================
@router.post("/{cita_id}/tratamientos/{tratamiento_id}")
def asociar_tratamiento(cita_id: int, tratamiento_id: int, db: Session = Depends(get_db)):
    cita = db.query(models.Cita).filter(models.Cita.id_cita == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    tratamiento = db.query(models.Tratamiento).filter(models.Tratamiento.id_tratamiento == tratamiento_id).first()
    if not tratamiento:
        raise HTTPException(status_code=404, detail="Tratamiento no encontrado")

    if tratamiento in cita.tratamientos:
        raise HTTPException(status_code=409, detail="El tratamiento ya está asociado a esta cita")

    cita.tratamientos.append(tratamiento)
    db.commit()
    db.refresh(cita)
    return {"mensaje": "Tratamiento asociado correctamente", "id_cita": cita_id, "id_tratamiento": tratamiento_id}


# ============================================================
# ACTUALIZAR TRATAMIENTO DE UNA CITA (PUT - Reemplaza el actual)
# ============================================================
@router.put("/{cita_id}/tratamientos/{tratamiento_id}")
def actualizar_tratamiento(cita_id: int, tratamiento_id: int, db: Session = Depends(get_db)):
    cita = db.query(models.Cita).filter(models.Cita.id_cita == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    tratamiento = db.query(models.Tratamiento).filter(models.Tratamiento.id_tratamiento == tratamiento_id).first()
    if not tratamiento:
        raise HTTPException(status_code=404, detail="Tratamiento no encontrado")

    # Limpiar tratamientos actuales y asignar el nuevo
    cita.tratamientos.clear()
    cita.tratamientos.append(tratamiento)
    db.commit()
    db.refresh(cita)
    return {"mensaje": "Tratamiento actualizado correctamente", "id_cita": cita_id, "id_tratamiento": tratamiento_id}


# ============================================================
# ELIMINAR TRATAMIENTO DE UNA CITA (DELETE)
# ============================================================
@router.delete("/{cita_id}/tratamientos/{tratamiento_id}")
def eliminar_tratamiento(cita_id: int, tratamiento_id: int, db: Session = Depends(get_db)):
    cita = db.query(models.Cita).filter(models.Cita.id_cita == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    tratamiento = db.query(models.Tratamiento).filter(models.Tratamiento.id_tratamiento == tratamiento_id).first()
    if not tratamiento:
        raise HTTPException(status_code=404, detail="Tratamiento no encontrado")

    if tratamiento in cita.tratamientos:
        cita.tratamientos.remove(tratamiento)
        db.commit()
        return {"mensaje": "Tratamiento eliminado de la cita correctamente"}
    
    raise HTTPException(status_code=404, detail="El tratamiento no está asociado a esta cita")
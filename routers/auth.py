# routers/auth.py - Autenticación y Registro

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import models
import schemas
from database import get_db
from utils import hash_password, verificar_password, validar_correo, generar_documento_unico

router = APIRouter(prefix="/auth", tags=["Autenticación"])


# ── LOGIN ─────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=schemas.LoginResponse)
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Autenticar usuario con correo y contraseña."""
    
    usuario = db.query(models.Usuario).filter(
        models.Usuario.correo == data.correo
    ).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Correo no registrado"
        )
    
    if not verificar_password(data.contrasena, usuario.contrasena):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña incorrecta"
        )
    
    if usuario.estado != "Activo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacte al administrador."
        )
    
    return schemas.LoginResponse(
        id_usuario=usuario.id_usuario,
        correo=usuario.correo,
        rol=usuario.rol,
        estado=usuario.estado,
        mensaje="Login exitoso"
    )


# ── REGISTRO COMPLETO (Usuario + Paciente) ──────────────────────────────────

@router.post("/registro", response_model=schemas.RegistroResponse, status_code=status.HTTP_201_CREATED)
def registro_usuario(data: schemas.RegistroRequest, db: Session = Depends(get_db)):
    """
    Registro completo desde el frontend.
    Crea un usuario con rol 'Paciente' y un paciente asociado.
    """
    # Validar correo
    if not validar_correo(data.correo):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico no tiene un formato válido"
        )
    
    # Verificar que el correo no esté registrado
    existing_user = db.query(models.Usuario).filter(
        models.Usuario.correo == data.correo
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado"
        )
    
    # Validar contraseña
    if len(data.contrasena) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe tener al menos 6 caracteres"
        )
    
    try:
        # 1. Crear el usuario
        nuevo_usuario = models.Usuario(
            correo=data.correo,
            contrasena=hash_password(data.contrasena),
            rol="Paciente",
            estado="Activo"
        )
        db.add(nuevo_usuario)
        db.flush()
        
        # 2. Generar documento único para el paciente
        documento = generar_documento_unico(db)
        
        # 3. Crear el paciente asociado
        nuevo_paciente = models.Paciente(
            nombre=data.nombre,
            apellido=data.apellido,
            documento=documento,
            telefono=data.telefono,
            correo=data.correo
        )
        db.add(nuevo_paciente)
        db.flush()
        
        # 4. Crear la relación usuario-paciente
        stmt = models.usuario_paciente.insert().values(
            id_usuario=nuevo_usuario.id_usuario,
            id_paciente=nuevo_paciente.id_paciente
        )
        db.execute(stmt)
        
        db.commit()
        
        return schemas.RegistroResponse(
            mensaje="Usuario y paciente registrados exitosamente",
            id_usuario=nuevo_usuario.id_usuario,
            id_paciente=nuevo_paciente.id_paciente,
            correo=nuevo_usuario.correo,
            rol=nuevo_usuario.rol
        )
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al registrar: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )
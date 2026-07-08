# routers/usuarios.py - CRUD completo de usuarios (CON REGISTRO Y CONTRASEÑA PLANO)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import get_db
from utils import hash_password, validar_correo, generar_documento_unico

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


# ── GET: Obtener todos los usuarios ──────────────────────────────────────────

@router.get("/", response_model=List[schemas.UsuarioOut])
def get_usuarios(db: Session = Depends(get_db)):
    """Obtener todos los usuarios"""
    try:
        usuarios = db.query(models.Usuario).all()
        return usuarios
    except Exception as e:
        print(f"❌ Error en get_usuarios: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener usuarios: {str(e)}"
        )


# ── GET: Obtener usuario por ID (CON CONTRASEÑA EN TEXTO PLANO) ─────────────

@router.get("/{id}", response_model=schemas.UsuarioOut)
def get_usuario(id: int, db: Session = Depends(get_db)):
    """Obtener un usuario por ID con contraseña en texto plano para edición"""
    usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Obtener la contraseña en texto plano desde el paciente (si existe)
    contrasena_plano = None
    
    # Buscar si el usuario tiene un paciente asociado
    if usuario.rol == "Paciente":
        # Buscar el paciente relacionado
        paciente = db.query(models.Paciente).join(
            models.usuario_paciente,
            models.usuario_paciente.c.id_paciente == models.Paciente.id_paciente
        ).filter(
            models.usuario_paciente.c.id_usuario == id
        ).first()
        
        if paciente and paciente.contrasena_plano:
            contrasena_plano = paciente.contrasena_plano
    
    # Crear un diccionario con los datos del usuario
    usuario_dict = {
        "id_usuario": usuario.id_usuario,
        "correo": usuario.correo,
        "contrasena": contrasena_plano if contrasena_plano else usuario.contrasena,
        "contrasena_plano": contrasena_plano,  # 🔥 Enviar al frontend
        "rol": usuario.rol,
        "estado": usuario.estado,
        "fecha_registro": usuario.fecha_registro,
        "ultimo_acceso": usuario.ultimo_acceso
    }
    
    return usuario_dict


# ── GET: Obtener usuario por correo ──────────────────────────────────────────

@router.get("/correo/{correo}", response_model=schemas.UsuarioOut)
def get_usuario_by_correo(correo: str, db: Session = Depends(get_db)):
    """Obtener un usuario por correo electrónico"""
    usuario = db.query(models.Usuario).filter(models.Usuario.correo == correo).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return usuario


# ── POST: Crear un nuevo usuario ─────────────────────────────────────────────

@router.post("/", response_model=schemas.UsuarioOut, status_code=status.HTTP_201_CREATED)
def create_usuario(data: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    """
    Crear un nuevo usuario (solo usuario, sin paciente asociado)
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
    
    # Validar rol
    roles_validos = ["Administrador", "Odontologo", "Paciente"]
    if data.rol not in roles_validos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rol inválido. Debe ser uno de: {', '.join(roles_validos)}"
        )
    
    # Crear usuario
    nuevo_usuario = models.Usuario(
        correo=data.correo,
        contrasena=hash_password(data.contrasena),
        rol=data.rol,
        estado=data.estado if hasattr(data, 'estado') else "Activo"
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


# ── PUT: Actualizar un usuario existente ─────────────────────────────────────

@router.put("/{id}", response_model=schemas.UsuarioOut)
def update_usuario(id: int, data: schemas.UsuarioUpdate, db: Session = Depends(get_db)):
    """
    Actualizar un usuario existente (todos los campos son opcionales)
    """
    # Buscar usuario
    usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Obtener solo los campos que se enviaron
    update_data = data.model_dump(exclude_unset=True)
    
    # Validar correo si se está actualizando
    if "correo" in update_data:
        if not validar_correo(update_data["correo"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico no tiene un formato válido"
            )
        
        # Verificar que el correo no esté en uso por otro usuario
        otro = db.query(models.Usuario).filter(
            models.Usuario.correo == update_data["correo"],
            models.Usuario.id_usuario != id
        ).first()
        if otro:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está registrado por otro usuario"
            )
    
    # Validar contraseña si se está actualizando
    if "contrasena" in update_data:
        if len(update_data["contrasena"]) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña debe tener al menos 6 caracteres"
            )
        
        #  ACTUALIZAR CONTRASEÑA EN TEXTO PLANO EN EL PACIENTE
        if usuario.rol == "Paciente":
            paciente = db.query(models.Paciente).join(
                models.usuario_paciente,
                models.usuario_paciente.c.id_paciente == models.Paciente.id_paciente
            ).filter(
                models.usuario_paciente.c.id_usuario == id
            ).first()
            
            if paciente:
                paciente.contrasena_plano = update_data["contrasena"]
                db.flush()
        
        update_data["contrasena"] = hash_password(update_data["contrasena"])
    
    # Validar rol si se está actualizando
    if "rol" in update_data:
        roles_validos = ["Administrador", "Odontologo", "Paciente"]
        if update_data["rol"] not in roles_validos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Rol inválido. Debe ser uno de: {', '.join(roles_validos)}"
            )
    
    # Validar estado si se está actualizando
    if "estado" in update_data:
        if update_data["estado"] not in ["Activo", "Inactivo"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Estado debe ser 'Activo' o 'Inactivo'"
            )
    
    # Aplicar los cambios
    for key, value in update_data.items():
        setattr(usuario, key, value)
    
    db.commit()
    db.refresh(usuario)
    return usuario

# ── DELETE: Eliminar un usuario ──────────────────────────────────────────────

@router.delete("/{id}")
def delete_usuario(id: int, db: Session = Depends(get_db)):
    """
    Eliminar un usuario y toda la información relacionada:
    - Usuario
    - Relación usuario_paciente
    - Paciente asociado
    - Citas del paciente
    - Historias clínicas
    - Servicios relacionados
    """

    # Buscar usuario
    usuario = (
        db.query(models.Usuario)
        .filter(models.Usuario.id_usuario == id)
        .first()
    )

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    try:

        # Guardar pacientes relacionados antes de eliminar usuario
        pacientes = list(usuario.pacientes)


        # Eliminar pacientes asociados
        # Al eliminar paciente se eliminan:
        # - citas
        # - historias
        # - servicios
        for paciente in pacientes:
            db.delete(paciente)


        # Eliminar usuario
        db.delete(usuario)


        # Guardar cambios
        db.commit()


        return {
            "mensaje": "Usuario y toda la información relacionada eliminada correctamente",
            "id_usuario": id
        }


    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar usuario: {str(e)}"
        )
# ── POST: Registro completo (usuario + paciente) ────────────────────────────
@router.post("/registro", response_model=schemas.RegistroResponse, status_code=status.HTTP_201_CREATED)
def registro_usuario(data: schemas.RegistroRequest, db: Session = Depends(get_db)):

    # Validar correo
    if not validar_correo(data.correo):
        raise HTTPException(
            status_code=400,
            detail="Correo inválido."
        )

    existe = db.query(models.Usuario).filter(
        models.Usuario.correo == data.correo
    ).first()

    if existe:
        raise HTTPException(
            status_code=400,
            detail="El correo ya está registrado."
        )

    try:

        # ==========================================
        # CREAR USUARIO
        # ==========================================

        usuario = models.Usuario(
            correo=data.correo,
            contrasena=hash_password(data.contrasena),
            rol=data.rol,
            estado=data.estado
        )

        db.add(usuario)
        db.flush()

        id_paciente = None
        id_odontologo = None

        # ==========================================
        # PACIENTE
        # ==========================================

        if data.rol == "Paciente":

            documento = data.documento

            if not documento:
                documento = generar_documento_unico(db)

            paciente = models.Paciente(

                nombre=data.nombre,
                apellido=data.apellido,
                documento=documento,

                fecha_nacimiento=data.fecha_nacimiento,
                genero=data.genero,
                direccion=data.direccion,

                telefono=data.telefono,
                correo=data.correo,

                eps=data.eps,
                alergias=data.alergias,

                contrasena_plano=data.contrasena

            )

            db.add(paciente)
            db.flush()

            id_paciente = paciente.id_paciente

            from models import usuario_paciente

            db.execute(

                usuario_paciente.insert().values(
                    id_usuario=usuario.id_usuario,
                    id_paciente=id_paciente
                )

            )

        # ==========================================
        # ODONTOLOGO
        # ==========================================

        elif data.rol == "Odontologo":

            documento = data.documento

            if not documento:
                documento = generar_documento_unico(db)

            odontologo = models.Odontologo(

                nombre=data.nombre,
                apellido=data.apellido,
                documento=documento,

                telefono=data.telefono,
                correo=data.correo,

                especialidad=data.especialidad,

                registro_profesional=None,
                horario=None,

                id_consultorio=1

            )

            db.add(odontologo)
            db.flush()

            id_odontologo = odontologo.id_odontologo

        # ==========================================
        # ADMINISTRADOR
        # ==========================================

        elif data.rol == "Administrador":

            pass

        db.commit()

        return schemas.RegistroResponse(

            mensaje="Usuario registrado correctamente",

            id_usuario=usuario.id_usuario,

            id_paciente=id_paciente,
            id_odontologo=id_odontologo,

            correo=usuario.correo,
            rol=usuario.rol

        )

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# ── POST: Cambiar contraseña de usuario ─────────────────────────────────────

@router.post("/{id}/cambiar-contrasena", status_code=status.HTTP_200_OK)
def cambiar_contrasena(
    id: int, 
    data: dict, 
    db: Session = Depends(get_db)
):
    """
    Cambiar la contraseña de un usuario
    """
    usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    nueva_contrasena = data.get("contrasena")
    if not nueva_contrasena:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña es requerida"
        )
    
    if len(nueva_contrasena) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe tener al menos 6 caracteres"
        )
    
    usuario.contrasena = hash_password(nueva_contrasena)
    
    # 🔥 TAMBIÉN ACTUALIZAR CONTRASEÑA EN TEXTO PLANO EN EL PACIENTE
    if usuario.rol == "Paciente":
        paciente = db.query(models.Paciente).join(
            models.usuario_paciente,
            models.usuario_paciente.c.id_paciente == models.Paciente.id_paciente
        ).filter(
            models.usuario_paciente.c.id_usuario == id
        ).first()
        
        if paciente:
            paciente.contrasena_plano = nueva_contrasena
    
    db.commit()
    
    return {
        "mensaje": "Contraseña actualizada correctamente",
        "id_usuario": id
    }
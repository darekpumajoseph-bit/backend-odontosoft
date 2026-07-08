# schemas.py - Versión COMPLETA Y CORREGIDA (Eliminado id_cita de Tratamiento)

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import date, time, datetime
from decimal import Decimal


# ── USUARIO ───────────────────────────────────────────────────────────────────

class UsuarioBase(BaseModel):
    correo: EmailStr
    rol: str = "Paciente"
    estado: str = "Activo"

class UsuarioCreate(UsuarioBase):
    contrasena: str = Field(..., min_length=6, description="Mínimo 6 caracteres")

class UsuarioUpdate(BaseModel):
    """Schema para actualizar usuario (todos los campos opcionales)"""
    correo: Optional[EmailStr] = None
    contrasena: Optional[str] = Field(None, min_length=6)
    rol: Optional[str] = None
    estado: Optional[str] = None

class UsuarioOut(UsuarioBase):
    id_usuario: int
    fecha_registro: Optional[datetime] = None
    ultimo_acceso: Optional[datetime] = None
    contrasena_plano: Optional[str] = None  
    model_config = ConfigDict(from_attributes=True)


# ── PACIENTE ──────────────────────────────────────────────────────────────────

class PacienteBase(BaseModel):
    nombre: str = Field(..., min_length=1)
    apellido: str = Field(..., min_length=1)
    documento: str = Field(..., min_length=1)
    fecha_nacimiento: Optional[date] = None
    genero: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None
    eps: Optional[str] = None
    alergias: Optional[str] = None

class PacienteCreate(PacienteBase):
    pass

class PacienteUpdate(BaseModel):
    """Schema para actualizar paciente (todos los campos opcionales)"""
    nombre: Optional[str] = Field(None, min_length=1)
    apellido: Optional[str] = Field(None, min_length=1)
    documento: Optional[str] = Field(None, min_length=1)
    fecha_nacimiento: Optional[date] = None
    genero: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None
    eps: Optional[str] = None
    alergias: Optional[str] = None
    contrasena_plano: Optional[str] = Field(None, min_length=6)  # 🔥 Para actualizar contraseña

class PacienteOut(PacienteBase):
    id_paciente: int
    contrasena_plano: Optional[str] = None  # 🔥 Para enviar contraseña en texto plano
    model_config = ConfigDict(from_attributes=True)


# ── LOGIN ────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    """Schema para login de usuario"""
    correo: EmailStr
    contrasena: str

class LoginResponse(BaseModel):
    """Schema para respuesta de login"""
    id_usuario: int
    correo: str
    rol: str
    estado: str
    mensaje: str


# ── REGISTRO COMPLETO () ──────────────────────────────────

class RegistroRequest(BaseModel):

    correo: EmailStr
    contrasena: str = Field(..., min_length=6)

    rol: str = "Paciente"
    estado: str = "Activo"

    # Datos comunes
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    documento: Optional[str] = None
    telefono: Optional[str] = None

    # Paciente
    fecha_nacimiento: Optional[date] = None
    genero: Optional[str] = None
    direccion: Optional[str] = None
    eps: Optional[str] = None
    alergias: Optional[str] = None

    # Odontólogo
    especialidad: Optional[str] = None

class RegistroResponse(BaseModel):

    mensaje: str
    id_usuario: int

    id_paciente: Optional[int] = None
    id_odontologo: Optional[int] = None

    correo: str
    rol: str

# ── CONSULTORIO ──────────────────────────────────────────────────────────────

class ConsultorioBase(BaseModel):
    nombre: str = Field(..., min_length=1)
    ubicacion: Optional[str] = None
    numero_sala: Optional[str] = None

class ConsultorioCreate(ConsultorioBase):
    pass

class ConsultorioUpdate(BaseModel):
    """Schema para actualizar consultorio (todos los campos opcionales)"""
    nombre: Optional[str] = Field(None, min_length=1)
    ubicacion: Optional[str] = None
    numero_sala: Optional[str] = None

class ConsultorioOut(ConsultorioBase):
    id_consultorio: int
    model_config = ConfigDict(from_attributes=True)


# ── ODONTOLOGO ───────────────────────────────────────────────────────────────

class OdontologoBase(BaseModel):
    nombre: str
    apellido: str
    documento: str
    telefono: Optional[str]
    correo: Optional[str]
    especialidad: Optional[str]
    id_consultorio: int

class OdontologoCreate(OdontologoBase):
    pass

class OdontologoUpdate(BaseModel):
    """Schema para actualizar odontólogo (todos los campos opcionales)"""
    nombre: Optional[str] = Field(None, min_length=1)
    apellido: Optional[str] = Field(None, min_length=1)
    documento: Optional[str] = Field(None, min_length=1)
    telefono: Optional[str] = None
    correo: Optional[str] = None
    especialidad: Optional[str] = None
    registro_profesional: Optional[str] = None
    horario: Optional[str] = None
    id_consultorio: Optional[int] = None

class OdontologoOut(OdontologoBase):
    id_odontologo: int
    model_config = ConfigDict(from_attributes=True)


# ── HISTORIA CLINICA ─────────────────────────────────────────────────────────

class HistoriaClinicaBase(BaseModel):
    fecha_apertura: date
    antecedentes: Optional[str] = None
    diagnostico_general: Optional[str] = None
    observaciones: Optional[str] = None
    id_paciente: int

class HistoriaClinicaCreate(HistoriaClinicaBase):
    pass

class HistoriaClinicaUpdate(BaseModel):
    """Schema para actualizar historia clínica (todos los campos opcionales)"""
    fecha_apertura: Optional[date] = None
    antecedentes: Optional[str] = None
    diagnostico_general: Optional[str] = None
    observaciones: Optional[str] = None
    id_paciente: Optional[int] = None

class HistoriaClinicaOut(HistoriaClinicaBase):
    id_historia: int
    model_config = ConfigDict(from_attributes=True)

# ── TRATAMIENTO ──────────────────────────────────────────────────────────────
class TratamientoBase(BaseModel):
    nombre: str = Field(..., min_length=1)
    descripcion: Optional[str] = None
    costo: Optional[Decimal] = Field(None, gt=0)
    duracion_estimada: Optional[str] = None


class TratamientoCreate(TratamientoBase):
    pass


class TratamientoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1)
    descripcion: Optional[str] = None
    costo: Optional[Decimal] = Field(None, gt=0)
    duracion_estimada: Optional[str] = None


class TratamientoOut(TratamientoBase):
    id_tratamiento: int
    model_config = ConfigDict(from_attributes=True)

# ── CITA ─────────────────────────────────────────────────────────────────────

class CitaBase(BaseModel):
    fecha: date
    hora: time
    estado: Optional[str] = "Pendiente"
    motivo_consulta: Optional[str] = None
    observaciones: Optional[str] = None
    id_paciente: int
    id_odontologo: int
    id_consultorio: int


class CitaCreate(CitaBase):
    pass


class CitaUpdate(BaseModel):
    fecha: Optional[date] = None
    hora: Optional[time] = None
    estado: Optional[str] = None
    motivo_consulta: Optional[str] = None
    observaciones: Optional[str] = None
    id_paciente: Optional[int] = None
    id_odontologo: Optional[int] = None
    id_consultorio: Optional[int] = None

class CitaOut(CitaBase):
    id_cita: int

    tratamientos: list["TratamientoOut"] = []

    model_config = ConfigDict(from_attributes=True)

# ── RECORDATORIO ─────────────────────────────────────────────────────────────

class RecordatorioBase(BaseModel):
    tipo: Optional[str] = None
    fecha_envio: Optional[datetime] = None
    estado: Optional[str] = "Pendiente"
    id_cita: int

class RecordatorioCreate(RecordatorioBase):
    pass

class RecordatorioUpdate(BaseModel):
    """Schema para actualizar recordatorio (todos los campos opcionales)"""
    tipo: Optional[str] = None
    fecha_envio: Optional[datetime] = None
    estado: Optional[str] = None
    id_cita: Optional[int] = None

class RecordatorioOut(RecordatorioBase):
    id_recordatorio: int
    model_config = ConfigDict(from_attributes=True)


# ── PAGO ─────────────────────────────────────────────────────────────────────

class PagoBase(BaseModel):
    fecha_pago: date
    monto: Decimal = Field(..., gt=0)
    metodo_pago: Optional[str] = None
    estado_pago: Optional[str] = "Pendiente"
    referencia: Optional[str] = None
    id_cita: int

class PagoCreate(PagoBase):
    pass

class PagoUpdate(BaseModel):
    """Schema para actualizar pago (todos los campos opcionales)"""
    fecha_pago: Optional[date] = None
    monto: Optional[Decimal] = Field(None, gt=0)
    metodo_pago: Optional[str] = None
    estado_pago: Optional[str] = None
    referencia: Optional[str] = None
    id_cita: Optional[int] = None

class PagoOut(PagoBase):
    id_pago: int
    model_config = ConfigDict(from_attributes=True)


# ── FACTURA ──────────────────────────────────────────────────────────────────

class FacturaBase(BaseModel):
    fecha_emision: date
    subtotal: Optional[Decimal] = Field(None, ge=0)
    impuesto: Optional[Decimal] = Field(None, ge=0)
    total: Optional[Decimal] = Field(None, ge=0)
    id_pago: int

class FacturaCreate(FacturaBase):
    pass

class FacturaUpdate(BaseModel):
    """Schema para actualizar factura (todos los campos opcionales)"""
    fecha_emision: Optional[date] = None
    subtotal: Optional[Decimal] = Field(None, ge=0)
    impuesto: Optional[Decimal] = Field(None, ge=0)
    total: Optional[Decimal] = Field(None, ge=0)
    id_pago: Optional[int] = None

class FacturaOut(FacturaBase):
    id_factura: int
    model_config = ConfigDict(from_attributes=True)


# ── ROL ──────────────────────────────────────────────────────────────────────

class RolBase(BaseModel):
    nombre: str = Field(..., min_length=1)
    descripcion: Optional[str] = None
    permisos: Optional[str] = "READ ONLY"

class RolCreate(RolBase):
    pass

class RolUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1)
    descripcion: Optional[str] = None
    permisos: Optional[str] = None

class RolOut(RolBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ── PROVEEDOR ─────────────────────────────────────────────────────────────────

class ProveedorBase(BaseModel):
    empresa: str = Field(..., min_length=1)
    contacto_asesor: Optional[str] = None
    telefono: Optional[str] = None
    suministro: Optional[str] = None
    estado_convenio: Optional[str] = "Vigente"

class ProveedorCreate(ProveedorBase):
    pass

class ProveedorUpdate(BaseModel):
    empresa: Optional[str] = Field(None, min_length=1)
    contacto_asesor: Optional[str] = None
    telefono: Optional[str] = None
    suministro: Optional[str] = None
    estado_convenio: Optional[str] = None

class ProveedorOut(ProveedorBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ── SERVICIO ──────────────────────────────────────────────────────────────────

class ServicioBase(BaseModel):
    paciente_id: int
    tratamiento_nombre: str = Field(..., min_length=1)
    odontologo_nombre: Optional[str] = None
    proxima_cita: Optional[str] = None
    estado_cuenta: Optional[str] = "Pendiente"

class ServicioCreate(ServicioBase):
    pass

class ServicioUpdate(BaseModel):
    paciente_id: Optional[int] = None
    tratamiento_nombre: Optional[str] = Field(None, min_length=1)
    odontologo_nombre: Optional[str] = None
    proxima_cita: Optional[str] = None
    estado_cuenta: Optional[str] = None

class ServicioOut(ServicioBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Resolver referencias adelantadas
CitaOut.model_rebuild()
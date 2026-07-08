# models.py - Versión COMPLETA Y CORREGIDA (Relación Muchos a Muchos Cita-Tratamiento)

from sqlalchemy import Column, Integer, String, ForeignKey, Text, Date, Time, Numeric, TIMESTAMP, Table, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

# ── TABLAS DE RELACIÓN MANY-TO-MANY USUARIO_PACIENTE ──────────────────────────────────────────
usuario_paciente = Table(
    "usuario_paciente",
    Base.metadata,
    Column("id_usuario", Integer, ForeignKey("usuario.id_usuario", ondelete="CASCADE"), primary_key=True),
    Column("id_paciente", Integer, ForeignKey("paciente.id_paciente", ondelete="CASCADE"), primary_key=True),
    extend_existing=True
)

usuario_tratamiento = Table(
    "usuario_tratamiento",
    Base.metadata,
    Column("id_usuario", Integer, ForeignKey("usuario.id_usuario", ondelete="CASCADE"), primary_key=True),
    Column("id_tratamiento", Integer, ForeignKey("tratamiento.id_tratamiento", ondelete="CASCADE"), primary_key=True),
    extend_existing=True
)

#  NUEVA TABLA PIVOTE PARA RELACIONAR CITAS Y TRATAMIENTOS (Muchos a Muchos)
cita_tratamiento = Table(
    "cita_tratamiento",
    Base.metadata,
    Column("id_cita", Integer, ForeignKey("cita.id_cita", ondelete="CASCADE"), primary_key=True),
    Column("id_tratamiento", Integer, ForeignKey("tratamiento.id_tratamiento", ondelete="CASCADE"), primary_key=True),
    extend_existing=True
)
# ── TABLA: PACIENTE ────────────────────────────────────────────────────────────

class Paciente(Base):
    __tablename__ = "paciente"
    __table_args__ = {'extend_existing': True}

    id_paciente = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    documento = Column(String(20), unique=True, nullable=False)
    fecha_nacimiento = Column(Date, nullable=True)
    genero = Column(String(20), nullable=True)
    direccion = Column(String(200), nullable=True)
    telefono = Column(String(20), nullable=True)
    correo = Column(String(100), nullable=True)
    eps = Column(String(100), nullable=True)
    alergias = Column(Text, nullable=True)

    # CAMPO - CONTRASEÑA EN TEXTO PLANO
    contrasena_plano = Column(String(100), nullable=True)


    # Relación con usuarios (Many-to-Many)
    usuarios = relationship(
        "Usuario",
        secondary=usuario_paciente,
        back_populates="pacientes"
    )


    # Historia clínica del paciente
    historias = relationship(
        "HistoriaClinica",
        back_populates="paciente",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


    # Citas del paciente
    # Si se elimina el paciente, se eliminan sus citas
    citas = relationship(
        "Cita",
        back_populates="paciente",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


    # Servicios asociados al paciente
    servicios = relationship(
        "Servicio",
        back_populates="paciente",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

# ── TABLA: USUARIO ────────────────────────────────────────────────────────────

class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = {'extend_existing': True}

    id_usuario = Column(Integer, primary_key=True, index=True)
    correo = Column(String(100), nullable=False, unique=True)
    contrasena = Column(String(255), nullable=False)
    rol = Column(String(30), nullable=False, default="Paciente")
    estado = Column(String(20), nullable=False, default="Activo")
    fecha_registro = Column(DateTime, default=datetime.now)
    ultimo_acceso = Column(DateTime, nullable=True)

    pacientes = relationship("Paciente",secondary=usuario_paciente,back_populates="usuarios",cascade="all, delete")
    tratamientos = relationship("Tratamiento", secondary=usuario_tratamiento, back_populates="usuarios")





# ── TABLA: CONSULTORIO ────────────────────────────────────────────────────────

class Consultorio(Base):
    __tablename__ = "consultorio"
    __table_args__ = {'extend_existing': True}

    id_consultorio = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    ubicacion = Column(String(150), nullable=True)
    numero_sala = Column(String(20), nullable=True)

    odontologos = relationship("Odontologo", back_populates="consultorio", cascade="all, delete-orphan")
    citas = relationship("Cita", back_populates="consultorio", cascade="all, delete-orphan")


# ── TABLA: ODONTOLOGO ─────────────────────────────────────────────────────────

class Odontologo(Base):
    __tablename__ = "odontologo"

    id_odontologo = Column(Integer, primary_key=True)

    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    documento = Column(String(20), unique=True, nullable=False)
    telefono = Column(String(20))
    correo = Column(String(100))
    especialidad = Column(String(100))

    id_consultorio = Column(
        Integer,
        ForeignKey("consultorio.id_consultorio", ondelete="CASCADE"),
        nullable=False
    )

    consultorio = relationship("Consultorio", back_populates="odontologos")
    citas = relationship("Cita", back_populates="odontologo")


# ── TABLA: HISTORIA CLINICA ──────────────────────────────────────────────────

class HistoriaClinica(Base):
    __tablename__ = "historia_clinica"
    __table_args__ = {'extend_existing': True}

    id_historia = Column(Integer, primary_key=True, index=True)
    fecha_apertura = Column(Date, nullable=False)
    antecedentes = Column(Text, nullable=True)
    diagnostico_general = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)
    id_paciente = Column(Integer, ForeignKey("paciente.id_paciente", ondelete="CASCADE"), nullable=False)

    paciente = relationship("Paciente", back_populates="historias")


# ── TABLA: CITA ──────────────────────────────────────────────────────────────

class Cita(Base):
    __tablename__ = "cita"
    __table_args__ = {'extend_existing': True}

    id_cita = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    estado = Column(String(30), nullable=True, default="Pendiente")
    motivo_consulta = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)
    id_paciente = Column(Integer, ForeignKey("paciente.id_paciente", ondelete="CASCADE"), nullable=False)
    id_odontologo = Column(Integer, ForeignKey("odontologo.id_odontologo", ondelete="CASCADE"), nullable=False)
    id_consultorio = Column(Integer, ForeignKey("consultorio.id_consultorio", ondelete="CASCADE"), nullable=False)

    paciente = relationship("Paciente", back_populates="citas")
    odontologo = relationship("Odontologo", back_populates="citas")
    consultorio = relationship("Consultorio", back_populates="citas")
    
    # 🔥 RELACIÓN ACTUALIZADA: Muchos a Muchos con Tratamiento
    tratamientos = relationship("Tratamiento", secondary=cita_tratamiento, back_populates="citas")
    
    recordatorios = relationship("Recordatorio", back_populates="cita", cascade="all, delete-orphan")
    pagos = relationship("Pago", back_populates="cita", cascade="all, delete-orphan")


# ── TABLA: TRATAMIENTO ────────────────────────────────────────────────────────

class Tratamiento(Base):
    __tablename__ = "tratamiento"
    __table_args__ = {'extend_existing': True}

    id_tratamiento = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    costo = Column(Numeric(10, 2), nullable=True)
    duracion_estimada = Column(String(100), nullable=True)
    
    #  ELIMINADO: id_cita y la relación 'cita' ya no existen aquí.
    # Ahora la relación se maneja mediante la tabla pivote 'cita_tratamiento'.

    #  NUEVA RELACIÓN: Muchos a Muchos con Cita
    citas = relationship("Cita", secondary=cita_tratamiento, back_populates="tratamientos")
    usuarios = relationship("Usuario", secondary=usuario_tratamiento, back_populates="tratamientos")


# ── TABLA: RECORDATORIO ──────────────────────────────────────────────────────

class Recordatorio(Base):
    __tablename__ = "recordatorio"
    __table_args__ = {'extend_existing': True}

    id_recordatorio = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(50), nullable=True)
    fecha_envio = Column(TIMESTAMP, nullable=True)
    estado = Column(String(30), nullable=True, default="Pendiente")
    id_cita = Column(Integer, ForeignKey("cita.id_cita", ondelete="CASCADE"), nullable=False)

    cita = relationship("Cita", back_populates="recordatorios")


# ── TABLA: PAGO ──────────────────────────────────────────────────────────────

class Pago(Base):
    __tablename__ = "pago"
    __table_args__ = {'extend_existing': True}

    id_pago = Column(Integer, primary_key=True, index=True)
    fecha_pago = Column(Date, nullable=False)
    monto = Column(Numeric(10, 2), nullable=False)
    metodo_pago = Column(String(50), nullable=True)
    estado_pago = Column(String(30), nullable=True, default="Pendiente")
    referencia = Column(String(100), nullable=True)
    id_cita = Column(Integer, ForeignKey("cita.id_cita", ondelete="CASCADE"), nullable=False)

    cita = relationship("Cita", back_populates="pagos")
    factura = relationship("Factura", back_populates="pago", uselist=False, cascade="all, delete-orphan")


# ── TABLA: FACTURA ───────────────────────────────────────────────────────────

class Factura(Base):
    __tablename__ = "factura"
    __table_args__ = {'extend_existing': True}

    id_factura = Column(Integer, primary_key=True, index=True)
    fecha_emision = Column(Date, nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=True)
    impuesto = Column(Numeric(10, 2), nullable=True)
    total = Column(Numeric(10, 2), nullable=True)
    id_pago = Column(Integer, ForeignKey("pago.id_pago", ondelete="CASCADE"), unique=True, nullable=False)

    pago = relationship("Pago", back_populates="factura")


# ── TABLA: ROL ───────────────────────────────────────────────────────────────

class Rol(Base):
    __tablename__ = "rol"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)
    permisos = Column(String(50), nullable=True, default="READ ONLY")


# ── TABLA: PROVEEDOR ─────────────────────────────────────────────────────────

class Proveedor(Base):
    __tablename__ = "proveedor"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    empresa = Column(String(200), nullable=False)
    contacto_asesor = Column(String(100), nullable=True)
    telefono = Column(String(20), nullable=True)
    suministro = Column(String(200), nullable=True)
    estado_convenio = Column(String(30), nullable=True, default="Vigente")


# ── TABLA: SERVICIO ──────────────────────────────────────────────────────────

class Servicio(Base):
    __tablename__ = "servicio"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("paciente.id_paciente", ondelete="CASCADE"), nullable=False)
    tratamiento_nombre = Column(String(100), nullable=False)
    odontologo_nombre = Column(String(100), nullable=True)
    proxima_cita = Column(String(50), nullable=True)
    estado_cuenta = Column(String(30), nullable=True, default="Pendiente")

    paciente = relationship("Paciente", back_populates="servicios")
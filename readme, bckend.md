# 🔧 Backend OdontoSoft — Documentación Técnica

![Python](https://img.shields.io/badge/Python-3.11+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-336791) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-FF6C00)

Documentación técnica del backend: arquitectura, modelos de datos, routers y mejores prácticas.

---

## 🏗️ Arquitectura

**Patrón:** Layered Architecture (Capas)

```
Presentation (main.py)
    ↓
Application (/routers/)
    ↓
Data (models.py, schemas.py)
    ↓
Persistence (database.py → PostgreSQL)
```

---

## 📂 Estructura

```
backend/
├── main.py              # App FastAPI, CORS, middleware, routers
├── database.py          # Conexión PostgreSQL + SessionLocal
├── models.py            # Tablas ORM (Paciente, Usuario, Cita, etc)
├── schemas.py           # Validación Pydantic (Create, Update, Out)
├── utils.py             # hash_password(), verify_password()
├── test_connection.py   # Script diagnóstico
├── requirements.txt     # Dependencias
├── .env                 # Variables (gitignored)
└── routers/             # Módulos CRUD
    ├── auth.py          # /auth/registro, /auth/login
    ├── usuarios.py      # CRUD usuarios
    ├── pacientes.py     # CRUD pacientes
    ├── odontologos.py   # CRUD odontólogos
    ├── citas.py         # CRUD citas
    ├── tratamientos.py  # CRUD tratamientos
    ├── historias_clinicas.py
    ├── consultorios.py
    ├── pagos.py
    ├── facturas.py
    ├── recordatorios.py
    ├── roles.py
    ├── proveedores.py
    └── servicios.py
```

---

## 📄 Archivos Core

### main.py
```python
# Crea tablas automáticamente
models.Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="OdontoSoft API", version="2.0.0")

# CORS
app.add_middleware(CORSMiddleware, allow_origins=["*"])

# Middleware logging
@app.middleware("http")
async def registrar_peticiones(request, call_next):
    # Registra método, ruta, tiempo

# Exception handlers
@app.exception_handler(RequestValidationError)  # 422
@app.exception_handler(IntegrityError)         # 409
@app.exception_handler(SQLAlchemyError)        # 500
@app.exception_handler(Exception)              # Generic

# Registra routers
app.include_router(auth.router)
app.include_router(usuarios.router)
# ... más

# Endpoints útiles
@app.get("/")           # Bienvenida
@app.get("/health")     # Health check
@app.get("/info")       # Info sistema
```

### database.py
```python
# Variables de entorno → URL PostgreSQL
DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{name}"

# Motor SQLAlchemy
engine = create_engine(DATABASE_URL)

# Sesión para transacciones
SessionLocal = sessionmaker(bind=engine)

# Base para ORM
Base = declarative_base()

# Dependencia inyectable
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Uso en routers:**
```python
@router.get("/pacientes/")
async def listar(db: Session = Depends(get_db)):
    return db.query(models.Paciente).all()
```

### models.py
Define tablas como clases Python:

```python
class Paciente(Base):
    __tablename__ = "paciente"
    
    id_paciente = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    documento = Column(String(20), unique=True)
    # ... más campos
    
    # Relaciones
    usuarios = relationship("Usuario", secondary=usuario_paciente)
    citas = relationship("Cita", back_populates="paciente", cascade="all, delete-orphan")
```

### schemas.py
Validación Pydantic con estructura **Base → Create → Update → Out**:

```python
class PacienteBase(BaseModel):
    nombre: str = Field(..., min_length=1)
    documento: str

class PacienteCreate(PacienteBase):
    pass

class PacienteUpdate(BaseModel):
    nombre: Optional[str] = None
    documento: Optional[str] = None

class PacienteOut(PacienteBase):
    id_paciente: int
    model_config = ConfigDict(from_attributes=True)
```

---

## 📊 Modelos Principales

| Tabla | Campos clave |
|-------|-------------|
| **usuario** | id, correo (UNIQUE), contrasena, rol, estado, fecha_registro |
| **paciente** | id, nombre, apellido, documento (UNIQUE), correo, eps, alergias |
| **cita** | id, fecha, hora, estado, id_paciente, id_odontologo, id_consultorio |
| **tratamiento** | id, nombre, descripcion, costo, duracion_estimada |
| **historia_clinica** | id, id_paciente, antecedentes, diagnostico, observaciones |
| **odontologo** | id, nombre, especialidad, id_consultorio |
| **pago** | id, id_cita, fecha_pago, monto, metodo_pago, estado_pago |
| **factura** | id, id_pago, fecha_emision, subtotal, impuesto, total |
| **rol** | id, nombre, descripcion, permisos |
| **consultorio** | id, nombre, ubicacion, numero_sala |

---

## 🛣️ Patrón CRUD

Cada router implementa:

```python
# CREATE
@router.post("/", response_model=schemas.PacienteOut, status_code=201)
async def crear(data: schemas.PacienteCreate, db: Session = Depends(get_db)):
    obj = models.Paciente(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

# READ (listar)
@router.get("/", response_model=list[schemas.PacienteOut])
async def listar(db: Session = Depends(get_db)):
    return db.query(models.Paciente).all()

# READ (uno)
@router.get("/{id}", response_model=schemas.PacienteOut)
async def obtener(id: int, db: Session = Depends(get_db)):
    obj = db.query(models.Paciente).filter_by(id_paciente=id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="No encontrado")
    return obj

# UPDATE
@router.put("/{id}", response_model=schemas.PacienteOut)
async def actualizar(id: int, data: schemas.PacienteUpdate, db: Session = Depends(get_db)):
    obj = db.query(models.Paciente).filter_by(id_paciente=id).first()
    if not obj:
        raise HTTPException(status_code=404)
    for key, value in data.dict(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj

# DELETE
@router.delete("/{id}", status_code=204)
async def eliminar(id: int, db: Session = Depends(get_db)):
    obj = db.query(models.Paciente).filter_by(id_paciente=id).first()
    if not obj:
        raise HTTPException(status_code=404)
    db.delete(obj)
    db.commit()
```

---

## ⚠️ Códigos HTTP

```
200 OK              ✅ Éxito (GET, PUT)
201 Created         ✅ Creado (POST)
204 No Content      ✅ Eliminado (DELETE)
400 Bad Request     ❌ Solicitud inválida
404 Not Found       ❌ Recurso no existe
409 Conflict        ❌ Duplicado / FK violation
422 Validation      ❌ Error validación Pydantic
500 Server Error    ❌ Error interno
```

---

## 🔐 Seguridad

```python
# Hash de contraseñas (SHA-256)
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain: str, hashed: str) -> bool:
    return hash_password(plain) == hashed

# ⚠️ Nota: En producción usar bcrypt o argon2
```

---

## 🎯 Mejores Prácticas

✅ **Inyección de dependencias** → `db: Session = Depends(get_db)`  
✅ **Validación Pydantic** → Automática en schemas  
✅ **Relaciones ORM** → Con `back_populates` y `cascade`  
✅ **Transacciones** → `commit()` y `rollback()`  
✅ **Queries eficientes** → `.filter_by()` en lugar de `.all()` + filter  

❌ **Evitar:** Crear sesiones manualmente, validar en el endpoint, queries sin filtros

---

## 🔍 Debugging

### Ver logs SQL
```python
# En database.py
engine = create_engine(DATABASE_URL, echo=True)  # Muestra queries
```

### Health check
```bash
curl http://localhost:8000/health
```

### Acceder a documentación
```
http://localhost:8000/docs       # Swagger
http://localhost:8000/redoc      # ReDoc
```

---

## 📈 Mejoras Futuras

- 🔐 JWT tokens (en lugar de sesiones)
- 🔄 Redis para caché
- 📧 Celery para emails async
- 🧪 pytest para tests
- 🐳 Docker
- 📊 Alembic para migraciones
- 🔔 WebSockets para notificaciones real-time
- 🛡️ bcrypt/argon2 para contraseñas

---

## 📞 Soporte

1. Revisa logs: `uvicorn main:app --reload`
2. Docs interactiva: http://localhost:8000/docs
3. Verifica BD: `python test_connection.py`

---

**Versión:** 2.0.0 | **Última actualización:** Julio 2026

Para guía general, consulta `README.md`

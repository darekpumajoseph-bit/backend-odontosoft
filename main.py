# main.py - Versión COMPLETA con CORS

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime
from database import engine
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import text
import models
import logging
import traceback
import sys

# ── Configurar logging ──────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# ── Crear tablas en la base de datos ──────────────────────────────────────

def create_tables():
    """Crear las tablas en la base de datos si no existen"""
    try:
        logger.info("🔄 Verificando/Creando tablas en la base de datos...")
        models.Base.metadata.create_all(bind=engine)
        logger.info("✅ Tablas creadas/verificadas correctamente")
    except Exception as e:
        logger.error(f"❌ Error al crear tablas: {str(e)}")
        logger.error(traceback.format_exc())
        raise e


# Ejecutar creación de tablas
create_tables()


# ── Crear aplicación FastAPI ──────────────────────────────────────────────

app = FastAPI(
    title="OdontoSoft API",
    description="Sistema de Gestión Odontológica — Backend REST con FastAPI + PostgreSQL",
    version="2.0.0",
    debug=True,
    docs_url="/docs",
    redoc_url="/redoc"
)


# =============================================
# 🔥 MIDDLEWARE CORS - COLOCA ESTO AQUÍ
# =============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permite todos los headers
    expose_headers=["*"], # Expone todos los headers
)


# ── Middleware de log de peticiones ──────────────────────────────────────

@app.middleware("http")
async def registrar_peticiones(request: Request, call_next):
    """Registrar todas las peticiones HTTP con detalles"""
    start_time = datetime.now()
    
    logger.info(f"➡️  {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        
        process_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"⬅️  {request.method} {request.url.path} → {response.status_code} ({process_time:.3f}s)")
        
        response.headers["X-Process-Time"] = str(process_time)
        return response
        
    except Exception as e:
        logger.error(f"❌ Error en {request.method} {request.url.path}: {str(e)}")
        logger.error(traceback.format_exc())
        raise e


# ── Manejadores de errores globales ──────────────────────────────────────

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Manejar errores de validación de Pydantic (422)"""
    logger.error(f"❌ Error de validación en {request.method} {request.url.path}")
    logger.error(f"   Errores: {exc.errors()}")
    
    error_messages = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        msg = error["msg"]
        error_messages.append(f"{field}: {msg}")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Error de validación de datos",
            "errors": exc.errors(),
            "messages": error_messages,
            "body": exc.body if hasattr(exc, 'body') else None
        }
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Manejar errores de integridad de base de datos (409)"""
    logger.error(f"❌ Error de integridad en {request.method} {request.url.path}")
    logger.error(f"   {str(exc)}")
    
    error_msg = str(exc.orig) if exc.orig else str(exc)
    
    if "duplicate key" in error_msg.lower() or "duplicate key value" in error_msg.lower():
        if "correo" in error_msg.lower():
            return JSONResponse(
                status_code=409,
                content={
                    "detail": "El correo electrónico ya está registrado",
                    "error": "duplicate_email"
                }
            )
        elif "documento" in error_msg.lower():
            return JSONResponse(
                status_code=409,
                content={
                    "detail": "El documento ya está registrado",
                    "error": "duplicate_document"
                }
            )
        elif "usuario_paciente" in error_msg.lower():
            return JSONResponse(
                status_code=409,
                content={
                    "detail": "La relación usuario-paciente ya existe",
                    "error": "duplicate_relation"
                }
            )
        else:
            return JSONResponse(
                status_code=409,
                content={
                    "detail": "El registro ya existe en la base de datos",
                    "error": "duplicate_entry"
                }
            )
    
    elif "foreign key" in error_msg.lower() or "references" in error_msg.lower():
        return JSONResponse(
            status_code=409,
            content={
                "detail": "El registro está siendo referenciado por otros datos. Elimine las referencias primero.",
                "error": "foreign_key_violation"
            }
        )
    
    return JSONResponse(
        status_code=409,
        content={
            "detail": f"Conflicto con los datos existentes",
            "error": error_msg
        }
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    """Manejar errores generales de SQLAlchemy (500)"""
    logger.error(f"❌ Error de base de datos en {request.method} {request.url.path}")
    logger.error(f"   {str(exc)}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error en la base de datos",
            "error": str(exc) if app.debug else "Contacte al administrador"
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Manejar errores HTTP personalizados"""
    logger.warning(f"⚠️  HTTP {exc.status_code} en {request.method} {request.url.path}")
    if exc.detail:
        logger.warning(f"   {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Manejar cualquier otra excepción no capturada (500)"""
    logger.error(f"❌ Error inesperado en {request.method} {request.url.path}")
    logger.error(f"   Tipo: {type(exc).__name__}")
    logger.error(f"   Mensaje: {str(exc)}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "error": str(exc) if app.debug else "Contacte al administrador"
        }
    )


# ── Importar y registrar routers ──────────────────────────────────────────

from routers import (
    auth,
    usuarios,
    pacientes,
    odontologos,
    consultorios,
    historias_clinicas,
    citas,
    tratamientos,
    recordatorios,
    pagos,
    facturas,
    roles,
    proveedores,
    servicios
)

# Registrar todos los routers
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(pacientes.router)
app.include_router(odontologos.router)
app.include_router(consultorios.router)
app.include_router(historias_clinicas.router)
app.include_router(citas.router)
app.include_router(tratamientos.router)
app.include_router(recordatorios.router)
app.include_router(pagos.router)
app.include_router(facturas.router)
app.include_router(roles.router)
app.include_router(proveedores.router)
app.include_router(servicios.router)

logger.info("✅ Todos los routers registrados correctamente")


# ── Endpoint raíz ──────────────────────────────────────────────────────────

@app.get("/", tags=["Root"])
async def root():
    """Endpoint de bienvenida de la API"""
    return {
        "sistema": "OdontoSoft API",
        "version": "2.0.0",
        "documentacion": "/docs",
        "documentacion_alternativa": "/redoc",
        "estado": "Activo",
        "base_datos": "PostgreSQL - ProyectoApi",
        "timestamp": datetime.now().isoformat()
    }


# ── Endpoint de salud (health check) ──────────────────────────────────────

@app.get("/health", tags=["Health"])
async def health_check():
    """Verificar el estado de la API y conexión a la base de datos"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "running",
            "database": "unknown"
        }
    }
    
    try:
        from database import SessionLocal
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        
        health_status["services"]["database"] = "connected"
        health_status["database"] = "connected"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        health_status["status"] = "unhealthy"
        health_status["services"]["database"] = "disconnected"
        health_status["database"] = "disconnected"
        health_status["error"] = str(e)
        
        return JSONResponse(
            status_code=503,
            content=health_status
        )


# ── Endpoint de información del sistema ──────────────────────────────────

@app.get("/info", tags=["Info"])
async def system_info():
    """Obtener información del sistema"""
    return {
        "sistema": "OdontoSoft",
        "version": "2.0.0",
        "framework": "FastAPI",
        "base_datos": "PostgreSQL",
        "ambiente": "desarrollo" if app.debug else "producción",
        "timestamp": datetime.now().isoformat()
    }


# ── Eventos de inicio/apagado ─────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    logger.info("=" * 70)
    logger.info("🚀 OdontoSoft API iniciada correctamente")
    logger.info(f"📚 Documentación disponible en: http://localhost:8000/docs")
    logger.info(f"📚 Documentación Redoc en: http://localhost:8000/redoc")
    logger.info(f"🔍 Health check en: http://localhost:8000/health")
    logger.info("=" * 70)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 OdontoSoft API cerrando...")


# ── Si se ejecuta directamente ────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
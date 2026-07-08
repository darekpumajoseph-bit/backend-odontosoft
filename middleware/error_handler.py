# middleware/error_handler.py - Manejo global de errores (VERSIÓN CORREGIDA)

from fastapi import FastAPI, Request, HTTPException  # <-- HTTPException añadido
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging
import traceback

# ── Configurar logging ──────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def setup_error_handlers(app: FastAPI):
    """
    Configurar manejadores de errores globales para la aplicación.
    
    Args:
        app: Instancia de FastAPI
    """
    
    # ── Handler para errores de validación de Pydantic ────────────────────
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Manejar errores de validación de Pydantic (422).
        """
        logger.error(f"❌ Error de validación en {request.method} {request.url.path}")
        logger.error(f"   Errores: {exc.errors()}")
        
        # Extraer mensajes de error amigables
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
    
    
    # ── Handler para errores de integridad de base de datos ───────────────
    
    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        """
        Manejar errores de integridad de base de datos (409).
        Ej: Claves duplicadas, violación de foreign key, etc.
        """
        logger.error(f"❌ Error de integridad en {request.method} {request.url.path}")
        logger.error(f"   {str(exc)}")
        
        error_msg = str(exc.orig) if exc.orig else str(exc)
        
        # Mensajes más amigables para el usuario
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
                "detail": "Conflicto con los datos existentes",
                "error": error_msg
            }
        )
    
    
    # ── Handler para errores generales de SQLAlchemy ──────────────────────
    
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        """
        Manejar errores generales de SQLAlchemy (500).
        """
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
    
    
    # ── Handler para errores HTTP personalizados ──────────────────────────
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        Manejar errores HTTP personalizados.
        """
        logger.warning(f"⚠️  HTTP {exc.status_code} en {request.method} {request.url.path}")
        if exc.detail:
            logger.warning(f"   {exc.detail}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    
    # ── Handler para cualquier otra excepción no capturada ────────────────
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """
        Manejar cualquier otra excepción no capturada (500).
        """
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
    
    logger.info("✅ Manejadores de errores configurados correctamente")
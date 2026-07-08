# utils.py - Funciones comunes para el backend

import hashlib
import re
import random
import string
from sqlalchemy.orm import Session
import models

# ── Hash de contraseña ────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hashea la contraseña usando SHA-256 con encoding UTF-8 (sin BOM)"""
    # Eliminar espacios y usar UTF-8 estándar
    password_clean = password.strip()
    return hashlib.sha256(password_clean.encode('utf-8')).hexdigest()


def verificar_password(password_plano: str, password_hash: str) -> bool:
    """Verifica si una contraseña en texto plano coincide con su hash."""
    return hash_password(password_plano) == password_hash


# ── Validación de correo ─────────────────────────────────────────────────────

def validar_correo(correo: str) -> bool:
    """Valida que el correo tenga formato correcto usando expresión regular."""
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, correo) is not None


# ── Generar documento único ──────────────────────────────────────────────────

def generar_documento_unico(db: Session) -> str:
    """Genera un número de documento único para el paciente."""
    while True:
        doc = "CC" + ''.join(random.choices(string.digits, k=8))
        existe = db.query(models.Paciente).filter(
            models.Paciente.documento == doc
        ).first()
        if not existe:
            return doc
        
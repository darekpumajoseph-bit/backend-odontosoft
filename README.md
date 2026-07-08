# 🦷 OdontoSoft — Sistema de Gestión Odontológica

![Estado](https://img.shields.io/badge/Estado-Activo-green) ![Versión](https://img.shields.io/badge/Versión-2.0.0-blue) ![Python](https://img.shields.io/badge/Python-3.11+-blue) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-336791)

Sistema integral para administración de clínicas odontológicas con **FastAPI** (backend) y **HTML5/CSS3/JavaScript** (frontend).

---

## 🎯 Características

✅ Gestión de pacientes | ✅ Agenda de citas | ✅ Historia clínica | ✅ Pagos y facturas  
✅ Catálogo de tratamientos | ✅ Control de roles | ✅ Recordatorios | ✅ GDPR compliant

---

## 📊 Stack

| Backend | Frontend | Base de Datos |
|---------|----------|---------------|
| Python 3.11+ | HTML5 semántico | PostgreSQL 13+ |
| FastAPI | CSS3 responsive | SQLAlchemy ORM |
| Uvicorn ASGI | JavaScript ES6+ | Pydantic v2 |

---

## 📁 Estructura

```
backend/              → API REST (FastAPI + PostgreSQL)
  ├── main.py         → App principal
  ├── database.py     → Conexión BD
  ├── models.py       → Tablas ORM
  ├── schemas.py      → Validación
  └── routers/        → CRUD endpoints

frontend/             → Interfaz web
  ├── html/           → Vistas (login, citas, pacientes, etc)
  ├── css/            → Estilos
  └── js/             → Lógica (api.js centraliza requests)
```

---

## 🚀 Instalación Rápida

### 1️⃣ Clonar repo
```bash
git clone https://github.com/darekpumajoseph-bit/arquitectura-de-software_Odontologia-.git
cd arquitectura-de-software_Odontologia-
```

### 2️⃣ Backend

```bash
cd backend

# Entorno virtual
python -m venv env
.\env\Scripts\activate  # Windows
# source env/bin/activate  # Mac/Linux

# Instalar dependencias
pip install -r requirements.txt

# Crear .env
echo DB_USER=postgres > .env
echo DB_PASSWORD=123456 >> .env
echo DB_HOST=localhost >> .env
echo DB_PORT=5432 >> .env
echo DB_NAME=ProyectoApi >> .env

# Crear BD en PostgreSQL
psql -U postgres -c "CREATE DATABASE \"ProyectoApi\" WITH ENCODING 'UTF8';"

# Verificar conexión
python test_connection.py

# Iniciar servidor
uvicorn main:app --reload
```

✅ Backend en **http://localhost:8000**

### 3️⃣ Frontend

En **nueva terminal**:

```bash
cd frontend

# Opción A: Live Server (VS Code)
# - Abre carpeta en VS Code
# - Instala extensión "Live Server" 
# - Clic derecho en login.html → "Open with Live Server"

# Opción B: Python
python -m http.server 5500
# Luego: http://localhost:5500/login.html
```

✅ Frontend en **http://localhost:5500**

---

## ✅ Verificar Instalación

1. **Backend:** http://localhost:8000/docs → Ver API Swagger
2. **Frontend:** http://localhost:5500/login.html → Ver login
3. **Test:** Registrar usuario → Mensaje verde = ✅ Todo funciona

---

## 🔗 Endpoints Principales

```
POST   /auth/registro           → Crear cuenta
POST   /auth/login              → Iniciar sesión

CRUD   /pacientes/              → Gestión de pacientes
CRUD   /citas/                  → Agenda
CRUD   /odontologos/            → Odontólogos
CRUD   /tratamientos/           → Catálogo
CRUD   /pagos/, /facturas/      → Finanzas
CRUD   /roles/                  → Permisos
```

Full docs: **http://localhost:8000/docs**

---

## 📊 Estado del Proyecto

| Componente | Estado | % |
|-----------|--------|---|
| Backend API | ✅ | 100% |
| Frontend UI | ✅ | 100% |
| Base de Datos | ✅ | 100% |
| Documentación | ✅ | 100% |
| Tests unitarios | 🔄 | 0% |
| Docker | 🔄 | 0% |

---

## 🐛 Problemas Comunes

| Problema | Solución |
|----------|----------|
| `ModuleNotFoundError: fastapi` | `pip install -r requirements.txt` |
| CORS error en navegador | Backend debe estar en http://localhost:8000 |
| BD rechaza conexión | PostgreSQL debe estar corriendo + revisar `.env` |
| Puerto 8000 ocupado | `uvicorn main:app --reload --port 8001` |

---

## 📱 Entidades

| Tabla | Descripción |
|-------|-------------|
| Usuario | Cuentas (Paciente/Odontólogo) |
| Paciente | Fichas con historia médica |
| Cita | Eventos de agenda |
| Tratamiento | Procedimientos + precios |
| Historia Clínica | Expedientes médicos |
| Pago | Transacciones |
| Factura | Documentos financieros |
| Rol | Perfiles de acceso |

---

## 🔒 Seguridad

✅ CORS configurado | ✅ Contraseñas hasheadas (SHA-256) | ✅ Validación Pydantic  
✅ Manejo de errores | ✅ Middleware de logging | ✅ GDPR compliant

---

## 📚 Documentación Detallada

- **API Tech:** Ver `readme, bckend.md` (arquitectura, modelos, patrones)
- **API Interactive:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

---

## 🤝 Contribuir

```bash
git checkout -b feature/mi-feature
git commit -am "Descripción"
git push origin feature/mi-feature
# Abre Pull Request
```

---

**Versión:** 2.0.0 | **Autor:** Darek Puma Joseph | **Licencia:** MIT

🦷 **¡Gracias por usar OdontoSoft!**

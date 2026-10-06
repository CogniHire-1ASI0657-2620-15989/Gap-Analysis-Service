# Gap Analysis Service

Es un microservicio FastAPI que genera reportes de compatibilidad entre el perfil profesional de un usuario y una vacante almacenada por Job Discovery.

El servicio analiza el título y `description_snippet` de la oferta con Groq cuando `GROQ_API_KEY` está configurada. La respuesta del LLM se limita al catálogo de habilidades local y el porcentaje final se calcula de forma determinista. Si Groq falla o excede su cuota, se usa automáticamente la estrategia por reglas.

## Configuración

1. Crea una base PostgreSQL, por ejemplo `gap_analysis_db`.
2. Copia `.env.example` como `.env` y revisa las URLs de Identity y Job Discovery.
3. Instala dependencias y aplica la migración:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8002
```

## Seguridad

El servicio confía en el API Gateway, que debe validar el JWT y reenviar `X-User-Id`. Las rutas directas sin ese encabezado devuelven `401`.

## Endpoints

- `GET /health`
- `POST /api/v1/gap-reports`
- `GET /api/v1/gap-reports/{job_id}`
- `GET /api/v1/gap-reports`

Para generar un reporte:

```http
POST /api/v1/gap-reports
X-User-Id: 1
Content-Type: application/json

{"job_id": 123}
```

El servicio consulta el perfil mediante Identity Service y la vacante mediante Job Discovery Service. Cada usuario posee su propio reporte por vacante; una nueva generación actualiza el reporte existente.

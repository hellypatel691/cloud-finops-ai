from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.organization import router as organization_router
from app.api.v1.project import router as project_router
from app.api.v1.upload import router as upload_router
from app.api.v1.billing import router as billing_router
from app.api.v1.anomaly import router as anomaly_router
from app.api.v1.forecast import router as forecast_router
from app.api.v1.explainability import router as explainability_router
from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router
from app.utils.exceptions import (
    http_exception_handler,
    value_error_handler,
    generic_error_handler,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="Cloud FinOps AI",
    version="1.0.0",
    description="AI-Powered Multi-Cloud Cost Anomaly Detection and Spend Forecasting",
    redirect_slashes=False,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(organization_router, prefix="/api/v1")
app.include_router(project_router, prefix="/api/v1")
app.include_router(upload_router, prefix="/api/v1")
app.include_router(billing_router, prefix="/api/v1")
app.include_router(anomaly_router, prefix="/api/v1")
app.include_router(forecast_router, prefix="/api/v1")
app.include_router(explainability_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")

# ── Exception handlers ────────────────────────────────────────────────────────
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(ValueError, value_error_handler)
app.add_exception_handler(Exception, generic_error_handler)


# ── Core routes ───────────────────────────────────────────────────────────────
@app.get("/")
def root():
    logger.info("Root endpoint called")
    return {
        "application": "Cloud FinOps AI",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"server": "running"}

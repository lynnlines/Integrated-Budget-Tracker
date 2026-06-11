from fastapi import FastAPI
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.api_v1 import api_router
from app.api.dashboard import router as dashboard_router
from app.core.config import settings
from app.core.jobs import register_default_jobs
from app.core.worker import Scheduler
from app.db.base import Base
from app.db.session import engine
import app.models  # noqa: F401


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("X-XSS-Protection", "1; mode=block")
        return response


app = FastAPI(
    title="Integrated Budget Tracker",
    docs_url=settings.docs_url_final,
    redoc_url=settings.redoc_url_final,
    openapi_url=settings.openapi_url_final,
)

if settings.https_redirect:
    app.add_middleware(HTTPSRedirectMiddleware)

if settings.allowed_hosts:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)

app.add_middleware(SecurityHeadersMiddleware)

scheduler = Scheduler(tick_seconds=30)
register_default_jobs(scheduler)


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    scheduler.start()


@app.on_event("shutdown")
def shutdown_event():
    scheduler.stop()


app.include_router(api_router, prefix="/api/v1")
app.include_router(dashboard_router)


@app.get("/")
def root():
    return {"status": "ok", "service": "Integrated Budget Tracker"}

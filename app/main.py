from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import httpx

from app.config import settings
from app.api.routes import router as api_router, limiter
from app.core.logging import RequestTracingMiddleware
from app.core.security import SecurityError
from app.core.exceptions import (
    security_exception_handler,
    httpx_timeout_handler,
    httpx_connect_handler,
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Production-Ready Website Audit API. "
        "Built for Digital Heroes Training Task (https://digitalheroesco.com)"
    ),
    docs_url="/docs",
    redoc_url="/redoc"
)

# State & Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Custom Handlers
app.add_exception_handler(SecurityError, security_exception_handler)
app.add_exception_handler(httpx.TimeoutException, httpx_timeout_handler)
app.add_exception_handler(httpx.ConnectError, httpx_connect_handler)

# Middleware
app.add_middleware(RequestTracingMiddleware)

# Mount Routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Root"])
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health",
        "attribution": "Built for Digital Heroes Training Task (https://digitalheroesco.com)"
    }

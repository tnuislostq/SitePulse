from fastapi import Request
from fastapi.responses import JSONResponse
import httpx
from app.core.security import SecurityError

async def security_exception_handler(request: Request, exc: SecurityError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "SecurityValidationError",
            "message": str(exc),
            "request_id": getattr(request.state, "request_id", None)
        }
    )

async def httpx_timeout_handler(request: Request, exc: httpx.TimeoutException):
    return JSONResponse(
        status_code=504,
        content={
            "error": "GatewayTimeout",
            "message": "The target website took too long to respond.",
            "request_id": getattr(request.state, "request_id", None)
        }
    )

async def httpx_connect_handler(request: Request, exc: httpx.ConnectError):
    return JSONResponse(
        status_code=502,
        content={
            "error": "BadGateway",
            "message": "Failed to establish a connection to the target server.",
            "request_id": getattr(request.state, "request_id", None)
        }
    )

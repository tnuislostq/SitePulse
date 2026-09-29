from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Request, Query, HTTPException, status
from pydantic import BaseModel, HttpUrl
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings
from app.services.auditor import AuditService
from app.services.cache import audit_cache

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

class AuditRequest(BaseModel):
    url: HttpUrl

class HeadingsDetail(BaseModel):
    h1: List[str]
    h2_count: int

class SeoSummary(BaseModel):
    has_title: bool
    has_meta_description: bool
    h1_count: int
    total_links: int
    total_images: int
    images_missing_alt_count: int

class AuditResponse(BaseModel):
    target_url: str
    status_code: int
    latency_ms: float
    is_https: bool
    page_title: Optional[str] = None
    meta_description: Optional[str] = None
    headings: HeadingsDetail
    seo_summary: SeoSummary
    open_graph: Dict[str, str]
    content_length_bytes: int
    cached: bool = False

@router.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "attribution": "Built for Digital Heroes Training Task (https://digitalheroesco.com)"
    }

@router.post(
    "/audit",
    response_model=AuditResponse,
    tags=["Audit"],
    summary="Perform a full technical & SEO audit on a URL"
)
@limiter.limit(settings.RATE_LIMIT_PER_MINUTE)
async def audit_url(
    request: Request,
    payload: AuditRequest,
    cache_ttl: Optional[int] = Query(
        default=settings.CACHE_TTL_SECONDS,
        ge=0,
        le=86400,
        description="Cache duration in seconds (0 to bypass)"
    )
):
    target_str = str(payload.url)

    # 1. Check Cache
    if cache_ttl and cache_ttl > 0:
        cached_result = audit_cache.get(target_str)
        if cached_result:
            cached_result["cached"] = True
            return cached_result

    # 2. Perform Audit
    result = await AuditService.perform_audit(target_str)
    result["cached"] = False

    # 3. Store in Cache
    if cache_ttl and cache_ttl > 0:
        audit_cache.set(target_str, result, ttl=cache_ttl)

    return result

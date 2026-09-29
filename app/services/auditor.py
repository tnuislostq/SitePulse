import time
from typing import Dict, Any, List
import httpx
from bs4 import BeautifulSoup
from app.config import settings
from app.core.security import validate_target_url

class AuditService:
    @staticmethod
    async def perform_audit(target_url: str) -> Dict[str, Any]:
        # Step 1: SSRF validation
        safe_url = validate_target_url(target_url)

        headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

        # Step 2: Asynchronous fetch with latency measurement
        start_time = time.perf_counter()
        async with httpx.AsyncClient(
            timeout=settings.DEFAULT_TIMEOUT_SECONDS,
            max_redirects=settings.MAX_REDIRECTS,
            follow_redirects=True
        ) as client:
            response = await client.get(safe_url, headers=headers)
        
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Step 3: Parse HTML
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string.strip() if soup.title and soup.title.string else None
        
        meta_desc = None
        desc_tag = soup.find("meta", attrs={"name": lambda x: x and x.lower() == "description"})
        if desc_tag and desc_tag.get("content"):
            meta_desc = desc_tag["content"].strip()

        # Headings analysis
        h1_tags = [h1.get_text(strip=True) for h1 in soup.find_all("h1")]
        h2_count = len(soup.find_all("h2"))

        # Links & images check
        links = soup.find_all("a", href=True)
        images = soup.find_all("img")
        images_missing_alt = [img.get("src", "unknown") for img in images if not img.get("alt")]

        # OpenGraph metadata
        og_data: Dict[str, str] = {}
        for og_tag in soup.find_all("meta", property=lambda x: x and x.startswith("og:")):
            prop = og_tag.get("property")
            content = og_tag.get("content")
            if prop and content:
                og_data[prop] = content

        return {
            "target_url": str(response.url),
            "status_code": response.status_code,
            "latency_ms": latency_ms,
            "is_https": response.url.scheme == "https",
            "page_title": title,
            "meta_description": meta_desc,
            "headings": {
                "h1": h1_tags,
                "h2_count": h2_count
            },
            "seo_summary": {
                "has_title": bool(title),
                "has_meta_description": bool(meta_desc),
                "h1_count": len(h1_tags),
                "total_links": len(links),
                "total_images": len(images),
                "images_missing_alt_count": len(images_missing_alt)
            },
            "open_graph": og_data,
            "content_length_bytes": len(response.content)
        }

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
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

@app.get("/", response_class=HTMLResponse, tags=["Dashboard"])
async def dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SitePulse — Website Audit Engine</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg: #090d16;
                --card-bg: #111827;
                --card-border: #1f2937;
                --primary: #3b82f6;
                --primary-hover: #2563eb;
                --accent: #10b981;
                --text-main: #f3f4f6;
                --text-muted: #9ca3af;
                --danger: #ef4444;
            }
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body {
                font-family: 'Plus Jakarta Sans', sans-serif;
                background-color: var(--bg);
                color: var(--text-main);
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }
            header {
                border-bottom: 1px solid var(--card-border);
                padding: 1.25rem 2rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: rgba(17, 24, 39, 0.7);
                backdrop-filter: blur(8px);
            }
            .brand {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                font-size: 1.25rem;
                font-weight: 700;
                letter-spacing: -0.02em;
            }
            .pulse-dot {
                width: 10px;
                height: 10px;
                background: var(--accent);
                border-radius: 50%;
                box-shadow: 0 0 10px var(--accent);
            }
            .nav-link {
                color: var(--text-muted);
                text-decoration: none;
                font-size: 0.9rem;
                font-weight: 500;
                transition: color 0.2s;
            }
            .nav-link:hover { color: var(--text-main); }
            main {
                flex: 1;
                max-width: 900px;
                width: 100%;
                margin: 3rem auto;
                padding: 0 1.5rem;
            }
            .hero-badge {
                display: inline-block;
                padding: 0.35rem 0.85rem;
                background: rgba(59, 130, 246, 0.1);
                color: #60a5fa;
                border-radius: 9999px;
                font-size: 0.8rem;
                font-weight: 600;
                margin-bottom: 1rem;
                border: 1px solid rgba(59, 130, 246, 0.2);
            }
            h1 {
                font-size: 2.25rem;
                font-weight: 700;
                letter-spacing: -0.03em;
                margin-bottom: 0.5rem;
            }
            p.subtitle {
                color: var(--text-muted);
                margin-bottom: 2rem;
                font-size: 1.05rem;
            }
            .input-box {
                background: var(--card-bg);
                border: 1px solid var(--card-border);
                border-radius: 12px;
                padding: 0.5rem;
                display: flex;
                gap: 0.5rem;
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
            }
            input[type="url"] {
                flex: 1;
                background: transparent;
                border: none;
                outline: none;
                color: var(--text-main);
                font-size: 1rem;
                padding: 0.75rem 1rem;
                font-family: inherit;
            }
            button {
                background: var(--primary);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0.75rem 1.5rem;
                font-size: 0.95rem;
                font-weight: 600;
                cursor: pointer;
                transition: background 0.2s;
            }
            button:hover { background: var(--primary-hover); }
            button:disabled { opacity: 0.6; cursor: not-allowed; }
            #results {
                margin-top: 2rem;
                display: none;
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 1rem;
                margin-bottom: 1.5rem;
            }
            .stat-card {
                background: var(--card-bg);
                border: 1px solid var(--card-border);
                border-radius: 10px;
                padding: 1.25rem;
            }
            .stat-label {
                font-size: 0.8rem;
                color: var(--text-muted);
                text-transform: uppercase;
                letter-spacing: 0.05em;
                font-weight: 600;
            }
            .stat-value {
                font-size: 1.5rem;
                font-weight: 700;
                margin-top: 0.35rem;
            }
            .details-card {
                background: var(--card-bg);
                border: 1px solid var(--card-border);
                border-radius: 10px;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
            }
            .details-title {
                font-size: 1.1rem;
                font-weight: 600;
                margin-bottom: 1rem;
            }
            .detail-row {
                display: flex;
                justify-content: space-between;
                padding: 0.6rem 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                font-size: 0.95rem;
            }
            .detail-row:last-child { border-bottom: none; }
            .detail-k { color: var(--text-muted); }
            .raw-json {
                background: #000;
                border-radius: 8px;
                padding: 1rem;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.85rem;
                color: #a7f3d0;
                overflow-x: auto;
                max-height: 250px;
            }
            .error-box {
                margin-top: 2rem;
                padding: 1rem 1.25rem;
                background: rgba(239, 68, 68, 0.1);
                border: 1px solid rgba(239, 68, 68, 0.2);
                border-radius: 10px;
                color: #fca5a5;
                display: none;
            }
            footer {
                margin-top: auto;
                border-top: 1px solid var(--card-border);
                padding: 1.5rem;
                text-align: center;
                font-size: 0.85rem;
                color: var(--text-muted);
            }
            footer a {
                color: #60a5fa;
                text-decoration: none;
                font-weight: 600;
            }
            footer a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <header>
            <div class="brand">
                <div class="pulse-dot"></div>
                SitePulse
            </div>
            <a href="/docs" target="_blank" class="nav-link">Interactive Swagger Docs &rarr;</a>
        </header>

        <main>
            <span class="hero-badge">Production-Ready Website Auditor</span>
            <h1>Audit Any Website</h1>
            <p class="subtitle">Run instant technical SEO, response latency, and SSRF security checks.</p>

            <form id="auditForm" class="input-box" onsubmit="runAudit(event)">
                <input type="url" id="targetUrl" placeholder="https://example.com" required autocomplete="off">
                <button type="submit" id="submitBtn">Audit Site</button>
            </form>

            <div id="errorBox" class="error-box"></div>

            <section id="results">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">HTTP Status</div>
                        <div class="stat-value" id="valStatus">-</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Latency</div>
                        <div class="stat-value" id="valLatency">-</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">HTTPS</div>
                        <div class="stat-value" id="valHttps">-</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Cache State</div>
                        <div class="stat-value" id="valCache">-</div>
                    </div>
                </div>

                <div class="details-card">
                    <div class="details-title">SEO & Metadata Analysis</div>
                    <div class="detail-row">
                        <span class="detail-k">Page Title</span>
                        <span class="detail-v" id="valTitle">-</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-k">Meta Description</span>
                        <span class="detail-v" id="valMeta">-</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-k">Total Links</span>
                        <span class="detail-v" id="valLinks">-</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-k">Images (Missing Alt)</span>
                        <span class="detail-v" id="valImages">-</span>
                    </div>
                </div>

                <div class="details-card">
                    <div class="details-title">Raw API Response</div>
                    <pre class="raw-json" id="rawJson"></pre>
                </div>
            </section>
        </main>

        <footer>
            Built for <a href="https://digitalheroesco.com" target="_blank" rel="noopener noreferrer">Digital Heroes Training Task</a>
        </footer>

        <script>
            async function runAudit(e) {
                e.preventDefault();
                const url = document.getElementById('targetUrl').value.trim();
                const btn = document.getElementById('submitBtn');
                const results = document.getElementById('results');
                const errorBox = document.getElementById('errorBox');

                btn.disabled = true;
                btn.textContent = 'Auditing...';
                errorBox.style.display = 'none';
                results.style.display = 'none';

                try {
                    const res = await fetch('/api/v1/audit', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ url: url })
                    });

                    const data = await res.json();

                    if (!res.ok) {
                        throw new Error(data.message || 'Audit failed. Check the URL and try again.');
                    }

                    document.getElementById('valStatus').textContent = data.status_code;
                    document.getElementById('valStatus').style.color = data.status_code === 200 ? 'var(--accent)' : 'var(--danger)';
                    document.getElementById('valLatency').textContent = data.latency_ms + 'ms';
                    document.getElementById('valHttps').textContent = data.is_https ? 'Secure (HTTPS)' : 'Insecure (HTTP)';
                    document.getElementById('valHttps').style.color = data.is_https ? 'var(--accent)' : 'var(--danger)';
                    document.getElementById('valCache').textContent = data.cached ? 'HIT' : 'MISS';

                    document.getElementById('valTitle').textContent = data.page_title || '(None)';
                    document.getElementById('valMeta').textContent = data.meta_description || '(None)';
                    document.getElementById('valLinks').textContent = data.seo_summary.total_links;
                    document.getElementById('valImages').textContent = `${data.seo_summary.total_images} total (${data.seo_summary.images_missing_alt_count} missing alt)`;

                    document.getElementById('rawJson').textContent = JSON.stringify(data, null, 2);
                    results.style.display = 'block';
                } catch (err) {
                    errorBox.textContent = err.message;
                    errorBox.style.display = 'block';
                } finally {
                    btn.disabled = false;
                    btn.textContent = 'Audit Site';
                }
            }
        </script>
    </body>
    </html>
    """

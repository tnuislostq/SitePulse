# SitePulse — Production-Ready Website Audit Engine

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Deployed on Render](https://img.shields.io/badge/Render-Live-46E3B7.svg?logo=render&logoColor=white)](https://sitepulse-audit.onrender.com)
[![Digital Heroes Attribution](https://img.shields.io/badge/Task-Digital%20Heroes-blue.svg)](https://digitalheroesco.com)

A high-performance, asynchronous website auditing engine built with FastAPI, HTTPX, and BeautifulSoup4. SitePulse performs deep DOM metadata extraction, network latency profiling, pre-flight SSRF threat mitigation, in-memory TTL caching, and per-client IP rate limiting.

> **Attribution:** Built for [Digital Heroes Training Task](https://digitalheroesco.com).

---

## 🔗 Live Deployments & Demos

| Resource | Direct Link |
| :--- | :--- |
| 🚀 **Live Interactive Dashboard** | [https://sitepulse-audit.onrender.com](https://sitepulse-audit.onrender.com) |
| 📚 **Interactive Swagger UI** | [https://sitepulse-audit.onrender.com/docs](https://sitepulse-audit.onrender.com/docs) |
| 📖 **ReDoc Documentation** | [https://sitepulse-audit.onrender.com/redoc](https://sitepulse-audit.onrender.com/redoc) |
| 🩺 **System Health Check** | [https://sitepulse-audit.onrender.com/api/v1/health](https://sitepulse-audit.onrender.com/api/v1/health) |

---

## ⚡ Core Features

- **Asynchronous Audit Engine:** Non-blocking I/O operations via `httpx.AsyncClient` prevent thread starvation under concurrent crawls.
- **SSRF Attack Mitigation:** Pre-flight DNS resolution validates target hosts against loopback (`127.0.0.0/8`), private (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), link-local (`169.254.0.0/16`), and multicast IP blocks before sending requests.
- **DOM & Technical SEO Extraction:** Analyzes HTTP status, SSL validation, response latency, title tags, meta descriptions, heading hierarchies (`h1`/`h2`), link totals, image alt attributes, and OpenGraph tags.
- **Configurable TTL Caching:** Integrated caching layer prevents duplicate outbound crawls for identical URLs within a configurable time window.
- **IP-Based Rate Limiting:** Enforces request quotas via `slowapi` to protect against client abuse.
- **Distributed Request Tracing:** Injects unique `X-Request-ID` and `X-Response-Time-ms` headers across every request and response lifecycle.
- **Automated CI/CD:** GitHub Actions test pipeline verifies endpoint stability on every push and pull request.

---

## 📖 API Contract

### 1. Health & Attribution
`GET /api/v1/health`

**Response (`200 OK`):**
```json
{
  "status": "healthy",
  "service": "SitePulse",
  "version": "1.0.0",
  "attribution": "Built for Digital Heroes Training Task ([https://digitalheroesco.com](https://digitalheroesco.com))"
}

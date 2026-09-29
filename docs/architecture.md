# SitePulse — System Architecture & High-Scale Design (Task B)

## 1. System Overview
SitePulse is an asynchronous website auditing engine built with FastAPI. It performs network latency profiling, SSRF security validation, and DOM metadata extraction.

---

## 2. Scaling to 10,000 Audits / Day with 500 Concurrent Spikes

To support burst loads of 500 concurrent audits without exhausting server resources or triggering remote rate limits, the architecture evolves from synchronous request processing to an asynchronous producer-consumer queue pattern.

### Architecture Diagram
+----------------------+
                    |   Cloudflare / CDN   | (DDoS protection, Edge Rate Limiting)
                    +-----------+----------+
                                |
                                v
                    +----------------------+
                    | Application Load     |
                    | Balancer (ALB)       |
                    +-----------+----------+
                                |
             +------------------+------------------+
             |                                     |
             v                                     v
   +--------------------+                +--------------------+
   | SitePulse API Node |                | SitePulse API Node |
   | (FastAPI Worker 1) |                | (FastAPI Worker 2) |
   +---------+----------+                +---------+----------+
             |                                     |
             +------------------+------------------+
                                | Enqueue Task
                                v
                    +----------------------+
                    |    Redis / Celery    | (Audit Task Queue)
                    +-----------+----------+
                                |
             +------------------+------------------+
             | Fetch Job                           | Fetch Job
             v                                     v
   +--------------------+                +--------------------+
   | Worker Pod (Scraper|                | Worker Pod (Scraper|
   | + Headless Browser)|                | + Headless Browser)|
   +---------+----------+                +---------+----------+
             | Store Result                        | Store Result
             +------------------+------------------+
                                |
                                v
   +-----------------------------------------------+
   |             PostgreSQL + Redis Cache          |
   |  (Audit History, TTL Cache, State Retention)  |
   +-----------------------------------------------+
   ---

## 3. Core Architectural Components

### A. Rate Limiting & Queue Decoupling
- **Ingress Rate Limiting:** Fixed-window and leaky-bucket algorithms via Redis rate limiting per client IP to prevent abuse.
- **Asynchronous Task Queue:** Heavy scraping tasks are offloaded to **Celery + Redis**. When 500 requests arrive simultaneously, the API immediately returns `202 Accepted` with a `job_id`, queuing the execution to prevent HTTP connection timeouts.

### B. Database & State Storage
- **Primary Database:** **PostgreSQL** stores audit history, status logs, and domain metrics using indexed URL lookups.
- **Caching Layer:** **Redis** with a 15-minute TTL on audited domains eliminates redundant crawls for identical URLs.

### C. Worker Pool & Concurrency Throttling
- Asynchronous workers use an outbound connection pool with a maximum concurrency limit per target domain (to prevent accidental DoS against audited sites).

### D. Observability & Monitoring
- **Prometheus & Grafana:** Track scrape latency ($p_{50}$, $p_{95}$, $p_{99}$), HTTP error rates (4xx/5xx), and queue lag.
- **Structured JSON Logging:** Requests are annotated with an `X-Request-ID` across all distributed services.

### E. Failure Handling & Circuit Breaking
- **SSRF Guard:** IP resolution check blocks all loopback, private RFC-1918, link-local, and reserved IP ranges.
- **Circuit Breaker:** Automatic backoff when target domains consistently return `429 Too Many Requests` or `5xx Server Error`.
- **Target Timeout Enforcement:** Hard socket timeout set to 10 seconds.

### F. Rollback & Deployment Strategy
- **Blue-Green / Canary Deployments:** Deploy new images to a secondary worker pool; route 10% of traffic to monitor error rates before 100% rollout.
- **Database Migrations:** Schema migrations run backwards-compatible changes (`expand-contract` pattern) so rollbacks require zero downtime.
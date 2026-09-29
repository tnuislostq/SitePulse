from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SitePulse"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Request & Audit Settings
    DEFAULT_TIMEOUT_SECONDS: float = 10.0
    MAX_REDIRECTS: int = 3
    USER_AGENT: str = "SitePulse-Audit-Bot/1.0 (+https://digitalheroesco.com)"
    
    # Rate Limiting & Caching
    RATE_LIMIT_PER_MINUTE: str = "60/minute"
    CACHE_TTL_SECONDS: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

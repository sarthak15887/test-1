from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    APP_NAME: str = "Nexus Research OS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # Database - PostgreSQL
    DATABASE_URL: str = "postgresql+asyncpg://nexus:nexus_password@localhost:5432/nexus_research"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Vector Database - Qdrant
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_PREFIX: str = "nexus_"
    
    # Graph Database - Neo4j
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "neo4j_password"
    NEO4J_DATABASE: str = "neo4j"
    
    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  # 1 hour
    
    # Message Queue - RabbitMQ
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # OAuth2 Providers (optional)
    OAUTH2_PROVIDERS: Optional[List[str]] = None
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    
    # LLM Configuration
    DEFAULT_LLM_PROVIDER: str = "openai"
    DEFAULT_LLM_MODEL: str = "gpt-4o"
    LITELM_MASTER_KEY: Optional[str] = None
    
    # Model-specific configurations
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    
    # Agent Configuration
    MAX_AGENT_ITERATIONS: int = 10
    AGENT_TIMEOUT_SECONDS: int = 300
    ENABLE_AGENT_LOGGING: bool = True
    
    # Sandbox Configuration
    SANDBOX_ENABLED: bool = True
    SANDBOX_TYPE: str = "docker"  # docker, firecracker, local (dev only)
    SANDBOX_TIMEOUT_SECONDS: int = 120
    SANDBOX_MEMORY_LIMIT: str = "512m"
    SANDBOX_CPU_LIMIT: float = 1.0
    
    # File Storage
    STORAGE_TYPE: str = "local"  # local, s3, gcs
    STORAGE_PATH: str = "/tmp/nexus_storage"
    AWS_S3_BUCKET: Optional[str] = None
    AWS_REGION: Optional[str] = None
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json, console
    ENABLE_OTEL: bool = False
    OTEL_EXPORTER_ENDPOINT: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10
    
    # Multi-tenancy
    ENABLE_MULTI_TENANCY: bool = True
    DEFAULT_QUOTA_DAILY_TOKENS: int = 100000
    DEFAULT_QUOTA_MONTHLY_RUNS: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://storeforge:storeforge123@localhost:5432/storeforge"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # API Keys (optional for testing)
    OPENAI_API_KEY: str = "test-openai-key"
    LEONARDO_API_KEY: str = "test-leonardo-key"
    SHOPIFY_API_SECRET: str = "test-shopify-secret"
    
    # AWS S3 (optional for testing)
    AWS_ACCESS_KEY_ID: str = "test-aws-key"
    AWS_SECRET_ACCESS_KEY: str = "test-aws-secret"
    AWS_S3_BUCKET: str = "test-bucket"
    AWS_REGION: str = "us-east-1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Stripe
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # App Settings
    PROJECT_NAME: str = "StoreForge AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",
        "https://localhost:3000",
        "http://localhost:8000",
        "https://localhost:8000",
    ]
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
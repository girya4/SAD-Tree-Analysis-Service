import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:password@db:5432/image_processing"
    postgres_db: str = "image_processing"
    postgres_user: str = "postgres"
    postgres_password: str = "password"
    
    # Redis
    redis_url: str = "redis://redis:6379/0"
    
    # Application
    secret_key: str = "your-secret-key-here-change-in-production"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # File uploads
    upload_dir: str = "uploads"
    max_file_size: int = 10485760  # 10MB
    allowed_extensions: str = "jpg,jpeg,png,gif,bmp"
    
    # Cookie settings
    cookie_name: str = "user_session"
    cookie_max_age: int = 86400  # 24 hours
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

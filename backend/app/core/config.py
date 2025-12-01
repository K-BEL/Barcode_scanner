"""Configuration management using environment variables."""
import os
from pathlib import Path
from typing import Optional, List

# Try to load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Barcode Scanner API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database - MySQL Configuration
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = Field(..., alias="DB_USERNAME")
    DB_PASSWORD: str 
    DB_NAME: str = Field(..., alias="DB_DATABASE")
    DB_CHARSET: str = "utf8mb4"
    DB_CONNECTION: Optional[str] = None  # Optional, for compatibility
    DB_POOL_SIZE: int = Field(default=10, ge=1, le=100, description="Database connection pool size")
    
    # Database URL (constructed from above, or override with full URL)
    DATABASE_URL: Optional[str] = None
    
    # File paths (relative to project root) - Only for bills storage
    BILLS_DIR: str = "Bills"
    
    # Barcode Scanner
    SCANNER_TIMEOUT: int = 30  # seconds
    CAMERA_INDEX: int = 0
    
    # API
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    
    # Frontend
    FRONTEND_BASE_URL: str = "http://127.0.0.1:8000"
    ALLOWED_ORIGINS: str = Field(
        default="",
        description="Comma-separated list of allowed CORS origins. Leave empty for development (allows all). In production, specify exact origins."
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        populate_by_name = True  # Allow both field name and alias
    
    @property
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent
    
    @property
    def bills_path(self) -> Path:
        """Get the bills directory path."""
        path = self.project_root / self.BILLS_DIR
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def cors_origins(self) -> List[str]:
        """
        Get list of allowed CORS origins.
        
        Security: In production (DEBUG=False), wildcard is not allowed.
        In development (DEBUG=True), if ALLOWED_ORIGINS is empty or "*", allows all origins.
        """
        # In production, never allow wildcard
        if not self.DEBUG:
            if not self.ALLOWED_ORIGINS or self.ALLOWED_ORIGINS == "*":
                # In production, default to frontend URL if not specified
                return [self.FRONTEND_BASE_URL]
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
        
        # In development, allow wildcard if explicitly set or if empty
        if not self.ALLOWED_ORIGINS or self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


# Global settings instance
settings = Settings()


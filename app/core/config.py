"""Configuration management using environment variables."""
import os
from pathlib import Path
from typing import Optional

# Try to load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Barcode Scanner API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database - MySQL Configuration
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "barcode_scanner"
    DB_CHARSET: str = "utf8mb4"
    
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
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
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


# Global settings instance
settings = Settings()


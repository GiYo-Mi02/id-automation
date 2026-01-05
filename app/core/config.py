"""
Configuration Management Module
===============================
Centralized settings using Pydantic BaseSettings with environment variable support.
Eliminates hardcoded credentials and magic numbers throughout the codebase.

Security Fixes Applied:
- [P0] Removed hardcoded database credentials
- [P0] Configurable CORS origins (no more wildcard)
- [P1] Centralized path configuration
"""

import os
from pathlib import Path
from functools import lru_cache
from typing import List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class DatabaseSettings(BaseSettings):
    """Database configuration with secure defaults."""
    
    host: str = Field(default="localhost", alias="DB_HOST")
    port: int = Field(default=3306, alias="DB_PORT")
    user: str = Field(default="school_id_user", alias="DB_USER")  # No more root default
    password: str = Field(default="", alias="DB_PASSWORD")
    database: str = Field(default="school_id_system", alias="DB_NAME")
    pool_size: int = Field(default=5, alias="DB_POOL_SIZE")
    pool_name: str = "school_id_pool"
    
    @field_validator("password")
    @classmethod
    def password_must_not_be_empty_in_production(cls, v: str) -> str:
        """Warn if password is empty (but don't block for dev environments)."""
        if not v and os.getenv("ENVIRONMENT", "development") == "production":
            raise ValueError("DB_PASSWORD must be set in production environment")
        return v
    
    @property
    def connection_config(self) -> dict:
        """Return dict suitable for mysql.connector."""
        return {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
            "database": self.database,
        }

    class Config:
        env_file = ".env"
        extra = "ignore"


class SecuritySettings(BaseSettings):
    """Security configuration - API keys, CORS, rate limiting."""
    
    # API Key Authentication
    api_key: str = Field(default="", alias="API_KEY")
    api_key_header: str = "X-API-Key"
    
    # CORS Configuration - NO MORE WILDCARDS
    cors_origins: Union[str, List[str]] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"],
        alias="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_allow_headers: List[str] = ["*"]
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, alias="RATE_LIMIT_REQUESTS")
    rate_limit_window_seconds: int = Field(default=60, alias="RATE_LIMIT_WINDOW")
    
    # File Upload Security
    max_upload_size_mb: int = Field(default=10, alias="MAX_UPLOAD_SIZE_MB")
    allowed_image_types: List[str] = ["image/png", "image/jpeg", "image/jpg"]
    
    @field_validator("api_key")
    @classmethod
    def api_key_required_in_production(cls, v: str) -> str:
        """Enforce API key in production."""
        env = os.getenv("ENVIRONMENT", "development")
        if not v and env == "production":
            raise ValueError("API_KEY must be set in production environment")
        return v
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    class Config:
        env_file = ".env"
        extra = "ignore"


class PathSettings(BaseSettings):
    """File system paths - eliminates magic strings throughout codebase."""
    
    base_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent)
    
    # Data directories
    data_dir: Optional[Path] = Field(default=None, alias="DATA_DIR")
    input_dir: Optional[Path] = Field(default=None, alias="INPUT_DIR")
    output_dir: Optional[Path] = Field(default=None, alias="OUTPUT_DIR")
    template_dir: Optional[Path] = Field(default=None, alias="TEMPLATE_DIR")
    models_dir: Optional[Path] = Field(default=None, alias="MODELS_DIR")
    print_sheets_dir: Optional[Path] = Field(default=None, alias="PRINT_SHEETS_DIR")
    
    # Configuration files
    layout_file: Optional[Path] = Field(default=None, alias="LAYOUT_FILE")
    settings_file: Optional[Path] = Field(default=None, alias="SETTINGS_FILE")
    
    def model_post_init(self, __context) -> None:
        """Set defaults relative to base_dir after initialization."""
        if self.data_dir is None:
            self.data_dir = self.base_dir / "data"
        if self.input_dir is None:
            self.input_dir = self.data_dir / "input"
        if self.output_dir is None:
            self.output_dir = self.data_dir / "output"
        if self.template_dir is None:
            self.template_dir = self.data_dir / "Templates"
        if self.models_dir is None:
            self.models_dir = self.data_dir / "models"
        if self.print_sheets_dir is None:
            self.print_sheets_dir = self.data_dir / "Print_Sheets"
        if self.layout_file is None:
            self.layout_file = self.data_dir / "layout.json"
        if self.settings_file is None:
            self.settings_file = self.data_dir / "settings.json"
    
    def ensure_directories(self) -> None:
        """Create all required directories if they don't exist."""
        directories = [
            self.data_dir,
            self.input_dir,
            self.output_dir,
            self.template_dir,
            self.models_dir,
            self.print_sheets_dir,
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    class Config:
        extra = "ignore"


class ImageProcessingSettings(BaseSettings):
    """Image processing configuration."""
    
    card_width: int = Field(default=591, alias="CARD_WIDTH")
    card_height: int = Field(default=1004, alias="CARD_HEIGHT")
    
    # AI Enhancement settings
    enable_face_restoration: bool = Field(default=True, alias="ENABLE_FACE_RESTORATION")
    enable_hair_cleanup: bool = Field(default=True, alias="ENABLE_HAIR_CLEANUP")
    enable_background_removal: bool = Field(default=True, alias="ENABLE_BG_REMOVAL")
    smooth_strength: int = Field(default=5, ge=1, le=10, alias="SMOOTH_STRENGTH")
    
    # GFPGAN Model
    gfpgan_model_name: str = "GFPGANv1.4.pth"
    
    @property
    def card_size(self) -> tuple:
        return (self.card_width, self.card_height)

    class Config:
        env_file = ".env"
        extra = "ignore"


class Settings(BaseSettings):
    """
    Master Settings Class
    =====================
    Aggregates all configuration sections. Use get_settings() for cached access.
    
    Usage:
        from app.core.config import get_settings
        settings = get_settings()
        print(settings.database.host)
        print(settings.security.cors_origins)
    """
    
    # Environment
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")
    app_name: str = "School ID Automation System"
    app_version: str = "2.0.0"
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # Sub-configurations
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    paths: PathSettings = Field(default_factory=PathSettings)
    image_processing: ImageProcessingSettings = Field(default_factory=ImageProcessingSettings)
    
    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings factory.
    
    Returns the same Settings instance throughout the application lifecycle.
    Use dependency injection in FastAPI routes:
    
        @app.get("/example")
        def example(settings: Settings = Depends(get_settings)):
            return {"db_host": settings.database.host}
    """
    return Settings()


# Legacy CONFIG dict for backwards compatibility during migration
# TODO: Remove after all modules are updated to use get_settings()
def get_legacy_config() -> dict:
    """
    Provides backwards-compatible CONFIG dict.
    
    DEPRECATED: Use get_settings() instead.
    This exists only to support gradual migration of existing code.
    """
    settings = get_settings()
    return {
        "INPUT_FOLDER": str(settings.paths.input_folder),
        "OUTPUT_FOLDER": str(settings.paths.output_folder),
        "TEMPLATE_FOLDER": str(settings.paths.template_folder),
        "LAYOUT_FILE": str(settings.paths.layout_file),
        "SETTINGS_FILE": str(settings.paths.settings_file),
        "CARD_SIZE": settings.image_processing.card_size,
    }


# Initialize and validate on import
_settings = get_settings()
_settings.paths.ensure_directories()

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    app_tag: str = ""
    version_tag: str = ""
    log_level: str = "INFO"
    database_url: str = "sqlite:///./app.db"
    cors_origins: str = "*"
    omop_database_url: str | None = None
    show_fhirsheets_logs: bool = False
    enable_run_logs: bool = False
    iteration_limit: int = 100 # Max number of iterations for event generation.
    root_path: str | None = None
    force_reseed: bool = False

    @property
    def cors_origins_list(self) -> list[str]:
        """Convert comma-separated string to list"""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore" 
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
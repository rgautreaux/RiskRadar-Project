from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR.parent / ".env"),
        env_file_encoding="utf-8",
    )

    # Database
    DATABASE_URL: str = ""
    DB_PATH: str = str(BASE_DIR / "riskradar.db")

    # --- JWT Authentication ---
    # IMPORTANT: Change JWT_SECRET_KEY in your .env file before production!
    JWT_SECRET_KEY: str = "CHANGE-ME-set-a-real-secret-in-dotenv"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --- LLM ---
    LLM_API_KEY: str = ""
    LLM_PROVIDER: str = ""
    LLM_MODEL: str = ""
    LLM_MAX_TOKENS: int = 2048

    # --- Scraper API Keys ---
    AIRNOW_API_KEY: str = ""
    NASA_FIRMS_MAP_KEY: str = ""
    FIRECRAWL_API_KEY: str = ""
    OpenAQ_API_KEY: str = ""

    # --- App Defaults ---
    DEFAULT_ZIP_CODE: str = "90001"
    DEFAULT_LAT: float = 34.0522
    DEFAULT_LON: float = -118.2437
    SCRAPE_INTERVAL_MINUTES: int = 30
    RETENTION_ENABLED: bool = False
    RETENTION_DRY_RUN: bool = True
    RETENTION_BATCH_SIZE: int = 500
    RETENTION_MAX_ROWS_PER_RUN: int = 5000
    RETENTION_ALERTS_DAYS: int = 365
    RETENTION_SUMMARIES_DAYS: int = 365
    RETENTION_SCRAPE_LOG_DAYS: int = 90
    RETENTION_NIGHTLY_HOUR_UTC: int = 3
    RETENTION_WEEKLY_DAY_UTC: str = "sun"
    RETENTION_WEEKLY_HOUR_UTC: int = 4
    NWS_USER_AGENT: str = "RiskRadar/1.0 (school-project)"
    SOURCES_CONFIG_PATH: str = str(BASE_DIR / "config" / "sources.yaml")

settings = Settings()

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
    CORS_ALLOWED_ORIGINS: str = "*"

    # --- JWT Authentication ---
    # IMPORTANT: Change JWT_SECRET_KEY in your .env file before production!
    JWT_SECRET_KEY: str = "CHANGE-ME-set-a-real-secret-in-dotenv"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --- LLM (OpenRouter) ---
    OPENROUTER_API_KEY: str = ""
    LLM_API_KEY: str = ""
    LLM_PROVIDER: str = "openrouter"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_MODEL_GUEST: str = "gpt-4o-mini"
    LLM_MODEL_PREMIUM: str = "gpt-4o"
    LLM_MAX_TOKENS: int = 4000


    # --- Scraper API Keys ---
    AIRNOW_API_KEY: str = ""
    NASA_FIRMS_MAP_KEY: str = ""
    FIRECRAWL_API_KEY: str = ""
    OpenAQ_API_KEY: str = ""

    # --- Notifications ---
    NOTIFICATION_PROVIDER: str = "noop"
    NOTIFICATION_DELIVERY_ENABLED: bool = False
    NOTIFICATION_TIMEOUT_SECONDS: float = 10.0
    EXPO_PUSH_URL: str = "https://exp.host/--/api/v2/push/send"
    EXPO_ACCESS_TOKEN: str = ""
    FCM_PROJECT_ID: str = ""
    FCM_SERVER_KEY: str = ""

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

    # --- Normalization rollout flags ---
    SUMMARIES_USE_JUNCTION_TABLE: bool = True
    USERS_USE_PREFERENCE_JUNCTION_TABLE: bool = True
    NORMALIZATION_DUAL_WRITE_LEGACY_JSON: bool = True
    GEO_USE_ZIP_LOOKUP: bool = True

    def resolved_llm_api_key(self) -> str:
        return self.LLM_API_KEY.strip() or self.OPENROUTER_API_KEY.strip()

    def resolved_llm_provider(self) -> str:
        return self.LLM_PROVIDER.strip().lower()

settings = Settings()

from pathlib import Path

from pydantic_settings import BaseSettings

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "SME CyberShield API"
    environment: str = "local"

    database_url: str = f"sqlite:///{BACKEND_DIR / 'sme_cybershield.db'}"

    response_mode: str = "dry_run"

    anomaly_threshold: float = 0.65
    feature_window_minutes: int = 5

    timezone: str = "Asia/Ho_Chi_Minh"
    default_language: str = "vi"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
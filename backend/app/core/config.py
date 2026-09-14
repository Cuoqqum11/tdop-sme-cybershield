from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "SME CyberShield API"
    environment: str = "local"

    database_url: str = "sqlite:///./sme_cybershield.db"

    response_mode: str = "dry_run"
    anomaly_threshold: float = 0.65

    timezone: str = "Asia/Ho_Chi_Minh"
    default_language: str = "vi"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Incident Intelligence"
    environment: str = "development"

    database_url: str = ""
    secret_key: str = Field(min_length=32)                                                                              # Authentication and JWT configuration.
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    llm_provider: str = ""
    llm_api_key: str = ""
    llm_model: str = ""

    upload_dir: str = "data/uploads"
    max_upload_size_mb: int = 10

    anomaly_threshold: float = 0.8

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
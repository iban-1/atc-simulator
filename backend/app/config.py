from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    cors_origin: str = "http://localhost:5173"
    tick_interval_s: float = 1.0

    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/logfast"
    secret_key: str = "dev-secret-change-in-production"
    github_client_id: str = ""
    github_client_secret: str = ""
    github_app_id: str = ""
    github_app_private_key_path: str = ""
    github_app_installation_id: str = ""
    ai_api_key: str = ""
    ai_base_url: str = "https://api.deepseek.com/v1"
    ai_model: str = "deepseek-v4-flash"  # DeepSeek V4 Flash (284B, 13B active, $0.14/$0.28 per M tokens)
    frontend_url: str = "http://localhost:5173"
    api_base_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

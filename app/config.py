from functools import lru_cache

from pydantic import BaseModel, BaseSettings, Field


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    openai_api_key: str | None = Field(default=None, env="OPENAI_API_KEY")
    maxcompute_access_id: str | None = Field(default=None, env="MAXCOMPUTE_ACCESS_ID")
    maxcompute_access_key: str | None = Field(default=None, env="MAXCOMPUTE_ACCESS_KEY")
    maxcompute_endpoint: str | None = Field(default=None, env="MAXCOMPUTE_ENDPOINT")
    maxcompute_project: str | None = Field(default=None, env="MAXCOMPUTE_PROJECT")
    ads_table: str | None = Field(default=None, env="ADS_TABLE")
    openai_model: str = Field("gpt-4o-mini", env="OPENAI_MODEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class ReportRequest(BaseModel):
    """Request payload for generating a report from ADS data."""

    date_from: str
    date_to: str
    metrics: list[str]
    dimensions: list[str]
    limit: int = 100


@lru_cache
def load_settings() -> Settings:
    """Load settings once, leveraging .env when present."""

    return Settings()

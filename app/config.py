from pydantic import BaseModel, BaseSettings, Field


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    maxcompute_access_id: str = Field(..., env="MAXCOMPUTE_ACCESS_ID")
    maxcompute_access_key: str = Field(..., env="MAXCOMPUTE_ACCESS_KEY")
    maxcompute_endpoint: str = Field(..., env="MAXCOMPUTE_ENDPOINT")
    maxcompute_project: str = Field(..., env="MAXCOMPUTE_PROJECT")
    ads_table: str = Field(..., env="ADS_TABLE")
    openai_model: str = Field("gpt-4o-mini", env="OPENAI_MODEL")


class ReportRequest(BaseModel):
    """Request payload for generating a report from ADS data."""

    date_from: str
    date_to: str
    metrics: list[str]
    dimensions: list[str]
    limit: int = 100


settings = Settings()

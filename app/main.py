from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from .config import ReportRequest, Settings, load_settings
from .reporting import ReportService

app = FastAPI(title="ADS Ask GPT", description="生成基于MaxCompute ADS数据的智能报表")

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


REQUIRED_ENV_FIELDS = (
    "openai_api_key",
    "maxcompute_access_id",
    "maxcompute_access_key",
    "maxcompute_endpoint",
    "maxcompute_project",
    "ads_table",
)


def get_settings() -> Settings:
    try:
        config = load_settings()
    except ValidationError as exc:  # pragma: no cover - defensive guard
        missing_fields = ", ".join(err.get("loc", ["?"])[0] for err in exc.errors())
        raise HTTPException(status_code=500, detail=f"Settings validation error: {missing_fields}")

    missing_required = [field for field in REQUIRED_ENV_FIELDS if not getattr(config, field)]
    if missing_required:
        raise HTTPException(
            status_code=500,
            detail=f"Missing required environment variables: {', '.join(missing_required)}",
        )

    return config


def get_report_service(conf: Settings = Depends(get_settings)) -> ReportService:
    try:
        return ReportService(conf)
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/", response_class=HTMLResponse)
def landing() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/report")
def create_report(request: ReportRequest, service: ReportService = Depends(get_report_service)) -> dict:
    return service.generate_report(request)

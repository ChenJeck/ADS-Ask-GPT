from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from .config import ReportRequest, Settings, settings
from .reporting import ReportService

app = FastAPI(title="ADS Ask GPT", description="生成基于MaxCompute ADS数据的智能报表")

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


def get_settings() -> Settings:
    return settings


def get_report_service(conf: Settings = Depends(get_settings)) -> ReportService:
    return ReportService(conf)


@app.get("/", response_class=HTMLResponse)
def landing() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/report")
def create_report(request: ReportRequest, service: ReportService = Depends(get_report_service)) -> dict:
    return service.generate_report(request)

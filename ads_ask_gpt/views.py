from __future__ import annotations

import json
from pathlib import Path

from django.http import FileResponse, HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from pydantic import ValidationError

from app.config import ReportRequest, Settings, load_settings
from app.reporting import ReportService

REQUIRED_ENV_FIELDS = (
    "openai_api_key",
    "maxcompute_access_id",
    "maxcompute_access_key",
    "maxcompute_endpoint",
    "maxcompute_project",
    "ads_table",
)

static_dir = Path(__file__).resolve().parent.parent / "app" / "static"


def _get_settings() -> Settings:
    try:
        config = load_settings()
    except ValidationError as exc:  # pragma: no cover - defensive guard
        missing_fields = ", ".join(err.get("loc", ["?"])[0] for err in exc.errors())
        raise RuntimeError(f"Settings validation error: {missing_fields}")

    missing_required = [field for field in REQUIRED_ENV_FIELDS if not getattr(config, field)]
    if missing_required:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing_required)}")

    return config


def _get_report_service() -> ReportService:
    settings = _get_settings()
    try:
        return ReportService(settings)
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise RuntimeError(str(exc))


@require_GET
def index(request: HttpRequest) -> HttpResponse:
    return FileResponse(static_dir / "index.html")


@require_GET
def health_check(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"status": "ok"})


@csrf_exempt
@require_POST
def report(request: HttpRequest) -> JsonResponse:
    try:
        payload = json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON payload"}, status=400)

    try:
        report_request = ReportRequest(**payload)
    except ValidationError as exc:
        return JsonResponse({"detail": exc.errors()}, status=422)

    try:
        service = _get_report_service()
        result = service.generate_report(report_request)
    except RuntimeError as exc:
        return JsonResponse({"detail": str(exc)}, status=500)

    return JsonResponse(result, safe=False)

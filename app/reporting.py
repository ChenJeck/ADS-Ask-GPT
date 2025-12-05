from typing import Any

from .clients import ChatGPTClient, MaxComputeClient
from .config import ReportRequest, Settings


class ReportService:
    """Coordinates MaxCompute reads and ChatGPT report generation."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._data_client = MaxComputeClient(settings)
        self._llm_client = ChatGPTClient(settings)

    def generate_report(self, request: ReportRequest) -> dict[str, Any]:
        rows = self._data_client.fetch_ads_rows(
            request.metrics, request.dimensions, request.date_from, request.date_to, request.limit
        )
        report_text = self._llm_client.build_report(rows, request.metrics, request.dimensions)
        return {"rows": rows, "report": report_text}

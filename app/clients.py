from collections.abc import Sequence
from typing import Any

from openai import OpenAI
from pyodps import ODPS

from .config import Settings


class MaxComputeClient:
    """Thin wrapper around pyodps for querying ADS tables."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = ODPS(
            settings.maxcompute_access_id,
            settings.maxcompute_access_key,
            project=settings.maxcompute_project,
            endpoint=settings.maxcompute_endpoint,
        )

    def fetch_ads_rows(
        self, metrics: Sequence[str], dimensions: Sequence[str], date_from: str, date_to: str, limit: int
    ) -> list[dict[str, Any]]:
        columns = list(dimensions) + list(metrics)
        select_clause = ", ".join(columns)
        where_clause = f"dt BETWEEN '{date_from}' AND '{date_to}'"
        query = f"SELECT {select_clause} FROM {self._settings.ads_table} WHERE {where_clause} LIMIT {limit}"
        with self._client.execute_sql(query).open_reader() as reader:
            return [dict(zip(columns, row)) for row in reader]


class ChatGPTClient:
    """Helper for sending structured prompts to the OpenAI API."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = OpenAI(api_key=settings.openai_api_key)

    def build_report(self, data_rows: Sequence[dict[str, Any]], metrics: Sequence[str], dimensions: Sequence[str]) -> str:
        prompt = self._build_prompt(data_rows, metrics, dimensions)
        completion = self._client.responses.create(
            model=self._settings.openai_model,
            input=[{"role": "user", "content": prompt}],
        )
        return completion.output_text

    def _build_prompt(self, data_rows: Sequence[dict[str, Any]], metrics: Sequence[str], dimensions: Sequence[str]) -> str:
        return (
            "你是一个数据分析助手。\n"
            "基于以下的ADS宽表数据，生成一份包含关键洞察和建议的中文报表。\n"
            "请重点关注度量字段: "
            + ", ".join(metrics)
            + "，并按这些维度拆分: "
            + ", ".join(dimensions)
            + "。\n"
            "数据示例(JSON):\n"
            + str(list(data_rows))
        )

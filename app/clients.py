from collections.abc import Sequence
from typing import Any

from openai import OpenAI
from odps import ODPS

from .config import Settings


class MaxComputeClient:
    """Thin wrapper around pyodps for querying ADS tables."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = None
        if not settings.demo_mode:
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
        if self._client is None:
            return self._build_sample_rows(columns, limit)

        select_clause = ", ".join(columns)
        where_clause = f"dt BETWEEN '{date_from}' AND '{date_to}'"
        query = f"SELECT {select_clause} FROM {self._settings.ads_table} WHERE {where_clause} LIMIT {limit}"
        with self._client.execute_sql(query).open_reader() as reader:
            return [dict(zip(columns, row)) for row in reader]

    @staticmethod
    def _build_sample_rows(columns: list[str], limit: int) -> list[dict[str, Any]]:
        demo_rows = [
            {**{col: "2024-06-01" for col in columns if col.lower().startswith("dt")}, "region": "华东", "pv": 1200, "uv": 800},
            {**{col: "2024-06-02" for col in columns if col.lower().startswith("dt")}, "region": "华北", "pv": 950, "uv": 640},
            {**{col: "2024-06-03" for col in columns if col.lower().startswith("dt")}, "region": "华南", "pv": 1430, "uv": 910},
        ]
        padded_rows = (demo_rows * ((limit // len(demo_rows)) + 1))[:limit]
        return [
            {**{col: row.get(col, row.get(col.lower(), "")) for col in columns}, **{k: v for k, v in row.items() if k not in columns}}
            for row in padded_rows
        ]


class ChatGPTClient:
    """Helper for sending structured prompts to the OpenAI API."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = None
        if not settings.demo_mode:
            self._client = OpenAI(api_key=settings.openai_api_key)

    def build_report(self, data_rows: Sequence[dict[str, Any]], metrics: Sequence[str], dimensions: Sequence[str]) -> str:
        if self._client is None:
            return self._build_demo_report(data_rows, metrics, dimensions)

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

    @staticmethod
    def _build_demo_report(
        data_rows: Sequence[dict[str, Any]], metrics: Sequence[str], dimensions: Sequence[str]
    ) -> str:
        metrics_display = ", ".join(metrics) if metrics else "(未选择)"
        dimensions_display = ", ".join(dimensions) if dimensions else "(未选择)"
        return (
            "演示模式：以下为基于示例数据生成的预览。\n"
            f"聚焦指标：{metrics_display}，按维度：{dimensions_display}。\n"
            "整体来看，PV 与 UV 在华南地区表现最佳，其次是华东。\n"
            "建议：在流量表现较弱的区域投放更多促活资源，并结合转化率优化落地页体验。"
        )

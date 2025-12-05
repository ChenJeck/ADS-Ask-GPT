# ADS-Ask-GPT

使用 FastAPI 构建的示例网站，提供 ChatGPT 与 MaxCompute (ADS) 集成的智能报表接口。

## 环境变量

在启动前准备以下配置：

- `OPENAI_API_KEY`：用于调用 ChatGPT 的密钥。
- `OPENAI_MODEL`：可选，默认 `gpt-4o-mini`。
- `MAXCOMPUTE_ACCESS_ID` 与 `MAXCOMPUTE_ACCESS_KEY`：MaxCompute 访问凭证。
- `MAXCOMPUTE_ENDPOINT`：MaxCompute Endpoint，例如 `http://service.odps.aliyun.com/api`。
- `MAXCOMPUTE_PROJECT`：目标项目名。
- `ADS_TABLE`：需要查询的 ADS 宽表名称。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API 调用示例

生成报表：

```bash
curl -X POST "http://localhost:8000/report" \ \
  -H "Content-Type: application/json" \ \
  -d '{
    "date_from": "2024-01-01",
    "date_to": "2024-01-07",
    "metrics": ["pv", "uv"],
    "dimensions": ["dt", "channel"],
    "limit": 50
  }'
```

健康检查：

```bash
curl http://localhost:8000/health
```

## 工作流程

1. 根据请求参数从 MaxCompute ADS 宽表拉取样本数据；
2. 将样本数据与维度/度量信息发送给 ChatGPT；
3. 返回包含原始样本与中文报表的 JSON 响应。

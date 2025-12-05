from fastapi import Depends, FastAPI
from fastapi.responses import HTMLResponse

from .config import ReportRequest, Settings, settings
from .reporting import ReportService

app = FastAPI(title="ADS Ask GPT", description="生成基于MaxCompute ADS数据的智能报表")


def get_settings() -> Settings:
    return settings


def get_report_service(conf: Settings = Depends(get_settings)) -> ReportService:
    return ReportService(conf)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/report")
def create_report(request: ReportRequest, service: ReportService = Depends(get_report_service)) -> dict:
    return service.generate_report(request)


@app.get("/", response_class=HTMLResponse)
def landing_page(conf: Settings = Depends(get_settings)) -> HTMLResponse:
    mode_label = "演示模式" if conf.demo_mode else "在线模式"
    return HTMLResponse(
        f"""
        <!DOCTYPE html>
        <html lang='zh-CN'>
        <head>
            <meta charset='UTF-8' />
            <meta name='viewport' content='width=device-width, initial-scale=1.0' />
            <title>ADS Ask GPT</title>
            <style>
                :root {{
                    --primary: #2563eb;
                    --bg: #f6f8fb;
                    --card: #ffffff;
                    --border: #e5e7eb;
                    --text: #111827;
                }}
                * {{ box-sizing: border-box; }}
                body {{ margin: 0; font-family: 'Inter', system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); }}
                .layout {{ display: grid; grid-template-columns: 260px 1fr; min-height: 100vh; }}
                aside {{ background: #0f172a; color: #e2e8f0; padding: 24px 20px; display: flex; flex-direction: column; gap: 24px; }}
                .brand {{ font-weight: 700; font-size: 18px; display: flex; align-items: center; gap: 10px; color: #fff; }}
                .brand span {{ display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; background: #1d4ed8; border-radius: 8px; }}
                .section-title {{ font-size: 12px; letter-spacing: 0.08em; color: #94a3b8; text-transform: uppercase; margin-bottom: 8px; }}
                .nav-group {{ display: flex; flex-direction: column; gap: 12px; }}
                .nav-item {{ padding: 10px 12px; border-radius: 10px; color: #e2e8f0; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); }}
                .nav-item strong {{ display: block; font-size: 14px; margin-bottom: 6px; }}
                .nav-item small {{ color: #cbd5e1; line-height: 1.5; }}
                main {{ padding: 28px; }}
                .panel {{ background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 24px; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05); margin-bottom: 18px; }}
                .panel h2 {{ margin: 0 0 10px; font-size: 18px; }}
                .panel p {{ margin: 0 0 16px; color: #4b5563; }}
                .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }}
                label {{ display: block; font-size: 13px; font-weight: 600; margin-bottom: 8px; color: #111827; }}
                input, textarea, select {{ width: 100%; padding: 12px; border-radius: 10px; border: 1px solid var(--border); background: #f9fafb; font-size: 14px; }}
                textarea {{ min-height: 110px; resize: vertical; }}
                .badge {{ display: inline-flex; align-items: center; gap: 6px; background: #e0f2fe; color: #075985; padding: 6px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; }}
                .actions {{ display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }}
                button {{ background: var(--primary); color: #fff; border: none; border-radius: 10px; padding: 12px 18px; font-size: 14px; cursor: pointer; box-shadow: 0 10px 20px rgba(37, 99, 235, 0.18); }}
                button.secondary {{ background: #e2e8f0; color: #0f172a; box-shadow: none; }}
                .output {{ background: #0b172a; color: #e2e8f0; border-radius: 12px; padding: 16px; border: 1px solid #1f2937; min-height: 140px; white-space: pre-wrap; }}
                .muted {{ color: #6b7280; font-size: 13px; }}
            </style>
        </head>
        <body>
            <div class="layout">
                <aside>
                    <div class="brand"><span>AI</span>ADS Ask GPT</div>
                    <div>
                        <div class="section-title">配置</div>
                        <div class="nav-group">
                            <div class="nav-item"><strong>API 密钥</strong><small>录入 OpenAI 及 MaxCompute 认证信息，或直接使用演示数据预览样式。</small></div>
                            <div class="nav-item"><strong>数据源</strong><small>选择或模拟 ADS 宽表字段，调整日期范围与行数限制。</small></div>
                            <div class="nav-item"><strong>报表样式</strong><small>选择度量、维度及描述方式，快速生成示例洞察。</small></div>
                        </div>
                    </div>
                    <div>
                        <div class="section-title">状态</div>
                        <div class="badge">当前：{mode_label}</div>
                        <p class="muted">未填写凭据时将自动切换到演示模式，使用内置示例数据渲染页面与报表。</p>
                    </div>
                </aside>
                <main>
                    <div class="panel">
                        <h2>API 与数据源配置</h2>
                        <p>在这里录入或修改连接信息，如果为空则自动走演示模式。</p>
                        <div class="grid">
                            <div>
                                <label>OpenAI API Key</label>
                                <input id="openaiKey" placeholder="可留空以使用演示报告" />
                            </div>
                            <div>
                                <label>MaxCompute Access ID</label>
                                <input id="accessId" placeholder="演示模式可留空" />
                            </div>
                            <div>
                                <label>MaxCompute Access Key</label>
                                <input id="accessKey" placeholder="演示模式可留空" />
                            </div>
                            <div>
                                <label>Project & Endpoint</label>
                                <input id="project" placeholder="project@service.aliyun.com" />
                            </div>
                            <div>
                                <label>ADS 宽表</label>
                                <input id="table" placeholder="ads_wide_table_name" />
                            </div>
                            <div>
                                <label>日期范围</label>
                                <input id="dateRange" value="2024-06-01 ~ 2024-06-03" />
                            </div>
                        </div>
                    </div>

                    <div class="panel">
                        <h2>报表选项</h2>
                        <p>选择度量、维度并预览示例数据生成的报告。</p>
                        <div class="grid">
                            <div>
                                <label>度量字段（逗号分隔）</label>
                                <input id="metrics" value="pv,uv" />
                            </div>
                            <div>
                                <label>维度字段（逗号分隔）</label>
                                <input id="dimensions" value="region" />
                            </div>
                            <div>
                                <label>行数限制</label>
                                <input id="limit" type="number" value="10" min="1" />
                            </div>
                            <div>
                                <label>备注</label>
                                <textarea id="notes" placeholder="例如：聚焦近三天地域表现"></textarea>
                            </div>
                        </div>
                        <div class="actions" style="margin-top: 16px;">
                            <button onclick="generate()">生成示例报表</button>
                            <button class="secondary" onclick="resetDemo()">恢复默认示例</button>
                            <span class="muted">不会调用真实接口，主要用于预览界面与样式。</span>
                        </div>
                    </div>

                    <div class="panel">
                        <h2>预览</h2>
                        <p>示例数据与报告将在下方展示。</p>
                        <div class="output" id="dataOutput">尚未生成数据</div>
                    </div>
                </main>
            </div>

            <script>
                function parseRange() {{
                    const raw = document.getElementById('dateRange').value || '';
                    const [from, to] = raw.split('~').map(v => v.trim());
                    return {{ date_from: from || '2024-06-01', date_to: to || '2024-06-03' }};
                }}

                async function generate() {{
                    const metrics = (document.getElementById('metrics').value || '').split(',').map(v => v.trim()).filter(Boolean);
                    const dimensions = (document.getElementById('dimensions').value || '').split(',').map(v => v.trim()).filter(Boolean);
                    const {{ date_from, date_to }} = parseRange();
                    const payload = {{
                        metrics,
                        dimensions,
                        date_from,
                        date_to,
                        limit: Number(document.getElementById('limit').value) || 10,
                    }};

                    const res = await fetch('/report', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify(payload),
                    }});
                    const data = await res.json();
                    const reportText = data.report || '演示模式：请填写配置以生成示例。';
                    const rows = JSON.stringify(data.rows, null, 2);
                    document.getElementById('dataOutput').textContent = `数据预览 (前 {payload.limit} 行)\n${rows}\n\n报告：\n${reportText}`;
                }}

                function resetDemo() {{
                    document.getElementById('metrics').value = 'pv,uv';
                    document.getElementById('dimensions').value = 'region';
                    document.getElementById('limit').value = 10;
                    document.getElementById('notes').value = '';
                    document.getElementById('dataOutput').textContent = '尚未生成数据';
                }}
            </script>
        </body>
        </html>
        """
    )

from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
import pandas as pd
from jinja2 import Template
import io
import base64
import matplotlib.pyplot as plt


TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset='utf-8' />
  <title>Survey Report - {{ dataset_id }}</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; }
    h1, h2 { color: #1b4965; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 24px; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background: #f3f6f9; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; }
    .card { border: 1px solid #eee; border-radius: 8px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .muted { color: #666; }
  </style>
</head>
<body>
  <h1>Automated Survey Report</h1>
  <p class='muted'>Dataset ID: {{ dataset_id }} | Rows: {{ row_count }} | Columns: {{ column_count }}</p>

  <h2>Sample Preview</h2>
  <table>
    <thead>
      <tr>
        {% for c in preview.columns %}<th>{{ c }}</th>{% endfor %}
      </tr>
    </thead>
    <tbody>
      {% for r in preview.rows %}
      <tr>{% for c in preview.columns %}<td>{{ r[c] }}</td>{% endfor %}</tr>
      {% endfor %}
    </tbody>
  </table>

  <h2>Numeric Distributions</h2>
  <div class='grid'>
    {% for item in charts %}
    <div class='card'>
      <h3>{{ item.column }}</h3>
      <img src="data:image/png;base64,{{ item.image }}" alt="{{ item.column }}" style="width:100%" />
    </div>
    {% endfor %}
  </div>

  <h2>Workflow Logs</h2>
  <ul>
    {% for log in logs %}
      <li>{{ log }}</li>
    {% endfor %}
  </ul>
</body>
</html>
"""


def _render_histogram_base64(series: pd.Series) -> str:
    plt.figure(figsize=(4, 3))
    series = pd.to_numeric(series, errors='coerce').dropna()
    if not len(series):
        series = pd.Series([0])
    plt.hist(series, bins=20, color="#3f8efc", alpha=0.8)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def generate_report_html(dataset_id: str, path: Path, meta: Dict[str, Any]) -> str:
    df = pd.read_csv(path)
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])][:6]
    charts = []
    for col in numeric_cols:
        img = _render_histogram_base64(df[col])
        charts.append({"column": col, "image": img})

    preview = {
        "columns": list(df.head(10).columns),
        "rows": df.head(10).to_dict(orient="records"),
    }
    template = Template(TEMPLATE)
    html = template.render(
        dataset_id=dataset_id,
        row_count=len(df),
        column_count=len(df.columns),
        preview=preview,
        charts=charts,
        logs=meta.get("logs", []),
    )
    return html
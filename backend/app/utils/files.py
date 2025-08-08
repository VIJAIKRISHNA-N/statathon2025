from __future__ import annotations
from fastapi import UploadFile
import pandas as pd
from pathlib import Path
import json
from typing import Dict, Any, Tuple


def save_upload_to_disk(file: UploadFile, dataset_dir: Path) -> Tuple[Path, pd.DataFrame]:
    suffix = Path(file.filename).suffix.lower()
    dest = dataset_dir / ("raw" + suffix)
    with open(dest, "wb") as f:
        f.write(file.file.read())
    if suffix in [".xls", ".xlsx"]:
        df = pd.read_excel(dest)
        csv_path = dataset_dir / "raw.csv"
        df.to_csv(csv_path, index=False)
        return csv_path, df
    elif suffix in [".csv", ".txt"]:
        df = pd.read_csv(dest)
        return dest, df
    else:
        raise ValueError("Unsupported file type. Please upload CSV or Excel.")


def load_dataframe_head(path: Path | str, n: int = 20) -> Dict[str, Any]:
    path = Path(path)
    df = pd.read_csv(path)
    head = df.head(n)
    return {
        "rows": head.to_dict(orient="records"),
        "columns": list(head.columns),
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
    }


META_FILE = "meta.json"


def read_metadata(dataset_dir: Path) -> Dict[str, Any] | None:
    path = dataset_dir / META_FILE
    if not path.exists():
        return None
    return json.loads(path.read_text())


def write_metadata(dataset_dir: Path, meta: Dict[str, Any]) -> None:
    path = dataset_dir / META_FILE
    path.write_text(json.dumps(meta, indent=2))
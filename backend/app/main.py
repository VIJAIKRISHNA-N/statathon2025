from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import uuid
from pathlib import Path

from .utils.files import save_upload_to_disk, load_dataframe_head, read_metadata, write_metadata
from .services.cleaning import CleaningConfig, run_cleaning
from .services.analysis import AnalysisConfig, run_analysis
from .services.report import generate_report_html

APP_ROOT = Path(__file__).resolve().parent
DATA_ROOT = APP_ROOT.parent / "data"
DATA_ROOT.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Survey Data Processing API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DatasetConfig(BaseModel):
    id_column: Optional[str] = None
    weight_column: Optional[str] = None
    numeric_columns: Optional[List[str]] = None
    categorical_columns: Optional[List[str]] = None


@app.post("/upload")
async def upload_dataset(file: UploadFile = File(...)) -> Dict:
    try:
        dataset_id = str(uuid.uuid4())
        dataset_dir = DATA_ROOT / dataset_id
        dataset_dir.mkdir(parents=True, exist_ok=True)
        saved_path, df = await save_upload_to_disk(file, dataset_dir)
        meta = {
            "dataset_id": dataset_id,
            "filename": file.filename,
            "raw_path": str(saved_path),
            "clean_path": None,
            "config": {},
            "logs": [],
            "columns": list(df.columns),
            "dtypes": {c: str(df[c].dtype) for c in df.columns},
        }
        write_metadata(dataset_dir, meta)
        preview = load_dataframe_head(saved_path)
        return {"dataset_id": dataset_id, "preview": preview, "columns": meta["columns"], "dtypes": meta["dtypes"]}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Upload failed: {exc}")


@app.get("/datasets/{dataset_id}/preview")
async def get_preview(dataset_id: str) -> Dict:
    dataset_dir = DATA_ROOT / dataset_id
    meta = read_metadata(dataset_dir)
    if not meta:
        raise HTTPException(status_code=404, detail="Dataset not found")
    path = meta.get("clean_path") or meta.get("raw_path")
    preview = load_dataframe_head(path)
    return {"dataset_id": dataset_id, "preview": preview}


@app.post("/datasets/{dataset_id}/config")
async def set_config(dataset_id: str, config: DatasetConfig) -> Dict:
    dataset_dir = DATA_ROOT / dataset_id
    meta = read_metadata(dataset_dir)
    if not meta:
        raise HTTPException(status_code=404, detail="Dataset not found")
    meta["config"] = config.dict()
    write_metadata(dataset_dir, meta)
    return {"ok": True, "config": meta["config"]}


@app.post("/datasets/{dataset_id}/clean")
async def clean_dataset(dataset_id: str, config: CleaningConfig) -> Dict:
    dataset_dir = DATA_ROOT / dataset_id
    meta = read_metadata(dataset_dir)
    if not meta:
        raise HTTPException(status_code=404, detail="Dataset not found")
    raw_path = Path(meta.get("clean_path") or meta.get("raw_path"))
    result = run_cleaning(raw_path, config)
    meta["clean_path"] = str(result.cleaned_path)
    meta.setdefault("logs", []).extend(result.logs)
    write_metadata(dataset_dir, meta)
    head = load_dataframe_head(result.cleaned_path)
    return {"ok": True, "preview": head, "logs": result.logs}


@app.post("/datasets/{dataset_id}/analyze")
async def analyze_dataset(dataset_id: str, config: AnalysisConfig) -> Dict:
    dataset_dir = DATA_ROOT / dataset_id
    meta = read_metadata(dataset_dir)
    if not meta:
        raise HTTPException(status_code=404, detail="Dataset not found")
    path = Path(meta.get("clean_path") or meta.get("raw_path"))
    analysis = run_analysis(path, config)
    return analysis


@app.get("/datasets/{dataset_id}/report", response_class=HTMLResponse)
async def get_report(dataset_id: str) -> HTMLResponse:
    dataset_dir = DATA_ROOT / dataset_id
    meta = read_metadata(dataset_dir)
    if not meta:
        raise HTTPException(status_code=404, detail="Dataset not found")
    path = Path(meta.get("clean_path") or meta.get("raw_path"))
    html = generate_report_html(dataset_id, path, meta)
    return HTMLResponse(content=html)


@app.get("/")
async def root():
    return {"status": "ok", "message": "Survey Data Processing API"}
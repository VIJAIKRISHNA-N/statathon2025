from __future__ import annotations
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pathlib import Path
import pandas as pd
import numpy as np


class AnalysisConfig(BaseModel):
    weight_column: Optional[str] = None
    numeric_columns: Optional[List[str]] = None
    categorical_columns: Optional[List[str]] = None
    confidence: float = 0.95


def _weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    total_w = np.sum(weights)
    if total_w == 0:
        return float("nan")
    return float(np.sum(values * weights) / total_w)


def _weighted_var(values: np.ndarray, weights: np.ndarray) -> float:
    # approximate population variance with weights
    average = _weighted_mean(values, weights)
    total_w = np.sum(weights)
    if total_w == 0:
        return float("nan")
    return float(np.sum(weights * (values - average) ** 2) / total_w)


def _moe_from_var(var: float, n_eff: float, confidence: float) -> float:
    if np.isnan(var) or n_eff <= 0:
        return float("nan")
    z = 1.96 if abs(confidence - 0.95) < 1e-6 else 1.96  # simplified
    se = np.sqrt(var / n_eff)
    return float(z * se)


def _effective_n(weights: np.ndarray) -> float:
    # Kish effective sample size
    if len(weights) == 0:
        return 0.0
    w = np.asarray(weights, dtype=float)
    if np.all(w == 0):
        return 0.0
    return (np.sum(w) ** 2) / np.sum(w ** 2)


def run_analysis(path: Path, config: AnalysisConfig) -> Dict[str, Any]:
    df = pd.read_csv(path)

    numeric_cols = config.numeric_columns or [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    categorical_cols = config.categorical_columns or [c for c in df.columns if pd.api.types.is_string_dtype(df[c]) or pd.api.types.is_categorical_dtype(df[c])]
    weight_col = config.weight_column if config.weight_column in df.columns else None

    weights = df[weight_col].fillna(0).to_numpy(dtype=float) if weight_col else np.ones(len(df))
    n_eff = _effective_n(weights)

    numeric_summary = {}
    for col in numeric_cols:
        values = pd.to_numeric(df[col], errors='coerce').to_numpy(dtype=float)
        mask = ~np.isnan(values)
        v = values[mask]
        w = weights[mask]
        uw_mean = float(np.nanmean(v)) if len(v) else float("nan")
        uw_var = float(np.nanvar(v)) if len(v) else float("nan")
        uw_moe = _moe_from_var(uw_var, len(v), config.confidence)
        if len(v) and np.sum(w) > 0:
            w_mean = _weighted_mean(v, w)
            w_var = _weighted_var(v, w)
            w_moe = _moe_from_var(w_var, _effective_n(w), config.confidence)
        else:
            w_mean = float("nan"); w_var = float("nan"); w_moe = float("nan")
        numeric_summary[col] = {
            "unweighted": {"mean": uw_mean, "variance": uw_var, "moe": uw_moe},
            "weighted": {"mean": w_mean, "variance": w_var, "moe": w_moe},
            "count": int(len(v))
        }

    categorical_summary = {}
    for col in categorical_cols:
        series = df[col].astype("string")
        if weight_col:
            tbl = series.to_frame().join(pd.Series(weights, name="w"))
            agg = tbl.groupby(col)["w"].sum().sort_values(ascending=False)
            total_w = float(agg.sum())
            distribution = {k: float(v) / total_w if total_w > 0 else 0.0 for k, v in agg.to_dict().items()}
        else:
            counts = series.value_counts(dropna=False)
            total = float(counts.sum())
            distribution = {k: float(v) / total if total > 0 else 0.0 for k, v in counts.to_dict().items()}
        categorical_summary[col] = {
            "top": list(distribution.items())[:20],
            "unique": int(series.nunique(dropna=False))
        }

    return {
        "numeric": numeric_summary,
        "categorical": categorical_summary,
        "weight_column": weight_col,
        "n": int(len(df)),
        "effective_n": float(n_eff),
    }
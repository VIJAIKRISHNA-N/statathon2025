from __future__ import annotations
from pydantic import BaseModel
from typing import List, Optional
from dataclasses import dataclass
from pathlib import Path
import pandas as pd
import numpy as np


class CleaningConfig(BaseModel):
    imputation_method: str = "median"  # mean|median|knn|none
    outlier_method: str = "iqr"  # iqr|zscore|none
    zscore_threshold: float = 3.0
    iqr_factor: float = 1.5
    columns: Optional[List[str]] = None  # if None, all numeric columns
    validation_min_max: Optional[dict] = None  # {column: {"min": x, "max": y}}


@dataclass
class CleaningResult:
    cleaned_path: Path
    logs: List[str]


def _impute(df: pd.DataFrame, method: str, columns: List[str]) -> (pd.DataFrame, List[str]):
    logs: List[str] = []
    if method == "none":
        return df, logs
    if method in {"mean", "median"}:
        for col in columns:
            if method == "mean":
                value = df[col].astype(float).mean()
            else:
                value = df[col].astype(float).median()
            missing = df[col].isna().sum()
            df[col] = df[col].fillna(value)
            logs.append(f"Imputed {missing} missing values in {col} with {method}={value:.4f}")
        return df, logs
    if method == "knn":
        # Optional: KNN would need scikit-learn. Fallback to median to keep environment lightweight.
        for col in columns:
            value = df[col].astype(float).median()
            missing = df[col].isna().sum()
            df[col] = df[col].fillna(value)
            logs.append(f"[Fallback] KNN not available; imputed {missing} values in {col} with median={value:.4f}")
        return df, logs
    raise ValueError("Unknown imputation method")


def _handle_outliers(df: pd.DataFrame, method: str, columns: List[str], zthr: float, iqr_k: float) -> (pd.DataFrame, List[str]):
    logs: List[str] = []
    if method == "none":
        return df, logs
    for col in columns:
        series = df[col].astype(float)
        if method == "zscore":
            mean = series.mean()
            std = series.std(ddof=0)
            mask = (np.abs((series - mean) / (std if std > 0 else 1)) > zthr)
            winsor_low = series[~mask].quantile(0.01)
            winsor_high = series[~mask].quantile(0.99)
            df[col] = series.clip(winsor_low, winsor_high)
            logs.append(f"Winsorized {col} using z-score>{zthr}")
        elif method == "iqr":
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            low = q1 - iqr_k * iqr
            high = q3 + iqr_k * iqr
            df[col] = series.clip(lower=low, upper=high)
            logs.append(f"Winsorized {col} using IQR*{iqr_k}")
        else:
            raise ValueError("Unknown outlier method")
    return df, logs


def _apply_validation(df: pd.DataFrame, rules: Optional[dict]) -> (pd.DataFrame, List[str]):
    logs: List[str] = []
    if not rules:
        return df, logs
    for col, bounds in rules.items():
        min_v = bounds.get("min", -np.inf)
        max_v = bounds.get("max", np.inf)
        before = df[col].isna().sum()
        df.loc[(df[col] < min_v) | (df[col] > max_v), col] = np.nan
        after = df[col].isna().sum()
        if after > before:
            logs.append(f"Validation set {after - before} out-of-range values to NaN in {col}")
    return df, logs


def run_cleaning(path: Path, config: CleaningConfig) -> CleaningResult:
    df = pd.read_csv(path)
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    target_cols = config.columns or numeric_cols

    vdf, vlogs = _apply_validation(df, config.validation_min_max)
    idf, ilogs = _impute(vdf, config.imputation_method, target_cols)
    odf, ologs = _handle_outliers(idf, config.outlier_method, target_cols, config.zscore_threshold, config.iqr_factor)

    cleaned_path = path.parent / "clean.csv"
    odf.to_csv(cleaned_path, index=False)

    logs = []
    logs.extend(vlogs)
    logs.extend(ilogs)
    logs.extend(ologs)

    return CleaningResult(cleaned_path=cleaned_path, logs=logs)
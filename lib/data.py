import pandas as pd
import numpy as np
import json
from typing import Dict, Any


def profileDataframe(df: pd.DataFrame) -> Dict[str, Any]:
    profile = {
        "n_rows": len(df),
        "n_columns": len(df.columns),
        "columns": []
    }

    for col in df.columns:
        series = df[col]
        col_type = detectColumnType(series)

        col_profile = {
            "name": col,
            "type": col_type,
            "missing_values": int(series.isna().sum()),
            "unique_values": int(series.nunique())
        }

        if col_type == "numeric":
            col_profile["stats"] = {
                "min": float(series.min()) if not series.isna().all() else None,
                "max": float(series.max()) if not series.isna().all() else None,
                "mean": float(series.mean()) if not series.isna().all() else None,
                "std": float(series.std()) if not series.isna().all() else None,
            }

        profile["columns"].append(col_profile)
    print(f"==== Profile ==== \n{profile}\n")
    return profile

def detectColumnType(series: pd.Series) -> str:
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    elif pd.api.types.is_numeric_dtype(series):
        return "numeric"
    elif pd.api.types.is_bool_dtype(series):
        return "boolean"
    elif series.nunique() < 30:
        return "categorical"
    else:
        return "text"

def detect_column_type(series: pd.Series) -> str:
    # 1. Уже datetime
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"

    # 2. Numeric
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"

    # 3. Boolean
    if pd.api.types.is_bool_dtype(series):
        return "boolean"

    # 4. Пробуем определить дату только если тип object (строка)
    if series.dtype == "object":
        non_null = series.dropna()

        if len(non_null) == 0:
            return "text"

        # пробуем парсинг
        parsed = pd.to_datetime(non_null, errors="coerce", dayfirst=True)

        success_rate = parsed.notna().mean()

        # если >= 80% значений распарсились - считаем datetime
        if success_rate > 0.8:
            return "datetime"

    # 5. Категориальные
    if series.nunique() < 30:
        return "categorical"

    return "text"

"""Pipeline principal do projeto."""

from __future__ import annotations

from pathlib import Path

from src.data.load_data import load_dataset, validate_required_columns
from src.features.feature_engineering import (
    ensure_municipio_id_format,
    fill_missing_values,
    normalize_columns,
)


def run_pipeline(data_path: str | Path, required_columns: list[str]) -> object:
    """Executa as etapas iniciais do pipeline de dados."""
    df = load_dataset(data_path)
    validate_required_columns(df, required_columns)
    df = normalize_columns(df)
    df = ensure_municipio_id_format(df)
    df = fill_missing_values(df)
    return df

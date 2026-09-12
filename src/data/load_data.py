"""Carregamento e validação inicial dos dados do projeto."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_dataset(path: str | Path) -> pd.DataFrame:
    """Carrega um dataset CSV em um DataFrame pandas."""
    dataset_path = Path(path)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {dataset_path}")

    df = pd.read_csv(dataset_path)
    return df


def validate_required_columns(df: pd.DataFrame, required_columns: list[str]) -> None:
    """Valida se todas as colunas esperadas existem no DataFrame."""
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError(f"Colunas ausentes: {missing}")

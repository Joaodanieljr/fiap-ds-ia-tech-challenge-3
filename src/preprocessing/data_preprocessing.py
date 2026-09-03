"""Funções genéricas para limpeza e preparação dos dados."""

from __future__ import annotations

import pandas as pd


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Padroniza nomes das colunas para minúsculas e sem espaços."""
    df = df.copy()
    df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]
    return df


def fill_missing_values(df: pd.DataFrame, strategy: str = "median") -> pd.DataFrame:
    """Preenche valores ausentes usando uma estratégia simples."""
    df = df.copy()

    for column in df.columns:
        if df[column].isnull().any():
            if pd.api.types.is_numeric_dtype(df[column]):
                if strategy == "median":
                    df[column] = df[column].fillna(df[column].median())
                elif strategy == "mean":
                    df[column] = df[column].fillna(df[column].mean())
                else:
                    df[column] = df[column].fillna(0)
            else:
                df[column] = df[column].fillna(df[column].mode()[0])

    return df

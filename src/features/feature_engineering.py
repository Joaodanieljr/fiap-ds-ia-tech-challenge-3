"""Funções de engenharia e transformação de features."""

from __future__ import annotations

import pandas as pd


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Padroniza nomes das colunas para formato consistente."""
    df = df.copy()
    df.columns = [str(column).strip().lower().replace(" ", "_") for column in df.columns]
    return df


def ensure_municipio_id_format(df: pd.DataFrame, column: str = "id_municipio") -> pd.DataFrame:
    """Mantém o identificador do município em formato textual com zeros à esquerda."""
    df = df.copy()
    if column in df.columns:
        df[column] = df[column].astype(str).str.zfill(7)
    return df


def fill_missing_values(df: pd.DataFrame, strategy: str = "median") -> pd.DataFrame:
    """Preenche valores ausentes por tipo de coluna."""
    df = df.copy()

    for column in df.columns:
        if df[column].isnull().any():
            if pd.api.types.is_numeric_dtype(df[column]):
                if strategy == "median":
                    fill_value = df[column].median()
                elif strategy == "mean":
                    fill_value = df[column].mean()
                else:
                    fill_value = 0
                df[column] = df[column].fillna(fill_value)
            else:
                mode_value = df[column].mode(dropna=True)
                if not mode_value.empty:
                    df[column] = df[column].fillna(mode_value.iloc[0])
                else:
                    df[column] = df[column].fillna("desconhecido")

    return df


def create_missing_history_flag(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    """Cria um indicador para municípios sem histórico de 2023."""
    df = df.copy()
    target_columns = columns or ["taxa_municipio_2023", "media_portugues_municipio_2023"]

    available_columns = [column for column in target_columns if column in df.columns]
    if not available_columns:
        df["sem_historico_2023"] = 0
        return df

    df["sem_historico_2023"] = df[available_columns].isnull().any(axis=1).astype(int)
    return df


def add_sector_participation_features(df: pd.DataFrame) -> pd.DataFrame:
    """Cria participações setoriais a partir do PIB e dos valores adicionados."""
    df = df.copy()

    sector_columns = {
        "participacao_agropecuaria": "va_agropecuaria",
        "participacao_industria": "va_industria",
        "participacao_servicos": "va_servicos",
        "participacao_adespss": "va_adespss",
    }

    for new_column, base_column in sector_columns.items():
        if base_column in df.columns and "pib" in df.columns:
            df[new_column] = df[base_column].div(df["pib"].replace(0, pd.NA))

    return df

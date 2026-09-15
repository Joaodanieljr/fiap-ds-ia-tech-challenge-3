"""Pipeline principal do projeto."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression

from src.data.load_data import load_dataset, validate_required_columns
from src.evaluation.metrics import compute_classification_metrics
from src.features.feature_engineering import (
    add_sector_participation_features,
    create_missing_history_flag,
    ensure_municipio_id_format,
    fill_missing_values,
    normalize_columns,
)
from src.modeling.train_model import compare_models, split_data, train_baseline_model


def run_pipeline(data_path: str | Path, required_columns: list[str]) -> object:
    """Executa as etapas iniciais do pipeline de dados."""
    df = load_dataset(data_path)
    validate_required_columns(df, required_columns)
    df = normalize_columns(df)
    df = ensure_municipio_id_format(df)
    df = fill_missing_values(df)
    return df


def build_feature_matrix(df: pd.DataFrame, target_column: str = "alfabetizado", group_column: str = "id_municipio") -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Constrói a matriz de features e separa alvo e grupo de validação."""
    df = df.copy()
    df = normalize_columns(df)
    df = ensure_municipio_id_format(df)
    df = create_missing_history_flag(df)
    df = add_sector_participation_features(df)
    df = fill_missing_values(df)

    feature_columns = [
        column for column in df.columns
        if column not in {target_column, group_column, "nome_municipio", "nome_regiao", "nome_mesorregiao"}
    ]

    features = df[feature_columns].copy()
    target = df[[target_column]].copy()
    groups = df[[group_column]].copy()
    return features, target, groups


def run_training_pipeline(df: pd.DataFrame, target_column: str = "alfabetizado", group_column: str = "id_municipio") -> dict:
    """Treina um modelo baseline para classificação binária no contexto do projeto."""
    X, y, groups = build_feature_matrix(df, target_column=target_column, group_column=group_column)

    X_train, X_test, y_train, y_test = split_data(X, y[target_column], test_size=0.2, random_state=42, stratify=y[target_column])

    categorical_columns = X.select_dtypes(include=["object", "category"]).columns.tolist()
    numeric_columns = [column for column in X.columns if column not in categorical_columns]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", numeric_columns),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_columns),
        ]
    )

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", LogisticRegression(max_iter=1000, random_state=42)),
        ]
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    return {
        "model": model,
        "metrics": compute_classification_metrics(y_test, y_pred, y_proba),
    }


def run_model_comparison(df: pd.DataFrame, target_column: str = "alfabetizado", group_column: str = "id_municipio", metric: str = "f1") -> list[dict]:
    """Executa comparação de modelos usando validação cruzada por município."""
    X, y, groups = build_feature_matrix(df, target_column=target_column, group_column=group_column)
    return compare_models(X, y[target_column], groups[group_column], metric=metric)

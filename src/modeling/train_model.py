"""Funções de treinamento, validação e comparação de modelos para classificação binária."""

from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import make_scorer, f1_score, precision_score, recall_score
from sklearn.model_selection import StratifiedGroupKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier


def split_data(X, y, test_size: float = 0.2, random_state: int = 42, stratify: Any | None = None):
    """Divide os dados em treino e teste, com fallback para datasets pequenos."""
    try:
        return train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=stratify)
    except ValueError:
        if stratify is None:
            raise
        return train_test_split(X, y, test_size=test_size, random_state=random_state)


def group_kfold_split(X, groups, y=None, n_splits: int = 5, shuffle: bool = True, random_state: int = 42):
    """Gera divisões por município para evitar vazamento entre grupos."""
    if y is None:
        if isinstance(X, pd.DataFrame) and "alfabetizado" in X.columns:
            y = X["alfabetizado"]
        else:
            raise ValueError("Para usar group_kfold_split, informe y ou inclua a coluna alfabetizado em X.")

    groups = pd.Series(groups).reset_index(drop=True)
    cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=shuffle, random_state=random_state)
    return cv.split(X, y, groups)


def train_baseline_model(model: BaseEstimator, X_train, y_train):
    """Treina um modelo de referência."""
    model.fit(X_train, y_train)
    return model


def _prepare_model_features(X: pd.DataFrame | Any) -> pd.DataFrame:
    """Remove identificadores, rótulos e colunas de peso para manter apenas atributos válidos."""
    if not isinstance(X, pd.DataFrame):
        X = pd.DataFrame(X)

    forbidden_columns = {
        "alfabetizado",
        "id_aluno",
        "id_escola",
        "id_municipio",
        "nome_municipio",
        "peso_aluno",
    }

    keep_columns = [column for column in X.columns if column not in forbidden_columns]
    return X[keep_columns].copy()


def _build_candidate_models() -> dict[str, BaseEstimator]:
    """Define modelos candidatos para a comparação de performance."""
    return {
        "logistic_regression": LogisticRegression(max_iter=1000, random_state=42),
        "decision_tree": DecisionTreeClassifier(random_state=42),
        "random_forest": RandomForestClassifier(n_estimators=200, random_state=42),
    }


def compare_models(X, y, groups, n_splits: int = 5, metric: str = "f1", random_state: int = 42):
    """Compara modelos usando StratifiedGroupKFold por município."""
    X_clean = _prepare_model_features(X)
    groups = pd.Series(groups).reset_index(drop=True)
    y = pd.Series(y).reset_index(drop=True)

    if len(X_clean) != len(y) or len(X_clean) != len(groups):
        raise ValueError("X, y e groups devem ter o mesmo número de linhas.")

    metric_name = metric.lower()
    scorer_map = {
        "accuracy": "accuracy",
        "precision": make_scorer(precision_score, zero_division=0),
        "recall": make_scorer(recall_score, zero_division=0),
        "f1": make_scorer(f1_score, zero_division=0),
    }

    if metric_name not in scorer_map:
        raise ValueError(f"Métrica não suportada: {metric}. Opções: {sorted(scorer_map)}")

    cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    results = []

    for model_name, estimator in _build_candidate_models().items():
        categorical_columns = X_clean.select_dtypes(include=["object", "category"]).columns.tolist()
        numeric_columns = [column for column in X_clean.columns if column not in categorical_columns]

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", Pipeline(steps=[("imputer", SimpleImputer(strategy="median"))]), numeric_columns),
                ("cat", Pipeline(steps=[("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical_columns),
            ]
        )

        pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("classifier", estimator),
            ]
        )

        scores = cross_val_score(
            pipeline,
            X_clean,
            y,
            groups=groups,
            cv=cv,
            scoring=scorer_map[metric_name],
        )

        results.append(
            {
                "model_name": model_name,
                "metrics": {metric_name: float(scores.mean()), "std": float(scores.std())},
                "scores": [float(score) for score in scores],
            }
        )

    return sorted(results, key=lambda item: item["metrics"][metric_name], reverse=True)

"""Funções de treinamento e validação de modelos para classificação binária."""

from __future__ import annotations

from typing import Any

from sklearn.base import BaseEstimator
from sklearn.model_selection import StratifiedGroupKFold, train_test_split


def split_data(X, y, test_size: float = 0.2, random_state: int = 42, stratify: Any | None = None):
    """Divide os dados em treino e teste, com fallback para datasets pequenos."""
    try:
        return train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=stratify)
    except ValueError:
        if stratify is None:
            raise
        return train_test_split(X, y, test_size=test_size, random_state=random_state)


def group_kfold_split(X, groups, n_splits: int = 5, shuffle: bool = True, random_state: int = 42):
    """Gera divisões por município para evitar vazamento entre grupos."""
    cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=shuffle, random_state=random_state)
    return cv.split(X, X["alfabetizado"], groups)


def train_baseline_model(model: BaseEstimator, X_train, y_train):
    """Treina um modelo de referência."""
    model.fit(X_train, y_train)
    return model

"""Exemplo genérico de treinamento de modelo."""

from __future__ import annotations

from sklearn.base import BaseEstimator
from sklearn.model_selection import train_test_split


def split_data(X, y, test_size: float = 0.2, random_state: int = 42):
    """Divide os dados em treino e teste."""
    return train_test_split(X, y, test_size=test_size, random_state=random_state)


def train_baseline_model(model: BaseEstimator, X_train, y_train):
    """Treina um modelo de referência."""
    model.fit(X_train, y_train)
    return model

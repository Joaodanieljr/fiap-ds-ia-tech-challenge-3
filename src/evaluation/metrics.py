"""Métricas genéricas para avaliação de modelos."""

from __future__ import annotations

from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score


def compute_classification_metrics(y_true, y_pred):
    """Retorna um dicionário com métricas de classificação."""
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, average="weighted", zero_division=0),
        "recall": recall_score(y_true, y_pred, average="weighted", zero_division=0),
        "f1": f1_score(y_true, y_pred, average="weighted", zero_division=0),
    }

import pandas as pd

from src.evaluation.metrics import compute_classification_metrics
from src.modeling.train_model import split_data


def test_split_data_returns_expected_shapes():
    X = pd.DataFrame({"feature_1": [1, 2, 3, 4], "feature_2": [5, 6, 7, 8]})
    y = pd.Series([0, 1, 0, 1])

    X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.5, random_state=42)

    assert len(X_train) == 2
    assert len(X_test) == 2
    assert len(y_train) == 2
    assert len(y_test) == 2


def test_compute_classification_metrics_returns_expected_keys():
    y_true = [1, 0, 1, 0]
    y_pred = [1, 0, 0, 0]
    y_proba = [0.9, 0.2, 0.4, 0.1]

    metrics = compute_classification_metrics(y_true, y_pred, y_proba)

    assert set(metrics.keys()) == {"accuracy", "precision", "recall", "f1", "roc_auc", "average_precision"}
    assert metrics["accuracy"] == 0.75

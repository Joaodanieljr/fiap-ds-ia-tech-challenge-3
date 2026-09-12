import pandas as pd

from src.evaluation.metrics import compute_classification_metrics
from src.modeling.train_model import compare_models, split_data


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


def test_compare_models_uses_group_validation_and_returns_ranked_results():
    df = pd.DataFrame(
        {
            "id_aluno": [f"a{i}" for i in range(12)],
            "id_escola": [f"e{i}" for i in range(12)],
            "id_municipio": ["0000001", "0000001", "0000002", "0000002", "0000003", "0000003", "0000004", "0000004", "0000005", "0000005", "0000006", "0000006"],
            "rede": ["municipal", "estadual", "municipal", "estadual", "municipal", "estadual", "municipal", "estadual", "municipal", "estadual", "municipal", "estadual"],
            "taxa_municipio_2023": [50, 52, 55, 57, 60, 62, 65, 68, 70, 72, 75, 78],
            "pib": [1000, 1200, 1100, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100],
            "peso_aluno": [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1],
            "alfabetizado": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        }
    )

    X, y, groups = df.drop(columns=["alfabetizado"]), df["alfabetizado"], df["id_municipio"]
    results = compare_models(X, y, groups, n_splits=3, metric="f1")

    assert len(results) >= 2
    assert all("model_name" in result for result in results)
    assert all("metrics" in result for result in results)
    assert results[0]["metrics"]["f1"] >= results[-1]["metrics"]["f1"]

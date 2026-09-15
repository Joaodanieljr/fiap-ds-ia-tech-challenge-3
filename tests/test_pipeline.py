import pandas as pd

from src.pipeline.run_pipeline import build_feature_matrix, run_training_pipeline


def test_build_feature_matrix_keeps_target_and_group_columns():
    df = pd.DataFrame(
        {
            "id_municipio": ["0000001", "0000002", "0000003"],
            "rede": ["municipal", "estadual", "municipal"],
            "taxa_municipio_2023": [50.0, None, 60.0],
            "pib": [1000, 2000, 3000],
            "va_agropecuaria": [100, 200, 300],
            "va_industria": [150, 200, 100],
            "va_servicos": [300, 500, 700],
            "va_adespss": [450, 900, 1100],
            "alfabetizado": [1, 0, 1],
        }
    )

    features, target, groups = build_feature_matrix(df)

    assert "alfabetizado" not in features.columns
    assert list(target.columns) == ["alfabetizado"]
    assert list(groups.columns) == ["id_municipio"]
    assert "sem_historico_2023" in features.columns
    assert "participacao_agropecuaria" in features.columns


def test_run_training_pipeline_returns_metrics_and_model():
    df = pd.DataFrame(
        {
            "id_municipio": ["0000001", "0000002", "0000003", "0000004"],
            "rede": ["municipal", "estadual", "municipal", "estadual"],
            "taxa_municipio_2023": [50.0, 55.0, 60.0, 65.0],
            "pib": [1000, 2000, 3000, 4000],
            "va_agropecuaria": [100, 200, 300, 400],
            "va_industria": [150, 200, 100, 100],
            "va_servicos": [300, 500, 700, 800],
            "va_adespss": [450, 900, 1100, 1200],
            "alfabetizado": [1, 0, 1, 0],
        }
    )

    result = run_training_pipeline(df, target_column="alfabetizado", group_column="id_municipio")

    assert "model" in result
    assert "metrics" in result
    assert set(result["metrics"].keys()) >= {"accuracy", "precision", "recall", "f1"}

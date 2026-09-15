import pandas as pd

from src.features.feature_engineering import (
    add_sector_participation_features,
    create_missing_history_flag,
    ensure_municipio_id_format,
    normalize_columns,
)


def test_normalize_columns_lowercases_and_replaces_spaces():
    df = pd.DataFrame({"Nome Municipio": ["A"], "Taxa de Alfabetizacao": [90]})

    result = normalize_columns(df)

    assert list(result.columns) == ["nome_municipio", "taxa_de_alfabetizacao"]


def test_ensure_municipio_id_format_zfills_values():
    df = pd.DataFrame({"id_municipio": [12, 3456, 7890123]})

    result = ensure_municipio_id_format(df)

    assert result["id_municipio"].tolist() == ["0000012", "0003456", "7890123"]


def test_create_missing_history_flag_marks_nulls():
    df = pd.DataFrame({
        "taxa_municipio_2023": [10.5, None, 11.0],
        "media_portugues_municipio_2023": [500.0, 480.0, None],
    })

    result = create_missing_history_flag(df)

    assert result["sem_historico_2023"].tolist() == [0, 1, 1]


def test_add_sector_participation_features_derive_ratios():
    df = pd.DataFrame(
        {
            "pib": [1000, 2000],
            "va_agropecuaria": [100, 200],
            "va_industria": [200, 400],
            "va_servicos": [300, 500],
            "va_adespss": [400, 900],
        }
    )

    result = add_sector_participation_features(df)

    assert result["participacao_agropecuaria"].tolist() == [0.1, 0.1]
    assert result["participacao_industria"].tolist() == [0.2, 0.2]
    assert result["participacao_servicos"].tolist() == [0.3, 0.25]
    assert result["participacao_adespss"].tolist() == [0.4, 0.45]

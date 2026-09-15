"""Pipeline principal do projeto."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
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
from src.modeling.train_model import _prepare_model_features, compare_models, split_data


def run_pipeline(data_path: str | Path, required_columns: list[str]) -> object:
    """Executa as etapas iniciais do pipeline de dados."""
    df = load_dataset(data_path)
    validate_required_columns(df, required_columns)
    df = normalize_columns(df)
    df = ensure_municipio_id_format(df)
    df = fill_missing_values(df)
    return df


def build_feature_matrix(df: pd.DataFrame, target_column: str = "alfabetizado", group_column: str = "id_municipio") -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Constrói a matriz de features e separa alvo e grupo de validação.

    A imputação de valores ausentes NÃO acontece aqui. Ela é responsabilidade do
    Pipeline, para que o ajuste ocorra apenas sobre o conjunto de treino e não vaze
    informação do conjunto de teste.

    A seleção de colunas usa _prepare_model_features, a mesma regra da comparação de
    modelos, para que os dois caminhos de treino não divirjam.
    """
    df = df.copy()
    df = normalize_columns(df)
    df = ensure_municipio_id_format(df)
    df = create_missing_history_flag(df)
    df = add_sector_participation_features(df)

    features = _prepare_model_features(df)
    target = df[[target_column]].copy()
    groups = df[[group_column]].copy()
    return features, target, groups


def _build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    """Monta o pré-processamento integrado ao modelo.

    Numéricas recebem imputação pela mediana e padronização de escala — sem escalar,
    a regressão logística converge mal, porque pib está na casa dos milhões e as taxas
    variam de 0 a 100. Categóricas recebem imputação pela moda e codificação one-hot.
    """
    categorical_columns = X.select_dtypes(include=["object", "category"]).columns.tolist()
    numeric_columns = [column for column in X.columns if column not in categorical_columns]

    transformador_numerico = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    transformador_categorico = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", transformador_numerico, numeric_columns),
            ("cat", transformador_categorico, categorical_columns),
        ]
    )


def _split_por_municipio(X: pd.DataFrame, y: pd.Series, groups: pd.Series, random_state: int = 42):
    """Separa treino e teste garantindo que um município fique inteiro de um lado só.

    Alunos do mesmo município compartilham todas as variáveis de contexto. Se o
    município aparecer nos dois conjuntos, a métrica mede memorização em vez de
    generalização.
    """
    n_grupos = groups.nunique()
    if n_grupos < 5:
        # Base pequena demais para dividir por município: cai no split estratificado
        # simples. Só acontece em teste unitário, nunca na base real.
        return split_data(X, y, test_size=0.2, random_state=random_state, stratify=y)

    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=random_state)
    indices_treino, indices_teste = next(cv.split(X, y, groups))
    return (
        X.iloc[indices_treino],
        X.iloc[indices_teste],
        y.iloc[indices_treino],
        y.iloc[indices_teste],
    )


def run_training_pipeline(df: pd.DataFrame, target_column: str = "alfabetizado", group_column: str = "id_municipio") -> dict:
    """Treina um modelo baseline para classificação binária no contexto do projeto."""
    X, y, groups = build_feature_matrix(df, target_column=target_column, group_column=group_column)

    y_series = y[target_column].reset_index(drop=True)
    groups_series = groups[group_column].reset_index(drop=True)
    X = X.reset_index(drop=True)

    X_train, X_test, y_train, y_test = _split_por_municipio(X, y_series, groups_series)

    model = Pipeline(
        steps=[
            ("preprocessor", _build_preprocessor(X)),
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

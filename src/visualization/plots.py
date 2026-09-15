"""Funções genéricas de visualização."""

from __future__ import annotations

import matplotlib.pyplot as plt
import seaborn as sns


def plot_distribution(data, column: str, title: str = "Distribuição"):
    """Plota a distribuição de uma variável."""
    sns.histplot(data[column], kde=True)
    plt.title(title)
    plt.xlabel(column)
    plt.ylabel("Frequência")
    plt.tight_layout()
    return plt.gcf()


def plot_correlation_matrix(data):
    """Plota a matriz de correlação das variáveis numéricas."""
    corr = data.corr(numeric_only=True)
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Matriz de Correlação")
    plt.tight_layout()
    return plt.gcf()

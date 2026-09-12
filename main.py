"""Script principal para executar o fluxo do projeto de alfabetização."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from src.pipeline.run_pipeline import run_training_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Executa o pipeline de dados e treinamento do Tech Challenge.")
    parser.add_argument("--data-path", type=str, required=True, help="Caminho do arquivo CSV com a base analítica.")
    parser.add_argument("--target-column", type=str, default="alfabetizado", help="Coluna alvo do problema.")
    parser.add_argument("--group-column", type=str, default="id_municipio", help="Coluna usada como agrupamento para validação.")
    parser.add_argument("--output-model", type=str, default=None, help="Caminho opcional para salvar o modelo treinado em .pkl.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_path = Path(args.data_path)

    if not data_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {data_path}")

    df = pd.read_csv(data_path)
    result = run_training_pipeline(df, target_column=args.target_column, group_column=args.group_column)

    print("Métricas do modelo:")
    print(json.dumps(result["metrics"], indent=2, ensure_ascii=False))

    if args.output_model:
        output_path = Path(args.output_model)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        import pickle

        with output_path.open("wb") as file:
            pickle.dump(result["model"], file)

        print(f"\nModelo salvo em: {output_path}")


if __name__ == "__main__":
    main()

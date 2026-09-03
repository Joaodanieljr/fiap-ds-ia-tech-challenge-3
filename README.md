# fiap-ds-ia-tech-challenge-3

Projeto genérico de Data Science e IA com estrutura organizada para desenvolvimento, treinamento e avaliação de modelos.

## Objetivo

Este repositório serve como base para projetos de análise e modelagem preditiva, seguindo boas práticas de organização, versionamento e reutilização de código.

## Estrutura do projeto

- `data/` - dados brutos, intermediários e finais
- `notebooks/` - notebooks de exploração e análise
- `src/` - código-fonte do projeto
  - `src/preprocessing/` - limpeza, tratamento e preparação dos dados
  - `src/modeling/` - treinamento e persistência de modelos
  - `src/evaluation/` - métricas, validação e comparação de resultados
  - `src/visualization/` - geração de gráficos e relatórios visuais
- `reports/` - relatórios, resultados e documentação
- `images/` - figuras, gráficos e artefatos visuais
- `requirements.txt` - dependências do projeto

## Fluxo de trabalho sugerido

1. Coleta e organização dos dados em `data/`
2. Exploração em notebooks em `notebooks/`
3. Limpeza e transformação em `src/preprocessing/`
4. Treinamento do modelo em `src/modeling/`
5. Avaliação e comparação em `src/evaluation/`
6. Visualização e comunicação dos resultados em `src/visualization/`

## Configuração do ambiente

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

## Boas práticas

- Separar dados, código e resultados em pastas específicas
- Usar notebooks apenas para exploração e prototipagem
- Centralizar lógica reutilizável em módulos Python em `src/`
- Registrar métricas e versões dos experimentos
- Documentar hipóteses, decisões e resultados em relatórios

## Versionamento

Este projeto também foi pensado para demonstrar boas práticas de Git, incluindo:

- histórico de commits
- branches e merges
- organização de alterações por contexto
- controle de versões de código e artefatos

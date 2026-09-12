# fiap-ds-ia-tech-challenge-3

Projeto de Data Science e IA para o Tech Challenge Fase 3, com foco em predição de alfabetização no contexto educacional brasileiro.

## Objetivo

Este repositório organiza o fluxo de análise, preparação de dados, engenharia de features, treinamento e avaliação de modelos para prever indicadores de alfabetização.

## Estrutura do projeto

- `data/` - dados brutos e processados
- `notebooks/` - notebooks de exploração e prototipagem
- `src/` - código reutilizável do projeto
  - `src/data/` - carregamento e validação de dados
  - `src/features/` - engenharia de features e transformação
  - `src/modeling/` - treinamento e seleção de modelos
  - `src/evaluation/` - métricas e validação
  - `src/visualization/` - gráficos e análises visuais
  - `src/pipeline/` - orquestração do fluxo principal
  - `src/utils/` - utilitários gerais
- `reports/` - documentação e relatórios
- `images/` - artefatos visuais
- `tests/` - testes automatizados
- `requirements.txt` - dependências

## Fluxo recomendado

1. Carregar a base analítica em `data/`
2. Validar colunas e integridade dos dados
3. Normalizar e transformar features em `src/features/`
4. Treinar e comparar modelos em `src/modeling/`
5. Avaliar resultado em `src/evaluation/`
6. Gerar visualizações em `src/visualization/`
7. Orquestrar o pipeline em `src/pipeline/`

## Regras importantes do domínio

- `id_municipio` deve ser tratado como texto com zeros à esquerda.
- A base deve manter separação clara entre features do aluno, do município e contextuais.
- O processo deve evitar vazamento de informação agregada em features do alvo.
- A validação do schema e das colunas é obrigatória antes do treino.

## Configuração do ambiente

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

## Próximos passos

- extrair a lógica dos notebooks para módulos em `src/`
- padronizar nomes e convenções de colunas
- revisar variáveis sensíveis e risco de vazamento
- estruturar o pipeline de treino e avaliação de forma reprodutível

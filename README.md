# FIAP - Tech Challenge Fase 3

Projeto de Data Science e Inteligência Artificial para prever alfabetização de alunos do 2º ano do Ensino Fundamental, com base em dados educacionais e contextuais do município.

## 1. Objetivo do projeto

Este repositório organiza o fluxo de análise, preparação de dados, engenharia de features, treinamento e avaliação de modelos para prever se um aluno está alfabetizado, conforme o critério oficial do Indicador Criança Alfabetizada.

O alvo principal do problema é a coluna `alfabetizado`, definida a partir da proficiência em Língua Portuguesa, com limiar de 743 pontos na escala Saeb.

---

## 2. Contexto do problema

O projeto foi construído com base em dados públicos da Base dos Dados e segue o escopo do Tech Challenge da FIAP. A base analítica está no grão do aluno, com contexto territorial e socioeconômico do município.

As decisões de modelagem e arquitetura foram pensadas para evitar vazamento de informação, principalmente em colunas agregadas do município. Isso inclui regras como:

- `id_municipio` deve ser tratado como identificador textual, com zeros à esquerda
- variáveis de desempenho do município entram com defasagem temporal
- colunas derivadas do alvo, como `proficiencia` e `alfabetizado_fonte`, não devem ser usadas como feature
- a validação cruzada deve respeitar o agrupamento por município

---

## 3. Arquitetura do projeto

```text
.
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
│   ├── 00_base_analitica.ipynb
│   ├── EDA_fase3.ipynb
│   └── feature_engineering_tech_challenge_3.ipynb
├── reports/
│   ├── dicionario_dados.md
│   └── readme_secao_base.md
├── src/
│   ├── data/
│   │   ├── __init__.py
│   │   └── load_data.py
│   ├── evaluation/
│   │   ├── __init__.py
│   │   └── metrics.py
│   ├── features/
│   │   ├── __init__.py
│   │   └── feature_engineering.py
│   ├── modeling/
│   │   ├── __init__.py
│   │   └── train_model.py
│   ├── pipeline/
│   │   ├── __init__.py
│   │   └── run_pipeline.py
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   └── data_preprocessing.py
│   ├── utils/
│   │   └── __init__.py
│   ├── visualization/
│   │   ├── __init__.py
│   │   └── plots.py
│   └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── test_feature_engineering.py
│   ├── test_modeling.py
│   └── test_pipeline.py
├── .gitignore
├── main.py
├── README.md
├── requirements.txt
└── .gitignore
```

### Descrição dos módulos

- `src/data/`: carregamento e validação de dados
- `src/features/`: engenharia e transformação de features
- `src/modeling/`: treino, split e seleção de modelos
- `src/evaluation/`: métricas, comparação e avaliação
- `src/pipeline/`: orquestração do fluxo principal
- `src/visualization/`: geração de gráficos e visualizações
- `src/preprocessing/`: preparação inicial de dados e transformações auxiliares
- `reports/`: documentação técnica e dicionário de dados
- `tests/`: validação automatizada das funcionalidades principais

---

## 4. Regras de negócio e cuidado com leakage

Este projeto tem regras importantes que precisam ser respeitadas ao longo da modelagem:

### 4.1. Alvo
- `alfabetizado` é a variável alvo
- o critério é: proficiência em Língua Portuguesa >= 743 pontos

### 4.2. Identificadores e agrupamentos
- `id_aluno` deve ser usado apenas como identificador
- `id_municipio` é a chave de agrupamento para validação
- não deve ser usado como feature de treinamento

### 4.3. Defasagem temporal
- dados de desempenho municipal devem entrar com defasagem
- o desempenho do município em 2024 não pode ser usado para prever o mesmo alvo em 2024, porque gera leakage

### 4.4. Colunas bloqueadas
As colunas abaixo não devem entrar na modelagem:

- `proficiencia`
- `alfabetizado_fonte`

Essas colunas geram diretamente o alvo ou representam a resposta oficial da fonte.

### 4.5. Features contextuais
Features do município e do território são válidas quando apresentadas como contexto e não como resultado do próprio alvo.

---

## 5. Fluxo do projeto

O fluxo recomendado do projeto é:

1. carregar dados
2. validar schema e colunas obrigatórias
3. normalizar nomes e padronizar formatos
4. gerar features e indicadores de contexto
5. preparar matriz de treino
6. treinar modelo de referência
7. avaliar métricas
8. comparar modelos
9. salvar resultados e modelo

---

## 6. Como rodar o projeto

### 6.1. Ambiente

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 6.2. Executar pipeline principal

```bash
python main.py --data-path data/processed/seu_arquivo.csv --target-column alfabetizado --group-column id_municipio --output-model models/modelo.pkl
```

### 6.3. Executar comparação de modelos por município

```bash
python main.py --data-path data/processed/seu_arquivo.csv --target-column alfabetizado --group-column id_municipio --compare-models --metric f1
```

### 6.4. Executar testes

```bash
python -m pytest -q tests/test_feature_engineering.py tests/test_modeling.py tests/test_pipeline.py
```

---

## 7. Métricas do projeto

As métricas principais para a tarefa de classificação binária são:

- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC
- Average Precision

Essas métricas estão implementadas em [src/evaluation/metrics.py](src/evaluation/metrics.py).

---

## 8. Estratégia de modelagem

A abordagem implementada neste projeto segue a lógica de baseline + comparação de modelos, sempre preservando a regra de validação por município.

### Baseline
- Regressão logística

### Modelos comparados
- regressão logística
- árvore de decisão
- random forest

### Validação
- holdout final para avaliação pontual
- validação cruzada por município com `StratifiedGroupKFold`

### Importante
- `id_municipio` é usado como agrupamento e não como feature
- o objetivo é medir generalização real e evitar vazamento por município repetido
- o módulo de comparação expõe a performance média por modelo e a dispersão da métrica

---

## 9. Ranking de risco

Uma parte importante do projeto é transformar a probabilidade de alfabetização em uma decisão útil. O ranking pode classificar os casos em:

- risco alto
- risco médio
- risco baixo

Exemplo:

- risco alto: probabilidade < 0,35
- risco médio: 0,35 a 0,65
- risco baixo: probabilidade > 0,65

Esse tipo de output pode ser usado para priorizar ações de apoio pedagógico e políticas públicas.

---

## 10. Testes automatizados

O projeto já conta com testes para as partes essenciais:

- [tests/test_feature_engineering.py](tests/test_feature_engineering.py)
- [tests/test_modeling.py](tests/test_modeling.py)
- [tests/test_pipeline.py](tests/test_pipeline.py)

Esses testes cubrem:
- normalização de colunas
- tratamento de identificadores
- flags de histórico ausente
- matrizes de features
- split e treino
- métricas de classificação
- comparação de modelos com validação por município

### Resultado verificado

O comando abaixo foi executado com sucesso:

```bash
python -m pytest -q tests/test_feature_engineering.py tests/test_modeling.py tests/test_pipeline.py
```

E o resultado verificado foi:

```text
9 passed in 2.16s
```

---

## 11. Documentação complementar

A documentação adicional do projeto está em:

- [reports/dicionario_dados.md](reports/dicionario_dados.md)
- [reports/readme_secao_base.md](reports/readme_secao_base.md)

Esses arquivos detalham o dicionário de dados e a lógica da base analítica.

---

## 12. Status do projeto

A estrutura atual foi organizada para apoiar o fluxo principal do projeto, com separação por responsabilidade, controle de leakage e comparação de modelos por município. O repositório já está em um estado funcional de treino, avaliação e validação inicial.

---

## 13. Próximos passos sugeridos

1. implementar tuning de hiperparâmetros com busca automatizada
2. ampliar a comparação de modelos com mais algoritmos e configurações
3. criar camada de ranking de risco e priorização por município
4. consolidar relatórios e análises executivas para apresentação final

---

## 14. Conclusão

Este repositório foi organizado para apoiar a análise, a modelagem e a avaliação de indicadores de alfabetização com foco em metodologia, rastreabilidade, controle de vazamento de informação e comparação objetiva de modelos. O projeto já atende ao escopo técnico principal do desafio e está preparado para evoluir para etapas mais avançadas de tuning e aplicação estratégica.

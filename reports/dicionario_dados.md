# Dicionário de Dados — Base Analítica

**Arquivo:** `data/base_analitica.parquet` (completo) · `data/base_analitica_amostra.parquet` (16%)
**Grão:** um aluno do 2º ano do Ensino Fundamental avaliado em 2024
**Volume:** 1.851.852 linhas · 5.517 municípios · 26 colunas
**Alvo:** `alfabetizado` — 59,8% positivos
**Amostra versionada:** 296.292 linhas (16%), estratificada por UF, rede e alvo — taxa
idêntica à da base completa
**Gerado por:** `notebooks/00_base_analitica.ipynb`
**Autor:** Vinicius Moreira | Última alteração: 2026-08

---

## Como ler este documento

Cada coluna tem um **papel**, e o papel define o que pode ser feito com ela:

| Papel | Significado |
|---|---|
| `alvo` | O que o modelo prevê |
| `identificador` | Não entra como feature em hipótese nenhuma |
| `agrupamento` | Usada para agrupar na validação cruzada, não como feature |
| `rótulo` | Serve para exibir em gráfico ou relatório, não para o modelo |
| `feature` | Entra no modelo |
| `peso` | Peso amostral — entra no `fit`, não como feature |

---

## Colunas

### Alvo

| Coluna | Tipo | Papel | Descrição |
|---|---|---|---|
| `alfabetizado` | Int64 | alvo | 1 se a proficiência em Língua Portuguesa ≥ 743 pontos na escala Saeb. Critério oficial do Indicador Criança Alfabetizada. Verificado contra o campo oficial da fonte: **0 divergências em 1,85M linhas** |

### Identificação e agrupamento

| Coluna | Tipo | Papel | Distintos | Observação |
|---|---|---|---|---|
| `id_aluno` | object | identificador | 1.851.852 | Único por linha. Usar como feature causa memorização |
| `id_escola` | object | agrupamento | 42.328 | Cardinalidade alta demais para one-hot. Serve para agrupar ou para target encoding com validação cuidadosa |
| `id_municipio` | object | agrupamento | 5.517 | **Chave do `StratifiedGroupKFold`.** Texto de 7 dígitos com zero à esquerda — nunca converter para número |
| `nome_municipio` | object | rótulo | 5.249 | Para exibição. Nomes se repetem entre estados, então não identifica município |

### Contexto do aluno

| Coluna | Tipo | Papel | Distintos | Observação |
|---|---|---|---|---|
| `rede` | object | feature | 3 | 1 Federal, 2 Estadual, 3 Municipal, 4 Privada. Categórica |
| `caderno` | object | feature | 22 | Versão da prova aplicada. Categórica de cardinalidade média — verificar na EDA se tem efeito real ou é ruído |
| `peso_aluno` | float64 | peso | 540 | Peso amostral do desenho do Saeb. **Não é característica do aluno.** Entra como `sample_weight` no `fit`, não como coluna de feature |

### Território

| Coluna | Tipo | Papel | Distintos | Observação |
|---|---|---|---|---|
| `sigla_uf` | object | feature | 26 | Unidade federativa |
| `nome_regiao` | object | feature | 5 | Macrorregião |
| `nome_mesorregiao` | object | feature | 135 | Cardinalidade média-alta. Avaliar agrupar categorias raras |
| `capital_uf` | Int64 | feature | 2 | 1 se é capital estadual |
| `amazonia_legal` | Int64 | feature | 2 | 1 se pertence à Amazônia Legal |

### Socioeconômico

Todos são atributos do município, não do aluno. População na referência mais recente
até 2024; PIB e valores adicionados na referência **2021**, último ano com os setoriais
publicados pelo IBGE.

| Coluna | Tipo | Papel | Observação |
|---|---|---|---|
| `populacao` | Int64 | feature | Porte do município |
| `pib` | Int64 | feature | PIB municipal absoluto. **Sugestão para a feature engineering:** `pib / populacao` é mais informativo que o valor bruto |
| `va_agropecuaria` | Int64 | feature | Valor adicionado do agro |
| `va_industria` | Int64 | feature | Valor adicionado da indústria |
| `va_servicos` | Int64 | feature | Valor adicionado dos serviços |
| `va_adespss` | Int64 | feature | Valor adicionado de administração, defesa, educação, saúde e seguridade |

> Sugestão: a participação setorial (`va_agropecuaria / pib`, etc.) tende a ser mais
> preditiva que o valor absoluto. Como todas vêm do mesmo ano, a razão é coerente.

### Desempenho do município no ano anterior

| Coluna | Tipo | Papel | Nulos | Observação |
|---|---|---|---|---|
| `taxa_municipio_2023` | float64 | feature | 10,78% | Taxa de alfabetização do município em 2023 |
| `media_portugues_municipio_2023` | float64 | feature | 10,78% | Proficiência média do município em 2023 |

**Leia isto antes de usar:** essas duas colunas são as mais preditivas da base e também as
mais delicadas. A regra é a data:

- Do **mesmo ano do alvo** seriam vazamento direto — são a média do próprio alvo
- De **2023**, como estão aqui, são informação legitimamente disponível antes de 2024

Os 10,78% de nulos são municípios que não participaram da avaliação em 2023. A ausência
não é aleatória: concentra municípios pequenos e regiões específicas. Sugestão de
tratamento: imputar e criar um indicador binário de "sem histórico", que carrega sinal
próprio.

### Metas pactuadas

Metas do Compromisso Nacional Criança Alfabetizada, definidas com antecedência. São
compromissos de política pública, não resultado observado.

| Coluna | Tipo | Papel | Nulos | Observação |
|---|---|---|---|---|
| `meta_alfabetizacao_2024` | float64 | feature | 4,67% | Meta para 2024. 2.745 valores distintos |
| `meta_alfabetizacao_2026` | float64 | feature | 3,19% | Meta para 2026. 2.284 valores distintos |
| `meta_alfabetizacao_2030` | float64 | feature | 3,19% | **Um único valor distinto: 80,0 para todo município.** Na prática só distingue "tem meta pactuada" de "não tem". Considerar descartar em favor das metas de 2024 e 2026, que carregam informação real |
| `nivel_alfabetizacao` | Int64 | feature | 3,19% | Estrato do município na pactuação, 6 níveis de 0 a 5, derivado do desempenho anterior. **É ordinal, não nominal** — a ordem significa algo, então `OrdinalEncoder` preserva o sinal e `OneHotEncoder` o descarta |
| `percentual_participacao` | float64 | feature | 3,19% | Participação do município na avaliação |

As metas existem apenas para a rede **Municipal**. Elas entram como atributo de contexto
do território para todos os alunos, inclusive os das redes estadual e privada. É decisão
consciente: caracteriza o território, não o aluno. Está registrada aqui e no README.

---

## Colunas bloqueadas — não estão no arquivo

Removidas antes da gravação do Parquet. A remoção é intencional: o vazamento mais grave
fica impossível por construção, sem depender de ninguém lembrar de excluir a coluna.

| Coluna | Motivo |
|---|---|
| `proficiencia` | Gera o alvo. Usar equivale a entregar a resposta |
| `alfabetizado_fonte` | É o próprio alvo, vindo pronto da fonte |

## Colunas que existem na fonte e não foram trazidas

| Coluna | Motivo |
|---|---|
| `municipio.taxa_alfabetizacao` (2024) | Média do alvo no mesmo ano — vazamento agregado |
| `municipio.media_portugues` (2024) | Média da proficiência no mesmo ano — vazamento agregado |
| `municipio.proporcao_aluno_nivel_0..8` | Distribuição da proficiência no mesmo ano — vazamento agregado |
| `serie` | Constante: só existe 2º ano do EF. Variância zero |
| `ano_populacao`, `ano_pib` | Constantes após o filtro. Registradas aqui em vez de ocupar coluna |
| `br_ibge_pib.gini` | Disponível por UF, não por município. Como `sigla_uf` já é feature, não acrescenta informação |
| `centroide` | Tipo GEOGRAPHY, não serializa bem em Parquet via pandas |

---

## Linhagem com a Fase 2

A base sai das mesmas tabelas da Base dos Dados que alimentaram a camada Gold da Fase 2.
A equivalência foi verificada numericamente — a tabela `municipio` do BigQuery reproduz o
`fato_indicador` da Gold em todas as métricas registradas na fase anterior:

| Métrica | Fase 2 | BigQuery |
|---|---|---|
| Linhas | 23.995 | 23.995 |
| Municípios | 5.550 | 5.550 |
| Anos | 2 | 2 |
| Taxa mínima | 2,12 | 2,12 |
| Taxa máxima | 100,0 | 100,0 |

**Correção herdada:** na Fase 2 o `fato_aluno_agregado` era de 2025 enquanto o
`fato_indicador` cobria 2023 e 2024 — os anos não se sobrepunham, então o cruzamento
previsto naquela fase não retornaria linhas. Nesta base, alvo e contexto estão alinhados
na mesma linha do tempo.

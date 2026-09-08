# Descrição da base utilizada

> Seção do README referente à base analítica. Escrita por Vinicius Moreira para
> integração no `README.md` do projeto.

## Origem e continuidade com a Fase 2

A base analítica desta fase é construída a partir das mesmas fontes que alimentaram a
camada Gold da Fase 2: o dataset público `br_inep_avaliacao_alfabetizacao` da Base dos
Dados, complementado pelo diretório de municípios do IBGE e pelas tabelas de população e
PIB municipal.

A equivalência entre as duas fases não é afirmada, é verificada. A consulta em
`notebooks/00_base_analitica.ipynb` reproduz o `fato_indicador` da Gold da Fase 2 e bate
em todas as métricas registradas naquela entrega:

| Métrica | Fase 2 | Reproduzido |
|---|---|---|
| Linhas | 23.995 | 23.995 |
| Municípios | 5.550 | 5.550 |
| Anos | 2 | 2 |
| Taxa mínima | 2,12 | 2,12 |
| Taxa máxima | 100,0 | 100,0 |

A Gold da Fase 2 entregava dados agregados por município. Como esta fase exige prever o
resultado de **um aluno**, a base foi reconstruída no grão de aluno a partir da mesma
origem, em vez de desagregada a partir do resultado já consolidado.

**Correção herdada da fase anterior:** na Fase 2 a tabela `fato_aluno_agregado` continha
dados de 2025, enquanto o `fato_indicador` cobria 2023 e 2024. Os períodos não se
sobrepunham, o que impedia o cruzamento previsto entre as duas tabelas. Nesta fase o alvo
e o contexto foram alinhados no mesmo período, e a inconsistência está resolvida.

## Composição da base

**Grão:** um aluno do 2º ano do Ensino Fundamental avaliado em 2024.

| | |
|---|---|
| Registros | 1.851.852 |
| Colunas | 26 |
| Municípios | 5.517 |
| Unidades federativas | 26 |
| Taxa de alfabetizados | 59,8% |

Foram excluídos os alunos ausentes na avaliação e aqueles cujo caderno de prova não foi
preenchido. Sem proficiência registrada não há como determinar o alvo, e mantê-los
introduziria ruído sem contrapartida informativa.

As variáveis cobrem quatro dimensões:

- **Educacionais** — rede de ensino, versão do caderno de prova, escola
- **Territoriais** — município, unidade federativa, macrorregião, mesorregião, condição
  de capital, pertencimento à Amazônia Legal
- **Socioeconômicas** — população, PIB municipal e valor adicionado por setor econômico
- **Metas de política pública** — metas pactuadas do Compromisso Nacional Criança
  Alfabetizada para 2024, 2026 e 2030, estrato de pactuação do município e percentual de
  participação na avaliação

## Definição do alvo

Um aluno é classificado como alfabetizado quando obtém **proficiência em Língua Portuguesa
igual ou superior a 743 pontos na escala Saeb** — o critério oficial do Indicador Criança
Alfabetizada, o mesmo que gerou os indicadores trabalhados na Fase 2.

A regra foi validada contra o campo de classificação da própria fonte: **zero divergências
em 1.851.852 registros**. A taxa nacional resultante, de 59,8%, é compatível com o
percentual divulgado pelo Inep para 2024.

## Tratamento de data leakage

O tratamento começa na construção da base, antes de qualquer etapa de modelagem. O
raciocínio central é que o vazamento neste problema não vem de uma coluna suspeita
isolada, mas de **agregações do próprio alvo** disponíveis na fonte.

**Removido do arquivo, não apenas documentado.** As colunas `proficiencia` e
`alfabetizado_fonte` são usadas para validar o alvo e descartadas antes da gravação do
Parquet. Elas não existem no arquivo que as demais etapas consomem — o vazamento mais
direto é impossível por construção, sem depender de nenhuma exclusão manual posterior.

**Agregações municipais do mesmo período ficaram fora.** As tabelas de município e de
unidade federativa da fonte trazem taxa de alfabetização, proficiência média e a
distribuição de alunos por nível de desempenho. Todas são funções do próprio alvo no mesmo
período. Nenhuma foi incorporada como variável explicativa.

**Contexto municipal entra com defasagem de um ano.** O desempenho do município é
representado pelos indicadores de 2023, anteriores ao alvo de 2024. É informação
legitimamente disponível no momento em que uma predição seria feita, e a distinção é a
data, não a coluna: os mesmos indicadores referentes a 2024 seriam vazamento.

A auditoria completa, coluna a coluna, com o papel de cada variável e a justificativa de
cada exclusão, está em `reports/dicionario_dados.md`.

## Reprodutibilidade

A base é gerada por consulta versionada em `notebooks/00_base_analitica.ipynb`, executável
sobre datasets públicos sem credencial privativa. A validação do alvo interrompe a
execução em caso de divergência com o critério oficial, impedindo que uma base com regra
de negócio inconsistente seja gravada.

Para desenvolvimento das demais etapas, o repositório inclui uma amostra estratificada por
unidade federativa, rede e alvo, com 296.292 registros — 16% da base, preservando a
distribuição do alvo em 59,8%.

## Limitações

**Cobertura desigual entre os anos.** A avaliação de 2023 alcançou 4.873 municípios contra
5.519 em 2024, por ser o primeiro ano de aplicação. Como consequência, 10,8% dos alunos
estão em municípios sem histórico anterior. A ausência não é aleatória: concentra
municípios menores e regiões específicas, o que exige cautela na interpretação dos
resultados para esses territórios.

**Defasagem dos dados econômicos.** Os valores adicionados setoriais do IBGE estão
publicados até 2021, e as variáveis econômicas foram fixadas nesse ano para manter
coerência interna entre elas. A defasagem é aceitável porque PIB municipal é característica
estrutural, com posição relativa estável entre municípios ao longo de poucos anos — e o
período coincide com a fase de educação infantil da coorte avaliada. Registra-se, porém,
que 2021 ainda refletia efeitos da pandemia, que atingiram os setores de forma desigual.

**Metas restritas à rede municipal.** As metas pactuadas existem apenas para a rede
Municipal. Elas foram incorporadas como atributo de contexto do território, aplicando-se a
todos os alunos do município independentemente da rede. É uma decisão deliberada: a meta
caracteriza o território, não o aluno.

**Recorte de série única.** A avaliação cobre exclusivamente o 2º ano do Ensino
Fundamental, de modo que os resultados não são extrapoláveis para outras etapas da
escolarização.

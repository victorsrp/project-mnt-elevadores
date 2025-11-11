# 📊 Regras de Negócio e Métricas do Dashboard

Este documento detalha as regras de negócio para a geração de dados simulados e a lógica de cálculo (Métricas DAX) para os KPIs e visuais do dashboard no Power BI, com base nos requisitos do projeto e no catálogo de dados.

---

## 1. 📋 Regras de Geração da Base de Dados

Estas regras garantem que os dados simulados (em CSV/Excel) sejam coesos e prontos para as métricas de MTBF e MTTR.

* **Volume de Dados:** A tabela `f_manutencoes` deverá conter entre 100 e 300 registros, conforme solicitado e previsto no catálogo.
* **Integridade Referencial:** Antes de gerar a `f_manutencoes`, todas as dimensões (`d_elevadores`, `d_tecnicos`, `d_tipo_falha`, `d_clientes`, `d_tempo`) devem ser criadas. As chaves estrangeiras em `f_manutencoes` (ex: `id_elevador`, `id_tecnico`) devem corresponder a IDs existentes nessas dimensões.
* **Lógica Temporal (MTBF/MTTR):**
    * Para calcular o **MTBF** (Tempo Médio Entre Falhas), os dados de `f_manutencoes` devem ser gerados de forma sequencial por elevador. O campo `tempo_entre_falhas_dias` deve ser a diferença (em dias) entre a `data_manutencao` de uma falha **corretiva** e a `data_manutencao` da falha **corretiva** anterior *para o mesmo* `id_elevador`.
    * Para calcular o **MTTR** (Tempo Médio Para Reparo), o campo `tempo_reparo_horas` deve ser preenchido, seguindo a regra de negócio do catálogo: falhas de criticidade 'alta' devem ter mais horas (5-10h) do que falhas de criticidade 'baixa' (1-2h).
* **Correlação de Custo:** O `custo_reparo_reais` deve ser diretamente proporcional ao `tempo_reparo_horas` e à `criticidade` da falha (extraída da `d_tipo_falha`). Manutenções "corretivas" devem ter, em média, um custo maior que as "preventivas".

---

## 2. 📊 Regras de Cálculo dos KPIs (Métricas DAX)

Esta é a lógica de cálculo (em linguagem DAX) que o Power BI usará para os *Indicadores Principais (KPI Cards)*:

* **Total de Elevadores Monitorados:**
    * `Total Elevadores = DISTINCTCOUNT(d_elevadores[id_elevador])`
* **Quantidade Total de Manutenções:**
    * `Total Manutenções = COUNTROWS(f_manutencoes)`
* **Custo Total de Manutenção:**
    * `Custo Total = SUM(f_manutencoes[custo_reparo_reais])`
* **Tempo Médio Para Reparo (MTTR):**
    * *Regra:* Deve calcular a média do `tempo_reparo_horas` **apenas** para manutenções do tipo "corretiva".
    * `MTTR (Horas) = CALCULATE( AVERAGE(f_manutencoes[tempo_reparo_horas]), f_manutencoes[tipo_manutencao] = "corretiva" )`
* **Tempo Médio Entre Falhas (MTBF):**
    * *Regra:* Deve calcular a média do `tempo_entre_falhas_dias` **apenas** para manutenções do tipo "corretiva" (onde uma "falha" ocorreu).
    * `MTBF (Dias) = CALCULATE( AVERAGE(f_manutencoes[tempo_entre_falhas_dias]), f_manutencoes[tipo_manutencao] = "corretiva" )`

---

## 3. 📈 Regras para Gráficos e Filtros

Esta é a regra de associação entre os campos do catálogo e os visuais solicitados:

* **Gráfico de Barras (Tipos de Manutenção):**
    * **Eixo:** Usar `f_manutencoes[tipo_manutencao]`.
    * **Valores:** Usar a métrica `[Total Manutenções]` (Contagem de `f_manutencoes`).
* **Gráfico de Linha (Evolução Mensal):**
    * **Eixo:** Usar a hierarquia de datas da `d_tempo` (ex: `d_tempo[Ano]` e `d_tempo[nome_mes]`). O relacionamento é `d_tempo[data]` conectada a `f_manutencoes[data_manutencao]`.
    * **Valores:** Usar a métrica `[Total Manutenções]`.
* **Gráfico de Pizza (Causas de Falhas):**
    * **Legenda:** Usar `d_tipo_falha[tipo_falha]` ou `d_tipo_falha[descricao_falha]`. O relacionamento é `d_tipo_falha[id_tipo_falha]` -> `f_manutencoes[id_tipo_falha]`.
    * **Valores:** Usar a métrica `[Total Manutenções]`, filtrado apenas para `tipo_manutencao = "corretiva"`.
* **Tabela Dinâmica (Histórico Detalhado):**
    * **Colunas:** Incluir campos das dimensões relacionadas, como: `f_manutencoes[data_manutencao]`, `d_elevadores[codigo_elevador]`, `d_tecnicos[nome_tecnico]`, `d_tipo_falha[descricao_falha]`, `f_manutencoes[custo_reparo_reais]` e `f_manutencoes[status_servico]`.
* **Comparativo de Custos (Preventiva vs. Corretiva):**
    * **Eixo:** Usar `f_manutencoes[tipo_manutencao]`.
    * **Valores:** Usar a métrica `[Custo Total]` (Soma de `f_manutencoes[custo_reparo_reais]`).

---

## 4. 🔎 Regras dos Filtros Interativos (Slicers)

* **Filtro por Tipo de Manutenção:** Deve usar o campo `f_manutencoes[tipo_manutencao]`.
* **Filtro por Período:** Deve usar os campos `d_tempo[ano]` e `d_tempo[nome_mes]`.
* **Filtro por Local do Elevador:** Deve usar os campos da `d_elevadores`, como `d_elevadores[bairro]`, `d_elevadores[cidade]` ou o campo composto `d_elevadores[localizacao_mapa]`.

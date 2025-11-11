# 📘 Catálogo de Dados — Projeto Manutenção de Elevadores

Este documento descreve todas as tabelas do projeto (dimensões e fatos) com suas colunas, tipos, descrições, exemplos e observações práticas para geração e controle dos dados.

---

## 🏢 Dimensão — d_elevadores

| Coluna | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| id_elevador | inteiro | Identificador único do elevador | 14 |
| codigo_elevador | texto | Código interno ou de patrimônio | ELV-014 |
| bairro | texto | Bairro onde o elevador está localizado | Vila Mariana |
| cidade | texto | Cidade de instalação do elevador | São Paulo |
| uf | texto | Unidade federativa (sigla) | SP |
| localizacao_mapa | texto | Campo concatenado para geolocalização no Power BI | Vila Mariana, São Paulo, SP |
| modelo | texto | Modelo do elevador | Atlas Sigma 2000 |
| ano_instalacao | inteiro | Ano de instalação do elevador | 2018 |
| fabricante | texto | Nome do fabricante | Otis |
| capacidade_kg | inteiro | Capacidade máxima de carga (em kg) | 600 |

### Notas:

* Gere `codigo_elevador` no formato "ELV-" + número sequencial.
* Use `faker.city()` para cidade, `faker.state_abbr()` para UF e `faker.bairro()` (ou lista customizada) para bairros.
* Crie `localizacao_mapa` como concatenação: `f"{bairro}, {cidade}, {uf}"`
* Distribua fabricantes entre uma lista curta (ex: \["Otis", "Atlas", "Schindler", "ThyssenKrupp"]).
* Evite acentos e padronize todos os textos em `snake_case` quando aplicável.

---

## 👷‍♂️ Dimensão — d_tecnicos

| Coluna | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| id_tecnico | inteiro | Identificador único do técnico | 5 |
| nome_tecnico | texto | Nome completo do técnico | Marcos Lima |
| nivel_experiencia | texto | Nível técnico (junior, pleno, senior) | pleno |
| regiao_atendimento | texto | Região principal de atuação (macro-região da cidade) | Zona Sul |
| cidade_base | texto | Cidade principal de operação do técnico | São Paulo |
| uf | texto | Unidade federativa (sigla) | SP |

### Notas:

* Use `faker.name()` para nomes.
* Distribua níveis (junior/pleno/senior) com pesos (ex: 40/40/20).
* Crie `regiao_atendimento` a partir de lista fixa (\["Zona Norte", "Zona Sul", "Zona Leste", "Zona Oeste", "Centro"]).
* Combine cidade + UF com mesma lógica da dimensão de elevadores.

---

## ⚙️ Dimensão — d_tipo_falha

| Coluna | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| id_tipo_falha | inteiro | Identificador da categoria de falha | 3 |
| tipo_falha | texto | Tipo principal da falha | elétrica |
| descricao_falha | texto | Descrição curta da falha | pane no motor ou fiação |
| criticidade | texto | Nível de criticidade (baixa, média, alta) | alta |

### Notas:

* Crie uma lista controlada com cerca de 8 a 10 tipos de falha.
* Relacione criticidade conforme a natureza da falha.
    * **Baixa:** ajustes simples (sensor, botão).
    * **Média:** falhas mecânicas leves.
    * **Alta:** falhas elétricas ou estruturais.
* As falhas servirão para alimentar indicadores de MTBF e MTTR.

---

## 🗓️ Dimensão — d_tempo

| Coluna | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| data | date | Data do evento | 2024-05-18 |
| ano | inteiro | Ano da data | 2024 |
| mes | inteiro | Mês (número) | 5 |
| nome_mes | texto | Nome do mês | Maio |
| trimestre | inteiro | Trimestre (1–4) | 2 |
| dia_semana | texto | Nome do dia da semana | Segunda-feira |

### Notas:

* Gerar via `pd.date_range('2023-01-01', '2025-12-31')`.
* Use `strftime` configurado para português para obter `nome_mes` e `dia_semana`.
* Esta tabela permitirá análises sazonais e cálculo de tendências no Power BI.

---

## 🏬 Dimensão — d_clientes

| Coluna | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| id_cliente | inteiro | Identificador único do cliente (condomínio ou empresa) | 8 |
| nome_cliente | texto | Nome do condomínio, prédio comercial ou empresa atendida | Condomínio Solar das Palmeiras |
| tipo_cliente | texto | Tipo de cliente (residencial, comercial, industrial) | residencial |
| cidade | texto | Cidade onde está localizado o cliente | São Paulo |
| bairro | texto | Bairro da unidade atendida | Vila Mariana |
| qtd_elevadores | inteiro | Quantidade total de elevadores no local | 4 |
| contrato_ativo | booleano | Indica se o contrato de manutenção está ativo | True |

### Notas:

* Use `faker.company()` ou nomes fictícios de condomínios.
* Distribua tipos de cliente em proporções aproximadas:
    * **residencial** (60%)
    * **comercal** (30%)
    * **industrial** (10%)
* `qtd_elevadores` pode variar entre 1 e 10, dependendo do tipo do cliente.
* Essa dimensão permitirá segmentar custos e indicadores de manutenção por cliente.

---

## 🧾 Fato — f_manutencoes

| Coluna | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| id_manutencao | inteiro | Identificador único da manutenção | 102 |
| id_elevador | inteiro | Chave estrangeira para d_elevadores | 14 |
| id_tecnico | inteiro | Chave estrangeira para d_tecnicos | 5 |
| id_tipo_falha | inteiro | Chave estrangeira para d_tipo_falha | 3 |
| id_cliente | inteiro | Chave estrangeira para d_clientes | 8 |
| data_manutencao | date | Data em que a manutenção foi executada | 2024-05-18 |
| tipo_manutencao | texto | Tipo da manutenção (preventiva ou corretiva) | corretiva |
| tempo_reparo_horas | float | Duração total do reparo em horas | 3.5 |
| tempo_entre_falhas_dias | float | Intervalo desde a última falha (MTBF) | 27.0 |
| custo_reparo_reais | float | Custo total da manutenção em reais | 820.50 |
| status_servico | texto | Situação da manutenção (concluído, pendente, cancelado) | concluído |
| observacoes | texto | Campo livre para anotações adicionais | substituição de motor |
| data_abertura | date | Data de abertura da ordem de serviço | 2024-05-16 |
| data_fechamento | date | Data de fechamento do serviço | 2024-05-18 |

### Regras de Negócio:

* **tipo_manutencao:** apenas “preventiva” ou “corretiva”.
* **tempo_reparo_horas:** correlacionar com criticidade da falha.
    * baixa → 1–2h
    * média → 2–5h
    * alta → 5–10h
* **tempo_entre_falhas_dias:** diferença entre manutenções sucessivas do mesmo elevador.
* **custo_reparo_reais:** vincular ao tempo de reparo e criticidade.
* **status_servico:** padrão “concluído”, podendo variar conforme simulação.
* Garantir que `data_fechamento` ≥ `data_abertura`.

---

## 🧩 Relacionamentos Entre Tabelas

```bash
d_clientes (1) ───< f_manutencoes >─── (1) d_elevadores
                    │
                    │
                    ├── (1) d_tecnicos
                    ├── (1) d_tipo_falha
                    └── (1) d_tempo
```
### Descrição:

* A tabela fato `f_manutencoes` centraliza todos os eventos de manutenção.
* Cada manutenção está associada a um elevador, um técnico, um tipo de falha, uma data e um cliente.
* O modelo segue o padrão estrela (Star Schema) — ideal para visualização e performance no Power BI.

---

## 🧠 Considerações Gerais

* Todos os nomes de tabelas e colunas seguem o padrão definido em `padroes_nomenclatura.md`.
* As dimensões devem ser geradas antes da tabela fato, para garantir integridade referencial.
* Os dados devem ser coerentes temporalmente, especialmente para métricas de MTBF e MTTR.
* O conjunto de dados final deverá conter entre 100 e 300 registros de manutenção (amostras realistas).

---

## 📄 Versão do Documento

* **Versão:** 1.0
* **Data:** Novembro/2025
* **Autor:** Victor Pereira
* **Projeto:** Manutenção de Elevadores – Base Simulada
* **Linguagem:** Português (BR)
* **Formato de Nomenclatura:** snake_case

# 📘 Padrões de Nomenclatura do Projeto

Este documento define as convenções de nomenclatura adotadas no projeto **TCC_Manutencao_Elevadores**, garantindo consistência entre scripts, tabelas, colunas, medidas e arquivos.

---

## 🧱 Convenção Geral

- Linguagem: **Português**
- Estilo: **snake_case** (letras minúsculas + underline)
- Evitar:
  - Acentos (`ã`, `é`, `ç` etc.)
  - Espaços ou caracteres especiais
  - Abreviações desnecessárias
- Priorizar nomes **claros e descritivos**, mesmo que mais longos.

**Exemplo:**
correto: tempo_reparo_horas
errado: TempoReparoHoras, tempoReparo, tmp_rep_hr

---

## 🗃️ Estrutura de Dados (Tabelas e Colunas)

### Tabelas
- **Fatos:** prefixo `f_`
- **Dimensões:** prefixo `d_`

**Exemplos:**
f_manutencoes
d_elevadores
d_tipo_falha
d_tecnicos
d_tempo

### Colunas
- Nomes descritivos e padronizados em `snake_case`
- Usar **id_** para chaves primárias e estrangeiras
- Unidades no nome quando relevante (ex: `_horas`, `_dias`, `_reais`)

**Exemplos:**
id_manutencao
id_elevador
tipo_falha
data_reparo
tempo_reparo_horas
custo_total_reais

---

## 🧩 Scripts (Python)

- Nomes de arquivos também seguem `snake_case`
- Usar verbos para scripts executáveis

**Exemplos:**  
gerar_dados.py  
calcular_metricas.py

Dentro do código:
- Variáveis: `snake_case`
- Funções: `snake_case`
- Constantes: `MAIUSCULO_COM_UNDERSCORE`

---

## 📊 Power BI / DAX

- Medidas devem usar **português e iniciais maiúsculas** (seguindo padrão visual de KPIs)
- Evitar abreviações técnicas no nome visível da medida

**Exemplos:**  
[Total Manutenções]  
[Custo Total]  
[MTTR (Horas)]  
[MTBF (Dias)]  

- Colunas calculadas seguem o padrão `snake_case`
- Tabelas dentro do modelo seguem o mesmo nome do arquivo de origem (`f_manutencoes`, `d_elevadores`, etc.)

---

## 🗂️ Estrutura de Pastas

Organização do repositório:  
/dados_origem # Bases simuladas (.xlsx)  
/dashboard # Arquivo .pbix do Power BI  
/docs # Documentação e diagramas  
/scripts # Scripts Python  

---

## 🧾 Padrões de Commit (Git)

- Usar mensagens curtas e descritivas, em português.
- Estrutura: `<tipo>: <descrição>`

**Tipos comuns:**
- `init:` configuração inicial
- `feat:` nova funcionalidade
- `fix:` correção de erro
- `docs:` documentação
- `style:` ajustes visuais ou layout
- `chore:` tarefas de manutenção

**Exemplos:**
init: adiciona estrutura inicial do projeto
feat: cria script de geração de dados simulados
docs: adiciona dicionário de dados e padrões de nomenclatura


---

## ✅ Resumo

| Categoria | Padrão |
|------------|---------|
| Linguagem | Português |
| Estilo | snake_case |
| Tabelas | f_ / d_ |
| Colunas | snake_case |
| Medidas DAX | Nome Capitalizado |
| Scripts | snake_case |
| Commits | tipo: descrição |

---

📄 **Versão:** 1.0  
📅 **Data:** Novembro/2025  
✍️ **Autor:** Victor Pereira

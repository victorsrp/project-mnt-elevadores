import pandas as pd
import random
import numpy as np
from faker import Faker
from datetime import timedelta, datetime
import locale

# --- 0. CONFIGURAÇÃO INICIAL ---

print("Iniciando a geração de dados (V2: Realista)...")

try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except locale.Error:
    print("Locale 'pt_BR.UTF-8' não encontrado, usando o padrão.")

fake = Faker('pt_BR')

# <--- MUDANÇA: Listas de regiões e níveis movidas para cá ---
REGIOES = ["Zona Norte", "Zona Sul", "Zona Leste", "Zona Oeste", "Centro"]
NIVEIS = ["junior", "pleno", "senior"]
N_MANUTENCOES = 300 # <--- MUDANÇA: Fixo em 300
N_ELEVADORES = 60
N_TECNICOS = 20
N_CLIENTES = 70


# --- 1. GERAÇÃO DAS DIMENSÕES ---

# 🗓️ d_tempo (Sem alterações)
print("Gerando d_tempo...")
datas = pd.date_range('2023-01-01', '2025-12-31', freq='D')
d_tempo = pd.DataFrame(datas, columns=['data'])
d_tempo['ano'] = d_tempo['data'].dt.year
d_tempo['mes'] = d_tempo['data'].dt.month
d_tempo['nome_mes'] = d_tempo['data'].dt.strftime('%B').str.capitalize()
d_tempo['trimestre'] = d_tempo['data'].dt.quarter
d_tempo['dia_semana'] = d_tempo['data'].dt.strftime('%A').str.capitalize()

# ⚙️ d_tipo_falha (Sem alterações)
print("Gerando d_tipo_falha...")
falhas_data = [
    {'id_tipo_falha': 1, 'tipo_falha': 'elétrica', 'descricao_falha': 'Pane no motor ou fiação', 'criticidade': 'alta'},
    {'id_tipo_falha': 2, 'tipo_falha': 'elétrica', 'descricao_falha': 'Falha no painel de controle', 'criticidade': 'média'},
    {'id_tipo_falha': 3, 'tipo_falha': 'mecânica', 'descricao_falha': 'Porta não fecha/abre', 'criticidade': 'média'},
    {'id_tipo_falha': 4, 'tipo_falha': 'mecânica', 'descricao_falha': 'Ruído excessivo ou vibração', 'criticidade': 'baixa'},
    {'id_tipo_falha': 5, 'tipo_falha': 'segurança', 'descricao_falha': 'Falha no sensor de porta', 'criticidade': 'baixa'},
    {'id_tipo_falha': 6, 'tipo_falha': 'segurança', 'descricao_falha': 'Parada de emergência acionada', 'criticidade': 'alta'},
    {'id_tipo_falha': 7, 'tipo_falha': 'preventiva', 'descricao_falha': 'Inspeção de rotina', 'criticidade': 'baixa'},
    {'id_tipo_falha': 8, 'tipo_falha': 'preventiva', 'descricao_falha': 'Lubrificação de componentes', 'criticidade': 'baixa'},
]
d_tipo_falha = pd.DataFrame(falhas_data)

# 🏬 d_clientes (Gerado primeiro, pois d_elevadores depende dele)
print("Gerando d_clientes...")
clientes_data = []
tipos_cliente = ["residencial", "comercial", "industrial"]
for i in range(1, N_CLIENTES + 1):
    tipo = random.choices(tipos_cliente, weights=[0.6, 0.3, 0.1], k=1)[0]
    if tipo == 'residencial':
        nome = f"Condomínio {fake.last_name()} {random.choice(['Gardens', 'Plaza', 'Towers'])}"
    else:
        nome = fake.company()
    clientes_data.append({
        'id_cliente': i,
        'nome_cliente': nome,
        'tipo_cliente': tipo,
        'cidade': fake.city(),
        'bairro': fake.bairro(),
        'qtd_elevadores': random.randint(1, 10),
        'contrato_ativo': random.choices([True, False], weights=[0.9, 0.1], k=1)[0]
    })
d_clientes = pd.DataFrame(clientes_data)

# 👷‍♂️ d_tecnicos (Sem grandes alterações, apenas usa a lista REGIOES)
print("Gerando d_tecnicos...")
tecnicos_data = []
for i in range(1, N_TECNICOS + 1):
    tecnicos_data.append({
        'id_tecnico': i,
        'nome_tecnico': fake.name(),
        'nivel_experiencia': random.choices(NIVEIS, weights=[0.4, 0.4, 0.2], k=1)[0],
        'regiao_atendimento': random.choice(REGIOES),
        'cidade_base': "São Paulo", # Simplificado
        'uf': "SP"
    })
d_tecnicos = pd.DataFrame(tecnicos_data)

# 🏢 d_elevadores
print("Gerando d_elevadores...")
elevadores_data = []
fabricantes = ["Otis", "Atlas", "Schindler", "ThyssenKrupp"]
modelos = ["Atlas Sigma 2000", "Otis Gen2", "Schindler 5500", "Thyssen Evo"]
for i in range(1, N_ELEVADORES + 1):
    bairro = fake.bairro()
    cidade = "São Paulo" # Simplificado para regiões
    uf = "SP"
    elevadores_data.append({
        'id_elevador': i,
        'codigo_elevador': f"ELV-{i:03d}",
        'bairro': bairro,
        'cidade': cidade,
        'uf': uf,
        'localizacao_mapa': f"{bairro}, {cidade}, {uf}",
        'modelo': random.choice(modelos),
        'ano_instalacao': random.randint(2010, 2023),
        'fabricante': random.choice(fabricantes),
        'capacidade_kg': random.choice([450, 600, 800]),
        'id_cliente': random.choice(d_clientes['id_cliente']), # <--- MUDANÇA 1: Elevador agora pertence a um cliente
        'regiao_atendimento': random.choice(REGIOES) # <--- MUDANÇA 3: Elevador agora tem uma região
    })
d_elevadores = pd.DataFrame(elevadores_data)

# <--- MUDANÇA 2: Criando o "Fator de Risco" para elevadores antigos ---
# Vamos dar um peso maior para elevadores mais antigos
ano_atual = datetime.now().year
d_elevadores['idade'] = ano_atual - d_elevadores['ano_instalacao']
# Cria um peso base (1) + 0.1 * idade. Um elevador de 10 anos terá peso 2.0
d_elevadores['fator_risco'] = 1 + (d_elevadores['idade'] * 0.1)


# --- 2. GERAÇÃO DA TABELA FATO ---

print("Gerando f_manutencoes (com lógica realista)...")
manutencoes_data = []

# Dicionários de consulta para performance (evita .loc em loop)
mapa_cliente_elevador = d_elevadores.set_index('id_elevador')['id_cliente'].to_dict()
mapa_regiao_elevador = d_elevadores.set_index('id_elevador')['regiao_atendimento'].to_dict()
mapa_tecnicos_regiao = d_tecnicos.groupby('regiao_atendimento')['id_tecnico'].apply(list).to_dict()

regras_criticidade = {
    'baixa': {'tempo_h': (1, 2.5), 'custo_base': 150},
    'média': {'tempo_h': (2, 5), 'custo_base': 400},
    'alta': {'tempo_h': (5, 10), 'custo_base': 800}
}
ids_preventiva = [7, 8]
ids_corretiva = [1, 2, 3, 4, 5, 6]

for i in range(1, N_MANUTENCOES + 1):
    
    tipo_manutencao = random.choices(["corretiva", "preventiva"], weights=[0.7, 0.3], k=1)[0]
    
    # --- Lógica de Geração Modificada ---
    
    id_elevador = 0
    if tipo_manutencao == "corretiva":
        # <--- MUDANÇA 2: Sorteio PONDERADO pelo fator_risco
        id_elevador = random.choices(
            d_elevadores['id_elevador'], 
            weights=d_elevadores['fator_risco'], 
            k=1
        )[0]
    else:
        # Manutenção preventiva é aleatória (agendada)
        id_elevador = random.choice(d_elevadores['id_elevador'])

    # <--- MUDANÇA 1: Cliente é pego do elevador, não sorteado
    id_cliente = mapa_cliente_elevador[id_elevador]
    
    # <--- MUDANÇA 3: Técnico é pego da região do elevador
    regiao_do_elevador = mapa_regiao_elevador[id_elevador]
    tecnicos_da_regiao = mapa_tecnicos_regiao.get(regiao_do_elevador, [])
    
    id_tecnico = 0
    if tecnicos_da_regiao:
        # Sorteia um técnico que atende aquela região
        id_tecnico = random.choice(tecnicos_da_regiao)
    else:
        # Fallback: se nenhuma técnico cobre a região (improvável), sorteia qualquer um
        id_tecnico = random.choice(d_tecnicos['id_tecnico'])

    # --- Fim da Lógica Modificada ---

    if tipo_manutencao == "corretiva":
        id_falha = random.choice(ids_corretiva)
    else:
        id_falha = random.choice(ids_preventiva)
        
    falha_info = d_tipo_falha.loc[d_tipo_falha['id_tipo_falha'] == id_falha].iloc[0]
    criticidade = falha_info['criticidade']
    regras = regras_criticidade[criticidade]
    
    data_abertura = fake.date_time_between(start_date=datetime(2023,1,1), end_date=datetime(2025,11,30))
    tempo_reparo = round(random.uniform(regras['tempo_h'][0], regras['tempo_h'][1]), 1)
    data_fechamento = data_abertura + timedelta(hours=tempo_reparo)
    
    custo_reparo = (regras['custo_base'] + (tempo_reparo * 80) + random.uniform(-50, 50))
    custo_reparo = round(custo_reparo, 2)

    if tipo_manutencao == "preventiva":
        custo_reparo = round(custo_reparo / 3, 2)
        
    manutencoes_data.append({
        'id_manutencao': i,
        'id_elevador': id_elevador,
        'id_tecnico': id_tecnico,
        'id_tipo_falha': id_falha,
        'id_cliente': id_cliente,
        'data_manutencao': data_fechamento.date(),
        'tipo_manutencao': tipo_manutencao,
        'tempo_reparo_horas': tempo_reparo,
        'custo_reparo_reais': custo_reparo,
        'status_servico': random.choices(["concluído", "pendente"], weights=[0.95, 0.05], k=1)[0],
        'observacoes': fake.sentence(nb_words=6) if tipo_manutencao == "corretiva" else "Manutenção preventiva padrão",
        'data_abertura': data_abertura.date(),
        'data_fechamento': data_fechamento.date(),
    })

f_manutencoes = pd.DataFrame(manutencoes_data)


# --- 3. PÓS-PROCESSAMENTO (CÁLCULO DE MTBF) ---
# (Sem alterações aqui, a lógica de cálculo do MTBF continua a mesma)

print("Calculando MTBF (tempo_entre_falhas_dias)...")
f_manutencoes['data_manutencao'] = pd.to_datetime(f_manutencoes['data_manutencao'])
f_manutencoes.sort_values(by=['id_elevador', 'data_manutencao'], inplace=True)

corretivas = f_manutencoes[f_manutencoes['tipo_manutencao'] == 'corretiva'].copy()
corretivas['data_ultima_falha'] = corretivas.groupby('id_elevador')['data_manutencao'].shift(1)
corretivas['tempo_entre_falhas_dias'] = (corretivas['data_manutencao'] - corretivas['data_ultima_falha']).dt.days

f_manutencoes = f_manutencoes.merge(
    corretivas[['id_manutencao', 'tempo_entre_falhas_dias']],
    on='id_manutencao',
    how='left'
)

# --- 4. EXPORTAÇÃO DOS ARQUIVOS ---
print("Exportando arquivos CSV...")

# Limpa colunas extras que não devem ir para o CSV (como 'idade' e 'fator_risco')
d_elevadores_export = d_elevadores.drop(columns=['idade', 'fator_risco'])

d_tempo['data'] = d_tempo['data'].dt.strftime('%Y-%m-%d')
f_manutencoes['data_manutencao'] = f_manutencoes['data_manutencao'].dt.strftime('%Y-%m-%d')
f_manutencoes['data_abertura'] = f_manutencoes['data_abertura'].astype(str)
f_manutencoes['data_fechamento'] = f_manutencoes['data_fechamento'].astype(str)

d_tempo.to_csv('d_tempo.csv', index=False, encoding='utf-8')
d_tipo_falha.to_csv('d_tipo_falha.csv', index=False, encoding='utf-8')
d_elevadores_export.to_csv('d_elevadores.csv', index=False, encoding='utf-8') # Exporta o Df limpo
d_tecnicos.to_csv('d_tecnicos.csv', index=False, encoding='utf-8')
d_clientes.to_csv('d_clientes.csv', index=False, encoding='utf-8')
f_manutencoes.to_csv('f_manutencoes.csv', index=False, encoding='utf-8')

print("\n--- Geração Concluída! (V2) ---")
print(f"Gerado {len(f_manutencoes)} registros de manutenção.")
print(f"Gerado {len(d_elevadores)} elevadores.")
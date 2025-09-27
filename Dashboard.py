import streamlit as st
import pandas as pd
from utils.google_sheets import df_vendas, df_metas
from utils.auth import verificar_autenticacao, login, get_usuario_atual, logout

# CONFIGURAÇÃO DA PÁGINA DEVE SER SEMPRE A PRIMEIRA COISA
st.set_page_config(page_title="Dashboard Vendas", layout="wide")

# VERIFICA AUTENTICAÇÃO - SE NÃO ESTIVER LOGADO, EXIBE LOGIN
if not verificar_autenticacao():
    login()

# SE CHEGOU ATÉ AQUI, O USUÁRIO ESTÁ AUTENTICADO
usuario = get_usuario_atual()

# SIDEBAR COM INFORMAÇÕES DO USUÁRIO E CONTROLES
with st.sidebar:
    st.write(f"Usuário: {usuario}")
    st.title("Dashboard de Vendas")
    
    # Botão de logout
    if st.button("Logout"):
        logout()

# ---------------------------
# CONFIGURAÇÕES DO DATAFRAME DE VENDAS
# ---------------------------
# Colunas que serão usadas para filtrar e exibir
COLUNAS_FILTRADAS_VENDAS = [
    "Data de Emissão", 
    "Descrição", 
    "Nro. Nota Fiscal",
    "Matriz",
    "Quantidade",
    "Valor Total"
]

COLUNAS_EXIBICAO_VENDAS = [
    "Data Venda", 
    "Descrição", 
    "Nro. Nota Fiscal",
    "Matriz",
    "Quantidade",
    "Valor Venda"
]

# ---------------------------
# INICIALIZAÇÃO DO DATAFRAME BASE DE VENDAS NO session_state
# ---------------------------
if "filtro_df_vendas_base" not in st.session_state:
    # Carrega dados e filtra colunas
    df_vendas_temp = pd.DataFrame(df_vendas)
    st.session_state["filtro_df_vendas_base"] = df_vendas_temp[COLUNAS_FILTRADAS_VENDAS].copy()

# Trabalha sempre em uma cópia do DataFrame base
filtro_df_vendas = st.session_state["filtro_df_vendas_base"].copy()

# ---------------------------
# LIMPEZA E FORMATAÇÃO DOS DADOS DE VENDAS
# ---------------------------
# Converte Valor Total para float (remove R$, pontos, substitui vírgula por ponto)
filtro_df_vendas["Valor Total"] = (
    filtro_df_vendas["Valor Total"]
    .astype(str)
    .str.replace("R\$", "", regex=True)
    .str.replace(".", "", regex=False)
    .str.replace(",", ".", regex=False)
    .str.replace(r"\s+", "", regex=True)
    .str.replace("^-", "-", regex=True)
    .replace("", 0)  # substitui strings vazias por 0
    .astype(float)
)

# Formata valor para exibição em Real brasileiro
filtro_df_vendas["Valor Venda"] = filtro_df_vendas["Valor Total"].apply(
    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

# Converte data para datetime e define como índice
filtro_df_vendas["Data de Emissão"] = pd.to_datetime(
    filtro_df_vendas["Data de Emissão"], 
    dayfirst=True,  # Formato brasileiro DD/MM/YYYY
    errors="coerce"  # Converte erros para NaT
)
filtro_df_vendas = filtro_df_vendas.set_index("Data de Emissão").sort_index()
# Cria coluna formatada para exibição
filtro_df_vendas["Data Venda"] = filtro_df_vendas.index.strftime("%d/%m/%Y")

# ---------------------------
# CONFIGURAÇÕES DO DATAFRAME DE METAS
# ---------------------------
if "filtro_df_metas_base" not in st.session_state:
    df_metas_temp = pd.DataFrame(df_metas)
    # Converte data para datetime
    df_metas_temp["Data"] = pd.to_datetime(df_metas_temp["Data"], dayfirst=True, errors="coerce")
    # Limpa e converte coluna Meta para float
    df_metas_temp["Meta"] = (
        df_metas_temp["Meta"]
        .astype(str)
        .str.replace("R\$", "", regex=True)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.replace(r"\s+", "", regex=True)
        .replace("", 0)
        .astype(float)
    )
    st.session_state["filtro_df_metas_base"] = df_metas_temp.copy()

filtro_df_metas = st.session_state["filtro_df_metas_base"].copy()

# ---------------------------
# SIDEBAR - FILTROS DE DATA
# ---------------------------
# Encontra o mês mais recente nos dados para definir valores padrão
mes_recente = filtro_df_vendas.index.max().to_period("M")
primeiro_dia = mes_recente.start_time.date()
ultimo_dia = mes_recente.end_time.date()

with st.sidebar:
    st.divider()
    # Inputs de data com valores padrão baseados no mês mais recente
    dt_inicio = st.date_input("Data Início:", value=primeiro_dia, format="DD/MM/YYYY")
    dt_fim = st.date_input("Data Fim:", value=ultimo_dia, format="DD/MM/YYYY")

# Converte para Timestamp para filtro correto no DataFrame
dt_inicio_ts = pd.Timestamp(dt_inicio)
dt_fim_ts = pd.Timestamp(dt_fim)

# ---------------------------
# FILTRAGEM DOS DADOS POR PERÍODO SELECIONADO
# ---------------------------
# Filtra vendas pelo período selecionado (usando índice de data)
df_vendas_filtrado = filtro_df_vendas.loc[dt_inicio_ts:dt_fim_ts]

# Filtra metas pelo período selecionado (comparando por mês)
filtro_df_metas_filtrado = filtro_df_metas[
    (filtro_df_metas["Data"].dt.to_period("M") >= dt_inicio_ts.to_period("M")) &
    (filtro_df_metas["Data"].dt.to_period("M") <= dt_fim_ts.to_period("M"))
]

# ---------------------------
# CÁLCULO DE MÉTRICAS
# ---------------------------
# Soma total de vendas e metas no período
soma_vendas = df_vendas_filtrado["Valor Total"].sum()
meta_soma = filtro_df_metas_filtrado["Meta"].sum()

# Calcula percentual atingido (evita divisão por zero)
percentual = (soma_vendas / meta_soma * 100) if meta_soma > 0 else 0

# Formata valores para exibição
soma_vendas_formatada = f"R$ {soma_vendas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
meta_soma_formatada = f"R$ {meta_soma:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
percentual_formatado = f"{percentual:.2f}%"

# ---------------------------
# EXIBIÇÃO DAS MÉTRICAS
# ---------------------------
st.subheader("Vendas")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Venda Período Selecionado", soma_vendas_formatada)
with col2:
    st.metric("Meta Período Selecionado", meta_soma_formatada)
with col3:
    st.metric("% Atingido", percentual_formatado)

# ---------------------------
# EXIBIÇÃO DO DATAFRAME DE VENDAS
# ---------------------------
# Prepara DataFrame para exibição
df_view_vendas = df_vendas_filtrado.copy()
df_exibicao_vendas = df_view_vendas[COLUNAS_EXIBICAO_VENDAS].reset_index(drop=True)
df_exibicao_vendas = df_exibicao_vendas.set_index("Data Venda")
st.dataframe(df_exibicao_vendas, use_container_width=True)
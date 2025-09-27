import streamlit as st
import pandas as pd
from utils.google_sheets import df_vendas, df_metas

# Configuração da página
st.set_page_config(layout="wide")

# ---------------------------
# Configurações df_vendas
# ---------------------------
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
# Criar state do DataFrame base df_vendas
# ---------------------------
if "filtro_df_vendas_base" not in st.session_state:
    df_vendas_temp = pd.DataFrame(df_vendas)
    st.session_state["filtro_df_vendas_base"] = df_vendas_temp[COLUNAS_FILTRADAS_VENDAS].copy()

# Trabalhar sempre em uma cópia
filtro_df_vendas = st.session_state["filtro_df_vendas_base"].copy()

# Conversão Valor Total -> Float
filtro_df_vendas["Valor Total"] = (
    filtro_df_vendas["Valor Total"]
    .astype(str)
    .str.replace("R\$", "", regex=True)
    .str.replace(".", "", regex=False)
    .str.replace(",", ".", regex=False)
    .str.replace(r"\s+", "", regex=True)
    .str.replace("^-", "-", regex=True)
    .astype(float)
)

# Formatar moeda
filtro_df_vendas["Valor Venda"] = filtro_df_vendas["Valor Total"].apply(
    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

# Converter Data de Emissão para datetime e definir index
filtro_df_vendas["Data de Emissão"] = pd.to_datetime(
    filtro_df_vendas["Data de Emissão"], 
    dayfirst=True,
    errors="coerce"
)
filtro_df_vendas = filtro_df_vendas.set_index("Data de Emissão").sort_index()
filtro_df_vendas["Data Venda"] = filtro_df_vendas.index.strftime("%d/%m/%Y")

# ---------------------------
# Configurações df_metas
# ---------------------------
if "filtro_df_metas_base" not in st.session_state:
    df_metas_temp = pd.DataFrame(df_metas)
    # Converte Data para datetime e mantém Meta
    df_metas_temp["Data"] = pd.to_datetime(df_metas_temp["Data"], dayfirst=True, errors="coerce")
    st.session_state["filtro_df_metas_base"] = df_metas_temp.copy()

filtro_df_metas = st.session_state["filtro_df_metas_base"].copy()

# ---------------------------
# Sidebar - filtro datas df_vendas
# ---------------------------
mes_recente = filtro_df_vendas.index.max().to_period("M")
primeiro_dia = mes_recente.start_time.date()
ultimo_dia = mes_recente.end_time.date()

with st.sidebar:
    dt_inicio = st.date_input("Data Início:", value=primeiro_dia, format="DD/MM/YYYY")
    dt_fim = st.date_input("Data Fim:", value=ultimo_dia, format="DD/MM/YYYY")

df_vendas_filtrado = filtro_df_vendas.loc[dt_inicio:dt_fim]

# ---------------------------
# Exibição df_vendas
# ---------------------------
df_view_vendas = df_vendas_filtrado.copy()
df_exibicao_vendas = df_view_vendas[COLUNAS_EXIBICAO_VENDAS].reset_index(drop=True)
df_exibicao_vendas = df_exibicao_vendas.set_index("Data Venda")

st.subheader("Vendas")
st.dataframe(df_exibicao_vendas, use_container_width=True)



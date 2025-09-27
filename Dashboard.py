import streamlit as st
import pandas as pd
from utils.google_sheets import df_vendas, df_metas

#Configuração da página
st.set_page_config(layout="wide")

#Variavel filtro coluna df
COLUNAS_FILTRADAS = [
    "Data de Emissão", 
    "Descrição", 
    "Nro. Nota Fiscal",
    "Matriz",
    "Quantidade",
    "Valor Total"
]

#Variavel filtro df view
COLUNAS_FILTRADAS_VIEW = [
    "Descrição", 
    "Nro. Nota Fiscal",
    "Matriz",
    "Quantidade",
    "Valor Total Formatado"
]

st.title("Dashboard")

#Seta o filtro das colunas no dataframe e seta a Data de Emissão como index
df = pd.DataFrame(df_vendas)
filtro_df = df[COLUNAS_FILTRADAS]

# Limpeza e conversão do "Valor Total"
filtro_df["Valor Total"] = (
    filtro_df["Valor Total"]
    .astype(str)                             # garante string
    .str.replace("R\$", "", regex=True)      # remove R$
    .str.replace(".", "", regex=False)       # remove pontos de milhar
    .str.replace(",", ".", regex=False)      # vírgula -> ponto
    .str.replace(r"\s+", "", regex=True)     # remove espaços extras
    .str.replace("^-", "-", regex=True)      # garante que - fique grudado
    .astype(float)                           # converte para número
)

# Formatar como moeda brasileira
filtro_df["Valor Total Formatado"] = filtro_df["Valor Total"].apply(
    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)



#Side Bar Dashboard

with st.sidebar:
  dt_inicio = st.date_input('Data Inicio:', format="DD/MM/YYYY")
  dt_fim = st.date_input('Data Fim:', format="DD/MM/YYYY")


# Exibe o dataframe ajustado com moeda brasileira
st.dataframe(filtro_df.dtypes)
st.dataframe(filtro_df)
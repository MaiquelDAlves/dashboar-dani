import streamlit as st
from utils.google_sheets import planilha_vendas, mostrar_planilha
from utils.filtros import filtro_principal
from module.sidebar import sidebar

data_planilha_vendas = mostrar_planilha(planilha_vendas)

def vendas(key_suffix):
    colunas_escolhidas = sidebar("vendas")  # 👈 key exclusiva para vendas
    df = filtro_principal(data_planilha_vendas)[colunas_escolhidas]
    st.dataframe(df)

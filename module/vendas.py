import streamlit as st
from utils.google_sheets import planilha_vendas, mostrar_planilha
from utils.filtros import filtro_principal
from module.sidebar import sidebar

# Carregar os dados da planilha de vendas
data_planilha_vendas = mostrar_planilha(planilha_vendas)

# Função para exibir os dados de vendas com filtros aplicados
def vendas(key_suffix):
    colunas_escolhidas = sidebar("vendas")  # 👈 key exclusiva para vendas
    df = filtro_principal(data_planilha_vendas)[colunas_escolhidas]
    if colunas_escolhidas == ["Valor Total"]:
        st.warning("Por favor, selecione pelo menos uma coluna")
    else:
      st.dataframe(df)
   

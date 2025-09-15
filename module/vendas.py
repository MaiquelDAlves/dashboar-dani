#vendas.py

import streamlit as st
from utils.google_sheets import planilha_vendas, mostrar_planilha
from utils.filtros import filtro_principal
from module.sidebar import sidebar
import time

# Carregar os dados da planilha de vendas
data_planilha_vendas = mostrar_planilha(planilha_vendas)

# Função para exibir os dados de vendas com filtros aplicados
def vendas(key_suffix):
    opcoes = sidebar(key_suffix)  # 👈 agora retorna dicionário
    df = filtro_principal(data_planilha_vendas)[opcoes["colunas"]]

    # Se não escolheu colunas
    if opcoes["colunas"] == ["Valor Total"]:
        st.warning("Por favor, selecione pelo menos uma coluna")
        return

    # Aplicar filtro
    if opcoes["filtrar"] and opcoes["filtro_coluna"] and opcoes["filtro_valor"]:
        df = df[df[opcoes["filtro_coluna"]] == opcoes["filtro_valor"]]

    # Reset filtro
    if opcoes["limpar"]:
        msg = st.empty()  # cria espaço temporário
        msg.success("Filtros removidos com sucesso!")
        time.sleep(2)     # espera 2 segundos
        msg.empty()       # remove a mensagem
        df = filtro_principal(data_planilha_vendas)[opcoes["colunas"]]

    st.dataframe(df)


   

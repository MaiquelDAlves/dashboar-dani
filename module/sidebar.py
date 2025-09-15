import streamlit as st
from utils.filtros import filtro_principal, filtro_coluna
from utils.google_sheets import planilha_vendas, mostrar_planilha

# Carregar os dados da planilha de vendas
data_planilha_vendas = mostrar_planilha(planilha_vendas)

def sidebar(key_suffix="vendas"):
    st.sidebar.title("Dashboard Dani")

    # Pega todas as colunas, exceto 'Valor Total'
    colunas_opcoes = [
        c for c in filtro_coluna(filtro_principal(data_planilha_vendas)) if c != "Valor Total"
    ]

    # Multiselect com key única
    opcao_multiselect = st.sidebar.multiselect(
        "Selecione as colunas para exibir:",
        options=colunas_opcoes,
        default=colunas_opcoes,
        key=f"colunas_{key_suffix}"   # 🔑 chave única por aba
    )

    # Garante que 'Valor Total' sempre esteja presente
    colunas_finais = opcao_multiselect + ["Valor Total"]

    return colunas_finais

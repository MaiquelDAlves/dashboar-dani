#sidebar.py

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

    # Selectbox para escolher a coluna de filtro
    opcao_selectbox_coluna = st.sidebar.selectbox(
        "Selecione a coluna para filtro:", 
        options=opcao_multiselect, 
        key=f"select_{key_suffix}"  
    )

    # Selectbox para escolher o valor
    opcao_selectbox_valor = None
    if opcao_selectbox_coluna:
        opcao_selectbox_valor = st.sidebar.selectbox(
            "Selecione o valor:",
            options=data_planilha_vendas[opcao_selectbox_coluna].unique(),
            key=f"valor_{key_suffix}"   
        )

    # Botões
    col1, col2 = st.sidebar.columns(2)
    status_filtrar = col1.button("Filtrar", key=f"btn_filtrar_{key_suffix}", width='stretch')
    status_limpar = col2.button("Limpar", key=f"btn_limpar_{key_suffix}", width='stretch')

    # Garante que 'Valor Total' sempre esteja presente
    colunas_finais = opcao_multiselect + ["Valor Total"]

    # Retorna TUDO necessário para aplicar no DataFrame
    return {
        "colunas": colunas_finais,
        "filtro_coluna": opcao_selectbox_coluna,
        "filtro_valor": opcao_selectbox_valor,
        "filtrar": status_filtrar,
        "limpar": status_limpar
    }

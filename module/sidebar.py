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
  

    filtro_sectbox_coluna = st.sidebar.selectbox(
        "Selecione a coluna:", 
        options=opcao_multiselect, 
        key=f"select_{key_suffix}"  # 🔑 chave
    )

    if not filtro_sectbox_coluna:
        return ["Valor Total"]  # Retorna apenas 'Valor Total' se nada for selecionado
    else:
        filtro_sectbox_valor = st.sidebar.selectbox(
            "Selecione o valor:",
            options=  data_planilha_vendas[filtro_sectbox_coluna].unique(),
            key=f"valor_{key_suffix}"  # 🔑 chave   
        )

    col1, col2 = st.sidebar.columns(2)
    col1.button("Filtrar", width='stretch')
    col2.button("Limpar", width='stretch')
        
    # Garante que 'Valor Total' sempre esteja presente
    colunas_finais = opcao_multiselect + ["Valor Total"]
    st.write(f"Colunas selecionadas: {colunas_finais}")
    return colunas_finais

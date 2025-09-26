# sidebar.py

import streamlit as st
from utils.filtros import filtro_principal, filtro_coluna
from utils.google_sheets import planilha_vendas, mostrar_planilha
import datetime
import pandas as pd

# Carregar os dados da planilha de vendas
data_planilha_vendas = mostrar_planilha(planilha_vendas)

def sidebar_datas(key_suffix="vendas"):
    """Apenas para selecionar datas - chamada uma vez"""
    st.sidebar.title("Dashboard Dani")

    # Garantir que "Data de Emissão" seja datetime
    data_planilha_vendas["Data de Emissão"] = pd.to_datetime(
        data_planilha_vendas["Data de Emissão"],
        dayfirst=True,
        errors="coerce"
    )

    # Determinar min e max do dataframe
    min_value = data_planilha_vendas["Data de Emissão"].min().date()
    max_value = data_planilha_vendas["Data de Emissão"].max().date()

    # Definir range inicial: primeiro dia do mês do max_value até max_value
    range_inicial = (datetime.date(max_value.year, max_value.month, 1), max_value)

    # Date input com KEY única
    data = st.sidebar.date_input(
        "Selecione uma data:",
        value=range_inicial,
        min_value=min_value,
        max_value=max_value,
        format="DD/MM/YYYY",
        key=f"date_input_{key_suffix}"
    )

    # Garantir que 'data' seja sempre tupla de duas datas
    if isinstance(data, datetime.date):
        data = (data, data)
    elif isinstance(data, (list, tuple)):
        if len(data) == 1:
            data = (data[0], data[0])
        elif len(data) == 0:
            data = range_inicial
        else:
            data = tuple(data)
    else:
        data = range_inicial

    return data

def sidebar_filtros(key_suffix="vendas", dados_filtrados_por_data=None):
    """Para os outros filtros - chamada depois com dados filtrados"""
    
    # Use dados filtrados se fornecidos, senão use dados completos
    dados_para_filtros = dados_filtrados_por_data if dados_filtrados_por_data is not None else data_planilha_vendas

    # Colunas disponíveis para filtro (usando dados filtrados!)
    colunas_opcoes = [
        c for c in filtro_coluna(filtro_principal(dados_para_filtros))
        if c not in ["Valor Total", "Quantidade", "Data de Emissão"]
    ]

    # COLUNAS FIXAS (sem multiselect)
    colunas_fixas = ["Data de Emissão"] + colunas_opcoes + ["Quantidade", "Valor Total"]

    # Selectbox para escolher a coluna de filtro
    opcao_selectbox_coluna = st.sidebar.selectbox(
        "Selecione a coluna para filtro:",
        options=["Todos"] + colunas_opcoes,
        key=f"select_{key_suffix}"
    )

    # Selectbox para escolher o valor (usando dados filtrados!)
    opcao_selectbox_valor = "Todos"  # Valor padrão
    
    # Só mostra selectbox de valor se uma coluna específica for selecionada
    if opcao_selectbox_coluna and opcao_selectbox_coluna != "Todos":
        # Ordenar valores únicos para melhor visualização
        valores_unicos = sorted(dados_para_filtros[opcao_selectbox_coluna].dropna().unique())
        opcao_selectbox_valor = st.sidebar.selectbox(
            "Selecione o valor:",
            options=["Todos"] + valores_unicos,
            key=f"valor_{key_suffix}"
        )

    return {
        "colunas": colunas_fixas,  # Colunas fixas em vez de dinâmicas
        "filtro_coluna": opcao_selectbox_coluna,
        "filtro_valor": opcao_selectbox_valor,
    }

# Função de compatibilidade para outros módulos
def sidebar(key_suffix="vendas"):
    """Função principal para compatibilidade com outros módulos"""
    datas = sidebar_datas(key_suffix)
    filtros = sidebar_filtros(key_suffix)
    
    # Combinar os resultados
    return {
        **filtros,
        "data": datas
    }
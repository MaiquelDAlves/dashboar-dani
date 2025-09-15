import streamlit as st
import pandas as pd
from utils.google_sheets import planilha_vendas, planilha_sellout, planilha_metas, mostrar_planilha

# Carregar os dados das planilhas
data_planilha_vendas = mostrar_planilha(planilha_vendas)

# Função para aplicar filtros aos dados
# Filtra as colunas específicas e define 'Data de Emissão' como índice
def filtro_principal(data):
    df = data[['Empresa', 
               'Data de Emissão', 
               'Descrição', 
               'Razão Social',
               'Grupo de Produto', 
               'Valor Total']
               ].set_index('Data de Emissão')
    return df

# Função para retornar as colunas do DataFrame filtrado
def filtro_coluna(filtro):
    col_filtrado = filtro.columns  
    return col_filtrado
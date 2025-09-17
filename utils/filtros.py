#filtros.py

import streamlit as st
import pandas as pd
from utils.google_sheets import planilha_vendas, planilha_sellout, planilha_metas, mostrar_planilha

COLUNAS_ANALISE = [
    'Empresa', 
    'Data de Emissão',
    'Quantidade', 
    'Descrição',
    'Matriz',
    'Grupo de Produto', 
    'Nro. Nota Fiscal',
    'Valor Total'
]

# Carregar os dados das planilhas
data_planilha_vendas = mostrar_planilha(planilha_vendas)

# Função para aplicar filtros aos dados
def filtro_principal(data):
    df = data[
      COLUNAS_ANALISE
    ]
    return df

# Função para retornar as colunas do DataFrame filtrado
def filtro_coluna(filtro):
    col_filtrado = filtro.columns  
    return col_filtrado

# Função para tratar os dados (converter tipos e formatar)

def tratar_dados(df):
    # Converter valor total para float - COM REGEX MELHOR
    if "Valor Total" in df.columns:
        df["Valor Total"] = (
            df["Valor Total"]
            .astype(str)
            .str.replace(r'[R$\s]', '', regex=True)  # Remove R$ e espaços
            .str.replace('.', '', regex=False)        # Remove pontos (milhares)
            .str.replace(',', '.', regex=False)       # Troca vírgula por ponto
            .astype(float)
        )

    if "Quantidade" in df.columns:
        df["Quantidade"] = pd.to_numeric(df["Quantidade"], errors="coerce").fillna(0).astype(int)

    if "Nro. Nota Fiscal" in df.columns:
        df["Nro. Nota Fiscal"] = df["Nro. Nota Fiscal"].fillna(0).astype(int)

    # Converter datas para datetime (mantenha como datetime)
    if "Data de Emissão" in df.columns:
        df["Data de Emissão"] = pd.to_datetime(
            df["Data de Emissão"], dayfirst=True, errors="coerce"
        )
    
    return df


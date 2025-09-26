#google_sheets.py

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
import os

# Escopos do Google
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_google_config():
    """Carrega configurações do Streamlit Secrets"""
    try:
        # Verifica se os secrets existem
        if not hasattr(st, 'secrets') or not st.secrets:
            raise ValueError("Secrets não disponíveis")
        
        # Obtém o ID da planilha
        planilha_id = st.secrets.get("GOOGLE_SHEETS_ID")
        if not planilha_id:
            raise ValueError("GOOGLE_SHEETS_ID não encontrado nos secrets")
        
        # Obtém as credenciais
        if "google_credentials" not in st.secrets:
            raise ValueError("google_credentials não encontrado nos secrets")
        
        creds_info = dict(st.secrets["google_credentials"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scopes=scopes)
        
        return planilha_id, creds
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar configurações: {e}")
        raise

# Inicializa as variáveis globais
try:
    planilha_id, creds = get_google_config()
    client = gspread.authorize(creds)
    planilha_completa = client.open_by_key(planilha_id)
    
    # Seleciona as abas da planilha
    planilha_vendas = planilha_completa.get_worksheet(0)
    planilha_sellout = planilha_completa.get_worksheet(1)
    planilha_metas = planilha_completa.get_worksheet(2)
    planilha_usuarios = planilha_completa.get_worksheet(3)
    
except Exception as e:
    # Define como None para evitar erros de importação
    planilha_vendas = None
    planilha_sellout = None
    planilha_metas = None
    planilha_usuarios = None
    print(f"⚠️ Aviso: Google Sheets não inicializado - {e}")

def mostrar_planilha(planilha):
    """Carrega dados da planilha"""
    if planilha is None:
        st.error("❌ Conexão com Google Sheets não disponível")
        return pd.DataFrame()
    
    try:
        dados = planilha.get_all_records()
        df = pd.DataFrame(dados)
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar planilha: {e}")
        return pd.DataFrame()
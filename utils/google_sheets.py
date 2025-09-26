#google_sheets.py

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
import json
import os

# Escopos do Google
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_google_sheets_config():
    """Obtém configuração de forma segura para ambos os ambientes"""
    
    # 1. Tenta carregar do Streamlit Secrets (deploy)
    try:
        if hasattr(st, 'secrets'):
            # Verifica se existe GOOGLE_SHEETS_ID nos secrets
            if 'GOOGLE_SHEETS_ID' in st.secrets:
                planilha_id = st.secrets['GOOGLE_SHEETS_ID']
                
                # Verifica se as credenciais estão nos secrets
                if 'google_credentials' in st.secrets:
                    # Converte as credenciais do TOML para dict
                    creds_info = dict(st.secrets.google_credentials)
                    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scopes=scopes)
                    return planilha_id, creds, "streamlit_secrets"
    except Exception as e:
        print(f"Erro ao carregar secrets: {e}")
        pass
    
    # 2. Fallback para local (NUNCA será executado no Streamlit Cloud)
    try:
        from dotenv import load_dotenv
        load_dotenv()
        planilha_id = os.getenv("GOOGLE_SHEETS_ID")
        
        if not planilha_id:
            raise ValueError("GOOGLE_SHEETS_ID não encontrado")
            
        # Tenta carregar do arquivo credentials.json
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scopes=scopes)
        return planilha_id, creds, "local"
    except Exception as e:
        print(f"Erro ao carregar localmente: {e}")
        raise ValueError("Não foi possível carregar as configurações em nenhum ambiente")

# Carrega configurações
try:
    planilha_id, creds, source = get_google_sheets_config()
    print(f"✅ Configurações carregadas de: {source}")
    
    client = gspread.authorize(creds)
    planilha_completa = client.open_by_key(planilha_id)
    
    # Seleciona as abas da planilha
    planilha_vendas = planilha_completa.get_worksheet(0)
    planilha_sellout = planilha_completa.get_worksheet(1)
    planilha_metas = planilha_completa.get_worksheet(2)
    planilha_usuarios = planilha_completa.get_worksheet(3)
    
except Exception as e:
    # Define variáveis como None para evitar erros de importação
    planilha_vendas = None
    planilha_sellout = None
    planilha_metas = None
    planilha_usuarios = None
    print(f"❌ Erro ao inicializar Google Sheets: {e}")

# Função para criar o data frame
def mostrar_planilha(planilha):
    if planilha is None:
        st.error("❌ Conexão com Google Sheets não inicializada")
        return pd.DataFrame()
    
    dados = planilha.get_all_records()
    df = pd.DataFrame(dados)
    return df
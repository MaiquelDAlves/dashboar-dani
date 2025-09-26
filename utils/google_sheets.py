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

def init_google_sheets():
    """Inicializa a conexão com Google Sheets de forma segura"""
    try:
        # Verifica se está no Streamlit Cloud (com secrets)
        if hasattr(st, 'secrets') and st.secrets:
            # Tenta carregar do Streamlit Secrets
            if 'GOOGLE_SHEETS_ID' in st.secrets and 'google_credentials' in st.secrets:
                planilha_id = st.secrets['GOOGLE_SHEETS_ID']
                creds_info = dict(st.secrets['google_credentials'])
                
                creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scopes=scopes)
                client = gspread.authorize(creds)
                planilha_completa = client.open_by_key(planilha_id)
                
                return {
                    'vendas': planilha_completa.get_worksheet(0),
                    'sellout': planilha_completa.get_worksheet(1),
                    'metas': planilha_completa.get_worksheet(2),
                    'usuarios': planilha_completa.get_worksheet(3),
                    'client': client
                }
        
        # Fallback para ambiente local
        from dotenv import load_dotenv
        load_dotenv()
        planilha_id = os.getenv("GOOGLE_SHEETS_ID")
        
        if planilha_id:
            creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scopes=scopes)
            client = gspread.authorize(creds)
            planilha_completa = client.open_by_key(planilha_id)
            
            return {
                'vendas': planilha_completa.get_worksheet(0),
                'sellout': planilha_completa.get_worksheet(1),
                'metas': planilha_completa.get_worksheet(2),
                'usuarios': planilha_completa.get_worksheet(3),
                'client': client
            }
    
    except Exception as e:
        print(f"❌ Erro ao inicializar Google Sheets: {e}")
    
    return None

# Inicializa as conexões
sheets_connection = init_google_sheets()

# Define as variáveis globais
if sheets_connection:
    planilha_vendas = sheets_connection['vendas']
    planilha_sellout = sheets_connection['sellout']
    planilha_metas = sheets_connection['metas']
    planilha_usuarios = sheets_connection['usuarios']
else:
    planilha_vendas = None
    planilha_sellout = None
    planilha_metas = None
    planilha_usuarios = None

def mostrar_planilha(planilha):
    """Carrega dados da planilha com tratamento de erro"""
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
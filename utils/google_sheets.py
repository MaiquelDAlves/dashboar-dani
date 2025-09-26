#google_sheets.py

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os

# Escopos do Google
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_google_sheets_config():
    """Obtém configuração de forma segura para ambos os ambientes"""
    try:
        # Tenta importar streamlit e verificar secrets (apenas se estiver em execução)
        import streamlit as st
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        
        # Só tenta usar st.secrets se estiver em uma sessão do Streamlit
        if get_script_run_ctx() is not None:
            try:
                if hasattr(st, 'secrets') and st.secrets:
                    planilha_id = st.secrets.get('GOOGLE_SHEETS_ID')
                    if planilha_id:
                        if 'google_credentials' in st.secrets:
                            creds_info = dict(st.secrets['google_credentials'])
                            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scopes=scopes)
                            return planilha_id, creds, "streamlit_secrets"
            except:
                pass
    except:
        pass
    
    # Fallback para local
    from dotenv import load_dotenv
    load_dotenv()
    planilha_id = os.getenv("GOOGLE_SHEETS_ID")
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scopes=scopes)
    return planilha_id, creds, "local"

# Carrega configurações
planilha_id, creds, source = get_google_sheets_config()

if not planilha_id or not creds:
    raise ValueError("Não foi possível carregar as configurações do Google Sheets")

print(f"✅ Configurações carregadas de: {source}")

client = gspread.authorize(creds)
planilha_completa = client.open_by_key(planilha_id)

# Seleciona as abas da planilha
planilha_vendas = planilha_completa.get_worksheet(0)
planilha_sellout = planilha_completa.get_worksheet(1)
planilha_metas = planilha_completa.get_worksheet(2)
planilha_usuarios = planilha_completa.get_worksheet(3)

# Função para criar o data frame
def mostrar_planilha(planilha):
    dados = planilha.get_all_records()
    df = pd.DataFrame(dados)
    return df
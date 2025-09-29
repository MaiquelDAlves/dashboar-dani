import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
import json

# Carrega variáveis locais (.env) quando não está no Streamlit Cloud
load_dotenv()

def get_google_sheets_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    try:
        # Modo Streamlit Cloud (usa st.secrets)
        if "google_sheets" in st.secrets:
            creds_dict = dict(st.secrets["google_sheets"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(
                creds_dict, scopes=scope
            )
        else:
            # Modo local - usa credentials.json
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            file_name = os.path.join(os.path.dirname(BASE_DIR), "credentials.json")
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                filename=file_name, scopes=scope
            )
    except Exception as e:
        st.error(f"Erro ao carregar credenciais: {e}")
        return None

    client = gspread.authorize(creds)
    return client

def load_data(aba):
    client = get_google_sheets_client()
    if client is None:
        return pd.DataFrame()

    # Pega o SHEET_ID dos secrets ou do .env
    SHEET_ID = (
        st.secrets.get("GOOGLE_SHEETS_ID")
        if "GOOGLE_SHEETS_ID" in st.secrets
        else os.getenv("GOOGLE_SHEETS_ID")
    )

    if not SHEET_ID:
        st.error("❌ ID da planilha não encontrado. Configure GOOGLE_SHEETS_ID no .env ou no secrets.")
        return pd.DataFrame()

    try:
        planilha_completa = client.open_by_key(SHEET_ID)
        planilha_vendas = planilha_completa.get_worksheet(aba)
        dados = planilha_vendas.get_all_records()
        df = pd.DataFrame(dados)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# Carregar os DataFrames (mantém compatibilidade com seu código atual)
df_vendas = load_data(0)
df_metas = load_data(2)

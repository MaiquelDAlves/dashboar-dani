# utils/google_sheets.py

import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import json
import streamlit as st

def get_google_sheets_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Verifica se está rodando no Streamlit Cloud (secrets disponíveis)
    if hasattr(st, 'secrets') and 'google_sheets' in st.secrets:
        # Usa os secrets do Streamlit
        creds_dict = dict(st.secrets['google_sheets'])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scopes=scope)
    else:
        # Modo local - usa o arquivo credentials.json
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        file_name = os.path.join(os.path.dirname(BASE_DIR), "credentials.json")
        creds = ServiceAccountCredentials.from_json_keyfile_name(filename=file_name, scopes=scope)
    
    client = gspread.authorize(creds)
    return client

def load_data(aba):
    client = get_google_sheets_client()
    
    # Use o ID da planilha diretamente
    SHEET_ID = "1QfKzFTBHllSmWcYHSeLq9pvqGSx6DPeTVe3eYvVKUXY"
    
    try:
        planilha_completa = client.open_by_key(SHEET_ID)
        planilha_vendas = planilha_completa.get_worksheet(aba)
        dados = planilha_vendas.get_all_records()
        df = pd.DataFrame(dados)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# Carregar os DataFrames
df_vendas = load_data(0)
df_metas = load_data(2)
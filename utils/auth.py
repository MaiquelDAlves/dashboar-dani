# utils/auth.py

import streamlit as st
import streamlit_authenticator as stauth
from utils.google_sheets import planilha_usuarios, mostrar_planilha
import pandas as pd

def carregar_usuarios():
    """Carrega os usuários da planilha do Google Sheets e retorna no formato esperado"""
    try:
        df = mostrar_planilha(planilha_usuarios)
        if df.empty:
            return None

        credentials = {"usernames": {}}

        for _, row in df.iterrows():
            username = row["username"]
            credentials["usernames"][username] = {
                "name": row["name"],
                "password": row["password"],  # já deve estar em hash
                "email": row.get("email", "")
            }

        return credentials

    except Exception as e:
        st.error(f"Erro ao carregar usuários: {e}")
        return None


def configurar_autenticador():
    """Configura e retorna o autenticador"""
    credentials = carregar_usuarios()
    
    if not credentials:
        st.error("Nenhum usuário encontrado ou erro ao carregar usuários")
        return None
    
    authenticator = stauth.Authenticate(
        credentials,
        'dashboard_dani',  # Nome do cookie
        'auth_key',        # Chave para criptografia
        30                 # Dias de expiração do cookie
    )
    
    return authenticator

import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd

def carregar_usuarios():
    """Carrega os usuários da planilha do Google Sheets"""
    try:
        from utils.google_sheets import planilha_usuarios, mostrar_planilha
        
        df = mostrar_planilha(planilha_usuarios)
        if df.empty:
            st.warning("Nenhum usuário encontrado na planilha")
            return None

        credentials = {"usernames": {}}

        for _, row in df.iterrows():
            username = row["username"]
            credentials["usernames"][username] = {
                "name": row["name"],
                "password": row["password"],
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
        # Cria um usuário padrão de fallback
        credentials = {
            "usernames": {
                "admin": {
                    "name": "Administrador",
                    "password": stauth.Hasher(["admin123"]).generate()[0],
                    "email": "admin@empresa.com"
                }
            }
        }
        st.warning("Usando usuário padrão de fallback")
    
    authenticator = stauth.Authenticate(
        credentials,
        'dashboard_dani',
        'auth_key',
        30
    )
    
    return authenticator

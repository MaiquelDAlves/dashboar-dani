import streamlit as st
from datetime import datetime, timedelta
import hashlib
import os
from dotenv import load_dotenv

# Carrega variáveis do .env apenas localmente
load_dotenv()

def get_usuario_senha(usuario):
    """
    Obtém a senha do usuário do .env (local) ou st.secrets (Streamlit Cloud)
    """
    try:
        # Tenta primeiro o Streamlit Secrets (produção)
        if hasattr(st, 'secrets') and 'USUARIOS' in st.secrets:
            return st.secrets['USUARIOS'].get(usuario.lower(), "")
        else:
            # Fallback para .env (desenvolvimento local)
            chave_env = f"USUARIO_{usuario.upper()}"
            return os.getenv(chave_env, "")
    except Exception:
        return ""

def init_auth():
    if "auth" not in st.session_state:
        st.session_state.auth = {
            "logado": False,
            "usuario": "",
            "expiracao": None
        }

def autenticar_usuario(usuario, senha):
    if not usuario or not senha:
        return False
    
    # Obtém a senha correta do ambiente
    senha_correta = get_usuario_senha(usuario)
    
    if not senha_correta:
        return False
    
    # Verifica a senha
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    senha_correta_hash = hashlib.sha256(senha_correta.encode()).hexdigest()
    
    return senha_hash == senha_correta_hash

def login():
    init_auth()

    if st.session_state.auth["logado"]:
        expiracao = st.session_state.auth["expiracao"]
        if expiracao and datetime.now() < expiracao:
            return True
        else:
            logout()

    st.title("🔐 Login - Dashboard Vendas")
    st.write("Por favor, faça login para acessar o sistema")

    with st.form("login_form"):
        usuario = st.selectbox("Usuário", ["maiquel", "daniela"])
        senha = st.text_input("Senha", type="password")
        lembrar = st.checkbox("Manter conectado por 30 dias", value=True)
        submit = st.form_submit_button("Entrar")

        if submit:
            if autenticar_usuario(usuario, senha):
                dias = 30 if lembrar else 1
                expiracao = datetime.now() + timedelta(days=dias)
                st.session_state.auth = {
                    "logado": True,
                    "usuario": usuario,
                    "expiracao": expiracao
                }
                st.success(f"Bem-vindo, {usuario}!")
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")

    st.stop()

def logout():
    st.session_state.auth = {
        "logado": False,
        "usuario": "",
        "expiracao": None
    }
    st.rerun()

def get_usuario_atual():
    init_auth()
    return st.session_state.auth.get("usuario", "")

def verificar_autenticacao():
    init_auth()
    if st.session_state.auth["logado"]:
        expiracao = st.session_state.auth["expiracao"]
        if expiracao and datetime.now() < expiracao:
            return True
        else:
            logout()
    return False
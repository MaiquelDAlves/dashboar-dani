import streamlit as st
from datetime import datetime, timedelta
import hashlib
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Usuários válidos (hashes gerados a partir do .env)
USUARIOS = {
    "maiquel": hashlib.sha256(os.getenv("USUARIO_MAIQUEL", "").encode()).hexdigest(),
    "daniela": hashlib.sha256(os.getenv("USUARIO_DANIELA", "").encode()).hexdigest()
}

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
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    return usuario in USUARIOS and USUARIOS[usuario] == senha_hash

def login():
    init_auth()

    if st.session_state.auth["logado"]:
        expiracao = st.session_state.auth["expiracao"]
        if expiracao and datetime.now() < expiracao:
            return True
        else:
            logout()

    st.title("Login")
    st.write("Por favor, faça login para acessar o sistema")

    with st.form("login_form"):
        usuario = st.text_input("Usuário")
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

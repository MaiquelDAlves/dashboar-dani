# utils/password_utils.py
import streamlit_authenticator as stauth
import streamlit as st

def gerar_hash_senha(senha):
    """Gera hash de uma senha para armazenamento seguro"""
    return stauth.Hasher([senha]).generate()[0]

def criar_usuario_interativo():
    """Interface para criar novo usuário (apenas para administradores)"""
    st.title("Criar Novo Usuário")
    
    with st.form("novo_usuario"):
        username = st.text_input("Username")
        nome = st.text_input("Nome Completo")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        confirmar_senha = st.text_input("Confirmar Senha", type="password")
        
        submitted = st.form_submit_button("Criar Usuário")
        
        if submitted:
            if senha != confirmar_senha:
                st.error("Senhas não coincidem")
                return
                
            if not all([username, nome, email, senha]):
                st.error("Todos os campos são obrigatórios")
                return
                
            senha_hash = gerar_hash_senha(senha)
            
            # Aqui você pode adicionar lógica para salvar no Google Sheets
            st.success(f"Usuário criado! Hash da senha: {senha_hash}")
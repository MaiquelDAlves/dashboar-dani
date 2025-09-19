# main.py (versão melhorada)
import streamlit as st
from utils.configuracoes_pg import configuracoes_pg
from utils.auth import configurar_autenticador
import module.menu as menu
import time

# Inicializar estados
if 'is_loading' not in st.session_state:
    st.session_state.is_loading = False
if 'show_login' not in st.session_state:
    st.session_state.show_login = True

# Mostrar spinner durante o carregamento
if st.session_state.is_loading:
    with st.spinner('Carregando dashboard...'):
        time.sleep(0.3)  # Delay suficiente para evitar flickering
    st.session_state.is_loading = False
    st.rerun()

# Configuração base - será ajustada conforme necessidade
if st.session_state.show_login:
    st.set_page_config(
        page_title="Dashboard Dani - Login",
        page_icon="🔐",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
else:
    configuracoes_pg()

authenticator = configurar_autenticador()

if authenticator:
    if st.session_state.get('authentication_status'):
        # Usuário autenticado - mostrar dashboard
        st.session_state.show_login = False
        
        # Botão de logout com tratamento adequado
        if authenticator.logout('Logout', 'sidebar'):
            st.session_state.clear()
            st.session_state.show_login = True
            st.session_state.is_loading = True
            st.rerun()
        
        st.sidebar.write(f'Bem-vindo(a), *{st.session_state["name"]}*!')
        menu.menu()
        
    else:
        # Mostrar tela de login
        st.session_state.show_login = True
        
        name, authentication_status, username = authenticator.login('Login', 'main')
        
        if authentication_status:
            st.session_state.is_loading = True
            st.rerun()
        elif authentication_status == False:
            st.error('Usuário/senha incorretos')
        elif authentication_status == None:
            st.warning('Por favor, digite seu usuário e senha')
            
else:
    st.set_page_config(
        page_title="Dashboard Dani - Erro",
        page_icon="❌",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    st.error("Sistema de autenticação não disponível. Contate o administrador.")
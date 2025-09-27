import streamlit as st
from utils.auth import verificar_autenticacao, login, get_usuario_atual

# CONFIGURAÇÃO DA PÁGINA (SEMPRE PRIMEIRO)
st.set_page_config(page_title="Sellout", layout="wide")

# VERIFICA AUTENTICAÇÃO - REDIRECIONA PARA LOGIN SE NECESSÁRIO
if not verificar_autenticacao():
    login()

# SE CHEGOU ATÉ AQUI, USUÁRIO ESTÁ AUTENTICADO
usuario = get_usuario_atual()

# SIDEBAR COM INFORMAÇÕES DO USUÁRIO
with st.sidebar:
    st.write(f"Usuário: {usuario}")
    st.title("Sellout")

# CONTEÚDO PRINCIPAL DA PÁGINA SELLOUT
st.title("Sellout")
st.write("Conteúdo da página Sellout...")
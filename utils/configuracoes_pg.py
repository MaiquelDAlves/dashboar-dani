import streamlit as st

def configuracoes_pg():
   st.set_page_config(
    page_title="Dashboard Dani",   # Título da aba do navegador
    page_icon="📊",               # Ícone da aba
    layout="wide",                # Layout: "centered" (padrão) ou "wide"
    initial_sidebar_state="expanded"  # Estado inicial da sidebar: "expanded", "collapsed" ou "auto"
)
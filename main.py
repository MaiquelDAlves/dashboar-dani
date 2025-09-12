import module.vendas as vendas
import module.sellout as sellout
import module.metas as metas
import streamlit as st
from utils.configuracoes_pg import configuracoes_pg

# Configurações da página
configuracoes_pg()

st.sidebar.title("Dashboard Dani")

# Criação das abas
tab1, tab2, tab3 = st.tabs(["Vendas", "Sell-out", "Metas"])

with tab1:
    st.header("Vendas")
    vendas.vendas()
with tab2:
    st.header("Sell-out ")
    sellout.sellout() 
with tab3:
    st.header("Metas")
    metas.metas()

import module.vendas as vendas
import module.sellout as sellout
import module.metas as metas
import streamlit as st
from utils.configuracoes_pg import configuracoes_pg

# Configurações da página
configuracoes_pg()


# Session statde de configuração da página
if 'pagina atual' not in st.session_state:
    st.session_state['pagina atual'] = 'Vendas'




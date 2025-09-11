import streamlit as st
from streamlit_option_menu import option_menu
import module.vendas as vendas
import module.sellout as sellout
import module.metas as metas
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente
load_dotenv()

# Configuração inicialização pagina
st.set_page_config(page_title="Dashboard Dani", layout="wide")

# Cabeçalho com menu horizontal
with st.container():
    selected = option_menu(
        menu_title="📊 Dashboard Dani",
        options=["Vendas", "Sell-out", "Metas"],
        icons=["cart", "bar-chart", "target"],
        orientation="horizontal",
        default_index=0,
    )

# Roteamento simples
if selected == "Vendas":
    vendas.show()
elif selected == "Sell-out":
    sellout.show()
elif selected == "Metas":
    metas.show()
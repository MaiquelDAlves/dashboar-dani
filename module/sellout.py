#sellout.py

import streamlit as st
from utils.google_sheets import planilha_sellout, mostrar_planilha
from utils.filtros import filtro_principal
from module.sidebar import sidebar

data_planilha_sellout = mostrar_planilha(planilha_sellout)

def sellout(key_suffix):
    st.write("### Sell-out")

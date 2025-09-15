import streamlit as st
from utils.google_sheets import planilha_metas, mostrar_planilha
from utils.filtros import filtro_principal
from module.sidebar import sidebar

data_planilha_metas = mostrar_planilha(planilha_metas)

def metas(key_suffix):
    st.write("### Metas")

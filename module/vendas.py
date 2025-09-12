import streamlit as st
import pandas as pd
from utils.google_sheets import planilha_vendas, planilha_sellout, planilha_metas, mostrar_planilha

data_planilha_vendas = mostrar_planilha(planilha_vendas)

def vendas():
  st.title("Módulo de Vendas")
  st.write(data_planilha_vendas)
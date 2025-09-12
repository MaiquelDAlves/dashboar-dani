import streamlit as st
import pandas as pd
from utils.google_sheets import planilha_vendas, planilha_sellout, planilha_metas, mostrar_planilha

# Carregar os dados da planilha de vendas
data_planilha_vendas = mostrar_planilha(planilha_vendas)

# Função para exibir os dados da planilha de vendas
def vendas():
  st.write(data_planilha_vendas)
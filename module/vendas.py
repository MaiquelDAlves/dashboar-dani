import streamlit as st
import pandas as pd
from utils.google_sheets import planilha_vendas, planilha_sellout, planilha_metas, mostrar_planilha

def vendas():
  st.title("Módulo de Vendas")
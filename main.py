# main.py

import streamlit as st
from utils.google_sheets import df_vendas, df_metas

st.title("Primeira aba da planilha")

if df_vendas is not None and not df_vendas.empty:
    st.dataframe(df_vendas)
    st.dataframe(df_metas)
else:
    st.warning("Nenhum dado foi carregado. Verifique a conexão com o Google Sheets.")
#menu.py

import streamlit as st
import module.vendas as vendas
import module.sellout as sellout
import module.metas as metas

def menu():
  tab1, tab2, tab3 = st.tabs(["Vendas", "Sell-out", "Metas"])

  with tab1:
      st.header("Vendas")
      vendas.vendas("vendas")
  with tab2:
      st.header("Sell-out ")
      sellout.sellout("sellout") 
  with tab3:
      st.header("Metas")
      metas.metas("metas")
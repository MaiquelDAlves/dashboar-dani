import streamlit as st
from utils.configuracoes_pg import configuracoes_pg
import module.sidebar as sidebar
import module.menu as menu

# Configurações da página
configuracoes_pg()

# Visualizaçõ do sidebar
sidebar.sidebar()

# Criação das abas
menu.menu()

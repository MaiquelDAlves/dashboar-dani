# vendas.py

import streamlit as st
import locale
from utils.google_sheets import planilha_vendas, mostrar_planilha
from utils.filtros import filtro_principal, tratar_dados
from module.sidebar import sidebar_datas, sidebar_filtros
import pandas as pd

# Configurar locale para moeda brasileira
locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

# Carregar e tratar os dados da planilha de vendas
data_planilha_vendas = tratar_dados(mostrar_planilha(planilha_vendas))

def vendas(key_suffix):
    # PRIMEIRO: Apenas obter as datas (chamada única)
    datas_selecionadas = sidebar_datas(key_suffix)
    
    # Converter datas para datetime
    data_inicio = pd.to_datetime(datas_selecionadas[0])
    data_fim = pd.to_datetime(datas_selecionadas[1])
    
    # Filtrar dados COMPLETOS pelo range de datas
    dados_completos = filtro_principal(data_planilha_vendas)
    dados_completos["Data de Emissão"] = pd.to_datetime(dados_completos["Data de Emissão"])
    
    mask_data = (dados_completos["Data de Emissão"] >= data_inicio) & \
                (dados_completos["Data de Emissão"] <= data_fim)
    dados_filtrados_por_data = dados_completos[mask_data]
    
    # SEGUNDO: Obter os outros filtros (com dados já filtrados por data)
    opcoes = sidebar_filtros(key_suffix, dados_filtrados_por_data)
    
    # Separar colunas opcionais do usuário das fixas
    colunas_fixas = {"Data de Emissão", "Quantidade", "Valor Total"}
    colunas_usuario = [c for c in opcoes["colunas"] if c not in colunas_fixas]

    if not colunas_usuario:
        st.warning("Por favor, selecione pelo menos uma coluna opcional para exibir.")
        return

    # Montar dataframe final (mantendo datetime para operações)
    df = dados_completos[mask_data][opcoes["colunas"]]
    
    # APLICAR FILTRO APENAS SE NÃO FOR "TODOS" EM AMBOS OS SELECTBOXES
    if (opcoes["filtro_coluna"] and 
        opcoes["filtro_coluna"] != "Todos" and 
        opcoes["filtro_valor"] and 
        opcoes["filtro_valor"] != "Todos"):
        
        # Aplicar filtro apenas se não for "Todos" em ambos
        df = df[df[opcoes["filtro_coluna"]] == opcoes["filtro_valor"]]
    
    # Criar cópia para exibição com data formatada
    df_display = df.copy()
    
    # Formatar a coluna "Data de Emissão" para DD/MM/AAAA
    if "Data de Emissão" in df_display.columns:
        df_display["Data de Emissão"] = df_display["Data de Emissão"].dt.strftime("%d/%m/%Y")
    
    # Set index para a data formatada
    df_display = df_display.set_index("Data de Emissão")
    
    # Exibir dataframe com data formatada
    st.dataframe(
        df_display.style.format({
            "Valor Total": lambda x: locale.currency(x, grouping=True, symbol=True)
        })
    )
    
    # Mostrar estatísticas
    total_registros = len(df_display)
    valor_total = df_display["Valor Total"].sum() if "Valor Total" in df_display.columns else 0
    
    st.info(f"Total de registros: {total_registros} | Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
    st.write(f"**Valor Total:** {locale.currency(valor_total, grouping=True, symbol=True)}")
 
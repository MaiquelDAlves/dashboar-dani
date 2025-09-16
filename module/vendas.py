# vendas.py

import streamlit as st
import locale
from utils.google_sheets import planilha_metas, planilha_vendas, mostrar_planilha
from utils.filtros import filtro_principal, tratar_dados
from module.sidebar import sidebar_datas, sidebar_filtros
import pandas as pd

# Configurar locale para moeda brasileira
locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

# Carregar e tratar os dados da planilha de vendas
data_planilha_vendas = tratar_dados(mostrar_planilha(planilha_vendas))
data_planilha_metas = tratar_dados(mostrar_planilha(planilha_metas))

def vendas(key_suffix):
    # 🔽 COLOCAR O CSS AQUI (primeira coisa na função) 🔽
    st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        border: 0.5px solid;
        border-color: #dee2e6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    [data-theme="dark"] div[data-testid="stMetric"] {
        border-color: #4a5568;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }

    div[data-testid="stMetric"] > div {
        text-align: center;
    }

    div[data-testid="stMetric"] > div:first-child {
        font-weight: 600;
        font-size: 14px;
        margin-bottom: 8px;
    }

    div[data-testid="stMetric"] > div:nth-child(2) {
        font-weight: 700;
        font-size: 24px;
    }
    </style>
    """, unsafe_allow_html=True)
    
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

    # Mostrar estatísticas CARDS
    
    valor_total = df_display["Valor Total"].sum() if "Valor Total" in df_display.columns else 0

    df_metas = data_planilha_metas.copy()

    # Converter a coluna de data para datetime
    df_metas["Data"] = pd.to_datetime(df_metas["Data"], dayfirst=True, errors="coerce")

    # CONVERSÃO CORRETA PARA FORMATO BRASILEIRO
    if "Meta" in df_metas.columns:
        df_metas["Meta"] = (
            df_metas["Meta"]
            .astype(str)
            .str.strip()
            .str.replace('R$', '', regex=False)
            .str.replace(' ', '', regex=False)
            .str.replace('.', '', regex=False)   # Remove separador de milhar
            .str.replace(',', '.', regex=False)  # Converte vírgula decimal para ponto
        )
        df_metas["Meta"] = pd.to_numeric(df_metas["Meta"], errors='coerce').fillna(0)

    # Criar a máscara para o período
    mask_metas = (df_metas["Data"] >= data_inicio) & (df_metas["Data"] <= data_fim)

    # Aplicar a máscara no DataFrame
    metas_no_periodo = df_metas[mask_metas]

    # Calcular soma das metas (agora convertidas para float)
    soma_metas = metas_no_periodo['Meta'].sum() if not metas_no_periodo.empty else 0

    # Mostrar informações das metas
    titulo_meta = "" 

    if opcoes["filtro_coluna"] and opcoes["filtro_coluna"] == "Todos":
        titulo_meta = "Total de Vendas"
    else:
        titulo_meta = f"Vendas - {opcoes['filtro_coluna']}: {opcoes['filtro_valor']}" if opcoes["filtro_coluna"] and opcoes["filtro_valor"] else "Total de Vendas"

    if len(metas_no_periodo) == 0:
        st.warning("Nenhuma meta encontrada para o período selecionado.")
    else:
        # Sempre criar 3 colunas
        col1, col2, col3 = st.columns(3)
        
        # COLUNA 1 (sempre visível)
        with col1:
            st.metric(titulo_meta, 
                    locale.currency(valor_total, grouping=True, symbol=True))
        
        # COLUNAS 2 e 3 (condicionais)
        if opcoes["filtro_coluna"] == "Todos":
            with col2:
                st.metric("Meta do Período", 
                        locale.currency(soma_metas, grouping=True, symbol=True))
            with col3:
                if soma_metas > 0:
                    percentual = (valor_total / soma_metas) * 100
                    st.metric("Atingimento", f"{percentual:.1f}%")
                else:
                    st.metric("Atingimento", "N/A")
        else:
            # Esconder colunas 2 e 3 mantendo o layout
            with col2:
                st.empty()  # Coluna vazia
            with col3:
                st.empty()  # Coluna vazia

    # Set index para a data formatada
    df_display = df_display.set_index("Data de Emissão")
    
    # Exibir dataframe com data formatada
    st.dataframe(
        df_display.style.format({
            "Valor Total": lambda x: locale.currency(x, grouping=True, symbol=True)
        })
    )
    
    
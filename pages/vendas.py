import streamlit as st
import pandas as pd
from utils.filtros import aplicar_filtros

def format_brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_number(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def show():
    
    # Carregar dados
    vendas = pd.read_excel('data/Vendas.xlsx', decimal=',')
    vendas['Data de Emissão'] = pd.to_datetime(vendas['Data de Emissão'], errors='coerce')

    # Aplica filtros e obtém informações do filtro aplicado
    df_filtrado, filtro_info = aplicar_filtros(vendas)

    if df_filtrado.empty:
        st.warning("Nenhum dado para exibir com os filtros selecionados.")
    else:
        # =======================
        # Cards de resumo
        # =======================
        total_vendas = df_filtrado["Valor Total"].sum()
        
        # Verifica se algum filtro específico foi aplicado (além de data)
        filtro_aplicado = filtro_info.get('filtro_aplicado', False)
        nome_filtro = filtro_info.get('nome_filtro', '')
        valor_filtro = filtro_info.get('valor_filtro', '')

        if filtro_aplicado:
            # Se filtro específico foi aplicado, mostra apenas total com nome do filtro
            col1, = st.columns(1)
            titulo = f"💰 Total de Vendas - {nome_filtro}: {valor_filtro}"
            col1.metric(titulo, format_brl(total_vendas))
        else:
            # Se não há filtro específico, mostra todos os cards (visão geral)
            meta_mensal = 100000  # fixo por enquanto
            atingimento = (total_vendas / meta_mensal) * 100 if meta_mensal > 0 else 0
            falta_meta = meta_mensal - total_vendas if total_vendas < meta_mensal else 0

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("💰 Total de Vendas", format_brl(total_vendas))
            col2.metric("🎯 Meta do Mês", format_brl(meta_mensal))
            col3.metric("📈 Atingimento", f"{atingimento:.1f}%")
            col4.metric("⚡ Falta para Meta", format_brl(falta_meta))

        # =======================
        # Tabela de vendas
        # =======================
        st.subheader("📋 Detalhes das Vendas")

        # Formata apenas as colunas numéricas que existem no DataFrame
        format_dict = {}
        if "Valor Total" in df_filtrado.columns:
            format_dict["Valor Total"] = format_number
        if "Quantidade" in df_filtrado.columns:
            format_dict["Quantidade"] = format_number

        if format_dict:
            df_styled = df_filtrado.style.format(format_dict)
            st.dataframe(df_styled, use_container_width=True)
        else:
            st.dataframe(df_filtrado, use_container_width=True)
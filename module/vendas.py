import streamlit as st
import pandas as pd
from utils.filtros import aplicar_filtros
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente
load_dotenv()

def format_brl(valor):
    """Formata valor para padrão BRL R$ 1.000,00"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_number(valor):
    """Formata número com separadores brasileiros"""
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def show():
    st.title("📊 Página de Vendas")
    
    # Usa a meta do .env ou valor padrão
    meta_mensal = float(os.getenv('META_MENSAL', 100000))
    
    try:
        # Tenta carregar o arquivo Excel com tratamento de erro
        vendas = pd.read_excel('data/Vendas.xlsx', decimal=',')
        vendas['Data de Emissão'] = pd.to_datetime(vendas['Data de Emissão'], errors='coerce')
        
        # Verifica se há dados
        if vendas.empty:
            st.warning("O arquivo de vendas está vazio.")
            return
            
    except FileNotFoundError:
        st.error("❌ Arquivo 'data/Vendas.xlsx' não encontrado.")
        st.info("💡 Verifique se o arquivo existe na pasta data/")
        return
    except Exception as e:
        st.error(f"❌ Erro ao carregar arquivo: {str(e)}")
        return
    
    # Aplica filtros com indicador de progresso
    with st.spinner("🔄 Aplicando filtros..."):
        df_filtrado, filtro_info = aplicar_filtros(vendas)

    if df_filtrado.empty:
        st.warning("⚠️ Nenhum dado para exibir com os filtros selecionados.")
    else:
        total_vendas = df_filtrado["Valor Total"].sum()
        filtro_aplicado = filtro_info.get('filtro_aplicado', False)
        nome_filtro = filtro_info.get('nome_filtro', '')
        valor_filtro = filtro_info.get('valor_filtro', '')

        if filtro_aplicado:
            col1, = st.columns(1)
            titulo = f"💰 Total de Vendas - {nome_filtro}: {valor_filtro}"
            col1.metric(titulo, format_brl(total_vendas))
        else:
            atingimento = (total_vendas / meta_mensal) * 100 if meta_mensal > 0 else 0
            falta_meta = meta_mensal - total_vendas if total_vendas < meta_mensal else 0

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("💰 Total de Vendas", format_brl(total_vendas))
            col2.metric("🎯 Meta do Mês", format_brl(meta_mensal))
            col3.metric("📈 Atingimento", f"{atingimento:.1f}%")
            col4.metric("⚡ Falta para Meta", format_brl(falta_meta))

        st.subheader("📋 Detalhes das Vendas")
        
        # Mostra informações do dataset
        st.caption(f"📊 {len(df_filtrado)} registros encontrados")
        
        format_dict = {}
        if "Valor Total" in df_filtrado.columns:
            format_dict["Valor Total"] = format_number
        if "Quantidade" in df_filtrado.columns:
            format_dict["Quantidade"] = format_number

        if format_dict:
            st.dataframe(df_filtrado.style.format(format_dict), use_container_width=True)
        else:
            st.dataframe(df_filtrado, use_container_width=True)
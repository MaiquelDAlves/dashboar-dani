import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.google_sheets import df_vendas, df_metas
from utils.auth import verificar_autenticacao, login, get_usuario_atual, logout

# CONFIGURAÇÃO DA PÁGINA DEVE SER SEMPRE A PRIMEIRA COISA
st.set_page_config(page_title="Dashboard Vendas", layout="wide")

# VERIFICA AUTENTICAÇÃO - SE NÃO ESTIVER LOGADO, EXIBE LOGIN
if not verificar_autenticacao():
    login()

# SE CHEGOU ATÉ AQUI, O USUÁRIO ESTÁ AUTENTICADO
usuario = get_usuario_atual()

# SIDEBAR COM INFORMAÇÕES DO USUÁRIO E CONTROLES
with st.sidebar:
    st.write(f"Usuário: {usuario}")
    st.title("Dashboard de Vendas")
    
    # Botão de logout
    if st.button("Logout"):
        logout()

# ---------------------------
# CONFIGURAÇÕES DO DATAFRAME DE VENDAS
# ---------------------------
COLUNAS_FILTRADAS_VENDAS = [
    "Data de Emissão", 
    "Descrição", 
    "Nro. Nota Fiscal",
    "Matriz",
    "Quantidade",
    "Valor Total"
]

COLUNAS_EXIBICAO_VENDAS = [
    "Data Venda", 
    "Descrição", 
    "Nro. Nota Fiscal",
    "Matriz",
    "Quantidade",
    "Valor Venda"
]

# ---------------------------
# INICIALIZAÇÃO DO DATAFRAME BASE DE VENDAS NO session_state
# ---------------------------
if "filtro_df_vendas_base" not in st.session_state:
    df_vendas_temp = pd.DataFrame(df_vendas)
    st.session_state["filtro_df_vendas_base"] = df_vendas_temp[COLUNAS_FILTRADAS_VENDAS].copy()

# Trabalha sempre em uma cópia do DataFrame base
filtro_df_vendas = st.session_state["filtro_df_vendas_base"].copy()

# ---------------------------
# LIMPEZA E FORMATAÇÃO DOS DADOS DE VENDAS
# ---------------------------
# Converte Valor Total para float
filtro_df_vendas["Valor Total"] = (
    filtro_df_vendas["Valor Total"]
    .astype(str)
    .str.replace("R\$", "", regex=True)
    .str.replace(".", "", regex=False)
    .str.replace(",", ".", regex=False)
    .str.replace(r"\s+", "", regex=True)
    .str.replace("^-", "-", regex=True)
    .replace("", 0)
    .astype(float)
)

# Formata valor para exibição em Real brasileiro
filtro_df_vendas["Valor Venda"] = filtro_df_vendas["Valor Total"].apply(
    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

# Converte data para datetime e define como índice
filtro_df_vendas["Data de Emissão"] = pd.to_datetime(
    filtro_df_vendas["Data de Emissão"], 
    dayfirst=True,
    errors="coerce"
)
filtro_df_vendas = filtro_df_vendas.set_index("Data de Emissão").sort_index()
filtro_df_vendas["Data Venda"] = filtro_df_vendas.index.strftime("%d/%m/%Y")

# ---------------------------
# CONFIGURAÇÕES DO DATAFRAME DE METAS
# ---------------------------
if "filtro_df_metas_base" not in st.session_state:
    df_metas_temp = pd.DataFrame(df_metas)
    df_metas_temp["Data"] = pd.to_datetime(df_metas_temp["Data"], dayfirst=True, errors="coerce")
    df_metas_temp["Meta"] = (
        df_metas_temp["Meta"]
        .astype(str)
        .str.replace("R\$", "", regex=True)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.replace(r"\s+", "", regex=True)
        .replace("", 0)
        .astype(float)
    )
    st.session_state["filtro_df_metas_base"] = df_metas_temp.copy()

filtro_df_metas = st.session_state["filtro_df_metas_base"].copy()

# ---------------------------
# SIDEBAR - FILTROS DE DATA
# ---------------------------
mes_recente = filtro_df_vendas.index.max().to_period("M")
primeiro_dia = mes_recente.start_time.date()
ultimo_dia = mes_recente.end_time.date()

with st.sidebar:
    st.divider()
    dt_inicio = st.date_input("Data Início:", value=primeiro_dia, format="DD/MM/YYYY")
    dt_fim = st.date_input("Data Fim:", value=ultimo_dia, format="DD/MM/YYYY")

# Converte para Timestamp para filtro correto no DataFrame
dt_inicio_ts = pd.Timestamp(dt_inicio)
dt_fim_ts = pd.Timestamp(dt_fim)

# ---------------------------
# FILTRAGEM DOS DADOS POR PERÍODO SELECIONADO
# ---------------------------
df_vendas_filtrado = filtro_df_vendas.loc[dt_inicio_ts:dt_fim_ts]

filtro_df_metas_filtrado = filtro_df_metas[
    (filtro_df_metas["Data"].dt.to_period("M") >= dt_inicio_ts.to_period("M")) &
    (filtro_df_metas["Data"].dt.to_period("M") <= dt_fim_ts.to_period("M"))
]

# ---------------------------
# PREPARAÇÃO DOS DADOS PARA OS GRÁFICOS
# ---------------------------
# Agrupa vendas por dia para o gráfico de barras
vendas_diarias = df_vendas_filtrado.groupby(df_vendas_filtrado.index.date)['Valor Total'].sum().reset_index()
vendas_diarias.columns = ['Data', 'Venda Diária']
vendas_diarias['Data'] = pd.to_datetime(vendas_diarias['Data'])

# Agrupa vendas por matriz para o gráfico de pizza
vendas_por_matriz = df_vendas_filtrado.groupby('Matriz')['Valor Total'].sum().reset_index()
vendas_por_matriz.columns = ['Matriz', 'Valor Total']
vendas_por_matriz = vendas_por_matriz.sort_values('Valor Total', ascending=False)

# ---------------------------
# CÁLCULO DE MÉTRICAS
# ---------------------------
soma_vendas = df_vendas_filtrado["Valor Total"].sum()
meta_soma = filtro_df_metas_filtrado["Meta"].sum()
percentual = (soma_vendas / meta_soma * 100) if meta_soma > 0 else 0

soma_vendas_formatada = f"R$ {soma_vendas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
meta_soma_formatada = f"R$ {meta_soma:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
percentual_formatado = f"{percentual:.2f}%"

# ---------------------------
# EXIBIÇÃO DAS MÉTRICAS
# ---------------------------
st.subheader("📊 Métricas Principais")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Venda Período Selecionado", soma_vendas_formatada)
with col2:
    st.metric("Meta Período Selecionado", meta_soma_formatada)
with col3:
    st.metric("% Atingido", percentual_formatado)

# ---------------------------
# GRÁFICOS MODERNOS
# ---------------------------
st.subheader("📈 Visualizações")

# Container para os gráficos
col1, col2 = st.columns(2)

with col1:
    # GRÁFICO DE BARRAS - VENDAS DIÁRIAS
    if not vendas_diarias.empty:
        fig_barras = px.bar(
            vendas_diarias, 
            x='Data', 
            y='Venda Diária',
            title='<b>💰 Vendas Diárias</b>',
            labels={'Venda Diária': 'Valor (R$)', 'Data': 'Data'},
            color='Venda Diária',
            color_continuous_scale='viridis',
            template='plotly_white'
        )
        
        # Personaliza o gráfico de barras
        fig_barras.update_layout(
            xaxis=dict(tickformat='%d/%m', title='Data'),
            yaxis=dict(title='Valor em R$'),
            hovermode='x unified',
            showlegend=False
        )
        
        fig_barras.update_traces(
            hovertemplate='<b>Data:</b> %{x|%d/%m/%Y}<br><b>Venda:</b> R$ %{y:,.2f}<extra></extra>'
        )
        
        st.plotly_chart(fig_barras, use_container_width=True)
    else:
        st.info("📊 Não há dados de vendas para o período selecionado")

with col2:
    # GRÁFICO DE PIZZA - PARTICIPAÇÃO POR MATRIZ
    if not vendas_por_matriz.empty and len(vendas_por_matriz) > 1:
        fig_pizza = px.pie(
            vendas_por_matriz,
            values='Valor Total',
            names='Matriz',
            title='<b>🏢 Participação por Matriz</b>',
            color_discrete_sequence=px.colors.qualitative.Set3,
            hole=0.4,  # Cria um gráfico donut
            template='plotly_white'
        )
        
        # Personaliza o gráfico de pizza
        fig_pizza.update_layout(
            legend=dict(
                orientation="v",
                yanchor="auto",
                y=1,
                xanchor="left",
                x=1.1
            )
        )
        
        fig_pizza.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Participação: %{percent}<br>Valor: R$ %{value:,.2f}<extra></extra>'
        )
        
        st.plotly_chart(fig_pizza, use_container_width=True)
    elif len(vendas_por_matriz) == 1:
        st.info(f"🏢 Apenas uma matriz encontrada: {vendas_por_matriz['Matriz'].iloc[0]}")
    else:
        st.info("🏢 Não há dados de matriz para o período selecionado")

# ---------------------------
# GRÁFICO ADICIONAL - EVOLUÇÃO TEMPORAL
# ---------------------------
st.subheader("📈 Evolução Temporal")

if not vendas_diarias.empty:
    fig_linha = px.area(
        vendas_diarias,
        x='Data',
        y='Venda Diária',
        title='<b>📈 Evolução das Vendas Diárias</b>',
        template='plotly_white'
    )
    
    fig_linha.update_traces(
        fill='tozeroy',
        line=dict(width=3, color='#4ECDC4'),
        fillcolor='rgba(78, 205, 196, 0.2)'
    )
    
    fig_linha.update_layout(
        xaxis=dict(title='Data'),
        yaxis=dict(title='Valor em R$'),
        hovermode='x unified'
    )
    
    fig_linha.update_traces(
        hovertemplate='<b>Data:</b> %{x|%d/%m/%Y}<br><b>Venda:</b> R$ %{y:,.2f}<extra></extra>'
    )
    
    st.plotly_chart(fig_linha, use_container_width=True)

# ---------------------------
# TABELA DETALHADA
# ---------------------------
st.subheader("📋 Detalhamento das Vendas")

df_view_vendas = df_vendas_filtrado.copy()
df_exibicao_vendas = df_view_vendas[COLUNAS_EXIBICAO_VENDAS].reset_index(drop=True)
df_exibicao_vendas = df_exibicao_vendas.set_index("Data Venda")

# Adiciona algumas métricas sobre a tabela
st.write(f"**Total de registros:** {len(df_exibicao_vendas)}")
st.write(f"**Período:** {dt_inicio.strftime('%d/%m/%Y')} a {dt_fim.strftime('%d/%m/%Y')}")

st.dataframe(df_exibicao_vendas, use_container_width=True)

# ---------------------------
# RESUMO POR MATRIZ (Tabela)
# ---------------------------
st.subheader("🏢 Resumo por Matriz")

if not vendas_por_matriz.empty:
    # Formata os valores para exibição
    vendas_por_matriz_display = vendas_por_matriz.copy()
    vendas_por_matriz_display['Valor Total'] = vendas_por_matriz_display['Valor Total'].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    
    # Calcula percentual de participação
    total_geral = vendas_por_matriz['Valor Total'].sum()
    vendas_por_matriz['Participação'] = (vendas_por_matriz['Valor Total'] / total_geral * 100).round(2)
    vendas_por_matriz_display['Participação'] = vendas_por_matriz['Participação'].apply(lambda x: f"{x}%")
    
    st.dataframe(vendas_por_matriz_display, use_container_width=True)
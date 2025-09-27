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

# Converte Quantidade para numérico
filtro_df_vendas["Quantidade"] = (
    filtro_df_vendas["Quantidade"]
    .astype(str)
    .str.replace(",", ".", regex=False)
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
# SIDEBAR - FILTROS (APLICAM À PRIMEIRA ABA)
# ---------------------------
mes_recente = filtro_df_vendas.index.max().to_period("M")
primeiro_dia = mes_recente.start_time.date()
ultimo_dia = mes_recente.end_time.date()

with st.sidebar:
    st.divider()
    st.subheader("Filtros Período")
    
    # Filtro de datas
    dt_inicio = st.date_input("Data Início:", value=primeiro_dia, format="DD/MM/YYYY")
    dt_fim = st.date_input("Data Fim:", value=ultimo_dia, format="DD/MM/YYYY")
    
    # NOVO: Filtro de matriz/loja
    matrizes_disponiveis = ['Todas'] + sorted(filtro_df_vendas['Matriz'].dropna().unique().tolist())
    matriz_selecionada = st.selectbox(
        "Selecione a Matriz:",
        options=matrizes_disponiveis,
        index=0
    )

# Converte para Timestamp para filtro correto no DataFrame
dt_inicio_ts = pd.Timestamp(dt_inicio)
dt_fim_ts = pd.Timestamp(dt_fim)

# ---------------------------
# FILTRAGEM DOS DADOS POR PERÍODO E MATRIZ SELECIONADA
# ---------------------------
# Filtra primeiro por data
df_vendas_filtrado = filtro_df_vendas.loc[dt_inicio_ts:dt_fim_ts]

# Aplica filtro de matriz se não for "Todas"
if matriz_selecionada != 'Todas':
    df_vendas_filtrado = df_vendas_filtrado[df_vendas_filtrado['Matriz'] == matriz_selecionada]

filtro_df_metas_filtrado = filtro_df_metas[
    (filtro_df_metas["Data"].dt.to_period("M") >= dt_inicio_ts.to_period("M")) &
    (filtro_df_metas["Data"].dt.to_period("M") <= dt_fim_ts.to_period("M"))
]

# ---------------------------
# PREPARAÇÃO DOS DADOS PARA AMBAS AS ABAS
# ---------------------------
# Dados para aba "Vendas por Período"
vendas_diarias = df_vendas_filtrado.groupby(df_vendas_filtrado.index.date)['Valor Total'].sum().reset_index()
vendas_diarias.columns = ['Data', 'Venda Diária']
vendas_diarias['Data'] = pd.to_datetime(vendas_diarias['Data'])

vendas_por_matriz = df_vendas_filtrado.groupby('Matriz')['Valor Total'].sum().reset_index()
vendas_por_matriz.columns = ['Matriz', 'Valor Total']
vendas_por_matriz = vendas_por_matriz.sort_values('Valor Total', ascending=False)

produtos_quantidade = df_vendas_filtrado.groupby('Descrição')['Quantidade'].sum().reset_index()
produtos_quantidade.columns = ['Produto', 'Quantidade Total']
produtos_quantidade = produtos_quantidade.sort_values('Quantidade Total', ascending=False)
produtos_quantidade_top10 = produtos_quantidade.head(10)

produtos_valor = df_vendas_filtrado.groupby('Descrição')['Valor Total'].sum().reset_index()
produtos_valor.columns = ['Produto', 'Valor Total']
produtos_valor = produtos_valor.sort_values('Valor Total', ascending=False)
produtos_valor_top10 = produtos_valor.head(10)

# Dados para aba "Análise Mensal"
# Agrupa vendas por mês
vendas_mensais = filtro_df_vendas.groupby(pd.Grouper(freq='M'))['Valor Total'].sum().reset_index()
vendas_mensais.columns = ['Mês', 'Venda Mensal']
vendas_mensais['Mês'] = vendas_mensais['Mês'].dt.to_period('M').dt.to_timestamp()
vendas_mensais['Mês Formatado'] = vendas_mensais['Mês'].dt.strftime('%b/%Y')

# Agrupa por mês e matriz
vendas_mensais_matriz = filtro_df_vendas.groupby([pd.Grouper(freq='M'), 'Matriz'])['Valor Total'].sum().reset_index()
vendas_mensais_matriz.columns = ['Mês', 'Matriz', 'Venda Mensal']
vendas_mensais_matriz['Mês'] = vendas_mensais_matriz['Mês'].dt.to_period('M').dt.to_timestamp()
vendas_mensais_matriz['Mês Formatado'] = vendas_mensais_matriz['Mês'].dt.strftime('%b/%Y')

# Dados anuais para tabela
vendas_anuais = filtro_df_vendas.groupby(filtro_df_vendas.index.year)['Valor Total'].sum().reset_index()
vendas_anuais.columns = ['Ano', 'Venda Anual']
vendas_anuais = vendas_anuais.sort_values('Ano', ascending=False)

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
# CRIAÇÃO DAS ABAS
# ---------------------------
tab1, tab2 = st.tabs(["📅 Vendas por Período", "📊 Análise Mensal"])

with tab1:
    # ---------------------------
    # ABA 1: VENDAS POR PERÍODO
    # ---------------------------
    st.subheader(f"📅 Análise do Período: {dt_inicio.strftime('%d/%m/%Y')} a {dt_fim.strftime('%d/%m/%Y')}")
    if matriz_selecionada != 'Todas':
        st.subheader(f"🏢 Matriz Selecionada: {matriz_selecionada}")
    
    # Métricas principais
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Venda Período Selecionado", soma_vendas_formatada)
    with col2:
        st.metric("Meta Período Selecionado", meta_soma_formatada)
    with col3:
        st.metric("% Atingido", percentual_formatado)

    # GRÁFICOS - MATRIZ (só mostra se não tiver matriz selecionada)
    if matriz_selecionada == 'Todas':
        st.subheader("🏢 Análise por Matriz")
        col1, col2 = st.columns(2)

        with col1:
            if not vendas_diarias.empty:
                fig_barras = px.bar(
                    vendas_diarias, 
                    x='Data', 
                    y='Venda Diária',
                    title='<b>💰 Vendas Diárias</b>',
                    color='Venda Diária',
                    color_continuous_scale='viridis',
                    template='plotly_white'
                )
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
            if not vendas_por_matriz.empty and len(vendas_por_matriz) > 1:
                fig_pizza = px.pie(
                    vendas_por_matriz,
                    values='Valor Total',
                    names='Matriz',
                    title='<b>🏢 Participação por Matriz</b>',
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    hole=0.4,
                    template='plotly_white'
                )
                fig_pizza.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hovertemplate='<b>%{label}</b><br>Participação: %{percent}<br>Valor: R$ %{value:,.2f}<extra></extra>'
                )
                st.plotly_chart(fig_pizza, use_container_width=True)
            else:
                st.info("🏢 Não há dados suficientes de matriz")
    else:
        # Se tem matriz selecionada, mostra apenas gráfico de vendas diárias
        st.subheader("💰 Vendas Diárias da Matriz")
        if not vendas_diarias.empty:
            fig_barras = px.bar(
                vendas_diarias, 
                x='Data', 
                y='Venda Diária',
                title=f'<b>💰 Vendas Diárias - {matriz_selecionada}</b>',
                color='Venda Diária',
                color_continuous_scale='viridis',
                template='plotly_white'
            )
            fig_barras.update_layout(
                xaxis=dict(tickformat='%d/%m', title='Data'),
                yaxis=dict(title='Valor em R$'),
                hovermode='x unified',
                showlegend=False
            )
            st.plotly_chart(fig_barras, use_container_width=True)

    # GRÁFICOS - PRODUTOS POR QUANTIDADE
    st.subheader("📦 Análise de Produtos por Quantidade")
    col3, col4 = st.columns(2)

    with col3:
        if not produtos_quantidade_top10.empty:
            fig_barras_quantidade = px.bar(
                produtos_quantidade_top10, 
                x='Produto', 
                y='Quantidade Total',
                title='<b>📦 Top 10 Produtos por Quantidade</b>',
                color='Quantidade Total',
                color_continuous_scale='blues',
                template='plotly_white'
            )
            fig_barras_quantidade.update_layout(xaxis=dict(tickangle=45))
            fig_barras_quantidade.update_traces(
                hovertemplate='<b>%{x}</b><br>Quantidade: %{y:,.0f} unidades<extra></extra>'
            )
            st.plotly_chart(fig_barras_quantidade, use_container_width=True)

    with col4:
        if not produtos_quantidade.empty and len(produtos_quantidade) > 1:
            if len(produtos_quantidade) > 8:
                top_produtos = produtos_quantidade.head(8)
                outros = pd.DataFrame({
                    'Produto': ['Outros'],
                    'Quantidade Total': [produtos_quantidade['Quantidade Total'].iloc[8:].sum()]
                })
                produtos_pizza_quantidade = pd.concat([top_produtos, outros])
            else:
                produtos_pizza_quantidade = produtos_quantidade
            
            fig_pizza_quantidade = px.pie(
                produtos_pizza_quantidade,
                values='Quantidade Total',
                names='Produto',
                title='<b>📦 Participação por Quantidade</b>',
                color_discrete_sequence=px.colors.qualitative.Pastel,
                hole=0.4,
                template='plotly_white'
            )
            fig_pizza_quantidade.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Participação: %{percent}<br>Quantidade: %{value:,.0f} un.<extra></extra>'
            )
            st.plotly_chart(fig_pizza_quantidade, use_container_width=True)

    # GRÁFICOS - PRODUTOS POR VALOR
    st.subheader("💰 Análise de Produtos por Valor")
    col5, col6 = st.columns(2)

    with col5:
        if not produtos_valor_top10.empty:
            fig_barras_valor = px.bar(
                produtos_valor_top10, 
                x='Produto', 
                y='Valor Total',
                title='<b>💰 Top 10 Produtos por Valor</b>',
                color='Valor Total',
                color_continuous_scale='greens',
                template='plotly_white'
            )
            fig_barras_valor.update_layout(xaxis=dict(tickangle=45))
            fig_barras_valor.update_traces(
                hovertemplate='<b>%{x}</b><br>Valor: R$ %{y:,.2f}<extra></extra>'
            )
            st.plotly_chart(fig_barras_valor, use_container_width=True)

    with col6:
        if not produtos_valor.empty and len(produtos_valor) > 1:
            if len(produtos_valor) > 8:
                top_produtos = produtos_valor.head(8)
                outros = pd.DataFrame({
                    'Produto': ['Outros'],
                    'Valor Total': [produtos_valor['Valor Total'].iloc[8:].sum()]
                })
                produtos_pizza_valor = pd.concat([top_produtos, outros])
            else:
                produtos_pizza_valor = produtos_valor
            
            fig_pizza_valor = px.pie(
                produtos_pizza_valor,
                values='Valor Total',
                names='Produto',
                title='<b>💰 Participação por Valor</b>',
                color_discrete_sequence=px.colors.qualitative.Bold,
                hole=0.4,
                template='plotly_white'
            )
            fig_pizza_valor.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Participação: %{percent}<br>Valor: R$ %{value:,.2f}<extra></extra>'
            )
            st.plotly_chart(fig_pizza_valor, use_container_width=True)

    # TABELA DETALHADA
    st.subheader("📋 Detalhamento das Vendas")
    df_view_vendas = df_vendas_filtrado.copy()
    df_exibicao_vendas = df_view_vendas[COLUNAS_EXIBICAO_VENDAS].reset_index(drop=True)
    df_exibicao_vendas = df_exibicao_vendas.set_index("Data Venda")
    st.write(f"**Total de registros:** {len(df_exibicao_vendas)}")
    st.dataframe(df_exibicao_vendas, use_container_width=True)

with tab2:
    # ---------------------------
    # ABA 2: ANÁLISE MENSAL SIMPLIFICADA
    # ---------------------------
    st.subheader("📊 Evolução Mensal de Vendas")
    
    # Métricas mensais simplificadas (removidas as que você não gostou)
    if not vendas_mensais.empty:
        ultimo_mes_valor = vendas_mensais['Venda Mensal'].iloc[-1]
        penultimo_mes_valor = vendas_mensais['Venda Mensal'].iloc[-2] if len(vendas_mensais) > 1 else 0
        variacao_mensal = ((ultimo_mes_valor - penultimo_mes_valor) / penultimo_mes_valor * 100) if penultimo_mes_valor > 0 else 0
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                f"Vendas {vendas_mensais['Mês Formatado'].iloc[-1]}",
                f"R$ {ultimo_mes_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                f"{variacao_mensal:+.1f}%"
            )
        
        with col2:
            media_mensal = vendas_mensais['Venda Mensal'].mean()
            st.metric(
                "Média Mensal",
                f"R$ {media_mensal:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )

    # GRÁFICO DE LINHA - EVOLUÇÃO MENSAL
    st.subheader("📈 Evolução Mensal")
    if not vendas_mensais.empty:
        fig_linha_mensal = px.line(
            vendas_mensais,
            x='Mês Formatado',
            y='Venda Mensal',
            title='<b>📈 Evolução das Vendas Mensais</b>',
            markers=True,
            template='plotly_white'
        )
        
        fig_linha_mensal.update_traces(
            line=dict(width=4, color='#4ECDC4'),
            marker=dict(size=8, color='#FF6B6B')
        )
        
        fig_linha_mensal.update_layout(
            xaxis=dict(title='Mês'),
            yaxis=dict(title='Valor em R$'),
            hovermode='x unified'
        )
        
        fig_linha_mensal.update_traces(
            hovertemplate='<b>Mês:</b> %{x}<br><b>Venda:</b> R$ %{y:,.2f}<extra></extra>'
        )
        
        st.plotly_chart(fig_linha_mensal, use_container_width=True)

    # GRÁFICO DE BARRAS - COMPARAÇÃO MENSAL POR MATRIZ
    st.subheader("🏢 Vendas Mensais por Matriz")
    if not vendas_mensais_matriz.empty:
        fig_barras_matriz = px.bar(
            vendas_mensais_matriz,
            x='Mês Formatado',
            y='Venda Mensal',
            color='Matriz',
            title='<b>🏢 Vendas por Matriz (Mensal)</b>',
            barmode='group',
            template='plotly_white'
        )
        
        fig_barras_matriz.update_layout(
            xaxis=dict(title='Mês'),
            yaxis=dict(title='Valor em R$')
        )
        
        st.plotly_chart(fig_barras_matriz, use_container_width=True)

    # NOVA TABELA DE VISUALIZAÇÃO ANUAL (substitui os gráficos removidos)
    st.subheader("📊 Visão Anual - Comparativo de Desempenho")
    
    if not vendas_anuais.empty:
        # Prepara dados para a tabela anual
        tabela_anual = vendas_anuais.copy()
        tabela_anual['Venda Anual Formatada'] = tabela_anual['Venda Anual'].apply(
            lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        
        # Calcula crescimento anual
        tabela_anual = tabela_anual.sort_values('Ano')
        tabela_anual['Crescimento Anual'] = tabela_anual['Venda Anual'].pct_change() * 100
        tabela_anual['Crescimento Anual'] = tabela_anual['Crescimento Anual'].fillna(0).round(1)
        
        # Ordena do ano mais recente para o mais antigo
        tabela_anual = tabela_anual.sort_values('Ano', ascending=False)
        
        # Formata crescimento
        tabela_anual['Crescimento Formatado'] = tabela_anual['Crescimento Anual'].apply(
            lambda x: f"{x:+.1f}%" if pd.notnull(x) else "-"
        )
        
        # Exibe tabela formatada
        st.dataframe(
            tabela_anual[['Ano', 'Venda Anual Formatada', 'Crescimento Formatado']],
            use_container_width=True,
            column_config={
                'Ano': 'Ano',
                'Venda Anual Formatada': 'Vendas Anuais',
                'Crescimento Formatado': 'Crescimento vs Ano Anterior'
            }
        )

    # TABELA RESUMO MENSAL DETALHADA
    st.subheader("📋 Resumo Mensal Detalhado")
    if not vendas_mensais.empty:
        resumo_mensal = vendas_mensais.copy()
        resumo_mensal['Venda Mensal Formatada'] = resumo_mensal['Venda Mensal'].apply(
            lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        
        # Calcula variação mensal
        resumo_mensal['Variação %'] = resumo_mensal['Venda Mensal'].pct_change() * 100
        resumo_mensal['Variação %'] = resumo_mensal['Variação %'].fillna(0).round(2)
        resumo_mensal['Variação %'] = resumo_mensal['Variação %'].apply(lambda x: f"{x:+.1f}%")
        
        # Ordena do mais recente para o mais antigo
        resumo_mensal = resumo_mensal.sort_values('Mês', ascending=False)
        
        st.dataframe(
            resumo_mensal[['Mês Formatado', 'Venda Mensal Formatada', 'Variação %']],
            use_container_width=True,
            column_config={
                'Mês Formatado': 'Mês',
                'Venda Mensal Formatada': 'Vendas Mensais',
                'Variação %': 'Variação Mensal'
            }
        )
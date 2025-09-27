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
    
    # Filtro de matriz/loja
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
# PREPARAÇÃO DOS DADOS PARA TODAS AS ABAS
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
vendas_mensais = filtro_df_vendas.groupby(pd.Grouper(freq='M'))['Valor Total'].sum().reset_index()
vendas_mensais.columns = ['Mês', 'Venda Mensal']
vendas_mensais['Mês'] = vendas_mensais['Mês'].dt.to_period('M').dt.to_timestamp()
vendas_mensais['Mês Formatado'] = vendas_mensais['Mês'].dt.strftime('%b/%Y')

vendas_mensais_matriz = filtro_df_vendas.groupby([pd.Grouper(freq='M'), 'Matriz'])['Valor Total'].sum().reset_index()
vendas_mensais_matriz.columns = ['Mês', 'Matriz', 'Venda Mensal']
vendas_mensais_matriz['Mês'] = vendas_mensais_matriz['Mês'].dt.to_period('M').dt.to_timestamp()
vendas_mensais_matriz['Mês Formatado'] = vendas_mensais_matriz['Mês'].dt.strftime('%b/%Y')

vendas_anuais = filtro_df_vendas.groupby(filtro_df_vendas.index.year)['Valor Total'].sum().reset_index()
vendas_anuais.columns = ['Ano', 'Venda Anual']
vendas_anuais = vendas_anuais.sort_values('Ano', ascending=False)

# Dados para NOVA ABA "Comparativos Anuais"
filtro_df_vendas_copy = filtro_df_vendas.copy()
filtro_df_vendas_copy['Ano'] = filtro_df_vendas_copy.index.year
filtro_df_vendas_copy['Mês'] = filtro_df_vendas_copy.index.month
filtro_df_vendas_copy['Mês_Nome'] = filtro_df_vendas_copy.index.strftime('%B')

# Agrupa por ano e mês para comparação
vendas_mensais_anual = filtro_df_vendas_copy.groupby(['Ano', 'Mês', 'Mês_Nome'])['Valor Total'].sum().reset_index()
vendas_mensais_anual = vendas_mensais_anual.sort_values(['Ano', 'Mês'])

# Pega os anos disponíveis
anos_disponiveis = sorted(vendas_mensais_anual['Ano'].unique())

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
# CRIAÇÃO DAS ABAS (AGORA COM 3 ABAS)
# ---------------------------
tab1, tab2, tab3 = st.tabs(["📅 Vendas por Período", "📊 Análise Mensal", "📈 Comparativos Anuais"])

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
    
    # Métricas mensais simplificadas
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
        vendas_mensais_matriz_ordenado = vendas_mensais_matriz.sort_values('Mês')
        
        fig_barras_matriz = px.bar(
            vendas_mensais_matriz_ordenado,
            x='Mês Formatado',
            y='Venda Mensal',
            color='Matriz',
            title='<b>🏢 Vendas por Matriz (Mensal)</b>',
            barmode='group',
            template='plotly_white',
            category_orders={"Mês Formatado": vendas_mensais_matriz_ordenado['Mês Formatado'].tolist()}
        )
        
        fig_barras_matriz.update_layout(
            xaxis=dict(title='Mês', type='category', categoryorder='array', 
                      categoryarray=vendas_mensais_matriz_ordenado['Mês Formatado'].tolist()),
            yaxis=dict(title='Valor em R$')
        )
        
        st.plotly_chart(fig_barras_matriz, use_container_width=True)

    # GRÁFICO DE BARRAS COMPARATIVO MENSAL (COM CORES VERMELHO/VERDE)
    st.subheader("📊 Comparativo Mensal com Variação")
    
    if len(vendas_mensais) > 1:
        comparativo_mensal = vendas_mensais.copy()
        comparativo_mensal['Variação %'] = comparativo_mensal['Venda Mensal'].pct_change() * 100
        comparativo_mensal['Variação %'] = comparativo_mensal['Variação %'].fillna(0)
        comparativo_mensal = comparativo_mensal.sort_values('Mês')
        
        comparativo_mensal['Cor'] = comparativo_mensal['Variação %'].apply(
            lambda x: '#00cc96' if x >= 0 else '#ef553b'
        )
        
        fig_comparativo = go.Figure()
        
        fig_comparativo.add_trace(go.Bar(
            x=comparativo_mensal['Mês Formatado'],
            y=comparativo_mensal['Venda Mensal'],
            marker_color=comparativo_mensal['Cor'],
            text=comparativo_mensal.apply(
                lambda x: f"R$ {x['Venda Mensal']:,.0f}<br>({x['Variação %']:+.1f}%)".replace(",", "X").replace(".", ",").replace("X", "."),
                axis=1
            ),
            textposition='outside',
            hovertemplate=(
                '<b>Mês:</b> %{x}<br>'
                '<b>Vendas:</b> R$ %{y:,.2f}<br>'
                '<b>Variação:</b> %{customdata:.1f}%<extra></extra>'
            ),
            customdata=comparativo_mensal['Variação %']
        ))
        
        fig_comparativo.update_layout(
            title='<b>📊 Comparativo Mensal com Variação Percentual</b>',
            xaxis=dict(
                title='Mês', 
                type='category', 
                categoryorder='array',
                categoryarray=comparativo_mensal['Mês Formatado'].tolist()
            ),
            yaxis=dict(title='Valor em R$'),
            template='plotly_white',
            showlegend=False,
            uniformtext_minsize=8,
            margin=dict(t=100)
        )
        
        st.plotly_chart(fig_comparativo, use_container_width=True)

    # TABELA DE VISUALIZAÇÃO ANUAL
    st.subheader("📈 Visão Anual - Comparativo de Desempenho")
    
    if not vendas_anuais.empty:
        tabela_anual = vendas_anuais.copy()
        tabela_anual['Venda Anual Formatada'] = tabela_anual['Venda Anual'].apply(
            lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        
        tabela_anual = tabela_anual.sort_values('Ano')
        tabela_anual['Crescimento Anual'] = tabela_anual['Venda Anual'].pct_change() * 100
        tabela_anual['Crescimento Anual'] = tabela_anual['Crescimento Anual'].fillna(0).round(1)
        
        tabela_anual = tabela_anual.sort_values('Ano', ascending=False)
        
        tabela_anual['Crescimento Formatado'] = tabela_anual['Crescimento Anual'].apply(
            lambda x: f"{x:+.1f}%" if pd.notnull(x) else "-"
        )
        
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
        
        resumo_mensal['Variação %'] = resumo_mensal['Venda Mensal'].pct_change() * 100
        resumo_mensal['Variação %'] = resumo_mensal['Variação %'].fillna(0).round(2)
        resumo_mensal['Variação %'] = resumo_mensal['Variação %'].apply(lambda x: f"{x:+.1f}%")
        
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

with tab3:
    # ---------------------------
    # NOVA ABA 3: COMPARATIVOS ANUAIS
    # ---------------------------
    st.header("📈 Comparativos Anuais")
    st.markdown("Análise comparativa entre anos específicos")
    
    # Filtros específicos para a aba de comparativos
    col_filtro1, col_filtro2 = st.columns(2)
    
    with col_filtro1:
        anos_comparacao = st.multiselect(
            "Selecione os anos para comparar:",
            options=anos_disponiveis,
            default=anos_disponiveis[-2:] if len(anos_disponiveis) >= 2 else anos_disponiveis
        )
    
    with col_filtro2:
        matriz_comparativo = st.selectbox(
            "Matriz para análise comparativa:",
            options=['Todas'] + sorted(filtro_df_vendas['Matriz'].dropna().unique().tolist()),
            index=0,
            key="matriz_comparativo"
        )
    
    # Filtra os dados conforme seleções
    vendas_comparativo = vendas_mensais_anual.copy()
    
    if anos_comparacao:
        vendas_comparativo = vendas_comparativo[vendas_comparativo['Ano'].isin(anos_comparacao)]
    
    # Aplica filtro de matriz se necessário
    if matriz_comparativo != 'Todas':
        vendas_matriz_filtrado = filtro_df_vendas_copy[filtro_df_vendas_copy['Matriz'] == matriz_comparativo]
        vendas_comparativo = vendas_matriz_filtrado.groupby(['Ano', 'Mês', 'Mês_Nome'])['Valor Total'].sum().reset_index()
        if anos_comparacao:
            vendas_comparativo = vendas_comparativo[vendas_comparativo['Ano'].isin(anos_comparacao)]
    
    # CORREÇÃO: Verificação correta para exibir conteúdo
    if not vendas_comparativo.empty and len(anos_comparacao) >= 1:
        # ---------------------------
        # MÉTRICAS COMPARATIVAS
        # ---------------------------
        st.subheader("📊 Métricas Comparativas")
        
        totais_anuais = vendas_comparativo.groupby('Ano')['Valor Total'].sum()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if len(totais_anuais) >= 1:
                ultimo_ano = max(totais_anuais.index)
                valor_ultimo_ano = totais_anuais[ultimo_ano]
                st.metric(
                    f"Total {ultimo_ano}",
                    f"R$ {valor_ultimo_ano:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                )
        
        with col2:
            if len(totais_anuais) >= 2:
                ano_anterior = sorted(totais_anuais.index)[-2]
                valor_ano_anterior = totais_anuais[ano_anterior]
                crescimento = ((valor_ultimo_ano - valor_ano_anterior) / valor_ano_anterior * 100) if valor_ano_anterior > 0 else 0
                st.metric(
                    f"Total {ano_anterior}",
                    f"R$ {valor_ano_anterior:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    f"{crescimento:+.1f}%"
                )
            else:
                st.metric("Comparação", "Selecione 2 anos")
        
        with col3:
            if len(totais_anuais) >= 2:
                st.metric(
                    "Diferença Absoluta",
                    f"R$ {(valor_ultimo_ano - valor_ano_anterior):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                )
            else:
                st.metric("Diferença", "-")
        
        with col4:
            if len(totais_anuais) >= 2:
                st.metric(
                    "Crescimento Percentual",
                    f"{crescimento:+.1f}%"
                )
            else:
                st.metric("Crescimento", "-")
        
        # CORREÇÃO: Ordem correta dos meses
        meses_nomes = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        
        # Mapeia nomes dos meses para números para ordenação correta
        mes_para_numero = {
            'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4, 'Maio': 5, 'Junho': 6,
            'Julho': 7, 'Agosto': 8, 'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12
        }
        
        # CORREÇÃO: Garante ordenação correta dos dados
        vendas_comparativo['Mês_Numero'] = vendas_comparativo['Mês_Nome'].map(mes_para_numero)
        vendas_comparativo_ordenado = vendas_comparativo.sort_values(['Ano', 'Mês_Numero'])
        
        # ---------------------------
        # GRÁFICO DE COMPARAÇÃO MENSAL ENTRE ANOS
        # ---------------------------
        st.subheader("📈 Comparativo Mensal entre Anos")
        
        vendas_comparativo_ordenado['Ano_Mês'] = vendas_comparativo_ordenado['Ano'].astype(str) + ' - ' + vendas_comparativo_ordenado['Mês_Nome']
        
        fig_comparativo_anos = px.line(
            vendas_comparativo_ordenado,
            x='Mês_Nome',
            y='Valor Total',
            color='Ano',
            title=f'<b>Comparativo Mensal entre Anos</b>',
            markers=True,
            template='plotly_white'
        )
        
        fig_comparativo_anos.update_layout(
            xaxis=dict(title='Mês', categoryorder='array', categoryarray=meses_nomes),
            yaxis=dict(title='Valor em R$'),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_comparativo_anos, use_container_width=True)
        
        # ---------------------------
        # GRÁFICO DE BARRAS COMPARATIVO - CORREÇÃO COMPLETA
        # ---------------------------
        st.subheader("📊 Comparativo por Mês - Visão Detalhada")
        
        # CORREÇÃO SIMPLIFICADA: Usar os dados reais em vez de criar DataFrame artificial
        # Criar coluna combinada para ordenação intercalada
        vendas_comparativo_ordenado['Ano_Mês_Combinado'] = vendas_comparativo_ordenado['Ano'].astype(str) + ' - ' + vendas_comparativo_ordenado['Mês_Nome']
        
        # ORDEM INTERCALADA CORRETA: Janeiro 2024, Janeiro 2025, Fevereiro 2024, Fevereiro 2025, etc.
        meses_ordenados = []
        anos_ordenados = sorted(vendas_comparativo_ordenado['Ano'].unique())
        
        for mes in meses_nomes:
            for ano in anos_ordenados:
                combinacao = f"{ano} - {mes}"
                # Verificar se essa combinação existe nos dados
                if combinacao in vendas_comparativo_ordenado['Ano_Mês_Combinado'].values:
                    meses_ordenados.append(combinacao)
        
        # CORREÇÃO: Verificar se temos dados para o gráfico
        if not vendas_comparativo_ordenado.empty:
            fig_barras_comparativo = px.bar(
                vendas_comparativo_ordenado,
                x='Ano_Mês_Combinado',
                y='Valor Total',
                color='Ano',
                title='<b>Comparativo de Vendas por Mês (Barras Intercaladas)</b>',
                template='plotly_white'
            )
            
            fig_barras_comparativo.update_layout(
                xaxis=dict(
                    title='Mês - Ano', 
                    categoryorder='array', 
                    categoryarray=meses_ordenados,
                    tickangle=45
                ),
                yaxis=dict(title='Valor em R$'),
                showlegend=True
            )
            
            st.plotly_chart(fig_barras_comparativo, use_container_width=True)
        else:
            st.info("📊 Não há dados suficientes para exibir o gráfico de barras")
        
        # ---------------------------
        # TABELA DE COMPARAÇÃO DETALHADA
        # ---------------------------
        st.subheader("📋 Tabela Comparativa Detalhada")
        
        # CORREÇÃO: Usar pivot_table de forma correta
        tabela_completa = vendas_comparativo_ordenado.pivot_table(
            index='Mês_Nome',
            columns='Ano',
            values='Valor Total',
            aggfunc='sum',
            fill_value=0
        ).reset_index()
        
        # Adicionar coluna de número do mês para ordenação
        tabela_completa['Mês_Numero'] = tabela_completa['Mês_Nome'].map(mes_para_numero)
        tabela_completa = tabela_completa.sort_values('Mês_Numero')
        
        # Remover coluna de número do mês da exibição
        tabela_exibicao = tabela_completa.drop('Mês_Numero', axis=1)
        
        # CORREÇÃO: Verificar se as colunas de ano existem antes de calcular diferenças
        colunas_ano = [col for col in tabela_exibicao.columns if col != 'Mês_Nome']
        
        if len(colunas_ano) >= 2:
            # Ordenar anos numericamente
            anos_tabela = sorted([int(col) for col in colunas_ano], reverse=True)
            
            for i in range(1, len(anos_tabela)):
                ano_atual = anos_tabela[i-1]
                ano_anterior = anos_tabela[i]
                
                if str(ano_atual) in tabela_exibicao.columns and str(ano_anterior) in tabela_exibicao.columns:
                    coluna_diferenca = f'Diferença {ano_anterior}-{ano_atual}'
                    coluna_crescimento = f'Crescimento % {ano_anterior}-{ano_atual}'
                    
                    # Calcular diferença
                    tabela_exibicao[coluna_diferenca] = (
                        tabela_exibicao[str(ano_atual)] - tabela_exibicao[str(ano_anterior)]
                    )
                    
                    # Calcular crescimento percentual
                    tabela_exibicao[coluna_crescimento] = (
                        (tabela_exibicao[str(ano_atual)] - tabela_exibicao[str(ano_anterior)]) / 
                        tabela_exibicao[str(ano_anterior)].replace(0, float('nan')) * 100
                    ).round(2)
        
        # Formatação final
        tabela_formatada = tabela_exibicao.copy()
        
        for col in tabela_formatada.columns:
            if col == 'Mês_Nome':
                continue
                
            # CORREÇÃO: Verificar se a coluna é string antes de usar 'in'
            if isinstance(col, str) and 'Crescimento' in col:
                tabela_formatada[col] = tabela_formatada[col].apply(
                    lambda x: f"{x:+.1f}%" if pd.notnull(x) and not pd.isna(x) else "-"
                )
            else:
                # Colunas de valores monetários
                tabela_formatada[col] = tabela_formatada[col].apply(
                    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") 
                    if pd.notnull(x) and not pd.isna(x) else "R$ 0,00"
                )
        
        # Exibir tabela
        st.dataframe(tabela_formatada, use_container_width=True)
        
        # ---------------------------
        # COMPARAÇÃO DE PERFORMANCE POR QUARTER - BARRAS INTERCALADAS
        # ---------------------------
        st.subheader("📅 Performance por Quarter")
        
        vendas_comparativo['Quarter'] = 'Q' + (((vendas_comparativo['Mês'] - 1) // 3) + 1).astype(str)
        performance_quarter = vendas_comparativo.groupby(['Ano', 'Quarter'])['Valor Total'].sum().reset_index()
        
        # CORREÇÃO: Criar coluna combinada para barras intercaladas
        performance_quarter['Ano_Quarter'] = performance_quarter['Ano'].astype(str) + ' - ' + performance_quarter['Quarter']
        
        # Ordem correta dos quarters intercalados: Q1/2024, Q1/2025, Q2/2024, Q2/2025, etc.
        quarters_ordenados = []
        quarter_ordem = ['Q1', 'Q2', 'Q3', 'Q4']
        
        for quarter in quarter_ordem:
            for ano in sorted(anos_comparacao):
                combinacao = f"{ano} - {quarter}"
                quarters_ordenados.append(combinacao)
        
        # CORREÇÃO: Verificar se temos dados para o gráfico de quarter
        if not performance_quarter.empty:
            fig_quarter = px.bar(
                performance_quarter,
                x='Ano_Quarter',
                y='Valor Total',
                color='Ano',
                title='<b>Comparativo de Performance por Quarter (Barras Intercaladas)</b>',
                template='plotly_white'
            )
            
            fig_quarter.update_layout(
                xaxis=dict(
                    title='Ano - Quarter', 
                    categoryorder='array', 
                    categoryarray=quarters_ordenados,
                    tickangle=45
                ),
                yaxis=dict(title='Valor em R$'),
                showlegend=True
            )
            
            st.plotly_chart(fig_quarter, use_container_width=True)
        else:
            st.info("📊 Não há dados suficientes para exibir o gráfico de quarters")
        
    else:
        # Mensagem mais específica
        if not anos_comparacao:
            st.info("📊 Selecione pelo menos um ano para visualizar os comparativos")
        elif vendas_comparativo.empty:
            st.info("📊 Não há dados disponíveis para os filtros selecionados")
    
    # ---------------------------
    # VISÃO GERAL ANUAL (sempre visível)
    # ---------------------------
    st.subheader("📈 Visão Geral Anual")
    
    if not vendas_anuais.empty:
        fig_evolucao_anual = px.line(
            vendas_anuais,
            x='Ano',
            y='Venda Anual',
            title='<b>Evolução das Vendas Anuais</b>',
            markers=True,
            template='plotly_white'
        )
        
        fig_evolucao_anual.update_traces(
            line=dict(width=4),
            marker=dict(size=8)
        )
        
        st.plotly_chart(fig_evolucao_anual, use_container_width=True)
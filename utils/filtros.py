import streamlit as st
import pandas as pd

def aplicar_filtros(df):
    """Aplica filtros de data e colunas para DataFrame. Retorna DataFrame e informações do filtro."""

    st.sidebar.header("🎛️ Filtros")
    
    # Container principal para os filtros
    with st.sidebar:
        with st.expander("🔧 Configurações de Filtro", expanded=True):
            
            # Colunas padrão
            colunas_exibir = ['Empresa', 'Data de Emissão', 'Descrição', 'Quantidade', 'Razão Social', 'Valor Total']
            display_columns = [c for c in colunas_exibir if c in df.columns]

            # Filtro de datas
            min_data = df['Data de Emissão'].min().date()
            max_data = df['Data de Emissão'].max().date()

            ultimo_registro = df['Data de Emissão'].max()
            inicio_mes = pd.Timestamp(ultimo_registro.year, ultimo_registro.month, 1).date()
            fim_mes_calendario = (pd.Timestamp(ultimo_registro.year, ultimo_registro.month, 1) + pd.offsets.MonthEnd(1)).date()
            fim_mes = min(fim_mes_calendario, max_data)

            data_range = st.date_input(
                "📅 Selecione o intervalo de datas",
                value=[inicio_mes, fim_mes],
                min_value=min_data,
                max_value=max_data,
                format="DD/MM/YYYY",
                help="Selecione o período para filtrar os dados"
            )

            # Verifica se data_range tem dois elementos (início e fim)
            if len(data_range) == 2:
                data_inicio = pd.to_datetime(data_range[0])
                data_fim = pd.to_datetime(data_range[1])
                mask = (df['Data de Emissão'] >= data_inicio) & (df['Data de Emissão'] <= data_fim)
                df_filtrado = df.loc[mask].copy()
            else:
                # Se não tiver dois elementos, usa todo o range disponível
                df_filtrado = df.copy()

            # Multiselect colunas - "Valor Total" é obrigatório
            default_columns = ['Data de Emissão', 'Valor Total']  # Colunas obrigatórias
            default_columns = [c for c in default_columns if c in display_columns]
            
            # Adiciona outras colunas padrão se existirem
            other_defaults = [c for c in display_columns if c not in default_columns]
            default_columns.extend(other_defaults)

            colunas_selecionadas = st.multiselect(
                "📋 Selecione as colunas para exibição",
                display_columns,
                default=default_columns,
                help="A coluna 'Valor Total' é obrigatória para os cálculos"
            )

            # Garante que "Valor Total" sempre esteja presente
            if 'Valor Total' in display_columns and 'Valor Total' not in colunas_selecionadas:
                colunas_selecionadas.append('Valor Total')
                st.info("⚠️ A coluna 'Valor Total' foi mantida pois é obrigatória para os cálculos.")

            if not colunas_selecionadas:
                st.warning("Selecione ao menos uma coluna.")
                return pd.DataFrame(), {'filtro_aplicado': False}

            # Informações do filtro aplicado
            filtro_info = {'filtro_aplicado': False, 'nome_filtro': '', 'valor_filtro': ''}

            # Selectbox para filtro extra (exceto numéricos)
            colunas_filtraveis = [c for c in colunas_selecionadas if c not in ['Quantidade', 'Valor Total', 'Data de Emissão']]

            if colunas_filtraveis:
                col_filtro = st.selectbox("🔍 Filtrar por coluna", colunas_filtraveis)
                opcoes = ["Todos"] + sorted(df_filtrado[col_filtro].dropna().unique())
                val_filtro = st.selectbox("🎯 Selecione o valor", opcoes)
                
                if val_filtro != "Todos":
                    df_filtrado = df_filtrado[df_filtrado[col_filtro] == val_filtro]
                    filtro_info = {
                        'filtro_aplicado': True,
                        'nome_filtro': col_filtro,
                        'valor_filtro': val_filtro
                    }

            # Formata a coluna Empresa para inteiro (sem casas decimais) se existir
            if 'Empresa' in df_filtrado.columns:
                df_filtrado['Empresa'] = df_filtrado['Empresa'].astype(int, errors='ignore')

            # Formata data e define como índice
            if 'Data de Emissão' in df_filtrado.columns:
                df_filtrado['Data de Emissão'] = df_filtrado['Data de Emissão'].dt.strftime('%d/%m/%Y')
                df_filtrado = df_filtrado.set_index('Data de Emissão')
                # Remove 'Data de Emissão' da lista de colunas selecionadas pois agora é índice
                if 'Data de Emissão' in colunas_selecionadas:
                    colunas_selecionadas.remove('Data de Emissão')

            # Garante que pelo menos uma coluna esteja selecionada (além do índice)
            if not colunas_selecionadas:
                colunas_selecionadas = ['Valor Total']  # Coluna mínima obrigatória

    return df_filtrado[colunas_selecionadas], filtro_info
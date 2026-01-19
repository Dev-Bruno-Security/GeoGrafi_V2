"""
Aplicação Streamlit simplificada para processamento de CEPs
- Apenas valida CEPs (não busca coordenadas)
- Muito mais rápida (0.1s por CEP vs 2.5s com coordenadas)
"""

import streamlit as st
import pandas as pd
import tempfile
import logging
from pathlib import Path
from io import BytesIO
from modules.csv_processor import CSVProcessor
from modules.logging_config import setup_logging

# Importação condicional do plotly
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Configuração
st.set_page_config(page_title="GeoGrafi - Validação CEP", layout="wide")
setup_logging(level='INFO')
logger = logging.getLogger(__name__)

# Estado
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False

st.title("🌍 GeoGrafi - Validação e Correção de CEPs")

with st.sidebar:
    st.header("⚙️ Configurações")
    st.info("""
    **Modo Rápido com Correção**
    
    ✅ Valida CEPs via ViaCEP  
    ✅ Corrige endereços  
    ✅ Retorna logradouro, bairro, cidade, UF
    
    ⚡ ~0.15s por CEP (com rate limiting)
    
    **Versão com coordenadas disponível em `app_geo.py`**
    """)

# Upload de arquivo
st.header("1️⃣ Upload do Arquivo")
col1, col2 = st.columns([3, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Selecione um arquivo CSV",
        type=['csv'],
        accept_multiple_files=False
    )

with col2:
    if uploaded_file:
        file_size_mb = uploaded_file.size / (1024 * 1024)
        st.metric("Tamanho", f"{file_size_mb:.1f} MB")

# Processamento
if uploaded_file:
    st.session_state.uploaded_file = uploaded_file
    
    st.header("2️⃣ Processamento")
    
    # Configurações de processamento
    col1, col2, col3 = st.columns(3)
    with col1:
        chunk_size = st.number_input("Tamanho do chunk", min_value=100, max_value=5000, value=1000, step=100)
    
    with col2:
        encoding = st.selectbox(
            "Encoding",
            ["utf-8", "iso-8859-1", "cp1252", "auto-detect"],
            index=0
        )
    
    with col3:
        delimiter = st.selectbox(
            "Delimitador",
            [",", ";", "|", "\t", "auto-detect"],
            index=0
        )
    
    # Preview do arquivo
    if uploaded_file:
        with st.expander("👁️ Visualizar primeiras linhas do arquivo", expanded=False):
            try:
                # Lê apenas as primeiras linhas para preview
                preview_df = pd.read_csv(uploaded_file, nrows=5, dtype=str)
                st.write(f"**Colunas detectadas:** {', '.join([f'`{col}`' for col in preview_df.columns])}")
                st.dataframe(preview_df)
                
                # Verifica se tem coluna de CEP
                has_cep = any('cep' in col.lower() or 'postal' in col.lower() or 'zip' in col.lower() 
                             for col in preview_df.columns)
                
                if has_cep:
                    st.success("✅ Coluna de CEP detectada!")
                else:
                    st.warning("⚠️ Nenhuma coluna de CEP detectada. Certifique-se de ter uma coluna chamada 'cep' ou 'CEP'.")
                
                # Reset file pointer
                uploaded_file.seek(0)
            except Exception as e:
                st.error(f"Erro ao ler preview: {e}")
                uploaded_file.seek(0)
    
    # Botão de processar
    if st.button("▶️ Processar Arquivo", key="process_btn"):
        with st.spinner("⏳ Processando arquivo..."):
            try:
                # Salva arquivo temporário
                with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
                    tmp.write(uploaded_file.getbuffer())
                    tmp_path = tmp.name
                
                logger.info(f"Arquivo temporário: {tmp_path}")
                
                # Cria processador (SEM busca de coordenadas = RÁPIDO)
                processor = CSVProcessor(
                    chunk_size=chunk_size,
                    use_cache=True,
                    fetch_coordinates=False  # 🔑 DESABILITADO = RÁPIDO
                )
                
                # Processa
                result = processor.process_file(tmp_path)
                
                st.session_state.processed_data = result
                st.session_state.processing_complete = True
                
                logger.info(f"Processamento completo: {len(result)} linhas")
                
            except Exception as e:
                st.error(f"❌ Erro ao processar: {str(e)}")
                logger.exception("Erro no processamento")

# Exibe resultados
if st.session_state.processing_complete and st.session_state.processed_data is not None:
    df = st.session_state.processed_data
    
    st.header("3️⃣ Resultados")
    
    # Estatísticas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Total de Linhas", len(df))
    with col2:
        valid_count = (df['cep_valido'] == True).sum() if 'cep_valido' in df.columns else 0
        st.metric("✅ CEPs Válidos", valid_count)
    with col3:
        invalid_count = (df['cep_valido'] == False).sum() if 'cep_valido' in df.columns else 0
        st.metric("❌ CEPs Inválidos", invalid_count)
    with col4:
        if 'cep_valido' in df.columns and len(df) > 0:
            taxa = (valid_count / len(df) * 100)
            st.metric("📈 Taxa de Sucesso", f"{taxa:.1f}%")
    
    # Visualização dos dados
    st.subheader("📋 Dados Processados")
    
    # Seleciona colunas importantes para exibir
    display_cols = []
    for col in ['cep_original', 'cep_corrigido', 'cep_valido', 'logradouro', 'bairro', 'cidade', 'uf']:
        if col in df.columns:
            display_cols.append(col)
    
    # Adiciona outras colunas que não são de processamento
    for col in df.columns:
        if col not in display_cols and col not in ['latitude', 'longitude']:
            display_cols.append(col)
    
    if display_cols:
        st.dataframe(df[display_cols], width='stretch')
    else:
        st.dataframe(df, width='stretch')
    
    # Download
    st.subheader("💾 Download")
    
    col1, col2 = st.columns(2)
    
    # Nome do arquivo
    output_name = "resultado"
    if st.session_state.uploaded_file:
        output_name = f"resultado_{st.session_state.uploaded_file.name}"
    
    with col1:
        csv_data = df.to_csv(index=False, encoding='utf-8')
        st.download_button(
            label="📥 Baixar CSV",
            data=csv_data,
            file_name=output_name if output_name.endswith('.csv') else output_name + '.csv',
            mime="text/csv"
        )
    
    with col2:
        # Cria buffer em memória para o Excel
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Resultado')
        buffer.seek(0)
        
        excel_name = output_name.replace('.csv', '.xlsx') if '.csv' in output_name else output_name + '.xlsx'
        st.download_button(
            label="📥 Baixar Excel",
            data=buffer,
            file_name=excel_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    # Filtros
    st.subheader("🔍 Análise")
    
    tab1, tab2, tab3 = st.tabs(["✅ CEPs Válidos", "❌ CEPs Inválidos", "📊 Estatísticas"])
    
    with tab1:
        if 'cep_valido' in df.columns:
            valid_df = df[df['cep_valido'] == True]
            st.write(f"**{len(valid_df)} CEPs válidos encontrados**")
            
            # Mostra colunas relevantes
            cols_to_show = [c for c in ['cep_original', 'cep_corrigido', 'logradouro', 'bairro', 'cidade', 'uf'] if c in valid_df.columns]
            if cols_to_show:
                st.dataframe(valid_df[cols_to_show], width='stretch')
            else:
                st.dataframe(valid_df, width='stretch')
        else:
            st.info("Coluna 'cep_valido' não encontrada")
    
    with tab2:
        if 'cep_valido' in df.columns:
            invalid_df = df[df['cep_valido'] == False]
            st.write(f"**{len(invalid_df)} CEPs inválidos encontrados**")
            
            if len(invalid_df) > 0:
                st.warning("⚠️ Estes CEPs não foram encontrados na base do ViaCEP. Verifique se estão corretos.")
                
                # Mostra CEPs inválidos
                cols_to_show = [c for c in ['cep_original', 'cep_corrigido'] if c in invalid_df.columns]
                if cols_to_show:
                    st.dataframe(invalid_df[cols_to_show], width='stretch')
                else:
                    st.dataframe(invalid_df, width='stretch')
            else:
                st.success("🎉 Todos os CEPs são válidos!")
        else:
            st.info("Coluna 'cep_valido' não encontrada")
    
    with tab3:
        st.write("**📊 Estatísticas do Processamento:**")
        
        valid_count = (df['cep_valido'] == True).sum() if 'cep_valido' in df.columns else 0
        invalid_count = (df['cep_valido'] == False).sum() if 'cep_valido' in df.columns else 0
        total = len(df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("📊 Total Processado", total)
            st.metric("✅ CEPs Válidos", valid_count)
            st.metric("❌ CEPs Inválidos", invalid_count)
        
        with col2:
            if total > 0:
                taxa_sucesso = (valid_count / total) * 100
                taxa_erro = (invalid_count / total) * 100
                
                st.metric("📈 Taxa de Sucesso", f"{taxa_sucesso:.1f}%")
                st.metric("📉 Taxa de Erro", f"{taxa_erro:.1f}%")
                
                # Gráfico visual (se plotly disponível)
                if PLOTLY_AVAILABLE:
                    fig = go.Figure(data=[go.Pie(
                        labels=['Válidos', 'Inválidos'],
                        values=[valid_count, invalid_count],
                        marker=dict(colors=['#28a745', '#dc3545']),
                        hole=0.4
                    )])
                    
                    fig.update_layout(
                        title="Distribuição de CEPs",
                        height=300
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # Gráfico de barras simples sem plotly
                    st.bar_chart({'Válidos': valid_count, 'Inválidos': invalid_count})
        
        # Resumo textual
        st.divider()
        st.write("**📝 Resumo:**")
        st.write(f"- De **{total}** CEPs processados:")
        st.write(f"  - ✅ **{valid_count}** foram validados com sucesso")
        st.write(f"  - ❌ **{invalid_count}** não foram encontrados na base do ViaCEP")
        
        if 'logradouro' in df.columns:
            with_address = df['logradouro'].notna().sum()
            st.write(f"  - 🏠 **{with_address}** possuem endereço completo")


# Footer
st.divider()
st.caption("🚀 GeoGrafi V2 - Validação e Correção de CEPs | Modo: Rápido com ViaCEP")

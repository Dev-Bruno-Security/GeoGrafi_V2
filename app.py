"""
Interface Streamlit Principal para Processamento de Dados Geográficos
Versão Modularizada - GeoGrafi v2.0
"""

import streamlit as st
import pandas as pd
import tempfile
from pathlib import Path

# Configuração de logging (silencioso por padrão)
from modules.logging_config import setup_logging
setup_logging(level='WARNING')

# Importações dos módulos
from modules import (
    CSVProcessor,
    get_config,
    update_config
)
from modules.streamlit_components import (
    apply_custom_css,
    show_success_message,
    show_error_message,
    show_info_message,
    display_file_info,
    display_dataframe_preview,
    create_settings_sidebar,
    create_download_button,
    display_processing_stats,
    initialize_session_state
)

# Configuração da página
st.set_page_config(
    page_title="GeoGrafi - Processador de CEP e Coordenadas",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplica CSS customizado
apply_custom_css()

# Inicializa session state
initialize_session_state({
    'processor': None,
    'result_df': None,
    'stats': None,
    'file_processed': False,
    'file_info': None
})

# Título
st.markdown("# 📍 GeoGrafi - Processador Geográfico")
st.markdown("### Enriqueça seus dados CSV com CEPs e coordenadas")

# Sidebar com configurações
settings = create_settings_sidebar()

# Atualiza configurações globais
update_config(
    chunk_size=settings['chunk_size'],
    max_workers=settings['max_workers'],
    use_cache=settings['use_cache']
)

# Abas principais
tab1, tab2, tab3 = st.tabs(["📤 Processar", "📋 Informações", "❓ Ajuda"])

with tab1:
    st.subheader("Upload de Arquivo")
    
    uploaded_file = st.file_uploader(
        "Escolha um arquivo CSV",
        type=["csv"],
        help="Arraste e solte ou clique para selecionar"
    )
    
    if uploaded_file:
        # Salva arquivo temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        # Mostra informações do arquivo
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        st.info(f"📄 Arquivo: {uploaded_file.name} ({file_size_mb:.2f} MB)")
        
        # Botão de processar
        if st.button("🚀 Processar Arquivo", type="primary"):
            try:
                with st.spinner("Processando dados..."):
                    # Cria processador
                    config = get_config()
                    processor = CSVProcessor(
                        chunk_size=config.processing.chunk_size,
                        max_workers=config.processing.max_workers,
                        use_cache=config.processing.use_cache,
                        cache_db=config.processing.cache_db_path,
                        fetch_coordinates=True  # ✅ Busca automática de coordenadas
                    )
                    
                    # Container para progresso
                    progress_container = st.container()
                    
                    with progress_container:
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        def update_progress(progress):
                            progress_bar.progress(min(progress / 100, 1.0))
                            status_text.text(f"Processando: {progress:.1f}%")
                        
                        # Processa arquivo
                        result_df = processor.process_file(
                            tmp_path,
                            progress_callback=update_progress
                        )
                    
                    # Armazena resultados
                    st.session_state.result_df = result_df
                    st.session_state.stats = processor.stats
                    st.session_state.file_processed = True
                    
                    # Limpa progresso
                    progress_bar.empty()
                    status_text.empty()
                    
                    show_success_message("Processamento concluído com sucesso!")
            
            except Exception as e:
                show_error_message(f"Erro ao processar arquivo: {str(e)}")
        
        # Exibe resultados se já processado
        if st.session_state.file_processed and st.session_state.result_df is not None:
            st.markdown("---")
            
            # Estatísticas
            display_processing_stats(st.session_state.stats)
            
            st.markdown("---")
            
            display_dataframe_preview(
                st.session_state.result_df,
                title="📊 Resultado do Processamento",
                max_rows=10
            )
            
            st.markdown("---")
            
            # Download
            st.subheader("💾 Download")
            col1, col2 = st.columns(2)
            
            with col1:
                create_download_button(
                    st.session_state.result_df,
                    filename="resultado_processado.csv",
                    label="📥 Baixar CSV Completo"
                )
            
            with col2:
                # Baixar apenas registros com coordenadas (se as colunas existirem)
                has_lat = 'DS_LATITUDE' in st.session_state.result_df.columns
                has_lon = 'DS_LONGITUDE' in st.session_state.result_df.columns
                has_lat_correta = 'DS_LATITUDE_CORRETA' in st.session_state.result_df.columns
                has_lon_correta = 'DS_LONGITUDE_CORRETA' in st.session_state.result_df.columns
                
                if (has_lat and has_lon) or (has_lat_correta and has_lon_correta):
                    # Usa colunas corretas se disponíveis, senão usa as originais
                    lat_col = 'DS_LATITUDE_CORRETA' if has_lat_correta else 'DS_LATITUDE'
                    lon_col = 'DS_LONGITUDE_CORRETA' if has_lon_correta else 'DS_LONGITUDE'
                    
                    df_with_coords = st.session_state.result_df[
                        st.session_state.result_df[lat_col].notna() &
                        st.session_state.result_df[lon_col].notna()
                    ]
                    
                    if not df_with_coords.empty:
                        create_download_button(
                            df_with_coords,
                            filename="resultado_com_coordenadas.csv",
                            label="📥 Baixar apenas com Coordenadas"
                        )
                    else:
                        st.info("Nenhum registro com coordenadas")
                else:
                    st.info("💡 As coordenadas são buscadas automaticamente durante o processamento")

with tab2:
    st.subheader("ℹ️ Sobre o GeoGrafi")
    
    st.markdown("""
    O **GeoGrafi** é uma ferramenta para enriquecimento de dados geográficos em arquivos CSV.
    
    ### Funcionalidades
    
    - ✅ **Validação de CEP**: Verifica e corrige CEPs usando ViaCEP (automático)
    - 🗺️ **Geocoding**: Adiciona coordenadas (latitude/longitude) usando Nominatim (automático)
    - 🔄 **Processamento em Chunks**: Suporta arquivos grandes com baixo uso de memória
    - 💾 **Cache Local**: Armazena resultados para acelerar processamento
    - ⚡ **Processamento Paralelo**: Usa múltiplas threads para maior velocidade
    
    ### Como funciona
    
    1. **Upload**: Envie seu arquivo CSV com dados de endereço
    2. **Processamento**: O sistema valida CEPs e busca coordenadas
    3. **Download**: Baixe o arquivo enriquecido com os dados corrigidos
    
    ### Colunas Esperadas
    
    - `CD_CEP`: Código do CEP
    - `NM_LOGRADOURO`: Nome do logradouro (rua, avenida, etc)
    - `NM_BAIRRO`: Nome do bairro
    - `NM_MUNICIPIO`: Nome do município
    - `NM_UF`: Sigla da UF (estado)
    - `DS_LATITUDE`: Latitude (será preenchida)
    - `DS_LONGITUDE`: Longitude (será preenchida)
    
    ### Colunas de Saída Adicionais
    
    - `CD_CEP_CORRETO`: CEP corrigido (se diferente do original)
    - `NM_LOGRADOURO_CORRETO`: Logradouro corrigido
    - `NM_BAIRRO_CORRETO`: Bairro corrigido
    - `NM_MUNICIPIO_CORRETO`: Município corrigido
    - `NM_UF_CORRETO`: UF corrigida
    """)
    
    st.markdown("---")
    
    st.subheader("🔧 Configurações")
    
    st.markdown("""
    ### Tamanho do Chunk
    
    Número de linhas processadas por vez. Valores maiores usam mais memória mas são mais rápidos.
    - **Pequeno (100-500)**: Para computadores com pouca memória
    - **Médio (500-2000)**: Balanço entre velocidade e memória
    - **Grande (2000-5000)**: Para arquivos muito grandes e computadores potentes
    
    ### Número de Workers
    
    Quantidade de threads paralelas para processamento.
    - **1-3**: Para conexões de internet lentas
    - **3-5**: Ideal para a maioria dos casos
    - **5-10**: Para conexões rápidas e muitos dados
    
    ### Cache Local
    
    Armazena resultados de CEPs e coordenadas já consultados para acelerar 
    processamentos futuros do mesmo arquivo ou arquivos similares.
    """)

with tab3:
    st.subheader("❓ Ajuda e Suporte")
    
    with st.expander("🤔 Como preparar meu arquivo CSV?"):
        st.markdown("""
        1. Certifique-se que seu arquivo tem as colunas corretas
        2. Use encoding UTF-8 ou Latin-1
        3. O delimitador pode ser vírgula, ponto-e-vírgula ou tab (detectado automaticamente)
        4. A primeira linha deve conter os nomes das colunas
        """)
    
    with st.expander("⚠️ O que fazer se der erro?"):
        st.markdown("""
        1. Verifique se o arquivo está no formato CSV
        2. Confirme que as colunas têm os nomes corretos
        3. Tente reduzir o tamanho do chunk
        4. Reduza o número de workers
        5. Verifique sua conexão com a internet
        """)
    
    with st.expander("🐌 Por que está lento?"):
        st.markdown("""
        - APIs externas têm limite de requisições por segundo
        - Arquivos grandes naturalmente levam mais tempo
        - Primeira execução é mais lenta (cache vazio)
        - Tente aumentar o chunk size se tiver memória disponível
        """)
    
    with st.expander("💡 Dicas de Performance"):
        st.markdown("""
        - **Use cache**: Acelera muito em processamentos repetidos
        - **Ajuste o chunk size**: Encontre o equilíbrio ideal para seu sistema
        - **Conexão estável**: Garante menos erros e reprocessamentos
        - **Processe aos poucos**: Divida arquivos muito grandes em partes menores
        """)
    
    st.markdown("---")
    
    st.info("""
    **GeoGrafi v2.0** - Desenvolvido com Streamlit, Pandas e APIs públicas
    
    Usa ViaCEP (CEPs brasileiros) e Nominatim/OpenStreetMap (geocoding gratuito)
    """)

# Rodapé
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #888;">GeoGrafi v2.0 | Processador de Dados Geográficos</div>',
    unsafe_allow_html=True
)

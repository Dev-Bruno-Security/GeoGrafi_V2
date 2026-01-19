"""
Componentes reutilizáveis de interface Streamlit para GeoGrafi
"""

import streamlit as st
from typing import Optional, Dict, Any, Callable
import pandas as pd


def apply_custom_css():
    """Aplica CSS customizado para o tema dark do Streamlit"""
    st.markdown("""
    <style>
        .stMetric {
            background-color: #1e2028;
            color: #e8ecf4;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #2f3340;
        }
        .stMetric label {
            color: #e8ecf4 !important;
        }
        .stMetric p {
            color: #8ab4ff !important;
            font-size: 24px !important;
            font-weight: bold !important;
        }
        .header-title {
            color: #8ab4ff;
            text-align: center;
        }
        .success-box {
            background-color: #123226;
            color: #d3f2e4;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #2ecc71;
            border-right: 1px solid #1f7a50;
        }
        .error-box {
            background-color: #2f1b22;
            color: #f6c1c8;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #e74c3c;
            border-right: 1px solid #80333d;
        }
        .info-box {
            background-color: #132736;
            color: #c7e9ff;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #17a2b8;
            border-right: 1px solid #0d4f63;
        }
        .warning-box {
            background-color: #332b1a;
            color: #ffe5b4;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #f39c12;
            border-right: 1px solid #7a5c15;
        }
    </style>
    """, unsafe_allow_html=True)


def show_success_message(message: str):
    """Exibe mensagem de sucesso com estilo customizado"""
    st.markdown(
        f'<div class="success-box">✅ {message}</div>',
        unsafe_allow_html=True
    )


def show_error_message(message: str):
    """Exibe mensagem de erro com estilo customizado"""
    st.markdown(
        f'<div class="error-box">❌ {message}</div>',
        unsafe_allow_html=True
    )


def show_info_message(message: str):
    """Exibe mensagem de informação com estilo customizado"""
    st.markdown(
        f'<div class="info-box">ℹ️ {message}</div>',
        unsafe_allow_html=True
    )


def show_warning_message(message: str):
    """Exibe mensagem de aviso com estilo customizado"""
    st.markdown(
        f'<div class="warning-box">⚠️ {message}</div>',
        unsafe_allow_html=True
    )


def display_metrics(stats: Dict[str, Any], col_count: int = 4):
    """
    Exibe métricas em colunas
    
    Args:
        stats: Dicionário com estatísticas (label: value)
        col_count: Número de colunas
    """
    cols = st.columns(col_count)
    
    for idx, (label, value) in enumerate(stats.items()):
        with cols[idx % col_count]:
            st.metric(label=label, value=value)


def display_file_info(file_info: Dict[str, Any]):
    """
    Exibe informações de arquivo
    
    Args:
        file_info: Dicionário com informações do arquivo
    """
    st.subheader("📄 Informações do Arquivo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Tamanho:** {file_info.get('size_mb', 'N/A')}")
        st.write(f"**Encoding:** {file_info.get('encoding', 'N/A')}")
    
    with col2:
        st.write(f"**Delimitador:** `{file_info.get('delimiter', 'N/A')}`")
        if 'total_rows' in file_info:
            st.write(f"**Total de linhas:** {file_info['total_rows']:,}")


def display_dataframe_preview(
    df: pd.DataFrame,
    title: str = "Prévia dos Dados",
    max_rows: int = 10
):
    """
    Exibe prévia de DataFrame com opções de visualização
    
    Args:
        df: DataFrame a ser exibido
        title: Título da seção
        max_rows: Número máximo de linhas a exibir
    """
    st.subheader(title)
    
    if df.empty:
        st.info("Nenhum dado disponível")
        return
    
    # Opções de visualização
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.write(f"**Shape:** {df.shape[0]} linhas × {df.shape[1]} colunas")
    
    with col2:
        view_option = st.selectbox(
            "Visualizar",
            ["Primeiras", "Últimas", "Amostra"],
            key=f"view_{title}"
        )
    
    with col3:
        n_rows = st.number_input(
            "Linhas",
            min_value=1,
            max_value=min(100, len(df)),
            value=min(max_rows, len(df)),
            key=f"rows_{title}"
        )
    
    # Exibe dados conforme opção
    if view_option == "Primeiras":
        st.dataframe(df.head(n_rows))
    elif view_option == "Últimas":
        st.dataframe(df.tail(n_rows))
    else:
        st.dataframe(df.sample(min(n_rows, len(df))))


def create_progress_tracker(total: int, label: str = "Processando...") -> Callable:
    """
    Cria um tracker de progresso
    
    Args:
        total: Total de itens a processar
        label: Label da barra de progresso
        
    Returns:
        Função de callback para atualizar progresso
    """
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def update_progress(current: int, extra_info: str = ""):
        progress = current / total if total > 0 else 0
        progress_bar.progress(min(progress, 1.0))
        
        info = f"{label} {current}/{total}"
        if extra_info:
            info += f" - {extra_info}"
        
        status_text.text(info)
    
    return update_progress


def create_file_uploader(
    label: str = "Escolha um arquivo CSV",
    accepted_types: list = None,
    help_text: str = None
) -> Optional[Any]:
    """
    Cria um uploader de arquivo com configurações padrão
    
    Args:
        label: Label do uploader
        accepted_types: Lista de tipos aceitos
        help_text: Texto de ajuda
        
    Returns:
        Arquivo carregado ou None
    """
    if accepted_types is None:
        accepted_types = ["csv", "txt"]
    
    return st.file_uploader(
        label,
        type=accepted_types,
        help=help_text or "Arraste e solte ou clique para selecionar"
    )


def create_settings_sidebar(
    defaults: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Cria sidebar com configurações padrão
    
    Args:
        defaults: Valores padrão das configurações
        
    Returns:
        Dicionário com configurações selecionadas
    """
    if defaults is None:
        defaults = {
            'chunk_size': 1000,
            'max_workers': 3,
            'use_cache': True
        }
    
    with st.sidebar:
        st.markdown("## ⚙️ Configurações")
        
        settings = {}
        
        # Chunk size
        settings['chunk_size'] = st.slider(
            "Tamanho do chunk (linhas)",
            min_value=100,
            max_value=5000,
            value=defaults.get('chunk_size', 1000),
            step=100,
            help="Número de linhas processadas por vez (impacta memória)"
        )
        
        # Max workers
        settings['max_workers'] = st.slider(
            "Número de workers",
            min_value=1,
            max_value=10,
            value=defaults.get('max_workers', 3),
            help="Threads paralelas para processamento"
        )
        
        # Cache
        settings['use_cache'] = st.checkbox(
            "Usar cache local",
            value=defaults.get('use_cache', True),
            help="Cacheia resultados para acelerar processamento"
        )
        
        return settings


def create_download_button(
    data: pd.DataFrame,
    filename: str = "resultado.csv",
    label: str = "📥 Baixar Resultado",
    mime: str = "text/csv"
) -> None:
    """
    Cria botão de download para DataFrame
    
    Args:
        data: DataFrame a ser baixado
        filename: Nome do arquivo
        label: Label do botão
        mime: Tipo MIME do arquivo
    """
    csv = data.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label=label,
        data=csv,
        file_name=filename,
        mime=mime
    )


def display_processing_stats(stats: Dict[str, Any]):
    """
    Exibe estatísticas de processamento
    
    Args:
        stats: Dicionário com estatísticas
    """
    st.subheader("📊 Estatísticas de Processamento")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de linhas", f"{stats.get('total_rows', 0):,}")
    
    with col2:
        st.metric("Linhas processadas", f"{stats.get('processed_rows', 0):,}")
    
    with col3:
        st.metric("CEPs corrigidos", f"{stats.get('fixed_ceps', 0):,}")
    
    with col4:
        st.metric("Coordenadas encontradas", f"{stats.get('found_coordinates', 0):,}")
    
    # Erros (se houver)
    if stats.get('errors'):
        with st.expander("⚠️ Ver Erros", expanded=False):
            st.write(f"Total de erros: {len(stats['errors'])}")
            if len(stats['errors']) <= 10:
                for error in stats['errors']:
                    st.write(f"- Linha {error.get('row', '?')}: {error.get('error', 'Erro desconhecido')}")
            else:
                st.write("Exibindo primeiros 10 erros:")
                for error in stats['errors'][:10]:
                    st.write(f"- Linha {error.get('row', '?')}: {error.get('error', 'Erro desconhecido')}")
                st.write(f"... e mais {len(stats['errors']) - 10} erros")


def initialize_session_state(defaults: Dict[str, Any] = None):
    """
    Inicializa variáveis de sessão do Streamlit
    
    Args:
        defaults: Dicionário com valores padrão para session_state
    """
    if defaults is None:
        defaults = {
            'processor': None,
            'result_df': None,
            'stats': None,
            'file_processed': False
        }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

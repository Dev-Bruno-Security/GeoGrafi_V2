"""
Módulo GeoGrafi - Processamento de dados geográficos
Enriquecimento de CSV com CEPs e coordenadas
"""

# Importações principais
from .cep_validator import CEPValidator
from .geocoder import Geocoder
from .csv_processor import CSVProcessor
from .csv_reader import CSVReader, CSVAnalyzer
from .cache_manager import CacheManager
from .config import (
    AppConfig,
    APIConfig,
    ProcessingConfig,
    ColumnMapping,
    get_config,
    update_config
)
from .utils import (
    clean_cep,
    format_cep,
    normalize_text,
    normalize_address,
    is_valid_coordinate,
    format_file_size,
    sanitize_filename,
    build_address_query,
    get_address_hash
)

# Versão do módulo
__version__ = "2.0.0"

# Exportações públicas
__all__ = [
    # Classes principais
    'CEPValidator',
    'Geocoder',
    'CSVProcessor',
    'CSVReader',
    'CSVAnalyzer',
    'CacheManager',
    
    # Configurações
    'AppConfig',
    'APIConfig',
    'ProcessingConfig',
    'ColumnMapping',
    'get_config',
    'update_config',
    
    # Utilitários
    'clean_cep',
    'format_cep',
    'normalize_text',
    'normalize_address',
    'is_valid_coordinate',
    'format_file_size',
    'sanitize_filename',
    'build_address_query',
    'get_address_hash',
]

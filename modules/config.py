"""
Módulo de configuração para o GeoGrafi
Centraliza todas as configurações do projeto
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class APIConfig:
    """Configurações de APIs externas"""
    # ViaCEP
    viacep_base_url: str = "https://viacep.com.br/ws"
    viacep_timeout: int = 30
    viacep_retry_attempts: int = 3
    viacep_retry_delay: float = 2.0
    viacep_rate_limit: float = 0.1
    
    # Nominatim (OpenStreetMap)
    nominatim_base_url: str = "https://nominatim.openstreetmap.org/search"
    nominatim_timeout: int = 20
    nominatim_retry_attempts: int = 3
    nominatim_retry_delay: float = 3.0
    nominatim_rate_limit: float = 1.5
    nominatim_app_name: str = "GeoGrafi"


@dataclass
class ProcessingConfig:
    """Configurações de processamento"""
    chunk_size: int = 1000
    max_workers: int = 3
    use_cache: bool = True
    cache_db_path: str = "cache.db"
    prefer_fast_engine: bool = True


@dataclass
class ColumnMapping:
    """Mapeamento de nomes de colunas"""
    # Colunas esperadas
    cep: str = "CD_CEP"
    logradouro: str = "NM_LOGRADOURO"
    bairro: str = "NM_BAIRRO"
    municipio: str = "NM_MUNICIPIO"
    uf: str = "NM_UF"
    latitude: str = "DS_LATITUDE"
    longitude: str = "DS_LONGITUDE"
    
    # Colunas de correção
    cep_correto: str = "CD_CEP_CORRETO"
    logradouro_correto: str = "NM_LOGRADOURO_CORRETO"
    bairro_correto: str = "NM_BAIRRO_CORRETO"
    municipio_correto: str = "NM_MUNICIPIO_CORRETO"
    uf_correto: str = "NM_UF_CORRETO"


@dataclass
class AppConfig:
    """Configuração geral da aplicação"""
    api: APIConfig = None
    processing: ProcessingConfig = None
    columns: ColumnMapping = None
    
    def __post_init__(self):
        if self.api is None:
            self.api = APIConfig()
        if self.processing is None:
            self.processing = ProcessingConfig()
        if self.columns is None:
            self.columns = ColumnMapping()


# Instância global de configuração
config = AppConfig()


def get_config() -> AppConfig:
    """Retorna a configuração global da aplicação"""
    return config


def update_config(
    chunk_size: Optional[int] = None,
    max_workers: Optional[int] = None,
    use_cache: Optional[bool] = None,
    cache_db_path: Optional[str] = None
) -> None:
    """
    Atualiza configurações de processamento
    
    Args:
        chunk_size: Tamanho dos chunks para processamento
        max_workers: Número de workers paralelos
        use_cache: Se deve usar cache local
        cache_db_path: Caminho do banco de cache
    """
    global config
    
    if chunk_size is not None:
        config.processing.chunk_size = chunk_size
    if max_workers is not None:
        config.processing.max_workers = max_workers
    if use_cache is not None:
        config.processing.use_cache = use_cache
    if cache_db_path is not None:
        config.processing.cache_db_path = cache_db_path

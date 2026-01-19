"""
Configuração de logging para o GeoGrafi
"""

import logging
import sys


def setup_logging(level='WARNING', log_file=None):
    """
    Configura o sistema de logging
    
    Args:
        level: Nível de logging ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        log_file: Arquivo para salvar logs (None = apenas console)
    """
    # Converte string para nível
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.WARNING)
    
    # Formato do log
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Configuração básica
    handlers = []
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    handlers.append(console_handler)
    
    # Handler para arquivo (se especificado)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Sempre DEBUG no arquivo
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        handlers.append(file_handler)
    
    # Configura root logger
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=handlers,
        force=True
    )
    
    # Silencia alguns loggers verbosos
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('chardet').setLevel(logging.WARNING)
    
    # Configura loggers dos módulos
    for module in ['cep_validator', 'geocoder', 'csv_processor', 'cache_manager']:
        logger = logging.getLogger(module)
        logger.setLevel(level)


def set_debug_mode():
    """Ativa modo debug (logs detalhados)"""
    setup_logging(level=logging.DEBUG)


def set_quiet_mode():
    """Ativa modo silencioso (apenas erros)"""
    setup_logging(level=logging.ERROR)


def set_normal_mode():
    """Ativa modo normal (informações importantes)"""
    setup_logging(level=logging.INFO)


# Configuração padrão ao importar
setup_logging(level=logging.WARNING)  # Modo silencioso por padrão

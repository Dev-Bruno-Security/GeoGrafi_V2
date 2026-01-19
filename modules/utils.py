"""
Módulo de utilitários para o GeoGrafi
Funções auxiliares compartilhadas entre módulos
"""

import re
from typing import Optional
import pandas as pd


def clean_cep(cep: str) -> Optional[str]:
    """
    Limpa e valida formato de CEP
    
    Args:
        cep: CEP a ser limpo
        
    Returns:
        CEP apenas com dígitos ou None se inválido
    """
    if not cep or pd.isna(cep):
        return None
    
    cep_clean = ''.join(filter(str.isdigit, str(cep)))
    
    if len(cep_clean) == 8:
        return cep_clean
    
    return None


def format_cep(cep: str) -> str:
    """
    Formata CEP para padrão XXXXX-XXX
    
    Args:
        cep: CEP com ou sem formatação
        
    Returns:
        CEP formatado ou string vazia se inválido
    """
    cep_clean = clean_cep(cep)
    
    if cep_clean:
        return f"{cep_clean[:5]}-{cep_clean[5:]}"
    
    return ""


def normalize_text(text: str) -> str:
    """
    Normaliza texto removendo espaços extras e caracteres especiais
    
    Args:
        text: Texto a ser normalizado
        
    Returns:
        Texto normalizado
    """
    if not text or pd.isna(text):
        return ''
    
    # Converte para string e remove espaços extras
    text = str(text).strip()
    
    # Remove múltiplos espaços
    text = re.sub(r'\s+', ' ', text)
    
    return text


def normalize_address(text: str) -> str:
    """
    Normaliza e padroniza endereços para geocoding
    
    Args:
        text: Endereço a ser normalizado
        
    Returns:
        Endereço normalizado
    """
    if not text or pd.isna(text):
        return ''
    
    text = normalize_text(text)
    
    # Remove números de lote, quadra, etc
    text = re.sub(r'\b(lote|lt|quadra|qd|casa|cs)\s*\d+\b', '', text, flags=re.IGNORECASE)
    
    # Remove complementos comuns
    text = re.sub(r'\b(apto|ap|apartamento|casa|cs|bloco|bl)\s*[0-9a-z]+\b', '', text, flags=re.IGNORECASE)
    
    # Padroniza abreviações
    replacements = {
        r'\brua\b': 'R',
        r'\bavenida\b': 'Av',
        r'\btravessa\b': 'Tv',
        r'\bpraça\b': 'Pç',
        r'\bsão\b': 'São',
        r'\bsanta\b': 'Santa',
    }
    
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Remove espaços extras novamente
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def is_valid_coordinate(lat: float, lon: float) -> bool:
    """
    Valida se coordenadas estão dentro de valores possíveis
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        True se coordenadas são válidas
    """
    try:
        lat = float(lat)
        lon = float(lon)
        return -90 <= lat <= 90 and -180 <= lon <= 180
    except (ValueError, TypeError):
        return False


def format_file_size(size_bytes: int) -> str:
    """
    Formata tamanho de arquivo em formato legível
    
    Args:
        size_bytes: Tamanho em bytes
        
    Returns:
        String formatada (ex: "1.5 GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.2f} PB"


def sanitize_filename(filename: str) -> str:
    """
    Sanitiza nome de arquivo removendo caracteres inválidos
    
    Args:
        filename: Nome do arquivo
        
    Returns:
        Nome sanitizado
    """
    # Remove caracteres inválidos
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove espaços extras
    filename = re.sub(r'\s+', '_', filename)
    
    return filename


def build_address_query(
    street: str = "",
    neighborhood: str = "",
    city: str = "",
    state: str = ""
) -> str:
    """
    Constrói query de endereço para geocoding
    
    Args:
        street: Logradouro
        neighborhood: Bairro
        city: Município
        state: UF
        
    Returns:
        Query formatada
    """
    parts = []
    
    if street:
        parts.append(normalize_address(street))
    if neighborhood:
        parts.append(normalize_text(neighborhood))
    if city:
        parts.append(normalize_text(city))
    if state:
        parts.append(state.strip().upper())
    
    return ", ".join(filter(None, parts))


def get_address_hash(address: str) -> str:
    """
    Gera hash para cache de endereços
    
    Args:
        address: Endereço completo
        
    Returns:
        Hash do endereço
    """
    import hashlib
    
    # Normaliza antes de gerar hash
    normalized = normalize_address(address).lower()
    
    return hashlib.md5(normalized.encode()).hexdigest()

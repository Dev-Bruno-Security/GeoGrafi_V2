"""
Processador de CSV em chunks para dados de alta volume
"""
import pandas as pd
from typing import Iterator, Callable, Optional, Dict, List
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import io
import chardet
import csv
import re
import time
import requests

from .cep_validator import CEPValidator
from .geocoder import Geocoder
from .cache_manager import CacheManager

logger = logging.getLogger(__name__)
if not logger.handlers:
    logger.setLevel(logging.INFO)

class CSVProcessor:
    """Processa arquivos CSV em chunks com enriquecimento de dados geográficos"""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        max_workers: int = 3,
        use_cache: bool = True,
        cache_db: str = "cache.db",
        col_mapping: Optional[Dict[str, str]] = None,
        fetch_coordinates: bool = False
    ):
        """
        Inicializa o processador
        
        Args:
            chunk_size: Número de linhas por chunk
            max_workers: Número de workers para processamento paralelo
            use_cache: Usar cache local
            cache_db: Caminho do banco de cache
            col_mapping: Mapeamento de colunas alternativas -> nomes esperados
            fetch_coordinates: Se deve buscar coordenadas (lento, usa Nominatim)
        """
        self.chunk_size = chunk_size
        self.max_workers = max_workers
        self.fetch_coordinates = fetch_coordinates  # NOVO: controlar busca de coordenadas
        self.cep_validator = CEPValidator(rate_limit_delay=0.15)
        self.geocoder = Geocoder(rate_limit_delay=1.5) if fetch_coordinates else None
        self.cache_manager = CacheManager(cache_db) if use_cache else None
        self.col_mapping = col_mapping or {}
        self.detected_encoding = None
        self.detected_delimiter = None
        self.stop_processing = False  # ✅ Flag para parar processamento
        
        self.stats = {
            'total_rows': 0,
            'processed_rows': 0,
            'fixed_ceps': 0,
            'found_coordinates': 0,
            'errors': []
        }
    
    def stop(self):
        """Para o processamento gracefully"""
        self.stop_processing = True
        logger.info("⛔ Solicitação de parada recebida")
    
    def resume(self):
        """Retoma o processamento"""
        self.stop_processing = False
        logger.info("▶️ Processamento retomado")
    
    def is_stopped(self) -> bool:
        """Verifica se o processamento foi parado"""
        return self.stop_processing
    
    def _detect_encoding(self, file_path: str, sample_size: int = 100000) -> str:
        """Detecta o encoding do arquivo automaticamente"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(sample_size)
                result = chardet.detect(raw_data)
                detected = result.get('encoding')
                confidence = result.get('confidence', 0.0)
                
                # Se não detectar com confiança, usar latin-1 (preserva todos bytes)
                if not detected or confidence < 0.5:
                    logger.warning(f"Encoding não confiável ({detected}, conf.: {confidence:.2%}). Usando latin-1")
                    return 'latin-1'
                
                logger.info(f"Encoding detectado: {detected} (confiança: {confidence:.2%})")
                return detected
        except Exception as e:
            logger.warning(f"Erro ao detectar encoding: {e}. Usando latin-1")
            return 'latin-1'
    
    def _detect_delimiter(self, file_path: str, encoding: str) -> str:
        """Detecta o delimitador do CSV automaticamente"""
        import csv
        try:
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                sample = f.read(8192)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                logger.info(f"Delimitador detectado: '{delimiter}'")
                return delimiter
        except Exception as e:
            logger.warning(f"Erro ao detectar delimitador: {e}. Usando vírgula")
            return ','
    
    def _validate_cep_quick(self, cep: str) -> bool:
        """
        Valida CEP de forma rápida (apenas formato, sem chamada de API)
        
        Returns:
            True se CEP tem formato válido (8 dígitos)
        """
        import re
        if not cep:
            return False
        
        # Remove caracteres não-numéricos
        cep_limpo = re.sub(r'\D', '', str(cep))
        
        # Verifica se tem 8 dígitos e não é sequência inválida
        if len(cep_limpo) != 8:
            return False
        
        # CEPs inválidos óbvios
        if cep_limpo in ['00000000', '11111111', '22222222', '33333333', 
                         '44444444', '55555555', '66666666', '77777777',
                         '88888888', '99999999']:
            return False
        
        return True
    
    def _normalize_address(self, text: str) -> str:
        """Normaliza e padroniza endereços"""
        if not text or pd.isna(text):
            return ''
        
        import re
        
        # Converte para string e remove espaços extras
        text = str(text).strip()
        text = re.sub(r'\s+', ' ', text)
        
        # Remove caracteres especiais no início/fim
        text = re.sub(r'^[^\w\s]+|[^\w\s]+$', '', text)
        
        # Padroniza abreviações comuns de logradouro
        abbreviations = {
            r'\bR\b\.?': 'Rua',
            r'\bRUA\b': 'Rua',
            r'\bAV\b\.?': 'Avenida',
            r'\bAVENIDA\b': 'Avenida',
            r'\bAVDA\b\.?': 'Avenida',
            r'\bALM\b\.?': 'Alameda',
            r'\bALAMEDA\b': 'Alameda',
            r'\bTRAV\b\.?': 'Travessa',
            r'\bTRAVESSA\b': 'Travessa',
            r'\bPÇ\b\.?': 'Praça',
            r'\bPC\b\.?': 'Praça',
            r'\bPRACA\b': 'Praça',
            r'\bPRAÇA\b': 'Praça',
            r'\bROD\b\.?': 'Rodovia',
            r'\bRODOVIA\b': 'Rodovia',
            r'\bEST\b\.?': 'Estrada',
            r'\bESTRADA\b': 'Estrada',
            r'\bLARGO\b': 'Largo',
            r'\bLGO\b\.?': 'Largo',
            r'\bVIA\b': 'Via',
            r'\bBECO\b': 'Beco',
            r'\bVILA\b': 'Vila',
            r'\bPARQUE\b': 'Parque',
            r'\bJARDIM\b': 'Jardim',
            r'\bCONJ\b\.?': 'Conjunto',
            r'\bCONJUNTO\b': 'Conjunto',
        }
        
        for pattern, replacement in abbreviations.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Capitaliza corretamente (Title Case), mas mantém algumas palavras em minúsculo
        words = text.split()
        lowercase_words = {'de', 'da', 'do', 'das', 'dos', 'e', 'a', 'o'}
        
        formatted_words = []
        for i, word in enumerate(words):
            # Primeira palavra sempre em maiúscula
            if i == 0 or word.lower() not in lowercase_words:
                formatted_words.append(word.capitalize())
            else:
                formatted_words.append(word.lower())
        
        text = ' '.join(formatted_words)
        
        return text.strip()
    
    def process_file(self, file_path: str, progress_callback: Optional[Callable[[float], None]] = None) -> pd.DataFrame:
        """
        Processa arquivo CSV RAPIDAMENTE.
        
        Se fetch_coordinates=False (padrão): Apenas valida CEPs (~0.1s por item)
        Se fetch_coordinates=True: Também busca coordenadas (LENTO: ~2-3s por item)
        
        Args:
            file_path: Caminho do arquivo CSV
            progress_callback: Função opcional para reportar progresso (0-100)
        
        Returns:
            DataFrame com coluna 'cep_valido' adicionada
        """
        import time
        
        logger.info(f"Iniciando processamento: {file_path}")
        start = time.time()
        
        # Detecção automática de encoding/delimiter
        if not self.detected_encoding:
            self.detected_encoding = self._detect_encoding(file_path)
        if not self.detected_delimiter:
            self.detected_delimiter = self._detect_delimiter(file_path, self.detected_encoding)
        
        logger.info(f"Encoding: {self.detected_encoding}, Delimitador: '{self.detected_delimiter}'")
        
        # Lê arquivo completo de uma vez (para manter simples)
        try:
            df = pd.read_csv(
                file_path,
                encoding=self.detected_encoding,
                encoding_errors='replace',
                delimiter=self.detected_delimiter,
                quotechar='"',
                skipinitialspace=True,
                on_bad_lines='warn',
                dtype=str  # 🔑 IMPORTANTE: Lê tudo como string para preservar zeros à esquerda
            )
        except Exception as e:
            logger.error(f"Erro ao ler CSV: {e}")
            raise
        
        logger.info(f"Arquivo carregado: {len(df)} linhas")
        logger.info(f"Colunas detectadas: {list(df.columns)}")
        
        # Identifica coluna de CEP
        cep_col = self._find_cep_column(df)
        if not cep_col:
            colunas_disponiveis = ", ".join([f"'{col}'" for col in df.columns])
            raise ValueError(
                f"❌ Coluna de CEP não encontrada!\n\n"
                f"Colunas disponíveis no arquivo: {colunas_disponiveis}\n\n"
                f"Dica: Renomeie uma coluna para 'cep' ou 'CEP' no seu arquivo CSV."
            )
        
        logger.info(f"Coluna de CEP encontrada: '{cep_col}'")
        
        # FASE 1: Validação e Correção de CEPs
        logger.info("Validando e corrigindo CEPs...")
        phase1_start = time.time()
        
        # Adiciona colunas para resultados
        df['cep_original'] = df[cep_col].astype(str)
        df['cep_valido'] = False
        df['cep_corrigido'] = None
        df['logradouro'] = None
        df['bairro'] = None
        df['cidade'] = None
        df['uf'] = None
        
        # Processa cada linha
        total_rows = len(df)
        for idx, row in df.iterrows():
            # Verifica se foi solicitado parar
            if self.stop_processing:
                logger.warning(f"⛔ Processamento interrompido na linha {idx + 1}/{total_rows}")
                break
            
            cep_original = str(row[cep_col]).strip()
            
            # Tenta buscar informações do CEP via ViaCEP
            cep_info = self.cep_validator.search_cep(cep_original)
            
            if cep_info and not cep_info.get('erro'):
                # CEP válido encontrado
                df.at[idx, 'cep_valido'] = True
                df.at[idx, 'cep_corrigido'] = cep_info.get('cep', cep_original)
                df.at[idx, 'logradouro'] = cep_info.get('logradouro', '')
                df.at[idx, 'bairro'] = cep_info.get('bairro', '')
                df.at[idx, 'cidade'] = cep_info.get('localidade', '')
                df.at[idx, 'uf'] = cep_info.get('uf', '')

                # Usa o CEP corrigido para preencher colunas originais vazias
                self._backfill_row_from_cep(df, idx, cep_info)

                # Se ViaCEP não trouxe logradouro/bairro, tenta usar o endereço original padronizado
                self._backfill_from_original(df, idx)
            else:
                # CEP inválido - NOVA: Tenta buscar CEP pelo endereço
                df.at[idx, 'cep_valido'] = False
                df.at[idx, 'cep_corrigido'] = cep_original
                
                # Tenta buscar CEP usando endereço disponível
                cep_by_address = self._search_cep_by_address(df, idx)
                if cep_by_address:
                    logger.info(f"CEP encontrado pelo endereço: {cep_by_address}")
                    df.at[idx, 'cep_corrigido'] = cep_by_address
                    # Busca novamente os dados do ViaCEP com o CEP encontrado
                    cep_info = self.cep_validator.search_cep(cep_by_address)
                    if cep_info and not cep_info.get('erro'):
                        df.at[idx, 'cep_valido'] = True
                        df.at[idx, 'logradouro'] = cep_info.get('logradouro', '')
                        df.at[idx, 'bairro'] = cep_info.get('bairro', '')
                        df.at[idx, 'cidade'] = cep_info.get('localidade', '')
                        df.at[idx, 'uf'] = cep_info.get('uf', '')
                        self._backfill_row_from_cep(df, idx, cep_info)
            
            # Reporta progresso (FASE 1: 0-70%)
            if progress_callback and (idx + 1) % 10 == 0:
                progress = ((idx + 1) / total_rows) * 70.0
                progress_callback(progress)

        # Preenche campos vazios de endereço a partir das informações corrigidas do CEP
        df = self._fill_missing_address_fields(df)
        
        # Reporta progresso após preenchimento (70%)
        if progress_callback:
            progress_callback(70.0)
        
        valid_count = (df['cep_valido'] == True).sum()
        logger.info(f"✓ {valid_count}/{len(df)} CEPs válidos em {time.time()-phase1_start:.1f}s")
        
        # FASE 2: Busca de coordenadas (OPCIONAL - MUITO LENTA)
        if self.fetch_coordinates and self.geocoder:
            logger.info("Buscando coordenadas (LENTO - pode levar minutos)...")
            phase2_start = time.time()
            
            # Colunas de destino
            df['DS_LATITUDE_CORRETA'] = None
            df['DS_LONGITUDE_CORRETA'] = None
            # Mantém também latitude/longitude se já existirem
            if 'DS_LATITUDE' not in df.columns:
                df['DS_LATITUDE'] = None
            if 'DS_LONGITUDE' not in df.columns:
                df['DS_LONGITUDE'] = None
            
            for idx, row in df.iterrows():
                # Verifica se foi solicitado parar
                if self.stop_processing:
                    logger.warning(f"⛔ Busca de coordenadas interrompida na linha {idx + 1}/{len(df)}")
                    break
                
                coords = None
                if row.get('cep_valido'):
                    # Tenta com CEP corrigido e endereço corrigido
                    coords = self._get_coordinates_with_fallback(row)
                else:
                    # Se CEP não é válido, tenta usar endereço original/corrigido
                    coords = self._get_coordinates_by_address(row)
                
                if coords:
                    lat, lon = coords[0], coords[1]
                    df.at[idx, 'DS_LATITUDE_CORRETA'] = lat
                    df.at[idx, 'DS_LONGITUDE_CORRETA'] = lon
                    # Preenche colunas principais se estiverem vazias
                    if pd.isna(df.at[idx, 'DS_LATITUDE']) or str(df.at[idx, 'DS_LATITUDE']).strip() == '':
                        df.at[idx, 'DS_LATITUDE'] = lat
                    if pd.isna(df.at[idx, 'DS_LONGITUDE']) or str(df.at[idx, 'DS_LONGITUDE']).strip() == '':
                        df.at[idx, 'DS_LONGITUDE'] = lon
                    self.stats['found_coordinates'] += 1
                
                # Reporta progresso (FASE 2: 70-100%)
                if progress_callback and (idx + 1) % 5 == 0:
                    progress = 70.0 + ((idx + 1) / total_rows) * 30.0
                    progress_callback(progress)
            
            logger.info(f"✓ Coordenadas buscadas em {time.time()-phase2_start:.1f}s")
        
        total = time.time() - start
        logger.info(f"✓ Processamento concluído em {total:.1f}s")
        
        # Reporta conclusão (100%)
        if progress_callback:
            progress_callback(100.0)
        
        return df

    def _fill_missing_address_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preenche campos de endereço vazios usando dados do ViaCEP.

        - Usa apenas linhas com `cep_valido == True`
        - Mantém valores existentes; só preenche quando está vazio ou NaN
        """

        # Se não houver flag de CEP válido ou dados básicos, sai cedo
        if 'cep_valido' not in df.columns:
            return df

        has_base_fields = all(col in df.columns for col in ['logradouro', 'bairro', 'cidade', 'uf'])
        if not has_base_fields:
            return df

        # Conjuntos de colunas equivalentes (case-insensitive)
        street_cols = {
            'logradouro', 'endereco', 'rua', 'ds_endereco', 'ds_logradouro',
            'nm_logradouro', 'nm_logradouro_atual', 'nm_logradouro_cor',
            'nm_endereco', 'nm_endereco_atual'
        }
        bairro_cols = {
            'bairro', 'ds_bairro', 'nm_bairro', 'nm_bairro_atual'
        }
        city_cols = {
            'cidade', 'municipio', 'nm_cidade', 'nm_municipio', 'ds_municipio'
        }
        uf_cols = {
            'uf', 'estado', 'sigla_uf', 'nm_uf', 'ds_uf'
        }

        def is_empty(value: object) -> bool:
            """Retorna True se valor for NaN ou string vazia."""
            if value is None or (isinstance(value, float) and pd.isna(value)):
                return True
            if isinstance(value, str):
                return value.strip() == ''
            return False

        # Máscara para linhas válidas
        mask_valid = df['cep_valido'] == True

        for col in df.columns:
            key = col.lower()
            if key in street_cols:
                source_series = df['logradouro']
            elif key in bairro_cols:
                source_series = df['bairro']
            elif key in city_cols:
                source_series = df['cidade']
            elif key in uf_cols:
                source_series = df['uf']
            else:
                continue

            # Define máscara de valores vazios na coluna alvo
            target_series = df[col]
            mask_empty = target_series.apply(is_empty)

            # Só preenche onde: linha é válida e célula está vazia
            fill_mask = mask_valid & mask_empty & source_series.notna() & (source_series.astype(str).str.strip() != '')
            df.loc[fill_mask, col] = source_series[fill_mask]

        return df

    def _backfill_row_from_cep(self, df: pd.DataFrame, idx: int, cep_info: Dict[str, str]) -> None:
        """Preenche colunas de endereço existentes que estejam vazias usando dados do CEP.

        Isso garante que, ao corrigir um CEP, as colunas originais do usuário
        (ex.: `NM_LOGRADOURO`, `NM_BAIRRO`, `NM_MUNICIPIO`, `NM_UF`) também sejam
        preenchidas caso estejam em branco.
        """

        if cep_info is None:
            return

        # Valores vindos do ViaCEP
        street = cep_info.get('logradouro', '') or ''
        bairro = cep_info.get('bairro', '') or ''
        city = cep_info.get('localidade', '') or ''
        uf = cep_info.get('uf', '') or ''

        # Mapeamentos canônicos para escrita (case-insensitive)
        street_targets = {
            'NM_LOGRADOURO', 'NM_LOGRADOURO_ATUAL', 'NM_LOGRADOURO_COR',
            'NM_ENDERECO', 'NM_ENDERECO_ATUAL', 'DS_LOGRADOURO', 'DS_ENDERECO',
            'logradouro', 'endereco', 'rua'
        }
        bairro_targets = {
            'NM_BAIRRO', 'NM_BAIRRO_ATUAL', 'DS_BAIRRO', 'bairro'
        }
        city_targets = {
            'NM_MUNICIPIO', 'NM_MUNICIPIO_ATUAL', 'DS_MUNICIPIO', 'NM_CIDADE',
            'cidade', 'municipio'
        }
        uf_targets = {
            'NM_UF', 'NM_UF_ATUAL', 'DS_UF', 'UF', 'estado', 'sigla_uf'
        }

        def maybe_fill(column_set, value):
            if not value:
                return
            for col in df.columns:
                if col.lower() in {c.lower() for c in column_set}:
                    current = df.at[idx, col]
                    if pd.isna(current) or str(current).strip() == '':
                        df.at[idx, col] = value

        maybe_fill(street_targets, street)
        maybe_fill(bairro_targets, bairro)
        maybe_fill(city_targets, city)
        maybe_fill(uf_targets, uf)

    def _backfill_from_original(self, df: pd.DataFrame, idx: int) -> None:
        """Padroniza e usa endereço original para preencher lacunas quando o CEP corrigido não traz dados.

        - Normaliza logradouro com a função interna de normalização.
        - Normaliza bairro/cidade/UF com title-case simples.
        """

        def first_non_empty(column_set):
            target_lower = {c.lower() for c in column_set}
            for col in df.columns:
                if col.lower() in target_lower:
                    val = df.at[idx, col]
                    if not pd.isna(val):
                        val_str = str(val).strip()
                        if val_str:
                            return val_str
            return ''

        def norm_simple(text: str) -> str:
            text = str(text).strip()
            if not text:
                return ''
            return ' '.join(word.capitalize() for word in text.split())

        street_targets = {
            'NM_LOGRADOURO', 'NM_LOGRADOURO_ATUAL', 'NM_LOGRADOURO_COR',
            'NM_ENDERECO', 'NM_ENDERECO_ATUAL', 'DS_LOGRADOURO', 'DS_ENDERECO',
            'logradouro', 'endereco', 'rua'
        }
        bairro_targets = {
            'NM_BAIRRO', 'NM_BAIRRO_ATUAL', 'DS_BAIRRO', 'bairro'
        }
        city_targets = {
            'NM_MUNICIPIO', 'NM_MUNICIPIO_ATUAL', 'DS_MUNICIPIO', 'NM_CIDADE',
            'cidade', 'municipio'
        }
        uf_targets = {
            'NM_UF', 'NM_UF_ATUAL', 'DS_UF', 'UF', 'estado', 'sigla_uf'
        }

        # Só age se estiver vazio o núcleo (logradouro/bairro) preenchido pelo CEP
        street_candidate = first_non_empty(street_targets)
        bairro_candidate = first_non_empty(bairro_targets)
        city_candidate = first_non_empty(city_targets)
        uf_candidate = first_non_empty(uf_targets)

        if (not df.at[idx, 'logradouro']) and street_candidate:
            df.at[idx, 'logradouro'] = self._normalize_address(street_candidate)
        if (not df.at[idx, 'bairro']) and bairro_candidate:
            df.at[idx, 'bairro'] = norm_simple(bairro_candidate)
        if (not df.at[idx, 'cidade']) and city_candidate:
            df.at[idx, 'cidade'] = norm_simple(city_candidate)
        if (not df.at[idx, 'uf']) and uf_candidate:
            df.at[idx, 'uf'] = uf_candidate.strip().upper()
    
    def _find_cep_column(self, df: pd.DataFrame) -> Optional[str]:
        """Encontra a coluna de CEP no DataFrame"""
        logger.debug(f"Colunas disponíveis: {list(df.columns)}")
        
        # Lista expandida de nomes possíveis
        common_names = [
            'cep', 'CEP', 'Cep',
            'cd_cep', 'CD_CEP', 'Cd_Cep', 'cd_CEP',
            'codigo_cep', 'CODIGO_CEP', 'Codigo_Cep', 'codigo_CEP',
            'codigo', 'CODIGO', 'Codigo',
            'postal_code', 'POSTAL_CODE', 'Postal_Code',
            'zipcode', 'ZIPCODE', 'ZipCode', 'Zipcode',
            'zip', 'ZIP', 'Zip',
            'codigo postal', 'CODIGO POSTAL', 'Codigo Postal'
        ]
        
        # Busca exata
        for col in df.columns:
            if col in common_names:
                logger.debug(f"Coluna encontrada (match exato): '{col}'")
                return col
        
        # Busca case-insensitive
        df_lower = {col.lower(): col for col in df.columns}
        for name in common_names:
            if name.lower() in df_lower:
                found_col = df_lower[name.lower()]
                logger.debug(f"Coluna encontrada (case-insensitive): '{found_col}'")
                return found_col
        
        # Busca parcial (contém 'cep')
        for col in df.columns:
            col_lower = col.lower()
            if 'cep' in col_lower or 'postal' in col_lower or 'zip' in col_lower:
                logger.debug(f"Coluna encontrada (busca parcial): '{col}'")
                return col
        
        logger.warning(f"Coluna de CEP não encontrada. Colunas disponíveis: {list(df.columns)}")
        return None
    
    def _read_csv_chunks(self, file_path: str) -> Iterator[pd.DataFrame]:
        """Lê arquivo CSV em chunks"""
        # Detecta encoding automaticamente
        if not self.detected_encoding:
            self.detected_encoding = self._detect_encoding(file_path)
        
        # Detecta delimitador automaticamente
        if not self.detected_delimiter:
            self.detected_delimiter = self._detect_delimiter(file_path, self.detected_encoding)
        
        logger.info(f"Lendo arquivo com encoding: {self.detected_encoding}, delimitador: '{self.detected_delimiter}'")
        
        try:
            # Primeiro, obtém o número total de linhas
            with open(file_path, 'r', encoding=self.detected_encoding, errors='replace') as f:
                self.stats['total_rows'] = sum(1 for _ in f) - 1  # -1 para header
            
            # Lê chunks
            for chunk in pd.read_csv(
                file_path,
                chunksize=self.chunk_size,
                encoding=self.detected_encoding,
                encoding_errors='replace',
                on_bad_lines='warn',
                delimiter=self.detected_delimiter,
                quotechar='"',
                skipinitialspace=True
            ):
                yield chunk
        
        except Exception as e:
            logger.error(f"Erro ao ler arquivo: {e}")
            # Tenta com latin-1 como último recurso
            logger.warning("Tentando com latin-1...")
            self.detected_encoding = 'latin-1'
            
            with open(file_path, 'r', encoding='latin-1') as f:
                self.stats['total_rows'] = sum(1 for _ in f) - 1
            
            for chunk in pd.read_csv(
                file_path,
                chunksize=self.chunk_size,
                encoding='latin-1',
                on_bad_lines='warn',
                delimiter=self.detected_delimiter,
                quotechar='"',
                skipinitialspace=True
            ):
                yield chunk
    
    def _process_chunk(self, chunk: pd.DataFrame) -> pd.DataFrame:
        """Processa um chunk do CSV"""
        chunk = chunk.copy()
        
        # Aplicar mapeamento de colunas se existir
        if self.col_mapping:
            # Inverter o mapeamento: self.col_mapping tem {nome_esperado: nome_real}
            chunk = chunk.rename(columns={v: k for k, v in self.col_mapping.items() if v in chunk.columns})
        
        # Adiciona coluna para CEP corrigido se não existir
        if 'CD_CEP_CORRETO' not in chunk.columns:
            chunk['CD_CEP_CORRETO'] = None
        if 'NM_LOGRADOURO_CORRETO' not in chunk.columns:
            chunk['NM_LOGRADOURO_CORRETO'] = None
        if 'NM_BAIRRO_CORRETO' not in chunk.columns:
            chunk['NM_BAIRRO_CORRETO'] = None
        if 'NM_MUNICIPIO_CORRETO' not in chunk.columns:
            chunk['NM_MUNICIPIO_CORRETO'] = None
        if 'NM_UF_CORRETO' not in chunk.columns:
            chunk['NM_UF_CORRETO'] = None
        if 'DS_LATITUDE' not in chunk.columns:
            chunk['DS_LATITUDE'] = None
        if 'DS_LONGITUDE' not in chunk.columns:
            chunk['DS_LONGITUDE'] = None
        
        # Processa cada linha
        for idx, row in chunk.iterrows():
            try:
                cep = str(row.get('CD_CEP', '')).strip()
                
                # Criterio 1: Validar CEP existente
                if cep and self.cep_validator.validate_cep_format(cep):
                    cep_data = self.cep_validator.search_cep(cep)
                    
                    if cep_data:
                        # CEP válido - marca como correto
                        chunk.at[idx, 'CD_CEP_CORRETO'] = cep
                        
                        # Preenche dados do endereço correto
                        chunk.at[idx, 'NM_LOGRADOURO_CORRETO'] = cep_data.get('logradouro', '')
                        chunk.at[idx, 'NM_BAIRRO_CORRETO'] = cep_data.get('bairro', '')
                        chunk.at[idx, 'NM_MUNICIPIO_CORRETO'] = cep_data.get('localidade', '')
                        chunk.at[idx, 'NM_UF_CORRETO'] = cep_data.get('uf', '')
                        
                        # Busca coordenadas
                        if pd.isna(row.get('DS_LATITUDE')) or pd.isna(row.get('DS_LONGITUDE')):
                            coords = self._get_coordinates_from_cep(cep_data)
                            if coords:
                                chunk.at[idx, 'DS_LATITUDE'] = coords[0]
                                chunk.at[idx, 'DS_LONGITUDE'] = coords[1]
                                self.stats['found_coordinates'] += 1
                    else:
                        # CEP inválido - Criterio 2: Buscar CEP por endereço
                        cep_corrigido = self._search_cep_by_address(row)
                        if cep_corrigido:
                            chunk.at[idx, 'CD_CEP_CORRETO'] = cep_corrigido
                            self.stats['fixed_ceps'] += 1
                            
                            # Busca dados do CEP corrigido
                            cep_data = self.cep_validator.search_cep(cep_corrigido)
                            if cep_data:
                                # Preenche dados do endereço correto
                                chunk.at[idx, 'NM_LOGRADOURO_CORRETO'] = cep_data.get('logradouro', '')
                                chunk.at[idx, 'NM_BAIRRO_CORRETO'] = cep_data.get('bairro', '')
                                chunk.at[idx, 'NM_MUNICIPIO_CORRETO'] = cep_data.get('localidade', '')
                                chunk.at[idx, 'NM_UF_CORRETO'] = cep_data.get('uf', '')
                                
                                # Busca coordenadas pelo CEP corrigido
                                coords = self._get_coordinates_from_cep(cep_data)
                                if coords:
                                    chunk.at[idx, 'DS_LATITUDE'] = coords[0]
                                    chunk.at[idx, 'DS_LONGITUDE'] = coords[1]
                                    self.stats['found_coordinates'] += 1
                
                # Se ainda não tem coordenadas, tenta por endereço
                if pd.isna(chunk.at[idx, 'DS_LATITUDE']) or pd.isna(chunk.at[idx, 'DS_LONGITUDE']):
                    coords = self._get_coordinates_by_address(row)
                    if coords:
                        chunk.at[idx, 'DS_LATITUDE'] = coords[0]
                        chunk.at[idx, 'DS_LONGITUDE'] = coords[1]
                        self.stats['found_coordinates'] += 1
                
                # Replica dados originais para colunas corretas se estiverem vazias
                if pd.isna(chunk.at[idx, 'NM_LOGRADOURO_CORRETO']) or chunk.at[idx, 'NM_LOGRADOURO_CORRETO'] == '':
                    logradouro_original = row.get('NM_LOGRADOURO', '')
                    if logradouro_original and str(logradouro_original).strip():
                        chunk.at[idx, 'NM_LOGRADOURO_CORRETO'] = str(logradouro_original).strip()
                
                if pd.isna(chunk.at[idx, 'NM_BAIRRO_CORRETO']) or chunk.at[idx, 'NM_BAIRRO_CORRETO'] == '':
                    bairro_original = row.get('NM_BAIRRO', '')
                    if bairro_original and str(bairro_original).strip():
                        chunk.at[idx, 'NM_BAIRRO_CORRETO'] = str(bairro_original).strip()
                
                if pd.isna(chunk.at[idx, 'NM_MUNICIPIO_CORRETO']) or chunk.at[idx, 'NM_MUNICIPIO_CORRETO'] == '':
                    municipio_original = row.get('NM_MUNICIPIO', '')
                    if municipio_original and str(municipio_original).strip():
                        chunk.at[idx, 'NM_MUNICIPIO_CORRETO'] = str(municipio_original).strip()
                
                if pd.isna(chunk.at[idx, 'NM_UF_CORRETO']) or chunk.at[idx, 'NM_UF_CORRETO'] == '':
                    uf_original = row.get('NM_UF', '')
                    if uf_original and str(uf_original).strip():
                        chunk.at[idx, 'NM_UF_CORRETO'] = str(uf_original).strip()
                
                # Padroniza formato dos endereços corretos
                if chunk.at[idx, 'NM_LOGRADOURO_CORRETO']:
                    chunk.at[idx, 'NM_LOGRADOURO_CORRETO'] = self._normalize_address(chunk.at[idx, 'NM_LOGRADOURO_CORRETO'])
                
                if chunk.at[idx, 'NM_BAIRRO_CORRETO']:
                    chunk.at[idx, 'NM_BAIRRO_CORRETO'] = self._normalize_address(chunk.at[idx, 'NM_BAIRRO_CORRETO'])
                
                # Se ainda não tem coordenadas, tenta buscar usando dados corretos
                if pd.isna(chunk.at[idx, 'DS_LATITUDE']) or pd.isna(chunk.at[idx, 'DS_LONGITUDE']):
                    coords = self._get_coordinates_with_fallback(chunk.loc[idx])
                    if coords:
                        chunk.at[idx, 'DS_LATITUDE'] = coords[0]
                        chunk.at[idx, 'DS_LONGITUDE'] = coords[1]
                        self.stats['found_coordinates'] += 1
            
            except Exception as e:
                logger.error(f"Erro ao processar linha {idx}: {str(e)}")
                self.stats['errors'].append({
                    'row': idx,
                    'error': str(e)
                })
        
        return chunk
    
    def _search_cep_by_address(self, df: pd.DataFrame, idx: int) -> Optional[str]:
        """
        Busca CEP correto usando endereço através da API ViaCEP
        
        Procura por: DS_ENDERECO (ou NM_LOGRADOURO), DS_BAIRRO, NM_CIDADE (ou NM_MUNICIPIO), NM_UF
        """
        row = df.iloc[idx]
        
        # Tenta encontrar o endereço nos campos disponíveis
        street = (str(row.get('DS_ENDERECO', '') or row.get('NM_LOGRADOURO', '')).strip())
        neighborhood = (str(row.get('DS_BAIRRO', '') or row.get('NM_BAIRRO', '')).strip())
        city = (str(row.get('NM_CIDADE', '') or row.get('NM_MUNICIPIO', '')).strip())
        state = (str(row.get('NM_UF', '')).strip())
        
        if not street or not city or not state:
            logger.debug(f"Linha {idx}: Endereço incompleto para busca de CEP")
            return None
        
        try:
            # Usa API ViaCEP para buscar endereços (formato: UF/cidade/logradouro)
            from urllib.parse import quote
            import requests
            
            state_encoded = quote(state)
            city_encoded = quote(city)
            street_encoded = quote(street)
            
            url = f"https://viacep.com.br/ws/{state_encoded}/{city_encoded}/{street_encoded}/json/"
            
            logger.debug(f"Buscando CEP: {url}")
            self.cep_validator._apply_rate_limit()
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # ViaCEP retorna array de resultados
                if isinstance(data, list) and len(data) > 0:
                    # Filtra por bairro se disponível (maior precisão)
                    if neighborhood:
                        for item in data:
                            if neighborhood.lower() in item.get('bairro', '').lower():
                                cep = item.get('cep', '').replace('-', '')
                                logger.info(f"CEP encontrado (por bairro): {cep} para {street}, {neighborhood}, {city}/{state}")
                                return cep
                    
                    # Se não encontrar por bairro, usa o primeiro resultado
                    cep = data[0].get('cep', '').replace('-', '')
                    logger.info(f"CEP encontrado (primeiro resultado): {cep} para {street}, {city}/{state}")
                    return cep
                else:
                    logger.debug(f"Nenhum CEP encontrado para: {street}, {city}/{state}")
            else:
                logger.warning(f"Erro ao buscar CEP: status {response.status_code}")
        
        except Exception as e:
            logger.warning(f"Erro ao buscar CEP por endereço (linha {idx}): {str(e)}")
        
        return None
    
    def _get_coordinates_from_cep(self, cep_data: Dict) -> Optional[tuple]:
        """Extrai coordenadas de dados do ViaCEP"""
        try:
            # ViaCEP não retorna coordenadas diretas
            # Precisamos buscar via geocoding do endereço
            street = cep_data.get('logradouro', '')
            neighborhood = cep_data.get('bairro', '')
            city = cep_data.get('localidade', '')
            state = cep_data.get('uf', '')
            
            return self.geocoder.search_by_address(street, "", neighborhood, city, state)
        
        except Exception as e:
            logger.warning(f"Erro ao extrair coordenadas: {str(e)}")
            return None
    
    def _get_coordinates_by_address(self, row: pd.Series) -> Optional[tuple]:
        """Busca coordenadas usando endereço completo"""
        try:
            # Tenta usar dados do ViaCEP primeiro, depois dados originais
            street = str(row.get('logradouro', '') or row.get('NM_LOGRADOURO', '')).strip()
            neighborhood = str(row.get('bairro', '') or row.get('NM_BAIRRO', '')).strip()
            city = str(row.get('cidade', '') or row.get('NM_MUNICIPIO', '')).strip()
            state = str(row.get('uf', '') or row.get('NM_UF', '')).strip()
            
            if not street or not city:
                return None
            
            return self.geocoder.search_by_address(street, "", neighborhood, city, state)
        
        except Exception as e:
            logger.warning(f"Erro ao buscar coordenadas por endereço: {str(e)}")
            return None
    
    def _get_coordinates_with_fallback(self, row: pd.Series) -> Optional[tuple]:
        """
        Busca coordenadas usando múltiplas estratégias de fallback
        Prioriza dados corretos do ViaCEP e tenta combinações mais específicas primeiro
        """
        try:
            # Dados do ViaCEP (já validados)
            cep_corrigido = row.get('cep_corrigido', '')
            logradouro = str(row.get('logradouro', '') or row.get('NM_LOGRADOURO', '')).strip()
            bairro = str(row.get('bairro', '') or row.get('NM_BAIRRO', '')).strip()
            municipio = str(row.get('cidade', '') or row.get('NM_MUNICIPIO', '')).strip()
            uf = str(row.get('uf', '') or row.get('NM_UF', '')).strip()
            
            # Estratégia 1: CEP corrigido + cidade
            if cep_corrigido and municipio:
                logger.debug(f"Tentando: CEP {cep_corrigido} + {municipio}")
                coords = self.geocoder.search_by_cep(cep_corrigido, municipio, "BR")
                if coords:
                    logger.debug(f"✓ Encontrado por CEP + cidade")
                    return coords
            
            # Estratégia 2: Endereço completo (logradouro + bairro + cidade + UF)
            if logradouro and municipio:
                logger.debug(f"Tentando: {logradouro}, {bairro}, {municipio}/{uf}")
                coords = self.geocoder.search_by_address(logradouro, "", bairro, municipio, uf)
                if coords:
                    logger.debug(f"✓ Encontrado por endereço completo")
                    return coords
            
            # Estratégia 3: Logradouro + cidade + UF (sem bairro)
            if logradouro and municipio and uf:
                logger.debug(f"Tentando: {logradouro}, {municipio}/{uf}")
                coords = self.geocoder.search_by_address(logradouro, "", "", municipio, uf)
                if coords:
                    logger.debug(f"✓ Encontrado por logradouro + cidade")
                    return coords
            
            # Estratégia 4: Apenas bairro + cidade + UF
            if bairro and municipio and uf:
                logger.debug(f"Tentando: {bairro}, {municipio}/{uf}")
                coords = self.geocoder.search_by_address("", "", bairro, municipio, uf)
                if coords:
                    logger.debug(f"✓ Encontrado por bairro + cidade")
                    return coords
            
            # Estratégia 5: Apenas cidade + UF (coordenadas do centro da cidade)
            if municipio and uf:
                logger.debug(f"Tentando: {municipio}/{uf}")
                coords = self.geocoder.search_by_address("", "", "", municipio, uf)
                if coords:
                    logger.debug(f"✓ Encontrado centro da cidade")
                    return coords
            
            logger.debug(f"Nenhuma coordenada encontrada para: {municipio}")
            return None
        
        except Exception as e:
            logger.warning(f"Erro ao buscar coordenadas com fallback: {str(e)}")
            return None

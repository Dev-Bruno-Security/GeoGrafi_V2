"""
Módulo para leitura eficiente de arquivos CSV grandes
Suporta arquivos OpenOffice.org 1.1 (.csv) sem perda de dados
"""

import pandas as pd
import csv
import os
from typing import Iterator, Optional, List, Dict, Any, Callable
from pathlib import Path
import chardet
import importlib.util


class CSVReader:
    """Classe para leitura eficiente de arquivos CSV grandes"""
    
    def __init__(
        self, 
        file_path: str, 
        encoding: Optional[str] = None, 
        delimiter: Optional[str] = None,
        prefer_fast_engine: bool = True
    ):
        """
        Inicializa o leitor de CSV
        
        Args:
            file_path: Caminho para o arquivo CSV
            encoding: Encoding do arquivo (auto-detectado se None)
            delimiter: Delimitador do arquivo (auto-detectado se None)
            prefer_fast_engine: Se True, tenta usar pyarrow quando disponível
        """
        self.file_path = Path(file_path)
        self.encoding = encoding
        self.delimiter = delimiter
        self.total_rows = 0
        self.has_header = True
        self.prefer_fast_engine = prefer_fast_engine
        self.engine_preferred = 'python'
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        # Detecta encoding automaticamente (se não informado)
        if not self.encoding:
            self._detect_encoding()
        # Detecta delimitador (se não informado) e se há cabeçalho
        if not self.delimiter:
            self._detect_delimiter_and_header()
        # Detecta engine preferida
        self._detect_engine()
    
    def _detect_encoding(self, sample_size: int = 100000) -> None:
        """Detecta o encoding do arquivo automaticamente"""
        print("Detectando encoding do arquivo...")
        
        with open(self.file_path, 'rb') as f:
            raw_data = f.read(sample_size)
            result = chardet.detect(raw_data)
            detected = result.get('encoding')
            confidence = result.get('confidence') or 0.0
            # Se não detectar com confiança razoável, usar latin-1 (preserva todos bytes)
            if not detected or confidence < 0.5:
                self.encoding = 'latin-1'
                print(f"Encoding não confiável ({detected}, conf.: {confidence:.2%}). Usando fallback: latin-1")
            else:
                self.encoding = detected
            
        print(f"Encoding detectado: {self.encoding} (confiança: {result.get('confidence', 0.0):.2%})")
    
    def _detect_delimiter_and_header(self) -> None:
        """Detecta o delimitador e se há cabeçalho no CSV"""
        print("Detectando delimitador e cabeçalho...")
        try:
            with open(self.file_path, 'r', encoding=self.encoding, newline='') as f:
                sample = f.read(8192)
                sniffer = csv.Sniffer()
                try:
                    self.delimiter = sniffer.sniff(sample).delimiter
                except csv.Error:
                    self.delimiter = ','  # fallback padrão
                try:
                    self.has_header = sniffer.has_header(sample)
                except csv.Error:
                    self.has_header = True
        except Exception:
            # Fallbacks conservadores
            self.delimiter = self.delimiter or ','
            self.has_header = True
        print(f"Delimitador detectado: '{self.delimiter}' | Cabeçalho: {self.has_header}")

    def _detect_engine(self) -> None:
        """Define engine preferida para leitura (pyarrow se disponível)"""
        if self.prefer_fast_engine and importlib.util.find_spec('pyarrow') is not None:
            self.engine_preferred = 'pyarrow'
        else:
            self.engine_preferred = 'python'
        print(f"Engine preferida: {self.engine_preferred}")

    def _read_csv(self, nrows: Optional[int] = None, chunksize: Optional[int] = None):
        """Wrapper robusto para pd.read_csv com fallback de engine"""
        common_kwargs = dict(
            filepath_or_buffer=self.file_path,
            encoding=self.encoding,
            delimiter=self.delimiter,
            nrows=nrows,
            chunksize=chunksize,
        )
        # Tenta engine rápida primeiro (se configurada)
        if self.engine_preferred == 'pyarrow':
            try:
                return pd.read_csv(**common_kwargs, engine='pyarrow')
            except Exception as e:
                print(f"Falha com engine 'pyarrow': {e}. Fazendo fallback para 'python'.")
        # Engine python com tratamento de linhas ruins
        try:
            return pd.read_csv(**common_kwargs, engine='python', on_bad_lines='warn')
        except TypeError:
            # Compatibilidade com versões mais antigas do pandas
            return pd.read_csv(**common_kwargs, engine='python')
    
    def get_file_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o arquivo"""
        file_size = self.file_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        file_size_gb = file_size / (1024 * 1024 * 1024)
        
        return {
            'path': str(self.file_path),
            'size_bytes': file_size,
            'size_mb': f"{file_size_mb:.2f} MB",
            'size_gb': f"{file_size_gb:.2f} GB",
            'encoding': self.encoding,
            'delimiter': self.delimiter
        }
    
    def read_in_chunks(self, chunk_size: int = 10000) -> Iterator[pd.DataFrame]:
        """
        Lê o arquivo em chunks (pedaços) para economizar memória
        
        Args:
            chunk_size: Número de linhas por chunk
            
        Yields:
            DataFrame com um chunk do arquivo
        """
        print(f"\nLendo arquivo em chunks de {chunk_size:,} linhas...")
        
        try:
            chunk_iterator = self._read_csv(chunksize=chunk_size)
            
            chunk_num = 0
            for chunk in chunk_iterator:
                chunk_num += 1
                self.total_rows += len(chunk)
                print(f"Chunk {chunk_num}: {len(chunk):,} linhas | Total processado: {self.total_rows:,}")
                yield chunk
                
        except Exception as e:
            print(f"Erro ao ler arquivo: {e}")
            raise
    
    def read_sample(self, n_rows: int = 100) -> pd.DataFrame:
        """
        Lê apenas as primeiras N linhas do arquivo
        
        Args:
            n_rows: Número de linhas a ler
            
        Returns:
            DataFrame com as primeiras linhas
        """
        print(f"\nLendo amostra de {n_rows} linhas...")
        
        return self._read_csv(nrows=n_rows)
    
    def count_rows(self) -> int:
        """Conta o número total de linhas no arquivo"""
        print("\nContando linhas...")
        
        count = 0
        with open(self.file_path, 'r', encoding=self.encoding, newline='') as f:
            for _ in f:
                count += 1
        
        # Subtrai 1 apenas se houver cabeçalho detectado
        return max(count - 1, 0) if self.has_header else count
    
    def get_column_names(self) -> List[str]:
        """Retorna os nomes das colunas"""
        df_sample = self.read_sample(n_rows=1)
        return df_sample.columns.tolist()
    
    def process_and_save(
        self,
        output_path: str,
        chunk_size: int = 10000,
        process_func: Optional[callable] = None
    ) -> None:
        """
        Processa o arquivo em chunks e salva em um novo arquivo
        
        Args:
            output_path: Caminho para o arquivo de saída
            chunk_size: Tamanho dos chunks
            process_func: Função opcional para processar cada chunk
        """
        print(f"\nProcessando e salvando em: {output_path}")
        
        first_chunk = True
        
        for chunk in self.read_in_chunks(chunk_size):
            # Aplica função de processamento se fornecida
            if process_func:
                chunk = process_func(chunk)
            
            # Salva o chunk
            chunk.to_csv(
                output_path,
                mode='w' if first_chunk else 'a',
                header=first_chunk,
                index=False,
                encoding='utf-8'
            )
            
            first_chunk = False
        
        print(f"\nProcessamento concluído! Total de linhas: {self.total_rows:,}")
    
    def analyze_data(self, sample_size: int = 50000) -> Dict[str, Any]:
        """
        Analisa uma amostra dos dados
        
        Args:
            sample_size: Tamanho da amostra para análise
            
        Returns:
            Dicionário com estatísticas dos dados
        """
        print(f"\nAnalisando amostra de {sample_size:,} linhas...")
        
        df = self.read_sample(sample_size)
        
        analysis = {
            'total_columns': len(df.columns),
            'column_names': df.columns.tolist(),
            'column_types': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'sample_rows': len(df),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024)
        }
        
        return analysis


class CSVAnalyzer:
    """Classe para análise avançada de arquivos CSV"""
    
    def __init__(self, reader: CSVReader):
        """
        Inicializa o analisador
        
        Args:
            reader: Instância de CSVReader
        """
        self.reader = reader
    
    def get_statistics(self, columns: List[str], sample_size: int = 50000) -> Dict[str, Any]:
        """
        Obtém estatísticas descritivas para colunas específicas
        
        Args:
            columns: Lista de colunas para analisar
            sample_size: Tamanho da amostra
            
        Returns:
            Dicionário com estatísticas
        """
        df = self.reader.read_sample(sample_size)
        
        stats = {}
        for col in columns:
            if col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    stats[col] = df[col].describe().to_dict()
                else:
                    stats[col] = {
                        'count': df[col].count(),
                        'unique': df[col].nunique(),
                        'top': df[col].mode()[0] if not df[col].mode().empty else None,
                        'freq': df[col].value_counts().iloc[0] if not df[col].empty else 0
                    }
        
        return stats
    
    def find_duplicates(self, columns: Optional[List[str]] = None, 
                       chunk_size: int = 10000) -> pd.DataFrame:
        """
        Encontra linhas duplicadas baseadas em colunas específicas
        
        Args:
            columns: Colunas para verificar duplicatas (None = todas)
            chunk_size: Tamanho dos chunks
            
        Returns:
            DataFrame com linhas duplicadas
        """
        all_data = []
        
        for chunk in self.reader.read_in_chunks(chunk_size):
            if columns:
                duplicates = chunk[chunk.duplicated(subset=columns, keep=False)]
            else:
                duplicates = chunk[chunk.duplicated(keep=False)]
            
            if not duplicates.empty:
                all_data.append(duplicates)
        
        if all_data:
            return pd.concat(all_data, ignore_index=True)
        else:
            return pd.DataFrame()
    
    def filter_data(
        self,
        condition: Callable[[pd.DataFrame], pd.Series],
        output_path: str,
        chunk_size: int = 10000
    ) -> int:
        """
        Filtra dados baseado em uma condição e salva em novo arquivo
        
        Args:
            condition: Função que retorna uma Series booleana
            output_path: Caminho do arquivo de saída
            chunk_size: Tamanho dos chunks
            
        Returns:
            Número de linhas filtradas
        """
        first_chunk = True
        total_filtered = 0
        
        for chunk in self.reader.read_in_chunks(chunk_size):
            filtered_chunk = chunk[condition(chunk)]
            
            if not filtered_chunk.empty:
                filtered_chunk.to_csv(
                    output_path,
                    mode='w' if first_chunk else 'a',
                    header=first_chunk,
                    index=False,
                    encoding='utf-8'
                )
                total_filtered += len(filtered_chunk)
                first_chunk = False
        
        return total_filtered

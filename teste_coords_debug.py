#!/usr/bin/env python3
"""
Script de teste para verificar busca de coordenadas
"""
import sys
sys.path.insert(0, '/workspaces/GeoGrafi_V2')

from modules.csv_processor import CSVProcessor
from modules.logging_config import setup_logging
import logging

# Ativa logs detalhados
setup_logging(level='DEBUG')
logger = logging.getLogger(__name__)

# Teste 1: Verificar se o geocoder está funcionando
print("\n=== TESTE 1: Geocoder ===")
processor = CSVProcessor(fetch_coordinates=True)

if processor.geocoder:
    print("✅ Geocoder inicializado")
    
    # Tenta buscar coordenadas de um endereço
    result = processor.geocoder.search_by_address(
        "Avenida Paulista",
        "",
        "Bela Vista",
        "São Paulo",
        "SP"
    )
    
    if result:
        print(f"✅ Coordenadas encontradas: {result}")
    else:
        print("❌ Nenhuma coordenada encontrada")
else:
    print("❌ Geocoder não inicializado")

# Teste 2: Processar arquivo de teste
print("\n=== TESTE 2: Processamento de Arquivo ===")
print("Processando /workspaces/GeoGrafi_V2/teste_sem_coords.csv...")

try:
    result_df = processor.process_file('/workspaces/GeoGrafi_V2/teste_sem_coords.csv')
    
    print(f"\n✅ Processamento concluído!")
    print(f"Total de linhas: {len(result_df)}")
    print(f"Colunas: {list(result_df.columns)}")
    
    # Verifica coordenadas
    print(f"\n=== Colunas de Coordenadas ===")
    lat_cols = [col for col in result_df.columns if 'LATITUDE' in col.upper()]
    lon_cols = [col for col in result_df.columns if 'LONGITUDE' in col.upper()]
    
    print(f"Colunas de Latitude: {lat_cols}")
    print(f"Colunas de Longitude: {lon_cols}")
    
    # Mostra primeiras 3 linhas
    print(f"\n=== Dados da Primeira Linha ===")
    for col in result_df.columns:
        val = result_df.iloc[0][col]
        print(f"{col}: {val}")
    
    # Estatísticas
    print(f"\n=== Estatísticas ===")
    print(f"Stats: {processor.stats}")
    
    # Verifica quantas linhas têm coordenadas
    if 'DS_LATITUDE_CORRETA' in result_df.columns:
        coords_count = result_df['DS_LATITUDE_CORRETA'].notna().sum()
        print(f"\nRegistros com DS_LATITUDE_CORRETA: {coords_count}/{len(result_df)}")
    
    if 'DS_LATITUDE' in result_df.columns:
        coords_count = result_df['DS_LATITUDE'].notna().sum()
        print(f"Registros com DS_LATITUDE: {coords_count}/{len(result_df)}")
    
except Exception as e:
    print(f"❌ Erro ao processar: {e}")
    import traceback
    traceback.print_exc()

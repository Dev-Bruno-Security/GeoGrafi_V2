#!/usr/bin/env python3
"""
Teste para validar busca de coordenadas
"""
import pandas as pd
import sys
sys.path.insert(0, '/workspaces/GeoGrafi_V2')

from modules.csv_processor import CSVProcessor

# Cria um CSV de teste pequeno
test_data = {
    'CD_CEP': ['01310100', '01502001'],
    'NM_LOGRADOURO': ['Avenida Paulista', 'Rua Iguatemi'],
    'NM_BAIRRO': ['Bela Vista', 'Centro'],
    'NM_MUNICIPIO': ['São Paulo', 'São Paulo'],
    'NM_UF': ['SP', 'SP']
}

test_df = pd.DataFrame(test_data)
test_file = '/tmp/test_coords.csv'
test_df.to_csv(test_file, index=False)

print(f"✅ Arquivo de teste criado: {test_file}")
print(f"   Linhas: {len(test_df)}")
print()

# Processa com busca de coordenadas
print("Processando com busca automática de coordenadas...")
print("(Isso pode levar alguns minutos...)")
print()

try:
    processor = CSVProcessor(fetch_coordinates=True)
    result_df = processor.process_file(test_file)
    
    print(f"\n✅ Processamento concluído!")
    print(f"   Colunas: {list(result_df.columns)}")
    print()
    
    # Verifica os resultados
    print("=== RESULTADOS ===\n")
    
    # Mostra cada linha
    for idx, row in result_df.iterrows():
        print(f"Linha {idx + 1}:")
        print(f"  CEP: {row.get('cep_corrigido')}")
        print(f"  Endereço: {row.get('logradouro')}, {row.get('bairro')}")
        print(f"  Cidade: {row.get('cidade')}, {row.get('uf')}")
        
        lat = row.get('DS_LATITUDE_CORRETA')
        lon = row.get('DS_LONGITUDE_CORRETA')
        
        if pd.notna(lat) and pd.notna(lon):
            print(f"  ✅ Coordenadas: {lat}, {lon}")
        else:
            print(f"  ❌ Sem coordenadas")
        print()
    
    # Estatísticas
    print("=== ESTATÍSTICAS ===")
    print(f"Stats: {processor.stats}")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

#!/usr/bin/env python3
from modules.csv_processor import CSVProcessor
import tempfile
import pandas as pd

# Cria arquivo de teste simples
test_data = '''cep,endereco
01310100,Av Paulista
01310200,Rua Augusta
12345678,Endereço inválido
'''

with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
    f.write(test_data)
    test_file = f.name

print(f'Arquivo de teste: {test_file}')
print('Iniciando processamento...')

processor = CSVProcessor(fetch_coordinates=False)
result = processor.process_file(test_file)

print('\n=== RESULTADO ===')
print(result)
print(f'\nCEPs válidos: {(result["cep_valido"] == True).sum()}')
print(f'CEPs inválidos: {(result["cep_valido"] == False).sum()}')

#!/usr/bin/env python3
"""Teste rápido de validação e correção de CEPs"""

from modules.csv_processor import CSVProcessor
import tempfile
import os

# Cria arquivo de teste
test_csv = """cep,endereco
01310-100,Av Paulista
55022-480,Bairro Mauricio
12345678,CEP Inválido
01305000,Rua Augusta
"""

with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
    f.write(test_csv)
    test_file = f.name

try:
    print("🧪 Testando Processador de CEPs\n")
    print("="*60)
    
    processor = CSVProcessor(fetch_coordinates=False)
    result = processor.process_file(test_file)
    
    print("\n✅ PROCESSAMENTO CONCLUÍDO!\n")
    print(f"📊 Total: {len(result)} linhas")
    print(f"✅ CEPs válidos: {(result['cep_valido'] == True).sum()}")
    print(f"❌ CEPs inválidos: {(result['cep_valido'] == False).sum()}")
    
    print("\n" + "="*60)
    print("📋 RESULTADO DETALHADO:\n")
    
    # Mostra colunas relevantes
    cols = ['cep_original', 'cep_valido', 'cep_corrigido', 'logradouro', 'cidade', 'uf']
    cols_disponiveis = [c for c in cols if c in result.columns]
    
    for idx, row in result.iterrows():
        print(f"\n{idx+1}. CEP: {row.get('cep_original', 'N/A')}")
        if row.get('cep_valido'):
            print(f"   ✅ Válido")
            if 'logradouro' in row and row['logradouro']:
                print(f"   📍 {row['logradouro']}")
            if 'cidade' in row and row['cidade']:
                print(f"   🏙️  {row['cidade']}-{row.get('uf', 'N/A')}")
        else:
            print(f"   ❌ Inválido - Não encontrado na base do ViaCEP")
    
    print("\n" + "="*60)
    
finally:
    os.unlink(test_file)
    print("\n✨ Teste concluído!")

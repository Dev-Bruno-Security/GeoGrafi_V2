"""
Testes básicos para os módulos do GeoGrafi
Execute: python tests.py
"""

import sys
from pathlib import Path


def test_imports():
    """Testa se todos os módulos podem ser importados"""
    print("🧪 Testando importações...")
    
    try:
        from modules import (
            CSVProcessor,
            CEPValidator,
            Geocoder,
            CSVReader,
            CSVAnalyzer,
            CacheManager,
            get_config,
            update_config,
            clean_cep,
            format_cep,
            normalize_address
        )
        print("   ✅ Todas as importações bem-sucedidas")
        return True
    except ImportError as e:
        print(f"   ❌ Erro de importação: {e}")
        return False


def test_cep_validator():
    """Testa validação de CEP"""
    print("\n🧪 Testando CEPValidator...")
    
    try:
        from modules import CEPValidator
        
        validator = CEPValidator()
        
        # Testa formato
        assert validator.validate_cep_format("50670-420") == True
        assert validator.validate_cep_format("12345") == False
        print("   ✅ Validação de formato OK")
        
        # Testa formatação
        assert validator.format_cep("50670420") == "50670-420"
        print("   ✅ Formatação OK")
        
        return True
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False


def test_utils():
    """Testa utilitários"""
    print("\n🧪 Testando utilitários...")
    
    try:
        from modules import clean_cep, format_cep, normalize_text, normalize_address
        
        # Testa clean_cep
        assert clean_cep("50670-420") == "50670420"
        assert clean_cep("12345") == None
        print("   ✅ clean_cep OK")
        
        # Testa format_cep
        assert format_cep("50670420") == "50670-420"
        print("   ✅ format_cep OK")
        
        # Testa normalize_text
        assert normalize_text("  Texto   com espaços  ") == "Texto com espaços"
        print("   ✅ normalize_text OK")
        
        # Testa normalize_address
        addr = normalize_address("Rua das Flores 123 - Apto 45")
        assert "Rua" in addr or "R" in addr
        print("   ✅ normalize_address OK")
        
        return True
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False


def test_config():
    """Testa configurações"""
    print("\n🧪 Testando configurações...")
    
    try:
        from modules import get_config, update_config
        
        # Obtém config
        config = get_config()
        assert config is not None
        print("   ✅ get_config OK")
        
        # Atualiza config
        update_config(chunk_size=2000)
        assert config.processing.chunk_size == 2000
        print("   ✅ update_config OK")
        
        # Restaura padrão
        update_config(chunk_size=1000)
        
        return True
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False


def test_cache_manager():
    """Testa gerenciador de cache"""
    print("\n🧪 Testando CacheManager...")
    
    try:
        from modules import CacheManager
        import os
        
        cache_file = "test_cache.db"
        
        # Remove cache anterior se existir
        if os.path.exists(cache_file):
            os.remove(cache_file)
        
        # Cria cache
        cache = CacheManager(cache_file)
        print("   ✅ Criação de cache OK")
        
        # Salva CEP
        test_cep = "50670420"
        test_data = {
            'logradouro': 'Av. Teste',
            'bairro': 'Bairro Teste',
            'localidade': 'Cidade Teste',
            'uf': 'PE'
        }
        cache.save_cep(test_cep, test_data)
        print("   ✅ Salvamento no cache OK")
        
        # Recupera CEP
        cached = cache.get_cep(test_cep)
        assert cached is not None
        assert cached['logradouro'] == 'Av. Teste'
        print("   ✅ Recuperação do cache OK")
        
        # Limpa
        if os.path.exists(cache_file):
            os.remove(cache_file)
        
        return True
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False


def test_csv_reader():
    """Testa leitor de CSV"""
    print("\n🧪 Testando CSVReader...")
    
    try:
        from modules import CSVReader
        import tempfile
        import os
        
        # Cria CSV temporário
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write("col1,col2,col3\n")
            f.write("valor1,valor2,valor3\n")
            f.write("valor4,valor5,valor6\n")
            temp_file = f.name
        
        # Testa leitura
        reader = CSVReader(temp_file)
        print("   ✅ Criação de reader OK")
        
        # Testa info
        info = reader.get_file_info()
        assert 'encoding' in info
        print("   ✅ get_file_info OK")
        
        # Testa sample
        sample = reader.read_sample(1)
        assert len(sample) == 1
        print("   ✅ read_sample OK")
        
        # Testa colunas
        cols = reader.get_column_names()
        assert len(cols) == 3
        print("   ✅ get_column_names OK")
        
        # Limpa
        os.remove(temp_file)
        
        return True
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False


def test_estrutura_projeto():
    """Verifica estrutura de arquivos do projeto"""
    print("\n🧪 Testando estrutura do projeto...")
    
    arquivos_essenciais = [
        'modules/__init__.py',
        'modules/cep_validator.py',
        'modules/geocoder.py',
        'modules/csv_processor.py',
        'modules/csv_reader.py',
        'modules/cache_manager.py',
        'modules/config.py',
        'modules/utils.py',
        'modules/streamlit_components.py',
        'app.py',
        'exemplos.py',
        'requirements.txt',
        'README_V2.md',
        'GUIA_RAPIDO_V2.md'
    ]
    
    todos_existem = True
    for arquivo in arquivos_essenciais:
        if not Path(arquivo).exists():
            print(f"   ❌ Arquivo ausente: {arquivo}")
            todos_existem = False
    
    if todos_existem:
        print("   ✅ Todos os arquivos essenciais presentes")
    
    return todos_existem


def run_all_tests():
    """Executa todos os testes"""
    print("\n" + "=" * 70)
    print("TESTES DO GEOGRAFI V2.0")
    print("=" * 70)
    
    testes = [
        ("Estrutura do Projeto", test_estrutura_projeto),
        ("Importações", test_imports),
        ("Utilitários", test_utils),
        ("Configurações", test_config),
        ("CEP Validator", test_cep_validator),
        ("Cache Manager", test_cache_manager),
        ("CSV Reader", test_csv_reader),
    ]
    
    resultados = []
    
    for nome, teste in testes:
        try:
            resultado = teste()
            resultados.append((nome, resultado))
        except Exception as e:
            print(f"\n❌ Erro crítico no teste '{nome}': {e}")
            resultados.append((nome, False))
    
    # Resume
    print("\n" + "=" * 70)
    print("RESUMO DOS TESTES")
    print("=" * 70 + "\n")
    
    passou = sum(1 for _, r in resultados if r)
    total = len(resultados)
    
    for nome, resultado in resultados:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"   {status} - {nome}")
    
    print("\n" + "=" * 70)
    print(f"Resultado: {passou}/{total} testes passaram")
    
    if passou == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
    else:
        print(f"⚠️  {total - passou} teste(s) falharam")
    
    print("=" * 70 + "\n")
    
    return passou == total


if __name__ == "__main__":
    sucesso = run_all_tests()
    sys.exit(0 if sucesso else 1)

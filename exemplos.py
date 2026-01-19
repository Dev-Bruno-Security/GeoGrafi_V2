"""
Exemplos de uso do GeoGrafi - Versão Modularizada
Demonstra como usar a biblioteca programaticamente
"""

from modules import (
    CSVReader,
    CSVProcessor,
    CEPValidator,
    Geocoder,
    CacheManager,
    format_cep,
    normalize_address
)


def exemplo_1_leitura_csv():
    """Exemplo 1: Leitura básica de arquivo CSV"""
    print("=" * 70)
    print("EXEMPLO 1: Leitura de Arquivo CSV")
    print("=" * 70)
    
    # Substitua pelo caminho do seu arquivo
    file_path = "exemplo_dados.csv"
    
    try:
        # Cria leitor (detecta encoding e delimitador automaticamente)
        reader = CSVReader(file_path)
        
        # Informações do arquivo
        info = reader.get_file_info()
        print("\n📄 Informações do arquivo:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        # Lê amostra
        print("\n📊 Primeiras 5 linhas:")
        sample = reader.read_sample(5)
        print(sample)
        
        # Colunas disponíveis
        print("\n📋 Colunas disponíveis:")
        for i, col in enumerate(reader.get_column_names(), 1):
            print(f"  {i}. {col}")
    
    except FileNotFoundError:
        print(f"\n❌ Arquivo não encontrado: {file_path}")
        print("   Crie um arquivo exemplo_dados.csv para testar")
    except Exception as e:
        print(f"\n❌ Erro: {e}")


def exemplo_2_validacao_cep():
    """Exemplo 2: Validação e busca de CEP"""
    print("\n" + "=" * 70)
    print("EXEMPLO 2: Validação de CEP")
    print("=" * 70)
    
    # Cria validador
    validator = CEPValidator()
    
    # Testa CEPs
    ceps_teste = ["50670-420", "01310-100", "12345-678", "40000-000"]
    
    for cep in ceps_teste:
        print(f"\n🔍 Testando CEP: {cep}")
        
        # Busca informações
        resultado = validator.search_cep(cep)
        
        if resultado:
            print(f"   ✅ CEP válido")
            print(f"   Logradouro: {resultado.get('logradouro', 'N/A')}")
            print(f"   Bairro: {resultado.get('bairro', 'N/A')}")
            print(f"   Cidade: {resultado.get('localidade', 'N/A')}")
            print(f"   UF: {resultado.get('uf', 'N/A')}")
        else:
            print(f"   ❌ CEP inválido ou não encontrado")


def exemplo_3_geocoding():
    """Exemplo 3: Busca de coordenadas (Geocoding)"""
    print("\n" + "=" * 70)
    print("EXEMPLO 3: Busca de Coordenadas (Geocoding)")
    print("=" * 70)
    
    # Cria geocoder
    geocoder = Geocoder()
    
    # Testa endereços
    enderecos = [
        {
            'street': 'Avenida Paulista',
            'city': 'São Paulo',
            'state': 'SP'
        },
        {
            'street': 'Rua do Catete',
            'neighborhood': 'Catete',
            'city': 'Rio de Janeiro',
            'state': 'RJ'
        }
    ]
    
    for endereco in enderecos:
        print(f"\n🗺️  Buscando coordenadas para:")
        print(f"   {endereco.get('street', '')}, {endereco.get('city', '')}")
        
        coords = geocoder.search_by_address(
            endereco.get('street', ''),
            endereco.get('neighborhood', ''),
            endereco.get('city', ''),
            endereco.get('state', '')
        )
        
        if coords:
            lat, lon = coords
            print(f"   ✅ Coordenadas encontradas:")
            print(f"   Latitude: {lat}")
            print(f"   Longitude: {lon}")
            print(f"   Google Maps: https://www.google.com/maps?q={lat},{lon}")
        else:
            print(f"   ❌ Coordenadas não encontradas")


def exemplo_4_processamento_completo():
    """Exemplo 4: Processamento completo de arquivo CSV"""
    print("\n" + "=" * 70)
    print("EXEMPLO 4: Processamento Completo")
    print("=" * 70)
    
    input_file = "exemplo_dados.csv"
    output_file = "exemplo_resultado.csv"
    
    try:
        print(f"\n📂 Arquivo de entrada: {input_file}")
        print(f"💾 Arquivo de saída: {output_file}")
        
        # Cria processador
        processor = CSVProcessor(
            chunk_size=100,
            max_workers=2,
            use_cache=True
        )
        
        print("\n🔄 Iniciando processamento...")
        
        # Processa arquivo
        def progress_callback(progress):
            print(f"   Progresso: {progress:.1f}%", end='\r')
        
        result = processor.process_file(
            input_file,
            progress_callback=progress_callback
        )
        
        # Salva resultado
        df = result['dataframe']
        df.to_csv(output_file, index=False, encoding='utf-8')
        
        print("\n\n✅ Processamento concluído!")
        print("\n📊 Estatísticas:")
        stats = result['stats']
        print(f"   Total de linhas: {stats['total_rows']}")
        print(f"   Linhas processadas: {stats['processed_rows']}")
        print(f"   CEPs corrigidos: {stats['fixed_ceps']}")
        print(f"   Coordenadas encontradas: {stats['found_coordinates']}")
        
        if stats['errors']:
            print(f"\n⚠️  Erros encontrados: {len(stats['errors'])}")
        
        print(f"\n💾 Resultado salvo em: {output_file}")
    
    except FileNotFoundError:
        print(f"\n❌ Arquivo não encontrado: {input_file}")
    except Exception as e:
        print(f"\n❌ Erro durante processamento: {e}")


def exemplo_5_utilitarios():
    """Exemplo 5: Utilitários diversos"""
    print("\n" + "=" * 70)
    print("EXEMPLO 5: Utilitários")
    print("=" * 70)
    
    # Formatação de CEP
    print("\n📍 Formatação de CEP:")
    cep = "50670420"
    print(f"   Original: {cep}")
    print(f"   Formatado: {format_cep(cep)}")
    
    # Normalização de endereço
    print("\n🏠 Normalização de Endereço:")
    endereco = "   Rua das Flores, 123 - Apto 45 - Lote 10  "
    print(f"   Original: '{endereco}'")
    print(f"   Normalizado: '{normalize_address(endereco)}'")
    
    # Cache
    print("\n💾 Cache Manager:")
    cache = CacheManager("exemplo_cache.db")
    
    # Salva no cache
    cache.save_cep("50670420", {
        'logradouro': 'Avenida Exemplo',
        'bairro': 'Bairro Teste',
        'localidade': 'Cidade',
        'uf': 'PE'
    })
    print("   ✅ CEP salvo no cache")
    
    # Recupera do cache
    cached_data = cache.get_cep("50670420")
    if cached_data:
        print(f"   ✅ CEP recuperado: {cached_data.get('logradouro')}")


def exemplo_6_leitura_em_chunks():
    """Exemplo 6: Leitura de arquivo grande em chunks"""
    print("\n" + "=" * 70)
    print("EXEMPLO 6: Leitura em Chunks (Arquivos Grandes)")
    print("=" * 70)
    
    file_path = "exemplo_dados.csv"
    
    try:
        reader = CSVReader(file_path)
        
        print(f"\n📂 Processando arquivo: {file_path}")
        print("🔄 Lendo em chunks de 10 linhas...\n")
        
        total_rows = 0
        chunk_count = 0
        
        for chunk in reader.read_in_chunks(chunk_size=10):
            chunk_count += 1
            total_rows += len(chunk)
            
            print(f"   Chunk {chunk_count}: {len(chunk)} linhas processadas")
            
            # Aqui você pode processar cada chunk
            # Ex: fazer transformações, filtros, etc.
        
        print(f"\n✅ Processamento concluído!")
        print(f"   Total de chunks: {chunk_count}")
        print(f"   Total de linhas: {total_rows}")
    
    except FileNotFoundError:
        print(f"\n❌ Arquivo não encontrado: {file_path}")
    except Exception as e:
        print(f"\n❌ Erro: {e}")


def main():
    """Função principal - executa todos os exemplos"""
    print("\n")
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  EXEMPLOS DE USO - GeoGrafi v2.0".center(68) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    
    exemplos = [
        ("1", "Leitura de CSV", exemplo_1_leitura_csv),
        ("2", "Validação de CEP", exemplo_2_validacao_cep),
        ("3", "Geocoding", exemplo_3_geocoding),
        ("4", "Processamento Completo", exemplo_4_processamento_completo),
        ("5", "Utilitários", exemplo_5_utilitarios),
        ("6", "Leitura em Chunks", exemplo_6_leitura_em_chunks),
    ]
    
    print("\nEscolha um exemplo para executar:")
    for num, nome, _ in exemplos:
        print(f"  {num}. {nome}")
    print("  0. Executar todos")
    print("  q. Sair")
    
    escolha = input("\nDigite sua escolha: ").strip().lower()
    
    if escolha == 'q':
        print("\n👋 Até logo!")
        return
    
    if escolha == '0':
        for _, _, func in exemplos:
            func()
            print("\n")
    else:
        for num, _, func in exemplos:
            if escolha == num:
                func()
                break
        else:
            print("\n❌ Opção inválida!")
    
    print("\n" + "=" * 70)
    print("Fim dos exemplos")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()

"""
Ponto de entrada principal do GeoGrafi v2.0
Permite executar o projeto como módulo: python -m GeoGrafi_V2
"""

import sys
import argparse


def main():
    """Função principal com opções de linha de comando"""
    parser = argparse.ArgumentParser(
        description="GeoGrafi v2.0 - Processador de Dados Geográficos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python -m GeoGrafi_V2               # Inicia interface web
  python -m GeoGrafi_V2 --web         # Inicia interface web
  python -m GeoGrafi_V2 --exemplos    # Executa exemplos interativos
  python -m GeoGrafi_V2 --processar dados.csv  # Processa arquivo via CLI
        """
    )
    
    parser.add_argument(
        '--web',
        action='store_true',
        help='Inicia interface web Streamlit (padrão)'
    )
    
    parser.add_argument(
        '--exemplos',
        action='store_true',
        help='Executa exemplos interativos'
    )
    
    parser.add_argument(
        '--processar',
        metavar='ARQUIVO',
        help='Processa arquivo CSV via linha de comando'
    )
    
    parser.add_argument(
        '--output',
        metavar='SAIDA',
        default='resultado.csv',
        help='Arquivo de saída (padrão: resultado.csv)'
    )
    
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=1000,
        help='Tamanho do chunk (padrão: 1000)'
    )
    
    parser.add_argument(
        '--workers',
        type=int,
        default=3,
        help='Número de workers (padrão: 3)'
    )
    
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Desabilita cache local'
    )
    
    args = parser.parse_args()
    
    # Processar arquivo via CLI
    if args.processar:
        processar_cli(
            args.processar,
            args.output,
            args.chunk_size,
            args.workers,
            not args.no_cache
        )
    # Executar exemplos
    elif args.exemplos:
        executar_exemplos()
    # Interface web (padrão)
    else:
        iniciar_web()


def iniciar_web():
    """Inicia interface Streamlit"""
    import subprocess
    
    print("🚀 Iniciando interface web...")
    print("   Abrindo navegador em: http://localhost:8501")
    print("\n   Pressione Ctrl+C para sair\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Encerrando aplicação...")


def executar_exemplos():
    """Executa exemplos interativos"""
    import exemplos
    exemplos.main()


def processar_cli(input_file, output_file, chunk_size, workers, use_cache):
    """Processa arquivo via linha de comando"""
    from modules import CSVProcessor
    import sys
    
    print("=" * 70)
    print("GeoGrafi v2.0 - Processamento CLI")
    print("=" * 70)
    print(f"\n📂 Arquivo de entrada: {input_file}")
    print(f"💾 Arquivo de saída: {output_file}")
    print(f"⚙️  Chunk size: {chunk_size}")
    print(f"⚙️  Workers: {workers}")
    print(f"⚙️  Cache: {'Ativado' if use_cache else 'Desativado'}")
    print("\n" + "=" * 70 + "\n")
    
    try:
        # Cria processador
        processor = CSVProcessor(
            chunk_size=chunk_size,
            max_workers=workers,
            use_cache=use_cache
        )
        
        print("🔄 Iniciando processamento...\n")
        
        # Callback de progresso
        def mostrar_progresso(progresso):
            barra = "█" * int(progresso / 2) + "░" * (50 - int(progresso / 2))
            sys.stdout.write(f"\r   [{barra}] {progresso:.1f}%")
            sys.stdout.flush()
        
        # Processa arquivo
        result = processor.process_file(
            input_file,
            progress_callback=mostrar_progresso
        )
        
        print("\n")
        
        # Salva resultado
        df = result['dataframe']
        df.to_csv(output_file, index=False, encoding='utf-8')
        
        # Estatísticas
        stats = result['stats']
        print("\n" + "=" * 70)
        print("✅ Processamento concluído!")
        print("=" * 70)
        print(f"\n📊 Estatísticas:")
        print(f"   Total de linhas: {stats['total_rows']:,}")
        print(f"   Linhas processadas: {stats['processed_rows']:,}")
        print(f"   CEPs corrigidos: {stats['fixed_ceps']:,}")
        print(f"   Coordenadas encontradas: {stats['found_coordinates']:,}")
        
        if stats['errors']:
            print(f"\n⚠️  Erros encontrados: {len(stats['errors'])}")
            if len(stats['errors']) <= 5:
                for erro in stats['errors']:
                    print(f"   - Linha {erro.get('row', '?')}: {erro.get('error', 'Erro desconhecido')}")
            else:
                print(f"   (Use --verbose para ver todos os erros)")
        
        print(f"\n💾 Resultado salvo em: {output_file}")
        print("\n" + "=" * 70 + "\n")
    
    except FileNotFoundError:
        print(f"\n❌ Erro: Arquivo não encontrado: {input_file}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro durante processamento: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

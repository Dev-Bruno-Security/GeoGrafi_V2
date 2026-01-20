#!/usr/bin/env python
"""
Script para iniciar a API REST do GeoGrafi
Pode ser executado como: python api_run.py
"""

import os
import sys
import argparse
from pathlib import Path

# Adiciona diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

from modules.api_server import run_api_server


def main():
    """Função principal para executar a API"""
    
    parser = argparse.ArgumentParser(
        description="GeoGrafi REST API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python api_run.py              # Inicia em localhost:8000
  python api_run.py --port 9000  # Inicia em porta customizada
  python api_run.py --host 0.0.0.0  # Aceita conexões externas
        """
    )
    
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Host para executar a API (padrão: 127.0.0.1)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Porta para executar a API (padrão: 8000)'
    )
    
    parser.add_argument(
        '--reload',
        action='store_true',
        help='Ativa reload automático em desenvolvimento'
    )
    
    args = parser.parse_args()
    
    print(f"""
    ╔════════════════════════════════════════╗
    ║     GeoGrafi - REST API v2.0          ║
    ║     Iniciando servidor...              ║
    ╚════════════════════════════════════════╝
    
    🌐 Host: {args.host}
    🔌 Porta: {args.port}
    📍 URL: http://{args.host}:{args.port}
    📚 Docs: http://{args.host}:{args.port}/docs
    
    ✨ Pressione CTRL+C para parar
    """)
    
    try:
        run_api_server(host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\n\n👋 Servidor parado com sucesso")
        sys.exit(0)


if __name__ == "__main__":
    main()

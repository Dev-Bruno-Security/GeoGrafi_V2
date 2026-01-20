"""
Testes para a API REST do GeoGrafi
Valida funcionalidade dos endpoints
"""

import requests
import json
from pathlib import Path
import pandas as pd
import io


class GeoGrafiAPITester:
    """Classe para testar a API do GeoGrafi"""
    
    def __init__(self, base_url: str = "http://localhost:8501", api_key: str = None):
        """
        Inicializa o testador da API
        
        Args:
            base_url: URL base da API
            api_key: Chave API para autenticação
        """
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    def test_health(self) -> bool:
        """Testa endpoint de health check"""
        print("\n📊 Testando Health Check...")
        try:
            response = requests.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health Check OK: {data['status']}")
                return True
            else:
                print(f"❌ Health Check Falhou: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            return False
    
    def test_info(self) -> bool:
        """Testa endpoint de informações da API"""
        print("\n📋 Testando Informações da API...")
        try:
            response = requests.get(f"{self.base_url}/api/info")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Informações obtidas:")
                print(f"   Serviço: {data.get('service')}")
                print(f"   Versão: {data.get('version')}")
                print(f"   Recursos: {len(data.get('features', []))} disponíveis")
                return True
            else:
                print(f"❌ Erro: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            return False
    
    def test_validate_cep(self, cep: str = "01310100") -> bool:
        """Testa validação de CEP"""
        print(f"\n✅ Testando Validação de CEP ({cep})...")
        
        if not self.api_key:
            print("⚠️  Pulando teste de CEP (sem API key)")
            return True
        
        try:
            response = requests.get(
                f"{self.base_url}/api/validate-cep",
                params={"cep": cep},
                headers=self.headers
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ CEP validado: {data.get('valid')}")
                return True
            else:
                print(f"❌ Erro: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            return False
    
    def test_process_csv(self, csv_path: str = None) -> bool:
        """Testa processamento de arquivo CSV"""
        print("\n🚀 Testando Processamento de CSV...")
        
        if not self.api_key:
            print("⚠️  Pulando teste (sem API key)")
            return True
        
        # Criar arquivo CSV de teste
        if csv_path is None:
            df = pd.DataFrame({
                "CD_CEP": ["01310100", "20040020"],
                "NM_LOGRADOURO": ["Avenida Paulista", "Avenida Presidente Wilson"],
                "NM_BAIRRO": ["Bela Vista", "Centro"],
                "NM_MUNICIPIO": ["São Paulo", "Rio de Janeiro"],
                "NM_UF": ["SP", "RJ"]
            })
            csv_path = "test_data.csv"
            df.to_csv(csv_path, index=False)
        
        try:
            with open(csv_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    f"{self.base_url}/api/process",
                    files=files,
                    headers=self.headers
                )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ CSV Processado:")
                print(f"   Status: {data.get('status')}")
                print(f"   Linhas processadas: {data.get('rows_processed')}")
                print(f"   CEPs válidos: {data.get('stats', {}).get('valid_ceps')}")
                return True
            else:
                print(f"❌ Erro: {response.status_code}")
                print(f"   Resposta: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            return False
        finally:
            # Limpar arquivo de teste
            if csv_path == "test_data.csv" and Path(csv_path).exists():
                Path(csv_path).unlink()
    
    def test_list_keys(self) -> bool:
        """Testa listagem de chaves API"""
        print("\n📋 Testando Listagem de Chaves...")
        
        if not self.api_key:
            print("⚠️  Pulando teste (sem API key)")
            return True
        
        try:
            response = requests.get(
                f"{self.base_url}/api/keys/list",
                headers=self.headers
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Chaves listadas:")
                print(f"   Total: {data.get('count')}")
                return True
            else:
                print(f"❌ Erro: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            return False
    
    def test_integration_info(self) -> bool:
        """Testa informações de integração"""
        print("\n🔗 Testando Informações de Integração...")
        try:
            response = requests.get(
                f"{self.base_url}/api/integration-info"
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Informações de Integração:")
                print(f"   Serviço: {data.get('service_name')}")
                print(f"   Endpoints: {len(data.get('endpoints', {}))} disponíveis")
                return True
            else:
                print(f"❌ Erro: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            return False
    
    def test_auth_required(self) -> bool:
        """Testa se autenticação é requerida"""
        print("\n🔐 Testando Autenticação...")
        try:
            # Tentar sem chave
            response = requests.get(
                f"{self.base_url}/api/keys/list"
            )
            if response.status_code == 401:
                print("✅ Autenticação corretamente requerida")
                return True
            else:
                print(f"⚠️  Autenticação pode não estar ativa")
                return False
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            return False
    
    def run_all_tests(self) -> dict:
        """Executa todos os testes"""
        print("""
╔════════════════════════════════════════╗
║  GeoGrafi API - Test Suite             ║
║  Validando funcionalidade da API       ║
╚════════════════════════════════════════╝
        """)
        
        results = {
            "health": self.test_health(),
            "info": self.test_info(),
            "auth_required": self.test_auth_required(),
            "integration_info": self.test_integration_info(),
        }
        
        if self.api_key:
            results["validate_cep"] = self.test_validate_cep()
            results["process_csv"] = self.test_process_csv()
            results["list_keys"] = self.test_list_keys()
        
        # Resumo
        print(f"""
╔════════════════════════════════════════╗
║  RESULTADO DOS TESTES                  ║
╚════════════════════════════════════════╝
        """)
        
        for test_name, result in results.items():
            status = "✅ PASSOU" if result else "❌ FALHOU"
            print(f"{test_name:20} {status}")
        
        passed = sum(1 for r in results.values() if r)
        total = len(results)
        
        print(f"\n📊 Total: {passed}/{total} testes passaram")
        
        return results


def main():
    """Função principal para rodar os testes"""
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Teste a API REST do GeoGrafi"
    )
    
    parser.add_argument(
        "--url",
        default="http://localhost:8501",
        help="URL base da API (padrão: http://localhost:8501)"
    )
    
    parser.add_argument(
        "--api-key",
        help="Chave API para autenticação"
    )
    
    args = parser.parse_args()
    
    tester = GeoGrafiAPITester(base_url=args.url, api_key=args.api_key)
    results = tester.run_all_tests()
    
    # Retornar código de saída apropriado
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    exit(main())

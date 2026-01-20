"""
Módulo de Gerenciamento de Chaves API
Permite armazenar e gerenciar chaves API para integração com n8n e outros serviços
"""

import os
import json
import secrets
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime


class APIKeyManager:
    """Gerenciador de chaves API da aplicação"""
    
    def __init__(self, config_dir: str = ".config"):
        """
        Inicializa o gerenciador de chaves API
        
        Args:
            config_dir: Diretório para armazenar configurações
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.api_keys_file = self.config_dir / "api_keys.json"
        self._load_keys()
    
    def _load_keys(self) -> None:
        """Carrega chaves API do arquivo de configuração"""
        if self.api_keys_file.exists():
            try:
                with open(self.api_keys_file, 'r') as f:
                    self.keys_data = json.load(f)
            except json.JSONDecodeError:
                self.keys_data = {"keys": {}, "metadata": {}}
        else:
            self.keys_data = {"keys": {}, "metadata": {}}
    
    def _save_keys(self) -> None:
        """Salva chaves API no arquivo de configuração"""
        with open(self.api_keys_file, 'w') as f:
            json.dump(self.keys_data, f, indent=2)
    
    def generate_api_key(self, name: str, description: str = "") -> str:
        """
        Gera uma nova chave API
        
        Args:
            name: Nome da chave API
            description: Descrição da chave API
        
        Returns:
            str: Chave API gerada
        """
        api_key = f"geo_{secrets.token_hex(32)}"
        
        self.keys_data["keys"][name] = {
            "key": api_key,
            "created_at": datetime.now().isoformat(),
            "description": description,
            "active": True,
            "last_used": None,
            "usage_count": 0
        }
        
        self._save_keys()
        return api_key
    
    def get_api_key(self, name: str) -> Optional[str]:
        """
        Obtém uma chave API pelo nome
        
        Args:
            name: Nome da chave API
        
        Returns:
            str: Chave API ou None se não encontrada
        """
        if name in self.keys_data["keys"]:
            key_data = self.keys_data["keys"][name]
            if key_data.get("active", True):
                # Atualiza uso
                key_data["last_used"] = datetime.now().isoformat()
                key_data["usage_count"] = key_data.get("usage_count", 0) + 1
                self._save_keys()
                return key_data["key"]
        return None
    
    def validate_api_key(self, api_key: str) -> bool:
        """
        Valida uma chave API
        
        Args:
            api_key: Chave API a validar
        
        Returns:
            bool: True se válida e ativa
        """
        for name, key_data in self.keys_data["keys"].items():
            if key_data["key"] == api_key and key_data.get("active", True):
                return True
        return False
    
    def list_api_keys(self, show_secret: bool = False) -> List[Dict]:
        """
        Lista todas as chaves API configuradas
        
        Args:
            show_secret: Se deve mostrar a chave completa
        
        Returns:
            list: Lista de chaves API
        """
        result = []
        for name, key_data in self.keys_data["keys"].items():
            key_info = {
                "name": name,
                "description": key_data.get("description", ""),
                "active": key_data.get("active", True),
                "created_at": key_data.get("created_at", ""),
                "last_used": key_data.get("last_used"),
                "usage_count": key_data.get("usage_count", 0)
            }
            if show_secret:
                key_info["key"] = key_data["key"]
            else:
                key_info["key_preview"] = key_data["key"][:20] + "..."
            result.append(key_info)
        return result
    
    def deactivate_api_key(self, name: str) -> bool:
        """
        Desativa uma chave API
        
        Args:
            name: Nome da chave API
        
        Returns:
            bool: True se desativada com sucesso
        """
        if name in self.keys_data["keys"]:
            self.keys_data["keys"][name]["active"] = False
            self._save_keys()
            return True
        return False
    
    def delete_api_key(self, name: str) -> bool:
        """
        Deleta uma chave API
        
        Args:
            name: Nome da chave API
        
        Returns:
            bool: True se deletada com sucesso
        """
        if name in self.keys_data["keys"]:
            del self.keys_data["keys"][name]
            self._save_keys()
            return True
        return False
    
    def get_integration_info(self) -> Dict:
        """
        Retorna informações para integração com n8n
        
        Returns:
            dict: Informações de integração
        """
        return {
            "service_name": "GeoGrafi",
            "version": "2.0",
            "api_endpoint": "http://localhost:8501/api",
            "auth_type": "bearer_token",
            "features": [
                "CEP Processing",
                "Address Enrichment",
                "Coordinate Generation",
                "Data Validation"
            ],
            "endpoints": {
                "process": "/api/process",
                "validate": "/api/validate",
                "health": "/api/health",
                "status": "/api/status"
            }
        }


# Instância global do gerenciador
_api_key_manager = None


def get_api_key_manager() -> APIKeyManager:
    """Retorna a instância global do gerenciador de chaves API"""
    global _api_key_manager
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager()
    return _api_key_manager

#!/usr/bin/env python3
"""Testes unitarios do APIKeyManager (sem dependencias externas)."""

import tempfile
import unittest
from pathlib import Path

from modules.api_key_manager import APIKeyManager


class TestAPIKeyManager(unittest.TestCase):
    """Valida comportamento essencial do gerenciador de chaves."""

    def test_key_lifecycle_and_usage_tracking(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = APIKeyManager(config_dir=temp_dir)

            api_key = manager.generate_api_key("n8n", "chave de integracao")

            # Formato esperado: prefixo fixo + 64 chars hex.
            self.assertTrue(api_key.startswith("geo_"))
            self.assertEqual(len(api_key), 68)
            self.assertTrue(manager.validate_api_key(api_key))

            keys_file = Path(temp_dir) / "api_keys.json"
            self.assertTrue(keys_file.exists())

            # get_api_key atualiza uso e retorna a chave ativa.
            returned_key = manager.get_api_key("n8n")
            self.assertEqual(returned_key, api_key)

            listed = manager.list_api_keys(show_secret=False)
            self.assertEqual(len(listed), 1)
            self.assertEqual(listed[0]["name"], "n8n")
            self.assertEqual(listed[0]["usage_count"], 1)
            self.assertIsNotNone(listed[0]["last_used"])
            self.assertIn("key_preview", listed[0])
            self.assertNotIn("key", listed[0])

            # Recarregar do disco preserva o estado.
            reloaded = APIKeyManager(config_dir=temp_dir)
            listed_reloaded = reloaded.list_api_keys(show_secret=True)
            self.assertEqual(listed_reloaded[0]["key"], api_key)
            self.assertEqual(listed_reloaded[0]["usage_count"], 1)

            # Desativacao invalida a chave para autenticacao.
            self.assertTrue(reloaded.deactivate_api_key("n8n"))
            self.assertFalse(reloaded.validate_api_key(api_key))
            self.assertIsNone(reloaded.get_api_key("n8n"))

            # Remocao limpa definitivamente o registro.
            self.assertTrue(reloaded.delete_api_key("n8n"))
            self.assertEqual(reloaded.list_api_keys(), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)

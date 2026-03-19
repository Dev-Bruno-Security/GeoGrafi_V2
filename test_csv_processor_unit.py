#!/usr/bin/env python3
"""Testes unitarios do CSVProcessor (sem chamadas de rede)."""

import unittest

import pandas as pd

from modules.csv_processor import CSVProcessor


class TestCSVProcessorFillMissingAddressFields(unittest.TestCase):
    """Valida preenchimento de campos de endereco a partir do retorno de CEP valido."""

    def setUp(self):
        self.processor = CSVProcessor(use_cache=False, fetch_coordinates=False)

    def test_fill_missing_only_for_valid_cep_rows(self):
        df = pd.DataFrame(
            [
                {
                    "cep_valido": True,
                    "logradouro": "Avenida Paulista",
                    "bairro": "Bela Vista",
                    "cidade": "Sao Paulo",
                    "uf": "SP",
                    "NM_LOGRADOURO": "",
                    "NM_BAIRRO": None,
                    "NM_MUNICIPIO": "",
                    "NM_UF": "",
                },
                {
                    "cep_valido": False,
                    "logradouro": "Rua Qualquer",
                    "bairro": "Centro",
                    "cidade": "Recife",
                    "uf": "PE",
                    "NM_LOGRADOURO": "",
                    "NM_BAIRRO": "",
                    "NM_MUNICIPIO": "",
                    "NM_UF": "",
                },
            ]
        )

        result = self.processor._fill_missing_address_fields(df.copy())

        # Linha com CEP valido: deve preencher colunas equivalentes vazias.
        self.assertEqual(result.loc[0, "NM_LOGRADOURO"], "Avenida Paulista")
        self.assertEqual(result.loc[0, "NM_BAIRRO"], "Bela Vista")
        self.assertEqual(result.loc[0, "NM_MUNICIPIO"], "Sao Paulo")
        self.assertEqual(result.loc[0, "NM_UF"], "SP")

        # Linha com CEP invalido: nao deve preencher campos originais.
        self.assertEqual(result.loc[1, "NM_LOGRADOURO"], "")
        self.assertEqual(result.loc[1, "NM_BAIRRO"], "")
        self.assertEqual(result.loc[1, "NM_MUNICIPIO"], "")
        self.assertEqual(result.loc[1, "NM_UF"], "")

    def test_keep_existing_values(self):
        df = pd.DataFrame(
            [
                {
                    "cep_valido": True,
                    "logradouro": "Rua Nova",
                    "bairro": "Boa Viagem",
                    "cidade": "Recife",
                    "uf": "PE",
                    "NM_LOGRADOURO": "Rua Ja Informada",
                    "NM_BAIRRO": "Bairro Ja Informado",
                    "NM_MUNICIPIO": "Cidade Ja Informada",
                    "NM_UF": "RJ",
                }
            ]
        )

        result = self.processor._fill_missing_address_fields(df.copy())

        # Campos ja preenchidos devem ser preservados.
        self.assertEqual(result.loc[0, "NM_LOGRADOURO"], "Rua Ja Informada")
        self.assertEqual(result.loc[0, "NM_BAIRRO"], "Bairro Ja Informado")
        self.assertEqual(result.loc[0, "NM_MUNICIPIO"], "Cidade Ja Informada")
        self.assertEqual(result.loc[0, "NM_UF"], "RJ")


if __name__ == "__main__":
    unittest.main(verbosity=2)

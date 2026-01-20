# 🚀 Guia Rápido - API e Integração com n8n

## ⚡ 5 Passos Rápidos para Integrar com n8n

### 1️⃣ Iniciar o GeoGrafi

```bash
cd /workspaces/GeoGrafi_V2
python -m streamlit run app.py
```

Acesso em: `http://localhost:8501`

### 2️⃣ Criar Chave API

1. Acesse `http://localhost:8501/pages/api_keys`
2. Clique em **"➕ Criar Chave"**
3. Digite um nome (ex: `n8n-producao`)
4. Clique em **"🔐 Gerar Chave API"**
5. **Copie e salve a chave com segurança**

Exemplo de chave gerada:
```
geo_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

### 3️⃣ Configurar Credenciais no n8n

No n8n:
1. **Vá para:** Credentials → New Credential
2. **Selecione:** HTTP Headers Auth
3. **Adicione Header:**
   - Name: `Authorization`
   - Value: `Bearer geo_sua_chave_aqui`
4. **Clique em:** Save

### 4️⃣ Criar Workflow no n8n

```
[Trigger] → [HTTP Request] → [Process Dados] → [Salvar Resultado]
```

**Configuração do HTTP Request:**
- **Method:** POST
- **URL:** `http://localhost:8501/api/process`
- **Use Credentials:** Selecionar a credencial criada
- **Body Type:** Form Data
- **Parameters:**
  - Name: `file`
  - Value: Arquivo CSV

### 5️⃣ Testar Integração

Clique em **"Send"** no n8n. Resposta esperada:

```json
{
  "status": "success",
  "rows_processed": 1000,
  "stats": {
    "total_rows": 1000,
    "valid_ceps": 950,
    "invalid_ceps": 50,
    "coordinates_found": 920
  },
  "timestamp": "2024-01-20T10:30:00"
}
```

---

## 🔧 Endpoints da API

### Health Check
```bash
curl http://localhost:8501/api/health
```

### Processar CSV
```bash
curl -X POST http://localhost:8501/api/process \
  -H "Authorization: Bearer geo_sua_chave" \
  -F "file=@dados.csv"
```

### Validar CEP
```bash
curl "http://localhost:8501/api/validate-cep?cep=01310100" \
  -H "Authorization: Bearer geo_sua_chave"
```

### Listar Chaves
```bash
curl http://localhost:8501/api/keys/list \
  -H "Authorization: Bearer geo_sua_chave"
```

---

## 📚 Exemplo Completo com n8n

### Cenário: Enriquecer Base de Contatos

**Dados de Entrada (CSV):**
```csv
nome,cep
João Silva,01310100
Maria Santos,20040020
```

**Workflow:**
1. Upload do CSV
2. Enviar ao GeoGrafi via HTTP POST
3. Receber dados enriquecidos com coordenadas
4. Salvar em Google Sheets ou banco de dados

**Resposta do GeoGrafi:**
```json
{
  "status": "success",
  "rows_processed": 2,
  "data": [
    {
      "nome": "João Silva",
      "cep": "01310100",
      "latitude": "-23.5505",
      "longitude": "-46.6333",
      "municipio": "São Paulo"
    },
    {
      "nome": "Maria Santos",
      "cep": "20040020",
      "latitude": "-22.9068",
      "longitude": "-43.1729",
      "municipio": "Rio de Janeiro"
    }
  ]
}
```

---

## 🔐 Segurança

### ✅ Faça
- Armazene a chave em variável de ambiente no n8n
- Regenere chaves a cada 90 dias
- Use HTTPS em produção
- Monitore o uso de cada chave

### ❌ Não faça
- Compartilhe a chave em Slack/WhatsApp
- Commite a chave no Git
- Use a mesma chave em múltiplos serviços
- Deixe a chave em arquivos de texto

---

## 🐛 Troubleshooting

### Erro: "401 Unauthorized"
✅ Solução: Verifique se a chave está correta e ativa

### Erro: "Invalid CSV format"
✅ Solução: Certifique-se que o CSV tem as colunas esperadas

### Erro: "Connection refused"
✅ Solução: Inicie o GeoGrafi primeiro com `streamlit run app.py`

### Timeout na requisição
✅ Solução: Aumente o timeout em n8n ou reduz o tamanho do CSV

---

## 📈 Performance

- **Máximo por requisição:** 1000 linhas
- **Rate limit:** 60 requisições/minuto
- **Tempo processamento:** ~2-5s por 100 linhas
- **Recomendação:** Processe em chunks de 500-1000

---

## 📞 Suporte Rápido

**Documentação Completa:**
- [N8N_INTEGRATION.md](N8N_INTEGRATION.md)

**Gerar Nova Chave via API:**
```bash
curl "http://localhost:8501/api/keys/new?name=minha_chave" \
  -H "Authorization: Bearer geo_chave_existente"
```

**Informações da API:**
```bash
curl http://localhost:8501/api/integration-info
```

---

## 💡 Dicas

1. **Teste com cURL primeiro** antes de integrar com n8n
2. **Monitore o uso** na página "📋 Minhas Chaves"
3. **Use descritivas** para identificar qual chave usa para quê
4. **Mantenha um log** de qual n8n usa qual chave

---

Pronto para integrar? Comece no passo 1! 🎉

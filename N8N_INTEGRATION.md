# 🔗 Integração GeoGrafi com n8n

## Visão Geral

O GeoGrafi fornece uma API REST completa para integração com **n8n**, permitindo automação de processamento de dados geográficos diretamente em seus workflows.

## 📋 Índice

1. [Configuração Inicial](#configuração-inicial)
2. [Gerenciamento de Chaves API](#gerenciamento-de-chaves-api)
3. [Endpoints Disponíveis](#endpoints-disponíveis)
4. [Exemplos de n8n](#exemplos-de-n8n)
5. [Tratamento de Erros](#tratamento-de-erros)
6. [Segurança](#segurança)

---

## Configuração Inicial

### 1. Iniciar o GeoGrafi

```bash
cd /workspaces/GeoGrafi_V2
python -m streamlit run app.py
```

A aplicação estará disponível em:
- **Local:** `http://localhost:8501`
- **Rede:** `http://seu-ip:8501`

### 2. Acessar Gerenciamento de API

1. Navegue até `http://localhost:8501`
2. Clique em **"🔑 Chaves API"** no menu lateral
3. Ou acesse diretamente: `http://localhost:8501/pages/api_keys`

---

## Gerenciamento de Chaves API

### Criar uma Chave API

1. Acesse a aba **"➕ Criar Chave"**
2. Preencha o nome da chave (ex: `n8n-webhook`)
3. Adicione uma descrição opcional
4. Clique em **"🔐 Gerar Chave API"**
5. ⚠️ **Importante:** Salve a chave em local seguro

### Formato da Chave

```
geo_<64-caracteres-hexadecimais>
```

Exemplo:
```
geo_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

### Gerenciar Chaves Existentes

- **Listar:** Acesse a aba **"📋 Minhas Chaves"**
- **Desativar:** Selecione a chave e clique **"❌ Desativar"**
- **Deletar:** Selecione a chave e clique **"🗑️ Deletar"**

---

## Endpoints Disponíveis

### 🏥 Health Check

**GET** `/api/health`

Verifica se a API está operacional.

**Requisição:**
```bash
curl http://localhost:8501/api/health
```

**Resposta (200 OK):**
```json
{
  "status": "healthy",
  "service": "GeoGrafi",
  "version": "2.0"
}
```

### 📊 Informações da API

**GET** `/api/info`

Retorna informações sobre a API e recursos disponíveis.

**Requisição:**
```bash
curl http://localhost:8501/api/info
```

**Resposta:**
```json
{
  "service": "GeoGrafi",
  "version": "2.0",
  "features": [
    "CEP validation and enrichment",
    "Address coordinate generation",
    "Batch processing",
    "Data caching"
  ],
  "supported_formats": ["CSV", "JSON"],
  "rate_limits": {
    "requests_per_minute": 60,
    "batch_size_max": 1000
  }
}
```

### 🚀 Processar CSV

**POST** `/api/process`

Processa um arquivo CSV com enriquecimento de dados geográficos.

**Headers:**
```
Authorization: Bearer seu_api_key
Content-Type: multipart/form-data
```

**Parâmetros:**
- `file` (required): Arquivo CSV a processar

**Requisição cURL:**
```bash
curl -X POST http://localhost:8501/api/process \
  -H "Authorization: Bearer geo_seu_api_key" \
  -F "file=@dados.csv"
```

**Resposta (200 OK):**
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
  "data": [
    {
      "CD_CEP": "01310100",
      "NM_LOGRADOURO": "Avenida Paulista",
      "DS_LATITUDE": "-23.5505",
      "DS_LONGITUDE": "-46.6333"
    }
  ],
  "timestamp": "2024-01-20T10:30:00"
}
```

### ✅ Validar CEP

**GET** `/api/validate-cep`

Valida um CEP específico.

**Parâmetros Query:**
- `cep` (required): CEP para validar

**Headers:**
```
Authorization: Bearer seu_api_key
```

**Requisição:**
```bash
curl "http://localhost:8501/api/validate-cep?cep=01310100" \
  -H "Authorization: Bearer geo_seu_api_key"
```

**Resposta:**
```json
{
  "cep": "01310100",
  "valid": true,
  "timestamp": "2024-01-20T10:30:00"
}
```

### 📋 Listar Chaves API

**GET** `/api/keys/list`

Lista todas as chaves API configuradas (sem mostrar o valor completo).

**Headers:**
```
Authorization: Bearer seu_api_key
```

**Requisição:**
```bash
curl http://localhost:8501/api/keys/list \
  -H "Authorization: Bearer geo_seu_api_key"
```

### 🔑 Criar Nova Chave API

**GET** `/api/keys/new`

Cria uma nova chave API programaticamente.

**Parâmetros Query:**
- `name` (required): Nome da chave
- `description` (optional): Descrição

**Headers:**
```
Authorization: Bearer seu_api_key
```

**Requisição:**
```bash
curl "http://localhost:8501/api/keys/new?name=webhook-n8n&description=Integração n8n" \
  -H "Authorization: Bearer geo_seu_api_key"
```

---

## Exemplos de n8n

### Exemplo 1: Workflow Simples de Processamento

**Passo 1: Preparar os dados**
- Node: HTTP Request (GET)
- URL: Seu arquivo CSV ou origem de dados

**Passo 2: Chamar API do GeoGrafi**
- Node: HTTP Request (POST)
- Method: `POST`
- URL: `http://localhost:8501/api/process`
- Headers:
  ```
  Authorization: Bearer seu_api_key_aqui
  ```
- Body: Enviar o arquivo CSV obtido no passo anterior

**Passo 3: Processar Resultado**
- Node: Item Lists (para iterar sobre resultados)
- Node: Webhook (para notificar sistemas downstream)

### Exemplo 2: Validação em Batch

**Configuração:**
- Node: Loop de CEPs
- Para cada CEP:
  - Node: HTTP Request (GET)
  - URL: `http://localhost:8501/api/validate-cep?cep={{$node["Loop"].item.binary.data}}`
  - Headers: `Authorization: Bearer seu_api_key`

### Exemplo 3: Integração com Google Sheets

**Workflow:**
1. **Trigger:** Novo registro no Google Sheets
2. **Node HTTP:** Enviar dados ao GeoGrafi
3. **Node Google Sheets:** Escrever resultados em nova coluna
4. **Webhook:** Notificar conclusão

---

## Tratamento de Erros

### Códigos de Status HTTP

| Status | Significado | Solução |
|--------|------------|---------|
| 200 | OK | Sucesso |
| 400 | Bad Request | Arquivo inválido, formato incorreto |
| 401 | Unauthorized | Chave API inválida ou ausente |
| 429 | Too Many Requests | Rate limit excedido |
| 500 | Internal Server Error | Erro no servidor |

### Exemplos de Erro

**Erro 401 - Chave inválida:**
```json
{
  "status": "error",
  "message": "Invalid API key",
  "timestamp": "2024-01-20T10:30:00"
}
```

**Erro 400 - Arquivo inválido:**
```json
{
  "status": "error",
  "message": "Invalid CSV format",
  "timestamp": "2024-01-20T10:30:00"
}
```

### Em n8n - Tratamento de Erros

Adicione um node **Error Handling**:

```javascript
// Verificar status da resposta
if ({{ $node["HTTP_Request"].statusCode }} !== 200) {
  // Capturar erro
  throw new Error(`API Error: {{ $node["HTTP_Request"].body.message }}`);
}
```

---

## Segurança

### ✅ Práticas Recomendadas

1. **Armazenar Chaves Seguramente**
   ```javascript
   // Em n8n, use credentials
   {{ $node["HTTP_Request"].credentials.apiKey }}
   ```

2. **Usar Variáveis de Ambiente**
   ```bash
   export GEOGRAFI_API_KEY="seu_api_key"
   ```

3. **Regenerar Chaves Regularmente**
   - Crie uma chave nova
   - Atualize em todos os workflows
   - Desative a chave antiga

4. **Usar HTTPS em Produção**
   ```bash
   # Ao invés de http://
   https://seu-dominio.com/api/process
   ```

### ❌ Não Faça

- ❌ Compartilhe chaves em Slack/email
- ❌ Commite chaves no Git
- ❌ Use a mesma chave em múltiplos serviços
- ❌ Armazene em txt ou planilha

### Rotação de Chaves

**Passo a passo:**

1. Crie uma nova chave API
2. Atualize todos os workflows n8n
3. Teste as integrações
4. Desative a chave antiga
5. Delete a chave antiga após 30 dias

---

## Monitoramento

### Verificar Uso de Chaves

Na página **"📋 Minhas Chaves"**, você pode ver:
- Data de criação
- Último uso
- Número total de usos

### Logs da API

Os logs da API são salvos em:
```
/workspaces/GeoGrafi_V2/.config/api_keys.json
```

---

## Suporte

Para dúvidas sobre a integração:

1. Consulte a aba **"📚 Documentação"** na página de chaves API
2. Verifique os exemplos neste documento
3. Teste com cURL primeiro antes de integrar com n8n

---

## Changelog

### v2.0
- ✅ API REST completa
- ✅ Gerenciamento de chaves API
- ✅ Suporte a integração n8n
- ✅ Autenticação Bearer Token
- ✅ Validação de CEP individual
- ✅ Processamento em batch


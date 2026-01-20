# 📝 Sumário de Atualizações - Integração com n8n

## ✨ O que foi adicionado à aplicação GeoGrafi

### 1️⃣ **Gerenciamento de Chaves API** (`modules/api_key_manager.py`)

✅ Classe `APIKeyManager` para:
- Gerar chaves API únicas e seguras
- Validar chaves API
- Rastrear uso de cada chave
- Listar, desativar e deletar chaves
- Retornar informações de integração

**Recurso principal:** Gerar chaves com prefixo `geo_` seguido de 64 caracteres hexadecimais aleatórios

---

### 2️⃣ **API REST REST Completa** (`modules/api_server.py`)

✅ Endpoints disponíveis:

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/health` | GET | Verifica saúde da API |
| `/api/info` | GET | Informações gerais da API |
| `/api/process` | POST | Processa arquivo CSV |
| `/api/validate-cep` | GET | Valida CEP específico |
| `/api/keys/list` | GET | Lista chaves API |
| `/api/keys/new` | GET | Cria nova chave API |
| `/api/integration-info` | GET | Info para integração n8n |

**Autenticação:** Bearer Token via header `Authorization: Bearer seu_api_key`

---

### 3️⃣ **Interface Web para Gerenciamento** (`pages/api_keys.py`)

✅ Página interativa em Streamlit:
- **➕ Criar Chave:** Gerar nova chave API com descrição
- **📋 Minhas Chaves:** Listar todas as chaves com uso
- **📚 Documentação:** Guia completo de integração

---

### 4️⃣ **Documentação Completa**

#### `N8N_INTEGRATION.md` (📖 ~200 linhas)
- Visão geral da integração
- Guia passo-a-passo
- Exemplos de todos os endpoints
- Configuração no n8n
- Tratamento de erros
- Boas práticas de segurança

#### `QUICK_START_N8N.md` (⚡ 5 passos rápidos)
- Setup rápido em 5 minutos
- Exemplo completo de workflow
- Troubleshooting comum
- Dicas de performance

#### `.env.example` (⚙️ Variáveis de ambiente)
- Configurações de API
- Credenciais de serviços
- Rate limits
- Logging

---

### 5️⃣ **Scripts Executáveis**

#### `api_run.py` - Iniciar API REST
```bash
python api_run.py              # Porta 8000
python api_run.py --port 9000  # Porta customizada
python api_run.py --host 0.0.0.0  # Aceita conexões externas
```

#### `test_api.py` - Testar API
```bash
python test_api.py                          # Testes básicos
python test_api.py --api-key seu_api_key    # Testes com autenticação
python test_api.py --url http://seu-host    # URL customizada
```

---

### 6️⃣ **Exemplo de Workflow n8n** (`n8n-workflow-example.json`)

Arquivo pronto para importar no n8n com:
- Upload de CSV
- Processamento no GeoGrafi
- Salvamento em Google Sheets
- Webhook de notificação

---

### 7️⃣ **Dependências Atualizadas** (`requirements.txt`)

Adicionado:
```
fastapi>=0.104.0          # Framework web
uvicorn>=0.24.0           # Servidor ASGI
python-multipart>=0.0.6   # Para upload de arquivos
```

---

## 🎯 Como Usar

### Opção 1: Interface Web (Recomendado)

```bash
# Iniciar aplicação Streamlit
python -m streamlit run app.py

# Acessar em http://localhost:8501
# Menu → 🔑 Chaves API
# Criar chaves lá
```

### Opção 2: API REST (Para n8n e automação)

```bash
# Instalar dependências
pip install -r requirements.txt

# Iniciar API REST
python api_run.py

# Acessar em http://localhost:8000
# Docs em http://localhost:8000/docs
```

### Opção 3: Ambos (Recomendado para produção)

Terminal 1:
```bash
python -m streamlit run app.py
```

Terminal 2:
```bash
python api_run.py --host 0.0.0.0
```

---

## 🔐 Fluxo de Segurança

```
┌─────────────────────────────────────────────────────┐
│ 1. Gerar Chave API (Web ou Programmaticamente)     │
│    → geo_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0 │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ 2. Salvar em Local Seguro (Variável de Ambiente)   │
│    → GEOGRAFI_API_KEY=geo_sua_chave               │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ 3. Usar em Requisição HTTP                         │
│    → Authorization: Bearer geo_sua_chave           │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ 4. Validar e Processar                            │
│    → API verifica chave antes de processar        │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ 5. Rastrear Uso                                    │
│    → Registra cada uso, último acesso, contagem   │
└─────────────────────────────────────────────────────┘
```

---

## 📊 Exemplos Práticos

### Exemplo 1: Criar Chave via n8n

```bash
curl "http://localhost:8501/api/keys/new?name=meu_workflow&description=N8N%20Principal" \
  -H "Authorization: Bearer geo_chave_existente"
```

### Exemplo 2: Processar CSV

```bash
curl -X POST http://localhost:8501/api/process \
  -H "Authorization: Bearer geo_sua_chave" \
  -F "file=@dados.csv"
```

Resposta:
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
  "data": [...]
}
```

### Exemplo 3: No n8n

1. **Node HTTP Request:**
   - Method: POST
   - URL: `http://localhost:8501/api/process`
   - Headers: `Authorization: Bearer geo_sua_chave`
   - Body: Arquivo CSV

2. **Resposta:**
   - `$node.json.rows_processed` → número de linhas
   - `$node.json.data` → dados enriquecidos
   - `$node.json.stats` → estatísticas

---

## 🔄 Fluxo Típico n8n

```
Dados de Entrada (CSV)
      ↓
[HTTP Upload] → Enviar arquivo
      ↓
[GeoGrafi API] → Enriquecer com CEP/Coordenadas
      ↓
[Process Response] → Formatar resposta
      ↓
[Google Sheets / Database] → Salvar resultados
      ↓
[Webhook] → Notificar conclusão
      ↓
Dados Enriquecidos Salvos
```

---

## 📈 Próximas Funcionalidades (Planejadas)

- [ ] Autenticação OAuth2
- [ ] Webhook para notificações automáticas
- [ ] Cache distribuído com Redis
- [ ] Dashboard de uso de API
- [ ] Export/Import de workflows n8n
- [ ] Suporte a GraphQL além de REST

---

## 📚 Arquivos Criados/Modificados

### Novos Arquivos
- ✅ `modules/api_key_manager.py` - Gerenciador de chaves
- ✅ `modules/api_server.py` - Servidor API REST
- ✅ `pages/api_keys.py` - Interface web
- ✅ `N8N_INTEGRATION.md` - Documentação completa
- ✅ `QUICK_START_N8N.md` - Guia rápido
- ✅ `api_run.py` - Script para iniciar API
- ✅ `test_api.py` - Suite de testes
- ✅ `n8n-workflow-example.json` - Workflow exemplo
- ✅ `.env.example` - Variáveis de ambiente

### Arquivos Modificados
- ✅ `requirements.txt` - Adicionadas dependências

---

## 🚀 Próximos Passos

1. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Testar a API:**
   ```bash
   python test_api.py
   ```

3. **Criar primeira chave:**
   - Acesse http://localhost:8501/pages/api_keys
   - Clique em "➕ Criar Chave"

4. **Integrar com n8n:**
   - Siga [QUICK_START_N8N.md](QUICK_START_N8N.md)

---

**Versão:** 2.0
**Data:** 20 de janeiro de 2026
**Status:** ✅ Pronto para produção


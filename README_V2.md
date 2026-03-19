# GeoGrafi V2 📍

Sistema modular para processamento e enriquecimento de dados geográficos em arquivos CSV. Valida CEPs e adiciona coordenadas automaticamente usando APIs públicas.

## 🚀 Características

- **Validação de CEP**: Usa ViaCEP para validar e corrigir CEPs brasileiros
- **Geocoding**: Adiciona coordenadas (latitude/longitude) usando Nominatim (OpenStreetMap)
- **Processamento em Chunks**: Suporta arquivos grandes com baixo uso de memória
- **Cache Local**: Armazena resultados para acelerar processamentos futuros
- **Processamento Paralelo**: Usa múltiplas threads para maior velocidade
- **Modular**: Arquitetura limpa e reutilizável
- **Interface Web**: Interface Streamlit intuitiva
- **API Programática**: Use como biblioteca Python

## 📋 Requisitos

- Python 3.8 ou superior
- Conexão com a internet (para APIs de CEP e geocoding)

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/Dev-Bruno-Security/GeoGrafi_V2.git
cd GeoGrafi_V2
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## 💻 Uso

### Interface Web (Streamlit)

Execute a aplicação web:

```bash
streamlit run app.py
```

A interface web oferece:
- Upload de arquivos CSV
- Configurações ajustáveis (chunk size, workers, cache)
- Visualização de progresso em tempo real
- Download de resultados
- Estatísticas de processamento

### Uso Programático

```python
from modules import CSVProcessor

# Cria processador
processor = CSVProcessor(
    chunk_size=1000,
    max_workers=3,
    use_cache=True
)

# Processa arquivo
result = processor.process_file("dados.csv")

# Acessa resultados
df = result['dataframe']
stats = result['stats']

# Salva resultado
df.to_csv("resultado.csv", index=False)
```

### Exemplos

Execute exemplos interativos:

```bash
python exemplos.py
```

Os exemplos incluem:
1. Leitura de CSV
2. Validação de CEP
3. Geocoding
4. Processamento completo
5. Utilitários
6. Leitura em chunks

## 📁 Estrutura do Projeto

```
GeoGrafi_V2/
├── modules/                    # Módulos principais
│   ├── __init__.py            # Exportações públicas
│   ├── cep_validator.py       # Validação de CEP (ViaCEP)
│   ├── geocoder.py            # Geocoding (Nominatim)
│   ├── csv_processor.py       # Processador principal
│   ├── csv_reader.py          # Leitura de CSV
│   ├── cache_manager.py       # Gerenciamento de cache
│   ├── config.py              # Configurações
│   ├── utils.py               # Utilitários
│   └── streamlit_components.py # Componentes UI
│
├── app.py                      # Interface Streamlit principal
├── exemplos.py                 # Exemplos de uso
├── test_csv_processor_unit.py   # Testes unitários do CSVProcessor
├── test_api_key_manager_unit.py # Testes unitários do APIKeyManager
├── requirements.txt            # Dependências
├── README.md                   # Este arquivo
└── GUIA_RAPIDO.md             # Guia rápido de uso

# Arquivos legados (mantidos para compatibilidade)
├── app_geo.py                  # Versão anterior do app
├── app_geo_simples.py          # Versão simplificada
├── csv_reader.py               # Leitor standalone
├── interface_visual.py         # Interface antiga
└── exemplo_uso.py              # Exemplos antigos
```

## 🎯 Formato de Dados

### Colunas de Entrada Esperadas

| Coluna | Descrição | Obrigatório |
|--------|-----------|-------------|
| `CD_CEP` | Código do CEP | Não* |
| `NM_LOGRADOURO` | Nome do logradouro | Não* |
| `NM_BAIRRO` | Nome do bairro | Não |
| `NM_MUNICIPIO` | Nome do município | Sim |
| `NM_UF` | Sigla da UF | Sim |
| `DS_LATITUDE` | Latitude (preenchida se vazia) | Não |
| `DS_LONGITUDE` | Longitude (preenchida se vazia) | Não |

*Pelo menos CEP ou Logradouro+Município+UF devem estar presentes

### Colunas de Saída Adicionais

| Coluna | Descrição |
|--------|-----------|
| `CD_CEP_CORRETO` | CEP corrigido (se diferente) |
| `NM_LOGRADOURO_CORRETO` | Logradouro corrigido |
| `NM_BAIRRO_CORRETO` | Bairro corrigido |
| `NM_MUNICIPIO_CORRETO` | Município corrigido |
| `NM_UF_CORRETO` | UF corrigida |

## 🔧 Configuração

### Via Código

```python
from modules import update_config

update_config(
    chunk_size=2000,      # Linhas por chunk
    max_workers=5,        # Threads paralelas
    use_cache=True,       # Habilitar cache
    cache_db_path="cache.db"  # Caminho do cache
)
```

### Via Interface Web

Use a barra lateral da aplicação Streamlit para ajustar:
- Tamanho do chunk (100-5000 linhas)
- Número de workers (1-10 threads)
- Cache local (ativar/desativar)

## 📊 APIs Utilizadas

### ViaCEP
- **URL**: https://viacep.com.br
- **Uso**: Validação e busca de CEPs brasileiros
- **Limitação**: ~5 requisições/segundo (aplicamos rate limiting)

### Nominatim (OpenStreetMap)
- **URL**: https://nominatim.openstreetmap.org
- **Uso**: Geocoding (endereço → coordenadas)
- **Limitação**: 1 requisição/segundo (política de uso justo)

## ⚡ Performance

### Recomendações

| Tamanho do Arquivo | Chunk Size | Workers | Tempo Estimado* |
|-------------------|------------|---------|-----------------|
| < 1.000 linhas | 500 | 2 | 2-5 min |
| 1.000 - 10.000 | 1.000 | 3 | 10-30 min |
| 10.000 - 50.000 | 2.000 | 5 | 30-90 min |
| > 50.000 | 5.000 | 5-10 | 2-5 horas |

*Tempos variam conforme conexão e disponibilidade das APIs

### Otimizações

1. **Use Cache**: Reduz drasticamente o tempo em reprocessamentos
2. **Ajuste Chunk Size**: Mais memória = chunks maiores = mais rápido
3. **Workers Moderados**: Muitos workers podem causar rate limiting
4. **Conexão Estável**: Evita timeouts e reprocessamentos

## 🛠️ Desenvolvimento

### Estrutura Modular

O projeto foi refatorado para uma arquitetura modular:

- **Separação de Responsabilidades**: Cada módulo tem função específica
- **Reutilização**: Componentes podem ser usados independentemente
- **Testabilidade**: Módulos isolados facilitam testes
- **Manutenção**: Código organizado e documentado

### Importações Simplificadas

```python
# Importação direta dos módulos
from modules import (
    CSVProcessor,
    CEPValidator,
    Geocoder,
    CSVReader,
    CacheManager,
    get_config,
    update_config
)

# Utilitários
from modules import (
    clean_cep,
    format_cep,
    normalize_address,
    is_valid_coordinate
)
```

## 📝 Exemplos de Código

### Validar CEP

```python
from modules import CEPValidator

validator = CEPValidator()
resultado = validator.search_cep("50670-420")

if resultado:
    print(f"Cidade: {resultado['localidade']}")
    print(f"UF: {resultado['uf']}")
```

### Buscar Coordenadas

```python
from modules import Geocoder

geocoder = Geocoder()
coords = geocoder.search_by_address(
    street="Avenida Paulista",
    city="São Paulo",
    state="SP"
)

if coords:
    lat, lon = coords
    print(f"Latitude: {lat}, Longitude: {lon}")
```

### Processar CSV

```python
from modules import CSVProcessor

processor = CSVProcessor(chunk_size=1000)

def mostrar_progresso(progress):
    print(f"Progresso: {progress:.1f}%")

result = processor.process_file(
    "dados.csv",
    progress_callback=mostrar_progresso
)

print(f"CEPs corrigidos: {result['stats']['fixed_ceps']}")
print(f"Coordenadas encontradas: {result['stats']['found_coordinates']}")
```

### Ler CSV Grande

```python
from modules import CSVReader

reader = CSVReader("arquivo_grande.csv")

# Processar em chunks
for chunk in reader.read_in_chunks(chunk_size=5000):
    # Processar cada chunk
    print(f"Processando {len(chunk)} linhas...")
```

## ✅ Testes Unitários

Para executar os testes unitários consolidados em um único comando:

```bash
python -m unittest -v test_csv_processor_unit.py test_api_key_manager_unit.py
```

Esses testes cobrem regras de negócio locais e não dependem de APIs externas.

### Como interpretar o resultado

- Se aparecer `OK` no final, todos os testes passaram.
- Se aparecer `FAILED`, verifique o nome do teste exibido para identificar o módulo com problema.
- Mensagens de `warning` (como dependências de biblioteca) não significam falha de teste, apenas alerta de ambiente.

## 🐛 Solução de Problemas

### Erro de Encoding

```python
# Force encoding específico
reader = CSVReader("arquivo.csv", encoding="latin-1")
```

### Timeout de API

- Reduza o número de workers
- Aumente o rate limiting nas configurações
- Verifique sua conexão com a internet

### Memória Insuficiente

- Reduza o chunk_size
- Processe o arquivo em partes menores
- Feche outros programas

### Cache Corrompido

```bash
# Delete o arquivo de cache
rm cache.db
```

## 📄 Licença

Este projeto é de código aberto. Sinta-se livre para usar, modificar e distribuir.

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer fork do projeto
2. Criar uma branch para sua feature
3. Fazer commit das mudanças
4. Fazer push para a branch
5. Abrir um Pull Request

## 📧 Suporte

Para problemas, dúvidas ou sugestões:
- Abra uma issue no GitHub
- Entre em contato através do repositório

## 🔄 Changelog

### v2.0.0 (Atual)
- ✨ Refatoração completa para arquitetura modular
- ✨ Novo módulo de configuração centralizada
- ✨ Componentes Streamlit reutilizáveis
- ✨ Utilitários compartilhados
- ✨ Interface web melhorada
- ✨ Exemplos interativos
- 📚 Documentação expandida

### v1.0.0
- Versão inicial com funcionalidades básicas
- Validação de CEP
- Geocoding
- Processamento em chunks

---

**GeoGrafi v2.0** - Processamento Inteligente de Dados Geográficos 📍

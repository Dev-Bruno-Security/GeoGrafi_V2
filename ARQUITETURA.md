# Arquitetura Modular - GeoGrafi V2

## Visão Geral

O GeoGrafi V2 foi completamente refatorado para seguir uma arquitetura modular, facilitando manutenção, testes e reutilização de código.

## Estrutura de Módulos

```
modules/
├── __init__.py                 # Exportações públicas e versão
├── cep_validator.py           # Validação de CEP via ViaCEP
├── geocoder.py                # Geocoding via Nominatim
├── csv_processor.py           # Processador principal de CSV
├── csv_reader.py              # Leitor de CSV otimizado
├── cache_manager.py           # Gerenciamento de cache SQLite
├── config.py                  # Configurações centralizadas
├── utils.py                   # Utilitários compartilhados
└── streamlit_components.py    # Componentes UI reutilizáveis
```

## Descrição dos Módulos

### 1. `cep_validator.py`
**Responsabilidade**: Validação e busca de CEPs

**Classes**:
- `CEPValidator`: Valida e busca CEPs usando ViaCEP

**Principais Métodos**:
- `search_cep(cep)`: Busca informações de um CEP
- `validate_cep_format(cep)`: Valida formato do CEP
- `format_cep(cep)`: Formata CEP para padrão XXXXX-XXX

**Dependências**:
- `requests`: Para chamadas HTTP
- Rate limiting integrado

### 2. `geocoder.py`
**Responsabilidade**: Busca de coordenadas geográficas

**Classes**:
- `Geocoder`: Busca coordenadas usando Nominatim

**Principais Métodos**:
- `search_by_address(street, neighborhood, city, state)`: Busca coordenadas
- `search_by_cep(cep, city, state)`: Busca coordenadas usando CEP

**Dependências**:
- `requests`: Para chamadas HTTP
- Nominatim API (OpenStreetMap)

### 3. `csv_processor.py`
**Responsabilidade**: Processamento completo de arquivos CSV

**Classes**:
- `CSVProcessor`: Orquestra todo o processo de enriquecimento

**Principais Métodos**:
- `process_file(file_path, progress_callback)`: Processa arquivo completo
- Integra CEPValidator, Geocoder e CacheManager

**Dependências**:
- `cep_validator`
- `geocoder`
- `cache_manager`
- `pandas`

### 4. `csv_reader.py`
**Responsabilidade**: Leitura eficiente de CSV grandes

**Classes**:
- `CSVReader`: Lê CSV com detecção automática de encoding/delimitador
- `CSVAnalyzer`: Análise estatística de dados

**Principais Métodos**:
- `read_in_chunks(chunk_size)`: Lê arquivo em partes
- `read_sample(n_rows)`: Lê amostra do arquivo
- `get_file_info()`: Informações do arquivo
- `analyze_data(sample_size)`: Análise estatística

**Dependências**:
- `pandas`
- `chardet`: Detecção de encoding

### 5. `cache_manager.py`
**Responsabilidade**: Cache local de resultados

**Classes**:
- `CacheManager`: Gerencia cache SQLite

**Principais Métodos**:
- `save_cep(cep, data)`: Salva CEP no cache
- `get_cep(cep)`: Recupera CEP do cache
- `save_coordinates(address, lat, lon)`: Salva coordenadas
- `get_coordinates(address)`: Recupera coordenadas

**Dependências**:
- `sqlite3`: Banco de dados

### 6. `config.py`
**Responsabilidade**: Configurações centralizadas

**Classes**:
- `APIConfig`: Configurações de APIs
- `ProcessingConfig`: Configurações de processamento
- `ColumnMapping`: Mapeamento de colunas
- `AppConfig`: Configuração global

**Funções**:
- `get_config()`: Retorna configuração atual
- `update_config(**kwargs)`: Atualiza configurações

### 7. `utils.py`
**Responsabilidade**: Utilitários compartilhados

**Funções**:
- `clean_cep(cep)`: Limpa e valida CEP
- `format_cep(cep)`: Formata CEP
- `normalize_text(text)`: Normaliza texto
- `normalize_address(text)`: Normaliza endereço
- `is_valid_coordinate(lat, lon)`: Valida coordenadas
- `format_file_size(size_bytes)`: Formata tamanho de arquivo
- `build_address_query(...)`: Constrói query de endereço
- `get_address_hash(address)`: Gera hash para cache

### 8. `streamlit_components.py`
**Responsabilidade**: Componentes UI reutilizáveis

**Funções**:
- `apply_custom_css()`: Aplica estilos CSS
- `show_success_message(msg)`: Mensagem de sucesso
- `show_error_message(msg)`: Mensagem de erro
- `display_metrics(stats)`: Exibe métricas
- `display_dataframe_preview(df)`: Prévia de DataFrame
- `create_progress_tracker(total)`: Tracker de progresso
- `create_download_button(data)`: Botão de download

## Princípios da Arquitetura

### 1. Separação de Responsabilidades (SRP)
Cada módulo tem uma única responsabilidade bem definida:
- `cep_validator`: Apenas validação de CEP
- `geocoder`: Apenas geocoding
- `csv_processor`: Orquestração do processo
- Etc.

### 2. Baixo Acoplamento
Módulos são independentes e podem ser usados separadamente:

```python
# Usar apenas validador de CEP
from modules import CEPValidator
validator = CEPValidator()

# Usar apenas geocoder
from modules import Geocoder
geocoder = Geocoder()

# Usar apenas leitor CSV
from modules import CSVReader
reader = CSVReader("arquivo.csv")
```

### 3. Alta Coesão
Funcionalidades relacionadas estão agrupadas no mesmo módulo.

### 4. Inversão de Dependência
Módulos de alto nível (`csv_processor`) dependem de abstrações, não de implementações concretas.

### 5. Configuração Centralizada
Todas as configurações em um único lugar (`config.py`), facilitando ajustes.

## Fluxo de Dados

```
[CSV Input] 
    ↓
[CSVReader] → Detecta encoding/delimitador
    ↓
[CSVProcessor] → Orquestra processamento
    ├─→ [CacheManager] → Verifica cache
    ├─→ [CEPValidator] → Valida/busca CEP
    ├─→ [Geocoder] → Busca coordenadas
    └─→ [CacheManager] → Salva resultados
    ↓
[CSV Output]
```

## Benefícios da Modularização

### 1. Manutenibilidade
- Código organizado e fácil de localizar
- Mudanças isoladas em módulos específicos
- Menor risco de quebrar outras partes

### 2. Testabilidade
- Cada módulo pode ser testado isoladamente
- Mock de dependências facilitado
- Testes mais rápidos e focados

### 3. Reutilização
- Módulos podem ser usados em outros projetos
- Componentes independentes
- API clara e bem documentada

### 4. Escalabilidade
- Fácil adicionar novos módulos
- Novos geocoders/validadores podem ser plugados
- Padrão extensível

### 5. Legibilidade
- Código mais limpo e organizado
- Imports claros e intencionais
- Documentação por módulo

## Exemplos de Uso

### Uso Individual de Módulos

```python
# Apenas validar CEPs
from modules import CEPValidator

validator = CEPValidator()
info = validator.search_cep("50670-420")
print(info['localidade'])  # Recife
```

```python
# Apenas geocoding
from modules import Geocoder

geocoder = Geocoder()
coords = geocoder.search_by_address("Av Paulista", "", "São Paulo", "SP")
print(coords)  # (-23.5619, -46.6556)
```

```python
# Apenas ler CSV
from modules import CSVReader

reader = CSVReader("dados.csv")
for chunk in reader.read_in_chunks(1000):
    print(f"Processando {len(chunk)} linhas")
```

### Uso Integrado

```python
from modules import CSVProcessor, get_config, update_config

# Configura
update_config(chunk_size=2000, max_workers=5)

# Processa
processor = CSVProcessor()
result = processor.process_file("dados.csv")

# Acessa resultados
df = result['dataframe']
stats = result['stats']
```

## Extensibilidade

### Adicionar Novo Geocoder

```python
# modules/new_geocoder.py
class NewGeocoder:
    def search_by_address(self, street, city, state):
        # Implementação usando nova API
        pass
```

### Adicionar Nova Fonte de CEP

```python
# modules/new_cep_provider.py
class NewCEPProvider:
    def search_cep(self, cep):
        # Implementação usando nova API
        pass
```

### Adicionar Novo Processador

```python
# Usa componentes existentes
from modules import CEPValidator, Geocoder, CacheManager

class CustomProcessor:
    def __init__(self):
        self.cep = CEPValidator()
        self.geo = Geocoder()
        self.cache = CacheManager()
    
    def custom_process(self, data):
        # Lógica customizada
        pass
```

## Testes

Execute os testes para verificar integridade:

```bash
python tests.py
```

Testes cobrem:
- ✅ Estrutura de arquivos
- ✅ Importações
- ✅ Utilitários
- ✅ Configurações
- ✅ CEP Validator
- ✅ Cache Manager
- ✅ CSV Reader

## Migração de Código Legado

Código antigo ainda funciona (arquivos `app_geo.py`, `csv_reader.py` na raiz), mas novos desenvolvimentos devem usar a estrutura modular:

### Antes (Legado)
```python
# Código duplicado em cada arquivo
class CEPValidator:
    # Implementação...

class Geocoder:
    # Implementação...
```

### Depois (Modular)
```python
# Import simples, sem duplicação
from modules import CEPValidator, Geocoder
```

## Documentação Adicional

- **README_V2.md**: Documentação completa do projeto
- **GUIA_RAPIDO_V2.md**: Guia rápido de uso
- **exemplos.py**: Exemplos práticos interativos

## Versão

**GeoGrafi v2.0.0** - Arquitetura Modular

---

*Documento de Arquitetura - GeoGrafi V2*

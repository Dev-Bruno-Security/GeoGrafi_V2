# Leitor de Arquivos CSV Grandes

Aplicação Python para leitura eficiente de arquivos CSV muito grandes (até 1,5GB+) sem perda de dados. Suporta arquivos OpenOffice.org 1.1 (.csv).

## 🚀 Características

- **Leitura em chunks**: Processa arquivos grandes em pedaços, economizando memória
- **Detecção automática de encoding**: Identifica automaticamente a codificação do arquivo
- **Detecção automática de delimitador**: Identifica vírgulas, ponto-e-vírgula, tabs, etc.
- **Análise de dados**: Estatísticas descritivas, valores faltantes, tipos de dados
- **Filtragem de dados**: Filtra e exporta apenas os dados necessários
- **Sem perda de dados**: Tratamento robusto de erros e avisos sobre linhas problemáticas
- **Interface interativa**: Menu fácil de usar no terminal

## 📋 Requisitos

- Python 3.7 ou superior
- pandas
- chardet

## 🔧 Instalação

1. Clone ou baixe este repositório

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## 💻 Uso Básico

### Modo Interativo

Execute o programa principal:

```bash
python csv_reader.py
```

O programa irá:
1. Solicitar o caminho do arquivo CSV
2. Detectar automaticamente encoding e delimitador
3. Mostrar informações do arquivo
4. Apresentar um menu com opções interativas

## ✅ Testes Unitários (GeoGrafi V2)

Para executar os testes unitários consolidados em um unico comando:

```bash
python -m unittest -v test_csv_processor_unit.py test_api_key_manager_unit.py
```

Esses testes cobrem regras de negocio locais e nao dependem de APIs externas.

### Como interpretar o resultado

- Se aparecer `OK` no final, todos os testes passaram.
- Se aparecer `FAILED`, verifique o nome do teste exibido para identificar o modulo com problema.
- Mensagens de `warning` (como dependencias de biblioteca) nao significam falha de teste, apenas alerta de ambiente.

### Modo Programático

```python
from csv_reader import CSVReader, CSVAnalyzer

# Criar instância do leitor
reader = CSVReader("seu_arquivo.csv")

# Ver informações do arquivo
info = reader.get_file_info()
print(info)

# Ler amostra dos dados
sample = reader.read_sample(100)
print(sample)

# Processar arquivo em chunks
for chunk in reader.read_in_chunks(chunk_size=10000):
    # Processar cada chunk
    print(f"Processando {len(chunk)} linhas")
    # Seu processamento aqui...

# Analisar dados
analysis = reader.analyze_data(sample_size=50000)
print(analysis)

# Contar linhas
total_rows = reader.count_rows()
print(f"Total de linhas: {total_rows:,}")
```

## 📊 Exemplos de Uso

### Exemplo 1: Ler arquivo grande

```python
from csv_reader import CSVReader

# Criar leitor
reader = CSVReader("dados_ibge.csv")

# Processar em chunks de 5000 linhas
for i, chunk in enumerate(reader.read_in_chunks(5000), 1):
    print(f"Chunk {i}: {len(chunk)} linhas")
    # Processar dados...
```

### Exemplo 2: Filtrar e exportar dados

```python
from csv_reader import CSVReader, CSVAnalyzer

reader = CSVReader("dados_completos.csv")

# Definir condição de filtro
def filtro(df):
    # Exemplo: filtrar apenas linhas onde População > 100000
    return df['População'] > 100000

# Filtrar e salvar
CSVAnalyzer.filter_data(
    reader,
    condition=filtro,
    output_path="dados_filtrados.csv",
    chunk_size=10000
)
```

### Exemplo 3: Calcular estatísticas

```python
from csv_reader import CSVReader, CSVAnalyzer

reader = CSVReader("dados.csv")

# Calcular estatísticas das colunas numéricas
stats = CSVAnalyzer.get_statistics(
    reader,
    columns=['População', 'PIB', 'Área'],
    chunk_size=10000
)

print(stats)
```

### Exemplo 4: Converter e processar

```python
from csv_reader import CSVReader

reader = CSVReader("arquivo_original.csv")

# Função de processamento personalizada
def processar_chunk(chunk):
    # Remover colunas desnecessárias
    chunk = chunk.drop(['coluna_indesejada'], axis=1)
    
    # Criar nova coluna
    chunk['nova_coluna'] = chunk['coluna_a'] + chunk['coluna_b']
    
    # Filtrar valores
    chunk = chunk[chunk['valor'] > 0]
    
    return chunk

# Processar e salvar
reader.process_and_save(
    output_path="arquivo_processado.csv",
    chunk_size=10000,
    process_func=processar_chunk
)
```

## 🎯 Funcionalidades Principais

### CSVReader

#### Métodos principais:

- `get_file_info()`: Informações sobre o arquivo (tamanho, encoding, delimitador)
- `read_in_chunks(chunk_size)`: Itera sobre o arquivo em chunks
- `read_sample(n_rows)`: Lê apenas as primeiras N linhas
- `count_rows()`: Conta o total de linhas
- `get_column_names()`: Retorna lista de colunas
- `analyze_data(sample_size)`: Análise estatística de uma amostra
- `process_and_save()`: Processa e salva em novo arquivo

### CSVAnalyzer

#### Métodos principais:

- `get_statistics()`: Calcula estatísticas descritivas
- `filter_data()`: Filtra dados baseado em condição

## 🛡️ Tratamento de Erros

A aplicação inclui:
- Detecção automática de encoding para evitar erros de leitura
- Avisos sobre linhas problemáticas (`on_bad_lines='warn'`)
- Tratamento de exceções com mensagens claras
- Validação de existência do arquivo

## ⚡ Otimização de Memória

Para arquivos muito grandes:

1. **Ajuste o chunk_size**: Menor = menos memória, mais lento
   - Arquivos < 500MB: chunk_size=50000
   - Arquivos 500MB-1GB: chunk_size=20000
   - Arquivos > 1GB: chunk_size=10000

2. **Use apenas colunas necessárias**:
```python
for chunk in reader.read_in_chunks(10000):
    chunk = chunk[['coluna1', 'coluna2']]  # Apenas colunas necessárias
    # Processar...
```

3. **Delete chunks após processamento**:
```python
for chunk in reader.read_in_chunks(10000):
    # Processar chunk
    del chunk  # Libera memória
```

## 📝 Notas Importantes

- O arquivo original **nunca é modificado**
- Todas as operações de escrita criam novos arquivos
- A detecção de encoding é feita nos primeiros 100KB do arquivo
- O programa assume que a primeira linha contém cabeçalhos

## 🐛 Solução de Problemas

### Erro de encoding
Se o encoding não for detectado corretamente, você pode especificar manualmente:
```python
reader = CSVReader("arquivo.csv")
reader.encoding = "latin-1"  # ou "iso-8859-1", "utf-16", etc.
```

### Erro de delimitador
Se o delimitador não for detectado corretamente:
```python
reader = CSVReader("arquivo.csv")
reader.delimiter = ";"  # ou "\t", "|", etc.
```

### Arquivo muito lento
Reduza o chunk_size:
```python
for chunk in reader.read_in_chunks(5000):  # Chunks menores
    # Processar...
```

## 📧 Suporte

Para problemas ou dúvidas, verifique:
1. Se o arquivo existe e o caminho está correto
2. Se você tem permissões de leitura no arquivo
3. Se há espaço em disco suficiente para operações de exportação
4. Se todas as dependências estão instaladas

## 🔄 Atualizações Futuras

- [ ] Suporte para formatos Excel (.xlsx, .xls)
- [ ] Interface gráfica (GUI)
- [ ] Exportação para banco de dados
- [ ] Visualização de gráficos
- [ ] Suporte para arquivos comprimidos (.zip, .gz)

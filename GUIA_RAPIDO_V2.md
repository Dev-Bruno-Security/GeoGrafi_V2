# Guia Rápido - GeoGrafi V2 📍

## Início Rápido (5 minutos)

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Rodar Interface Web
```bash
streamlit run app.py
```

### 3. Upload e Processar
1. Arraste seu CSV para o upload
2. Ajuste configurações na barra lateral (opcional)
3. Clique em "🚀 Processar Arquivo"
4. Aguarde o processamento
5. Baixe o resultado

## Uso Programático (3 linhas)

```python
from modules import CSVProcessor

processor = CSVProcessor()
result = processor.process_file("seu_arquivo.csv")
result['dataframe'].to_csv("resultado.csv", index=False)
```

## Configurações Essenciais

### Para Arquivos Pequenos (< 1.000 linhas)
```python
processor = CSVProcessor(
    chunk_size=500,
    max_workers=2
)
```

### Para Arquivos Médios (1.000 - 10.000 linhas)
```python
processor = CSVProcessor(
    chunk_size=1000,
    max_workers=3
)
```

### Para Arquivos Grandes (> 10.000 linhas)
```python
processor = CSVProcessor(
    chunk_size=2000,
    max_workers=5
)
```

## Formato de Arquivo

### Mínimo Necessário
Seu CSV precisa ter pelo menos:
- `NM_MUNICIPIO` (município)
- `NM_UF` (estado)
- `CD_CEP` OU `NM_LOGRADOURO` (CEP ou endereço)

### Exemplo de CSV Válido
```csv
CD_CEP,NM_LOGRADOURO,NM_MUNICIPIO,NM_UF
50670-420,Av. Agamenon Magalhães,Recife,PE
01310-100,Av. Paulista,São Paulo,SP
```

## Exemplos Rápidos

### Validar um CEP
```python
from modules import CEPValidator

validator = CEPValidator()
info = validator.search_cep("50670-420")
print(info['localidade'])  # Recife
```

### Buscar Coordenadas
```python
from modules import Geocoder

geocoder = Geocoder()
coords = geocoder.search_by_address(
    "Avenida Paulista",
    city="São Paulo",
    state="SP"
)
print(coords)  # (-23.5619, -46.6556)
```

### Processar com Progresso
```python
from modules import CSVProcessor

processor = CSVProcessor()

def mostrar_progresso(pct):
    print(f"{pct:.1f}% concluído")

result = processor.process_file(
    "dados.csv",
    progress_callback=mostrar_progresso
)
```

### Ler CSV Grande em Chunks
```python
from modules import CSVReader

reader = CSVReader("arquivo_grande.csv")

for chunk in reader.read_in_chunks(chunk_size=1000):
    print(f"Processando {len(chunk)} linhas")
    # Faça algo com cada chunk
```

## Estatísticas de Resultado

```python
result = processor.process_file("dados.csv")

stats = result['stats']
print(f"Total: {stats['total_rows']} linhas")
print(f"CEPs corrigidos: {stats['fixed_ceps']}")
print(f"Coordenadas: {stats['found_coordinates']}")
print(f"Erros: {len(stats['errors'])}")
```

## Cache

### Usar Cache (Recomendado)
```python
processor = CSVProcessor(use_cache=True)
```

### Limpar Cache
```bash
rm cache.db
```

### Cache Customizado
```python
processor = CSVProcessor(
    use_cache=True,
    cache_db="meu_cache.db"
)
```

## Solução Rápida de Problemas

### ❌ Arquivo não encontrado
- Verifique o caminho do arquivo
- Use caminho absoluto: `/home/user/arquivo.csv`

### ❌ Erro de encoding
```python
reader = CSVReader("arquivo.csv", encoding="latin-1")
```

### ❌ Muito lento
- Habilite o cache
- Aumente o chunk_size
- Reduza o max_workers (evita rate limit)

### ❌ Erro de memória
- Reduza o chunk_size
- Processe em partes menores

### ❌ Timeout de API
- Verifique conexão internet
- Reduza max_workers
- Aguarde alguns segundos e tente novamente

## Importações Úteis

```python
# Principais
from modules import (
    CSVProcessor,      # Processador completo
    CEPValidator,      # Validar CEP
    Geocoder,          # Buscar coordenadas
    CSVReader,         # Ler CSV grande
    CacheManager,      # Gerenciar cache
)

# Configuração
from modules import (
    get_config,        # Obter config atual
    update_config,     # Atualizar config
)

# Utilitários
from modules import (
    clean_cep,         # Limpar CEP
    format_cep,        # Formatar CEP
    normalize_address, # Normalizar endereço
)
```

## Performance

| Linhas | Chunk | Workers | Tempo* |
|--------|-------|---------|--------|
| 100 | 500 | 2 | ~1 min |
| 1.000 | 1.000 | 3 | ~5 min |
| 10.000 | 2.000 | 5 | ~30 min |
| 50.000 | 5.000 | 5 | ~2 horas |

*Tempos aproximados com cache vazio

## Executar Exemplos

```bash
python exemplos.py
```

Escolha um exemplo:
1. Leitura de CSV
2. Validação de CEP
3. Geocoding
4. Processamento Completo
5. Utilitários
6. Leitura em Chunks

## Interface Web - Atalhos

1. **Upload rápido**: Arraste o arquivo para a página
2. **Configurar**: Barra lateral esquerda
3. **Processar**: Botão azul grande
4. **Download**: Após processar, rolar até o final
5. **Ver erros**: Expandir seção de estatísticas

## Módulos Individuais

### Apenas Validar CEPs
```python
from modules import CEPValidator

validator = CEPValidator()

ceps = ["50670-420", "01310-100"]
for cep in ceps:
    info = validator.search_cep(cep)
    print(f"{cep}: {info['localidade'] if info else 'Inválido'}")
```

### Apenas Geocoding
```python
from modules import Geocoder

geocoder = Geocoder()

enderecos = [
    ("Av. Paulista", "São Paulo", "SP"),
    ("Praça da Sé", "São Paulo", "SP"),
]

for rua, cidade, uf in enderecos:
    coords = geocoder.search_by_address(rua, "", cidade, uf)
    print(f"{rua}: {coords}")
```

### Apenas Ler CSV
```python
from modules import CSVReader

reader = CSVReader("dados.csv")

# Info do arquivo
print(reader.get_file_info())

# Primeiras linhas
print(reader.read_sample(10))

# Todas as colunas
print(reader.get_column_names())
```

## Dicas Pro 💡

1. **Cache é seu amigo**: Primeira execução demora, próximas são rápidas
2. **Chunk size ideal**: Metade da sua RAM disponível ÷ tamanho médio da linha
3. **Workers**: 3-5 é o ideal. Mais pode causar rate limiting
4. **Teste pequeno primeiro**: Processe 100 linhas antes do arquivo completo
5. **Internet estável**: Use cabo ao invés de WiFi para arquivos grandes

## Checklist Antes de Processar ✅

- [ ] Arquivo CSV está no formato correto
- [ ] Colunas obrigatórias presentes
- [ ] Encoding compatível (UTF-8 ou Latin-1)
- [ ] Internet funcionando
- [ ] Espaço em disco disponível
- [ ] Testar com amostra pequena primeiro

## Ajuda Rápida

- **Documentação completa**: Veja `README_V2.md`
- **Exemplos**: Execute `python exemplos.py`
- **Interface web**: `streamlit run app.py`
- **Issues**: Abra no GitHub

---

**Pronto para começar!** 🚀

Execute `streamlit run app.py` e comece a processar seus dados!

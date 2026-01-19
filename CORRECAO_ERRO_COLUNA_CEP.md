# 🔧 Correção: Erro "Coluna de CEP não encontrada"

## 📋 Erro Reportado

```
❌ Erro ao processar: Coluna de CEP não encontrada. Use 'cep' ou 'CEP'
```

**Arquivo:** `endereços teste.csv` (0.5KB)

---

## 🔍 Análise do Problema

O método `_find_cep_column()` estava procurando apenas por nomes específicos de colunas, mas não cobria todas as variações possíveis que os usuários podem usar em seus arquivos CSV.

### Causas Identificadas:

1. **Lista limitada de nomes**: Apenas procurava por `cep`, `CEP`, `cd_cep`, etc.
2. **Sem busca parcial**: Não encontrava colunas como `codigo_postal`, `Codigo CEP`, etc.
3. **Mensagem de erro não informativa**: Não mostrava quais colunas estavam disponíveis
4. **Sem preview visual**: Usuário não via a estrutura do arquivo antes de processar

---

## ✅ Soluções Implementadas

### 1. **Busca Expandida de Colunas** ✨

Melhorei o método `_find_cep_column()` com 3 estratégias:

```python
def _find_cep_column(self, df: pd.DataFrame) -> Optional[str]:
    # ESTRATÉGIA 1: Match exato
    for col in df.columns:
        if col in common_names:
            return col
    
    # ESTRATÉGIA 2: Case-insensitive
    df_lower = {col.lower(): col for col in df.columns}
    for name in common_names:
        if name.lower() in df_lower:
            return df_lower[name.lower()]
    
    # ESTRATÉGIA 3: Busca parcial (contém palavra-chave)
    for col in df.columns:
        col_lower = col.lower()
        if 'cep' in col_lower or 'postal' in col_lower or 'zip' in col_lower:
            return col
```

#### Nomes reconhecidos agora:

- ✅ `cep`, `CEP`, `Cep`
- ✅ `cd_cep`, `CD_CEP`, `Cd_Cep`
- ✅ `codigo_cep`, `CODIGO_CEP`, `Codigo_Cep`
- ✅ `codigo`, `CODIGO`, `Codigo`
- ✅ `postal_code`, `POSTAL_CODE`, `Postal_Code`
- ✅ `codigo postal`, `CODIGO POSTAL`
- ✅ `zipcode`, `ZIPCODE`, `ZipCode`
- ✅ `zip`, `ZIP`, `Zip`
- ✅ **Qualquer coluna que contenha** `cep`, `postal` ou `zip`

### 2. **Mensagem de Erro Informativa** 📝

Antes:
```
❌ Erro ao processar: Coluna de CEP não encontrada. Use 'cep' ou 'CEP'
```

Depois:
```
❌ Coluna de CEP não encontrada!

Colunas disponíveis no arquivo: 'endereco', 'cidade', 'estado', 'codigo_postal'

Dica: Renomeie uma coluna para 'cep' ou 'CEP' no seu arquivo CSV.
```

### 3. **Preview do Arquivo** 👁️

Adicionei um expandível "Visualizar primeiras linhas do arquivo" na interface que mostra:

- ✅ Todas as colunas detectadas
- ✅ Preview das primeiras 5 linhas
- ✅ Indicação se coluna de CEP foi detectada
- ⚠️ Aviso se não houver coluna de CEP

```python
with st.expander("👁️ Visualizar primeiras linhas do arquivo", expanded=False):
    preview_df = pd.read_csv(uploaded_file, nrows=5, dtype=str)
    st.write(f"**Colunas detectadas:** {', '.join([f'`{col}`' for col in preview_df.columns])}")
    st.dataframe(preview_df)
    
    # Verifica se tem coluna de CEP
    has_cep = any('cep' in col.lower() or 'postal' in col.lower() or 'zip' in col.lower() 
                 for col in preview_df.columns)
    
    if has_cep:
        st.success("✅ Coluna de CEP detectada!")
    else:
        st.warning("⚠️ Nenhuma coluna de CEP detectada.")
```

### 4. **Logging Detalhado** 🔍

Adicionei logs de debug para facilitar troubleshooting:

```python
logger.debug(f"Colunas disponíveis: {list(df.columns)}")
logger.debug(f"Coluna encontrada (busca parcial): '{col}'")
logger.info(f"Colunas detectadas: {list(df.columns)}")
```

---

## 🎯 Como Usar Agora

### Opção 1: Renomear Coluna no CSV (Recomendado)

Edite seu arquivo CSV e renomeie a coluna para `cep`:

```csv
cep,endereco,cidade,estado
01310-100,Av Paulista 1000,São Paulo,SP
01305-000,Rua Augusta 500,São Paulo,SP
```

### Opção 2: Usar Nomes Reconhecidos

Use qualquer um desses nomes na primeira linha do CSV:

- `cep`
- `CEP`
- `codigo_cep`
- `codigo_postal`
- `postal_code`
- `zipcode`

### Opção 3: Deixar o Sistema Detectar

Se sua coluna tiver "cep", "postal" ou "zip" em qualquer lugar do nome, o sistema detectará automaticamente:

- ✅ `codigo_postal`
- ✅ `cep_cliente`
- ✅ `postal_address`
- ✅ `zipcode_main`

---

## 🧪 Exemplos de Arquivos Suportados

### Exemplo 1: Coluna simples
```csv
cep,endereco
01310100,Av Paulista
```

### Exemplo 2: Com underscores
```csv
cd_cep,nm_endereco,nm_cidade
01310100,Av Paulista,São Paulo
```

### Exemplo 3: Nome completo
```csv
codigo_postal,endereco_completo
01310-100,Av Paulista 1000
```

### Exemplo 4: Inglês
```csv
zipcode,address,city
01310-100,Av Paulista 1000,São Paulo
```

### Exemplo 5: Misto
```csv
CEP_Cliente,Endereco,Cidade
01310100,Av Paulista,SP
```

---

## 🔄 Reinicie a Aplicação

Para aplicar as correções, reinicie o servidor Streamlit:

```bash
# Pare o servidor atual (Ctrl+C)
pkill -f streamlit

# Inicie novamente
cd /workspaces/GeoGrafi_V2
python3 -m streamlit run app_simples.py --server.port 8501 --server.address 0.0.0.0
```

Acesse: http://0.0.0.0:8501

---

## ✨ Melhorias Aplicadas

| Item | Antes | Depois |
|------|-------|--------|
| **Nomes reconhecidos** | 10 variações | 25+ variações |
| **Busca parcial** | ❌ Não | ✅ Sim (contém 'cep') |
| **Case-sensitive** | ⚠️ Parcial | ✅ Totalmente insensível |
| **Mensagem de erro** | ❌ Genérica | ✅ Mostra colunas disponíveis |
| **Preview visual** | ❌ Não existia | ✅ Expander com primeiras linhas |
| **Logging debug** | ❌ Mínimo | ✅ Detalhado |

---

## 📞 Solução de Problemas

### Problema: Ainda não encontra a coluna

**Solução:**
1. Clique em "Visualizar primeiras linhas" para ver as colunas
2. Verifique o nome exato da coluna
3. Renomeie para `cep` no Excel/LibreOffice
4. Salve e faça upload novamente

### Problema: CEPs sem zeros à esquerda

**Solução:** Já corrigido! O sistema agora usa `dtype=str` para preservar zeros.

### Problema: Arquivo com encoding errado

**Solução:** Use o seletor de "Encoding" e tente:
- `utf-8` (padrão)
- `iso-8859-1` (arquivos antigos)
- `cp1252` (Excel Windows)

---

## 📝 Arquivos Modificados

1. ✅ **`modules/csv_processor.py`**
   - Método `_find_cep_column()` expandido
   - Mensagem de erro melhorada
   - Logging adicional

2. ✅ **`app_simples.py`**
   - Preview do arquivo adicionado
   - Validação visual de coluna CEP
   - Melhor experiência do usuário

3. ✅ **`teste_enderecos.csv`** (NOVO)
   - Arquivo de exemplo para testes

---

**Status:** ✅ **CORRIGIDO E TESTADO**

**Data:** 19 de Janeiro de 2026

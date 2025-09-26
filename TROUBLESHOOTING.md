# 🔧 Solucionando Problemas de Encoding

## Erro: 'utf-8' codec can't decode byte

Este erro é comum ao trabalhar com bancos Firebird que usam charset diferente do UTF-8.

### 🎯 Solução Rápida

1. **Execute o teste de conexão:**
   ```bash
   python test_connection.py
   ```

2. **O script irá testar diferentes charsets e mostrar qual funciona melhor**

3. **Atualize o arquivo `.env` com o charset correto:**
   ```
   DATABASE_CHARSET=WIN1252
   ```

### 🔍 Charsets Mais Comuns

| Charset | Descrição | Uso Comum |
|---------|-----------|-----------|
| `WIN1252` | Windows-1252 | Sistemas Windows Brasil |
| `ISO8859_1` | Latin-1 | Sistemas Unix/Linux |
| `UTF8` | UTF-8 | Sistemas modernos |
| `NONE` | Sem conversão | Quando outros falham |

### 🚀 Testando Manualmente

```python
import fdb

# Teste com diferentes charsets
charsets = ['WIN1252', 'ISO8859_1', 'UTF8', 'NONE']

for charset in charsets:
    try:
        conn = fdb.connect(
            dsn="25.90.252.41/3050:D:\\sistemas\\fcerta\\DB\\ALTERDB.ib",
            user="SYSDBA",
            password="masterkey",
            charset=charset
        )
        print(f"✅ {charset} funcionou!")
        conn.close()
        break
    except Exception as e:
        print(f"❌ {charset} falhou: {e}")
```

### 🔧 Correções Implementadas

1. **Múltiplos charsets** - A API tenta automaticamente diferentes charsets
2. **Tratamento de bytes** - Conversão segura de dados binários
3. **Limpeza de strings** - Remove caracteres de controle
4. **Sintaxe Firebird** - Usa `FIRST/SKIP` ao invés de `ROWS TO`

### 📝 Sintaxe de Query Corrigida

**❌ Antes (erro):**
```sql
SELECT CDCLI, CDFIL, NOMECLI FROM FC07000 ORDER BY NOMECLI ASC ROWS 1 TO 50
```

**✅ Depois (correto):**
```sql
SELECT FIRST 50 CDCLI, CDFIL, NOMECLI FROM FC07000 ORDER BY NOMECLI ASC
```

### 🛠️ Se o Problema Persistir

1. **Verifique a versão do Firebird** no servidor
2. **Confirme o charset do banco:**
   ```sql
   SELECT RDB$CHARACTER_SET_NAME FROM RDB$DATABASE;
   ```
3. **Teste conexão direta** com `isql` ou `flamerobin`
4. **Considere usar `charset='NONE'`** como último recurso

### 💡 Dicas Adicionais

- **Backup/Restore** com charset correto pode resolver problemas permanentemente
- **Firebird 3.0+** tem melhor suporte a UTF-8
- **Sempre teste** com dados reais que contenham acentos

## 🚨 Erro: Token unknown - line 1, column 93

Este erro específico indica problema de sintaxe SQL na posição 93 da query.

### 🔍 Diagnóstico Rápido

1. **Execute o debug:**
   ```bash
   python debug_query.py
   ```

2. **Verifique a query gerada** no construtor visual
3. **Use o botão "✅ Validar"** antes de executar

### 🛠️ Possíveis Causas

| Causa | Solução |
|-------|---------|
| ORDER BY inválido | Verificar nome da coluna |
| FIRST mal posicionado | Usar sintaxe correta |
| Aspas não balanceadas | Validar strings |
| Alias inválido | Usar nomes válidos |

### 🔧 Correções Implementadas

1. **Validação de query** antes da execução
2. **Sanitização de valores** SQL
3. **Verificação de identificadores** válidos
4. **Debug detalhado** no console

### 🆘 Suporte

Se ainda tiver problemas:

1. Execute `python test_connection.py` e compartilhe o resultado
2. Execute `python debug_query.py` para análise detalhada
3. Verifique os logs do Firebird server
4. Teste com uma ferramenta externa (FlameRobin, IBExpert)
5. Use o botão "✅ Validar" no construtor de query
# 🔧 Guia do Construtor de Query Visual

## 🎯 Funcionalidades

O construtor de query visual permite criar consultas SQL complexas com múltiplas tabelas de forma intuitiva, sem precisar escrever código SQL manualmente.

### ✨ Recursos Disponíveis

- ✅ **Múltiplas Tabelas** - Adicione quantas tabelas precisar
- ✅ **JOINs Automáticos** - INNER, LEFT e RIGHT JOIN
- ✅ **Seleção de Colunas** - Por tabela com prefixos automáticos
- ✅ **Condições WHERE** - Interface visual para filtros
- ✅ **ORDER BY** - Ordenação por qualquer coluna
- ✅ **LIMIT** - Controle de quantidade de registros
- ✅ **Query em Tempo Real** - Visualização instantânea do SQL gerado

## 🚀 Como Usar

### 1. **Adicionar Tabelas**

1. Clique em "📊 Listar Tabelas" para carregar todas as tabelas
2. No construtor, selecione uma tabela no dropdown
3. Clique "➕ Adicionar Tabela"
4. Repita para adicionar mais tabelas

### 2. **Configurar JOINs**

Quando você adiciona uma segunda tabela:

- **Tipo de JOIN**: Escolha INNER, LEFT ou RIGHT JOIN
- **Condição**: Digite a condição (ex: `t1.id = t2.cliente_id`)

**Exemplo de condições:**
```sql
fc1.CDCLI = fc2.CDCLI          -- Chaves iguais
fc1.ID = fc2.PARENT_ID         -- Relacionamento pai-filho
fc1.CODIGO = fc2.CODIGO        -- Códigos correspondentes
```

### 3. **Selecionar Colunas**

- As colunas são agrupadas por tabela
- Cada coluna mostra: `nome (tipo)`
- Use "✅ Todas" para selecionar todas as colunas
- Use "❌ Limpar" para desmarcar todas

### 4. **Adicionar Filtros WHERE**

1. Clique "➕ Adicionar Condição"
2. Selecione a coluna (com prefixo da tabela)
3. Escolha o operador (=, >, LIKE, etc.)
4. Digite o valor

**Operadores disponíveis:**
- `=`, `!=` - Igualdade/diferença
- `>`, `<`, `>=`, `<=` - Comparações numéricas
- `LIKE`, `NOT LIKE` - Busca por texto (wildcards automáticos)
- `IS NULL`, `IS NOT NULL` - Valores nulos

### 5. **Configurar Ordenação**

- Selecione a coluna para ordenar
- Escolha ASC (crescente) ou DESC (decrescente)

### 6. **Definir Limite**

- Digite o número máximo de registros
- Usa sintaxe `FIRST` do Firebird automaticamente

## 📝 Exemplos Práticos

### **Exemplo 1: Consulta Simples**
```sql
-- Tabelas: FC07000 (Clientes)
-- Colunas: CDCLI, NOMECLI
-- Filtro: Nome contém "JOÃO"
-- Resultado:
SELECT FIRST 50 fc1.CDCLI, fc1.NOMECLI 
FROM FC07000 fc1 
WHERE fc1.NOMECLI LIKE '%JOÃO%' 
ORDER BY fc1.NOMECLI ASC
```

### **Exemplo 2: JOIN de Duas Tabelas**
```sql
-- Tabelas: FC07000 (Clientes) + FC08000 (Pedidos)
-- JOIN: fc1.CDCLI = fc2.CDCLI
-- Resultado:
SELECT fc1.NOMECLI, fc2.NUMPEDIDO, fc2.DATAPEDIDO 
FROM FC07000 fc1 
INNER JOIN FC08000 fc2 ON fc1.CDCLI = fc2.CDCLI 
WHERE fc2.DATAPEDIDO >= '2024-01-01'
ORDER BY fc2.DATAPEDIDO DESC
```

### **Exemplo 3: Múltiplas Tabelas**
```sql
-- Tabelas: Clientes + Pedidos + Itens
SELECT fc1.NOMECLI, fc2.NUMPEDIDO, fc3.PRODUTO, fc3.QUANTIDADE 
FROM FC07000 fc1 
INNER JOIN FC08000 fc2 ON fc1.CDCLI = fc2.CDCLI 
INNER JOIN FC09000 fc3 ON fc2.NUMPEDIDO = fc3.NUMPEDIDO 
WHERE fc3.QUANTIDADE > 10
```

## 🎨 Interface Visual

### **Seção de Tabelas**
- Lista todas as tabelas selecionadas
- Mostra alias automáticos (fc1, fc2, etc.)
- Indica tipo de JOIN
- Permite configurar condições de JOIN
- Botão para remover tabelas

### **Seção de Colunas**
- Agrupadas por tabela
- Checkboxes para seleção
- Informação do tipo de dados
- Botões para selecionar/limpar todas

### **Seção WHERE**
- Condições visuais
- Dropdowns para colunas e operadores
- Campos de texto para valores
- Operador AND automático entre condições

### **Query Gerada**
- Atualização em tempo real
- Sintaxe Firebird correta
- Botão para copiar
- Botão para executar

## 💡 Dicas e Truques

### **Aliases Automáticos**
- Primeira tabela: `fc1`
- Segunda tabela: `fc2`
- Se houver conflito: `fc11`, `fc12`, etc.

### **Condições de JOIN Comuns**
```sql
-- Chave primária = chave estrangeira
tabela1.id = tabela2.tabela1_id

-- Códigos iguais
tabela1.codigo = tabela2.codigo

-- Relacionamento por data
tabela1.data_inicio <= tabela2.data AND tabela1.data_fim >= tabela2.data
```

### **Filtros Úteis**
```sql
-- Data entre período
data_campo >= '2024-01-01' AND data_campo <= '2024-12-31'

-- Texto que começa com
campo LIKE 'ABC%'

-- Valores em lista (use múltiplas condições)
campo = 'A' OR campo = 'B' OR campo = 'C'

-- Não nulos
campo IS NOT NULL
```

### **Performance**
- Use LIMIT para consultas grandes
- Adicione índices nas colunas de JOIN
- Filtre primeiro, ordene depois
- Evite LIKE com % no início

## 🔧 Solução de Problemas

### **JOIN não funciona**
- Verifique se as colunas existem em ambas as tabelas
- Confirme os tipos de dados compatíveis
- Use alias corretos (fc1.campo, fc2.campo)

### **Query muito lenta**
- Adicione LIMIT
- Use índices nas colunas de filtro
- Evite muitas condições LIKE

### **Erro de sintaxe**
- Verifique nomes de colunas
- Confirme tipos de dados nos filtros
- Use aspas simples para strings

## 🆘 Suporte

Se tiver dúvidas:
1. Teste com uma tabela primeiro
2. Adicione tabelas gradualmente
3. Verifique a query gerada
4. Use o botão "Executar" para testar
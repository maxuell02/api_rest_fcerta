# Firebird Database API

API REST em Python para disponibilizar todas as tabelas de um banco de dados Firebird.

## Funcionalidades

- ✅ Listar todas as tabelas do banco
- ✅ Visualizar schema/estrutura das tabelas
- ✅ Consultar dados com paginação
- ✅ Inserir novos registros
- ✅ Atualizar registros existentes
- ✅ Deletar registros
- ✅ Executar queries SELECT customizadas
- ✅ Health check da API e banco
- ✅ Filtro simples por coluna e valor
- ✅ Status detalhado do banco

## Endpoints Principais

Observação: por segurança, a API só aceita tabelas no padrão `FCxxxxx` (ex.: `FC07000`, `FC08000`).

### GET /tables
Lista todas as tabelas disponíveis no banco.

### GET /tables/{table_name}
Retorna dados de uma tabela específica.
- `limit`: número máximo de registros (opcional)
- `offset`: número de registros a pular (opcional)

### GET /tables/{table_name}/schema
Retorna a estrutura/schema de uma tabela.

### GET /tables/{table_name}/find
Filtra registros por uma coluna e valor.
- `column`: nome da coluna (obrigatório)
- `value`: valor a comparar (obrigatório)
- `op`: operador (`=`, `<>`, `>`, `<`, `>=`, `<=`, `LIKE`) (padrão `=`)
- `limit`, `offset`: paginação (opcional)

### POST /tables/{table_name}
Insere um novo registro na tabela.

### PUT /tables/{table_name}
Atualiza registros existentes na tabela.

### DELETE /tables/{table_name}
Remove registros da tabela.

### GET /db/status
Mostra status de conexão do banco e informações básicas (sem expor segredos).

## Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` com:

```
DATABASE_PATH=D:\sistemas\fcerta\DB\ALTERDB.ib
DATABASE_HOST=25.90.252.41
DATABASE_USERNAME=SYSDBA
DATABASE_PASSWORD=masterkey
DATABASE_PORT=3050
```

## Instalação Local

```bash
pip install -r requirements.txt
python main.py
```

A API estará disponível em `https://api-rest-fcerta.onrender.com`

## Deploy no Render

### ⚡ Deploy Rápido (5 minutos)
```bash
# Preparação automática
python deploy_to_render.py

# OU manualmente
git add . && git commit -m "Deploy" && git push origin main
```

### 🎯 Configuração no Render
```yaml
Build Command: pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir fdb || echo "FDB opcional"
Start Command: python start.py

Environment Variables:
DATABASE_HOST = 25.90.252.41
DATABASE_PATH = D:\sistemas\fcerta\DB\ALTERDB.ib
DATABASE_USERNAME = SYSDBA
DATABASE_PASSWORD = masterkey
DATABASE_PORT = 3050
DATABASE_CHARSET = WIN1252
```

### 🧭 Passo a Passo no Render (UI)
- Acesse `https://render.com` e clique em `New +` → `Web Service`
- Conecte seu repositório GitHub com este projeto
- Configure:
  - `Runtime`: `Python`
  - `Build Command`: conforme acima
  - `Start Command`: `python start.py`
  - `Environment Variables`: conforme acima
- Clique em `Create Web Service` e aguarde o build
- Teste `GET /health` na URL pública do serviço

### 🌐 Notas de Rede
- O `DATABASE_HOST` precisa ser acessível pela internet a partir do Render
- IPs de redes privadas/VPN (ex.: `25.x` Hamachi) não funcionam no Render
- Garanta que a porta `3050` esteja aberta e acessível externamente
- Se necessário, use um túnel/VPN corporativo com gateway público

### ✅ Sistema à Prova de Falhas
- ✅ **5 níveis de fallback** automático
- ✅ **Funciona sempre** (pelo menos modo mock)
- ✅ **Zero dependências problemáticas**
- ✅ **Deploy garantido** em qualquer situação

### 📚 Guias Disponíveis
- 🚀 **[RENDER_QUICK_START.md](RENDER_QUICK_START.md)** - 5 minutos
- 📖 **[RENDER_DEPLOY_GUIDE.md](RENDER_DEPLOY_GUIDE.md)** - Completo
- 🔧 **[DEPLOY_STATUS.md](DEPLOY_STATUS.md)** - Status atual

## Documentação Interativa

Após iniciar a API, acesse:
- Swagger UI: `https://api-rest-fcerta.onrender.com/docs`
- ReDoc: `https://api-rest-fcerta.onrender.com/redoc`

## Exemplos de Uso
 
### Ambiente Render
- Base URL: `https://api-rest-fcerta.onrender.com`
- Saúde: `https://api-rest-fcerta.onrender.com/health`
- Status DB: `https://api-rest-fcerta.onrender.com/db/status`

### Ativar dados reais no Render
- Use `requirements.txt` com `fdb` (já atualizado).
- Reimplante para aplicar dependências e o novo `start.py` que prioriza `main`.
- Garanta que o `DATABASE_HOST` é público (não `25.x`) e com porta `3050` aberta.
- Valide com `GET /db/status`; deve retornar `database: "connected"` usando modo real.

#### Exemplos com a URL do Render
```bash
# Saúde
curl https://api-rest-fcerta.onrender.com/health

# Listar tabelas
curl https://api-rest-fcerta.onrender.com/tables

# Dados com paginação
curl "https://api-rest-fcerta.onrender.com/tables/FC07000?limit=10&offset=0"

# Filtrar (LIKE)
curl "https://api-rest-fcerta.onrender.com/tables/FC07000/find?column=NOMECLI&value=Silva&op=LIKE&limit=5"

# Multi busca
curl -X POST https://api-rest-fcerta.onrender.com/multi/find \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"table": "FC07000", "column": "CDCLI", "value": 1},
      {"table": "FC08000", "column": "CDCLI", "value": 1, "limit": 5}
    ]
  }'

# Query parametrizada
curl -X POST https://api-rest-fcerta.onrender.com/query/params \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT FIRST 10 CDCLI, NOMECLI FROM FC07000 WHERE CDCLI = ?",
    "params": [1]
  }'
```

### Listar tabelas
```bash
curl https://api-rest-fcerta.onrender.com/tables
```

### Consultar dados de uma tabela
```bash
curl "https://api-rest-fcerta.onrender.com/tables/FC07000?limit=10&offset=0"
```

### Filtrar dados de uma tabela
```bash
# Igualdade (op padrão "=")
curl "https://api-rest-fcerta.onrender.com/tables/FC07000/find?column=CDCLI&value=1"

# LIKE (contém)
curl "https://api-rest-fcerta.onrender.com/tables/FC07000/find?column=NOMECLI&value=Silva&op=LIKE&limit=5"
```

### Buscar em múltiplas tabelas
```bash
curl -X POST https://api-rest-fcerta.onrender.com/multi/find \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"table": "FC07000", "column": "CDCLI", "value": 1},
      {"table": "FC08000", "column": "CDCLI", "value": 1, "limit": 5}
    ]
  }'
```

### Executar SELECT parametrizado
```bash
curl -X POST https://api-rest-fcerta.onrender.com/query/params \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT FIRST 10 CDCLI, NOMECLI FROM FC07000 WHERE CDCLI = ?",
    "params": [1]
  }'
```

### Inserir dados
```bash
curl -X POST https://api-rest-fcerta.onrender.com/tables/FC07000 \
  -H "Content-Type: application/json" \
  -d '{"data": {"NOMECLI": "João Silva", "EMAIL": "joao@email.com"}}'
```

### Atualizar dados
```bash
curl -X PUT https://api-rest-fcerta.onrender.com/tables/FC07000 \
  -H "Content-Type: application/json" \
  -d '{
    "data": {"EMAIL": "joao.silva@email.com"},
    "where_clause": "CDCLI = ?",
    "where_params": [1]
  }'
```

### Deletar dados
```bash
curl -X DELETE https://api-rest-fcerta.onrender.com/tables/FC07000 \
  -H "Content-Type: application/json" \
  -d '{
    "where_clause": "CDCLI = ?",
    "where_params": [1]
  }'
```

### Status do banco
```bash
curl https://api-rest-fcerta.onrender.com/db/status
```

## Segurança

- A API permite apenas queries SELECT no endpoint de query customizada
- Use HTTPS em produção
- Configure CORS adequadamente para seu ambiente
- Considere implementar autenticação para endpoints de escrita

## Tecnologias

- FastAPI
- Python FDB (Firebird driver)
- Uvicorn
- Pydantic

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

## Endpoints Principais

### GET /tables
Lista todas as tabelas disponíveis no banco.

### GET /tables/{table_name}
Retorna dados de uma tabela específica.
- `limit`: número máximo de registros (opcional)
- `offset`: número de registros a pular (opcional)

### GET /tables/{table_name}/schema
Retorna a estrutura/schema de uma tabela.

### POST /tables/{table_name}
Insere um novo registro na tabela.

### PUT /tables/{table_name}
Atualiza registros existentes na tabela.

### DELETE /tables/{table_name}
Remove registros da tabela.

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

A API estará disponível em `http://localhost:8000`

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
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Exemplos de Uso

### Listar tabelas
```bash
curl http://localhost:8000/tables
```

### Consultar dados de uma tabela
```bash
curl http://localhost:8000/tables/USUARIOS?limit=10&offset=0
```

### Inserir dados
```bash
curl -X POST http://localhost:8000/tables/USUARIOS \
  -H "Content-Type: application/json" \
  -d '{"data": {"nome": "João", "email": "joao@email.com"}}'
```

### Atualizar dados
```bash
curl -X PUT http://localhost:8000/tables/USUARIOS \
  -H "Content-Type: application/json" \
  -d '{
    "data": {"nome": "João Silva"},
    "where_clause": "id = ?",
    "where_params": [1]
  }'
```

### Deletar dados
```bash
curl -X DELETE http://localhost:8000/tables/USUARIOS \
  -H "Content-Type: application/json" \
  -d '{
    "where_clause": "id = ?",
    "where_params": [1]
  }'
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
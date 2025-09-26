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
```

## Instalação Local

```bash
pip install -r requirements.txt
python main.py
```

A API estará disponível em `http://localhost:8000`

## Deploy no Render

1. Conecte seu repositório GitHub ao Render
2. Configure as variáveis de ambiente no painel do Render
3. O deploy será automático usando o arquivo `render.yaml`

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

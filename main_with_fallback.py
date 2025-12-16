from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import os
import re
import socket

# Tentar importar database real, se falhar usar mock
try:
    from database import FirebirdDatabase
    print("✅ Usando database real (FDB)")
except ImportError as e:
    print(f"⚠️  FDB não disponível: {e}")
    print("🔄 Usando database mock para demonstração")
    from database_mock import FirebirdDatabase

app = FastAPI(
    title="Firebird Database API",
    description="API REST para acessar todas as tabelas do banco de dados Firebird",
    version="1.0.0"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instância do banco
db = FirebirdDatabase()

# Modelos Pydantic
class InsertData(BaseModel):
    data: Dict[str, Any]

class UpdateData(BaseModel):
    data: Dict[str, Any]
    where_clause: str
    where_params: List[Any]

class DeleteData(BaseModel):
    where_clause: str
    where_params: List[Any]

class MultiFindItem(BaseModel):
    table: str
    column: str
    value: Any
    op: Optional[str] = "="
    limit: Optional[int] = None
    offset: Optional[int] = None

class MultiFindRequest(BaseModel):
    items: List[MultiFindItem]

@app.get("/")
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "message": "Firebird Database API",
        "version": "1.0.0",
        "mode": "mock" if "database_mock" in str(type(db)) else "real",
        "endpoints": {
            "tables": "/tables",
            "table_data": "/tables/{table_name}",
            "table_schema": "/tables/{table_name}/schema"
        }
    }

@app.get("/health")
async def health_check():
    """Verifica se a API e o banco estão funcionando"""
    try:
        connection = db.get_connection()
        if hasattr(connection, 'close'):
            connection.close()
        return {
            "status": "healthy", 
            "database": "connected",
            "mode": "mock" if "database_mock" in str(type(db)) else "real"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.get("/tables")
async def get_tables():
    """Retorna lista de todas as tabelas do banco"""
    try:
        tables = db.get_all_tables()
        return {
            "tables": tables,
            "count": len(tables)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tables/{table_name}/schema")
async def get_table_schema(table_name: str):
    """Retorna o schema (estrutura) de uma tabela específica"""
    try:
        if not re.fullmatch(r'FC\d{5}', table_name.upper()):
            raise HTTPException(status_code=400, detail="Nome de tabela inválido. Use padrão FCxxxxx")
        columns = db.get_table_columns(table_name)
        if not columns:
            raise HTTPException(status_code=404, detail=f"Tabela '{table_name}' não encontrada")
        
        return {
            "table": table_name,
            "columns": columns
        }
    except Exception as e:
        if "não encontrada" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tables/{table_name}")
async def get_table_data(
    table_name: str,
    limit: Optional[int] = Query(None, description="Número máximo de registros a retornar"),
    offset: Optional[int] = Query(None, description="Número de registros a pular")
):
    """Retorna dados de uma tabela específica com paginação opcional"""
    try:
        if not re.fullmatch(r'FC\d{5}', table_name.upper()):
            raise HTTPException(status_code=400, detail="Nome de tabela inválido. Use padrão FCxxxxx")
        result = db.execute_select(table_name, limit, offset)
        return result
    except Exception as e:
        if "doesn't exist" in str(e).lower() or "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Tabela '{table_name}' não encontrada")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tables/{table_name}/find")
async def find_in_table(
    table_name: str,
    column: str = Query(..., description="Nome da coluna para filtro"),
    value: str = Query(..., description="Valor a ser comparado"),
    op: str = Query("=", description="Operador (=, <>, >, <, >=, <=, LIKE)"),
    limit: Optional[int] = Query(None, description="Máximo de registros"),
    offset: Optional[int] = Query(None, description="Registros a pular")
):
    """Filtra registros de uma tabela por coluna e valor"""
    try:
        if not re.fullmatch(r'FC\d{5}', table_name.upper()):
            raise HTTPException(status_code=400, detail="Nome de tabela inválido. Use padrão FCxxxxx")
        allowed_ops = ["=", "<>", ">", "<", ">=", "<=", "LIKE"]
        op_upper = op.upper()
        if op_upper not in allowed_ops:
            raise HTTPException(status_code=400, detail=f"Operador inválido. Use: {', '.join(allowed_ops)}")
        
        # Tenta converter value para número quando fizer sentido
        parsed_value: Any = value
        if op_upper != "LIKE":
            try:
                if "." in value:
                    parsed_value = float(value)
                else:
                    parsed_value = int(value)
            except ValueError:
                parsed_value = value
        
        where_clause = f"{column.upper()} {op_upper} ?"
        # Suporta tanto DB real quanto mock
        result = db.execute_select_where(table_name, where_clause, [parsed_value], limit, offset)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/multi/find")
async def multi_find(req: MultiFindRequest):
    try:
        allowed_ops = ["=", "<>", ">", "<", ">=", "<=", "LIKE"]
        results = {}
        total = 0
        for item in req.items:
            tbl = item.table.upper()
            if not re.fullmatch(r'FC\d{5}', tbl):
                raise HTTPException(status_code=400, detail=f"Nome de tabela inválido: {tbl}")
            op_upper = (item.op or "=").upper()
            if op_upper not in allowed_ops:
                raise HTTPException(status_code=400, detail=f"Operador inválido em {tbl}. Use: {', '.join(allowed_ops)}")
            parsed_value: Any = item.value
            if op_upper != "LIKE" and isinstance(parsed_value, str):
                try:
                    if "." in parsed_value:
                        parsed_value = float(parsed_value)
                    else:
                        parsed_value = int(parsed_value)
                except ValueError:
                    pass
            where_clause = f"{item.column.upper()} {op_upper} ?"
            res = db.execute_select_where(tbl, where_clause, [parsed_value], item.limit, item.offset)
            results[tbl] = res
            total += res.get("count", 0)
        return {"results": results, "total_count": total, "tables": list(results.keys())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tables/{table_name}")
async def insert_data(table_name: str, insert_data: InsertData):
    """Insere um novo registro na tabela especificada"""
    try:
        if not re.fullmatch(r'FC\d{5}', table_name.upper()):
            raise HTTPException(status_code=400, detail="Nome de tabela inválido. Use padrão FCxxxxx")
        result = db.execute_insert(table_name, insert_data.data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/tables/{table_name}")
async def update_data(table_name: str, update_data: UpdateData):
    """Atualiza registros na tabela especificada"""
    try:
        if not re.fullmatch(r'FC\d{5}', table_name.upper()):
            raise HTTPException(status_code=400, detail="Nome de tabela inválido. Use padrão FCxxxxx")
        result = db.execute_update(
            table_name, 
            update_data.data, 
            update_data.where_clause, 
            update_data.where_params
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/tables/{table_name}")
async def delete_data(table_name: str, delete_data: DeleteData):
    """Deleta registros da tabela especificada"""
    try:
        if not re.fullmatch(r'FC\d{5}', table_name.upper()):
            raise HTTPException(status_code=400, detail="Nome de tabela inválido. Use padrão FCxxxxx")
        result = db.execute_delete(
            table_name, 
            delete_data.where_clause, 
            delete_data.where_params
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint para executar queries customizadas (use com cuidado)
@app.post("/query")
async def execute_custom_query(query_data: Dict[str, Any]):
    """Executa uma query SQL customizada (apenas SELECT por segurança)"""
    try:
        query = query_data.get("query", "").strip()
        
        # Permite apenas SELECT por segurança
        if not query.upper().startswith("SELECT"):
            raise HTTPException(status_code=400, detail="Apenas queries SELECT são permitidas")
        
        # Usa a nova função com tratamento de encoding melhorado
        result = db.execute_custom_query(query)
        return result
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/params")
async def execute_custom_query_params(query_data: Dict[str, Any]):
    try:
        query = str(query_data.get("query", "")).strip()
        params = query_data.get("params", [])
        if not query.upper().startswith("SELECT"):
            raise HTTPException(status_code=400, detail="Apenas queries SELECT são permitidas")
        result = db.execute_custom_query_params(query, params if isinstance(params, list) else [])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/db/status")
async def db_status():
    """Verifica status da conexão e mostra informações básicas"""
    try:
        conn = db.get_connection()
        if hasattr(conn, 'close'):
            conn.close()
        return {
            "status": "ok",
            "database": "connected",
            "mode": "mock" if "database_mock" in str(type(db)) else "real",
            "host": os.getenv("DATABASE_HOST"),
            "port": int(os.getenv("DATABASE_PORT", 3050)),
            "charset": os.getenv("DATABASE_CHARSET", "WIN1252")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha na conexão: {str(e)}")

@app.get("/db/ping")
async def db_ping(timeout: Optional[float] = 5.0):
    """Teste de rede: tenta abrir socket no host/porta do banco (sem autenticar)"""
    host = os.getenv("DATABASE_HOST")
    port = int(os.getenv("DATABASE_PORT", 3050))
    if not host:
        raise HTTPException(status_code=400, detail="DATABASE_HOST não configurado")
    try:
        with socket.create_connection((host, port), timeout=float(timeout or 5.0)):
            return {"reachable": True, "host": host, "port": port, "timeout": timeout}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Inacessível: {host}:{port} - {str(e)}")
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    
    # Configuração para desenvolvimento local
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        reload=False,  # Desabilitado para produção
        access_log=True
    )

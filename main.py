from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from database import FirebirdDatabase
import os

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

@app.get("/")
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "message": "Firebird Database API",
        "version": "1.0.0",
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
        connection.close()
        return {"status": "healthy", "database": "connected"}
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
        result = db.execute_select(table_name, limit, offset)
        return result
    except Exception as e:
        if "doesn't exist" in str(e).lower() or "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Tabela '{table_name}' não encontrada")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tables/{table_name}")
async def insert_data(table_name: str, insert_data: InsertData):
    """Insere um novo registro na tabela especificada"""
    try:
        result = db.execute_insert(table_name, insert_data.data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/tables/{table_name}")
async def update_data(table_name: str, update_data: UpdateData):
    """Atualiza registros na tabela especificada"""
    try:
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
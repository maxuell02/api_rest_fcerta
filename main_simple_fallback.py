"""
Versão super simples da API que sempre funciona
"""

import os
import sys
from typing import Dict, Any, List, Optional

# Tenta importar FastAPI, se falhar usa dados mock
try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    # Fallback para tipos básicos
    class BaseModel:
        pass

# Dados mock sempre disponíveis
MOCK_TABLES = ['FC07000', 'FC08000', 'FC09000', 'FC10000']

MOCK_DATA = {
    'FC07000': [
        {'CDCLI': 1, 'NOMECLI': 'João Silva', 'EMAIL': 'joao@email.com'},
        {'CDCLI': 2, 'NOMECLI': 'Maria Santos', 'EMAIL': 'maria@email.com'},
        {'CDCLI': 3, 'NOMECLI': 'Pedro Costa', 'EMAIL': 'pedro@email.com'}
    ],
    'FC08000': [
        {'NUMPEDIDO': 1001, 'CDCLI': 1, 'DATAPEDIDO': '2024-01-15', 'VALOR': 150.50},
        {'NUMPEDIDO': 1002, 'CDCLI': 2, 'DATAPEDIDO': '2024-01-16', 'VALOR': 275.80}
    ]
}

MOCK_COLUMNS = {
    'FC07000': [
        {'name': 'CDCLI', 'type': 'INTEGER', 'length': 4, 'nullable': False},
        {'name': 'NOMECLI', 'type': 'VARCHAR', 'length': 100, 'nullable': True},
        {'name': 'EMAIL', 'type': 'VARCHAR', 'length': 150, 'nullable': True}
    ],
    'FC08000': [
        {'name': 'NUMPEDIDO', 'type': 'INTEGER', 'length': 4, 'nullable': False},
        {'name': 'CDCLI', 'type': 'INTEGER', 'length': 4, 'nullable': False},
        {'name': 'DATAPEDIDO', 'type': 'DATE', 'length': 8, 'nullable': True},
        {'name': 'VALOR', 'type': 'DOUBLE', 'length': 8, 'nullable': True}
    ]
}

# Classe mock para database
class MockDatabase:
    def get_connection(self):
        return True
    
    def get_all_tables(self):
        return MOCK_TABLES
    
    def get_table_columns(self, table_name: str):
        return MOCK_COLUMNS.get(table_name.upper(), [])
    
    def execute_select(self, table_name: str, limit: Optional[int] = None, offset: Optional[int] = None):
        data = MOCK_DATA.get(table_name.upper(), [])
        if limit:
            data = data[:limit]
        
        return {
            'table': table_name,
            'columns': list(data[0].keys()) if data else [],
            'data': data,
            'count': len(data)
        }
    
    def execute_insert(self, table_name: str, data: Dict[str, Any]):
        return {'message': f'Mock: Registro inserido na tabela {table_name}'}
    
    def execute_update(self, table_name: str, data: Dict[str, Any], where_clause: str, where_params: List[Any]):
        return {'message': f'Mock: Registro atualizado na tabela {table_name}'}
    
    def execute_delete(self, table_name: str, where_clause: str, where_params: List[Any]):
        return {'message': f'Mock: Registro deletado da tabela {table_name}'}
    
    def execute_custom_query(self, query: str):
        return {
            'columns': ['RESULTADO'],
            'data': [{'RESULTADO': f'Mock result for: {query[:50]}...'}],
            'count': 1,
            'query': query
        }

if FASTAPI_AVAILABLE:
    # Versão FastAPI
    app = FastAPI(
        title="Firebird Database API - Simple Fallback",
        description="API REST com fallback automático para dados mock",
        version="1.0.0-simple"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Instância do banco mock
    db = MockDatabase()

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
        return {
            "message": "Firebird Database API - Simple Fallback",
            "version": "1.0.0-simple",
            "mode": "mock",
            "status": "FastAPI disponível",
            "endpoints": {
                "tables": "/tables",
                "table_data": "/tables/{table_name}",
                "table_schema": "/tables/{table_name}/schema"
            }
        }

    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "database": "mock",
            "mode": "simple-fastapi",
            "fastapi_version": "available"
        }

    @app.get("/tables")
    async def get_tables():
        tables = db.get_all_tables()
        return {"tables": tables, "count": len(tables)}

    @app.get("/tables/{table_name}/schema")
    async def get_table_schema(table_name: str):
        columns = db.get_table_columns(table_name)
        if not columns:
            raise HTTPException(status_code=404, detail=f"Tabela '{table_name}' não encontrada")
        return {"table": table_name, "columns": columns}

    @app.get("/tables/{table_name}")
    async def get_table_data(
        table_name: str,
        limit: Optional[int] = Query(None),
        offset: Optional[int] = Query(None)
    ):
        result = db.execute_select(table_name, limit, offset)
        return result

    @app.post("/tables/{table_name}")
    async def insert_data(table_name: str, insert_data: InsertData):
        result = db.execute_insert(table_name, insert_data.data)
        return result

    @app.put("/tables/{table_name}")
    async def update_data(table_name: str, update_data: UpdateData):
        result = db.execute_update(
            table_name, 
            update_data.data, 
            update_data.where_clause, 
            update_data.where_params
        )
        return result

    @app.delete("/tables/{table_name}")
    async def delete_data(table_name: str, delete_data: DeleteData):
        result = db.execute_delete(
            table_name, 
            delete_data.where_clause, 
            delete_data.where_params
        )
        return result

    @app.post("/query")
    async def execute_custom_query(query_data: Dict[str, Any]):
        query = query_data.get("query", "").strip()
        if not query.upper().startswith("SELECT"):
            raise HTTPException(status_code=400, detail="Apenas queries SELECT são permitidas")
        
        result = db.execute_custom_query(query)
        return result

else:
    # Fallback sem FastAPI - apenas para importação
    print("⚠️ FastAPI não disponível, usando fallback básico")
    
    class SimpleApp:
        def __init__(self):
            self.db = MockDatabase()
        
        def get_health(self):
            return {
                "status": "healthy",
                "database": "mock", 
                "mode": "simple-no-fastapi"
            }
    
    app = SimpleApp()

if __name__ == "__main__":
    if FASTAPI_AVAILABLE:
        import uvicorn
        port = int(os.environ.get("PORT", 8000))
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        print("FastAPI não disponível. Use simple_main.py para servidor HTTP básico.")
        sys.exit(1)
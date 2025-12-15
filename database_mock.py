"""
Versão mock da database.py para testes quando FDB não funciona
"""

import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class FirebirdDatabase:
    def __init__(self):
        self.host = os.getenv('DATABASE_HOST')
        self.database_path = os.getenv('DATABASE_PATH')
        self.username = os.getenv('DATABASE_USERNAME')
        self.password = os.getenv('DATABASE_PASSWORD')
        self.port = int(os.getenv('DATABASE_PORT', 3050))
        self.charset = os.getenv('DATABASE_CHARSET', 'WIN1252')
        
    def get_connection(self):
        """Mock connection - apenas para teste"""
        print(f"Mock connection to {self.host}:{self.port}")
        return True
    
    def get_all_tables(self) -> List[str]:
        """Retorna tabelas mock para teste"""
        return [
            'FC07000',  # Clientes
            'FC08000',  # Pedidos
            'FC09000',  # Itens
            'FC10000',  # Produtos
            'FC11000'   # Categorias
        ]
    
    def get_table_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """Retorna colunas mock para teste"""
        mock_columns = {
            'FC07000': [
                {'name': 'CDCLI', 'type': 'INTEGER', 'length': 4, 'nullable': False},
                {'name': 'NOMECLI', 'type': 'VARCHAR', 'length': 100, 'nullable': True},
                {'name': 'EMAIL', 'type': 'VARCHAR', 'length': 150, 'nullable': True},
                {'name': 'TELEFONE', 'type': 'VARCHAR', 'length': 20, 'nullable': True}
            ],
            'FC08000': [
                {'name': 'NUMPEDIDO', 'type': 'INTEGER', 'length': 4, 'nullable': False},
                {'name': 'CDCLI', 'type': 'INTEGER', 'length': 4, 'nullable': False},
                {'name': 'DATAPEDIDO', 'type': 'DATE', 'length': 8, 'nullable': True},
                {'name': 'VALOR', 'type': 'DOUBLE', 'length': 8, 'nullable': True}
            ]
        }
        
        return mock_columns.get(table_name.upper(), [
            {'name': 'ID', 'type': 'INTEGER', 'length': 4, 'nullable': False},
            {'name': 'NOME', 'type': 'VARCHAR', 'length': 100, 'nullable': True}
        ])
    
    def execute_select(self, table_name: str, limit: Optional[int] = None, offset: Optional[int] = None) -> Dict[str, Any]:
        """Retorna dados mock para teste"""
        
        mock_data = {
            'FC07000': [
                {'CDCLI': 1, 'NOMECLI': 'João Silva', 'EMAIL': 'joao@email.com', 'TELEFONE': '11999999999'},
                {'CDCLI': 2, 'NOMECLI': 'Maria Santos', 'EMAIL': 'maria@email.com', 'TELEFONE': '11888888888'},
                {'CDCLI': 3, 'NOMECLI': 'Pedro Costa', 'EMAIL': 'pedro@email.com', 'TELEFONE': '11777777777'}
            ],
            'FC08000': [
                {'NUMPEDIDO': 1001, 'CDCLI': 1, 'DATAPEDIDO': '2024-01-15', 'VALOR': 150.50},
                {'NUMPEDIDO': 1002, 'CDCLI': 2, 'DATAPEDIDO': '2024-01-16', 'VALOR': 275.80},
                {'NUMPEDIDO': 1003, 'CDCLI': 1, 'DATAPEDIDO': '2024-01-17', 'VALOR': 89.90}
            ]
        }
        
        data = mock_data.get(table_name.upper(), [
            {'ID': 1, 'NOME': 'Registro Mock 1'},
            {'ID': 2, 'NOME': 'Registro Mock 2'}
        ])
        
        # Aplicar limit se especificado
        if limit:
            data = data[:limit]
            
        columns = list(data[0].keys()) if data else []
        
        return {
            'table': table_name,
            'columns': columns,
            'data': data,
            'count': len(data)
        }
    
    def execute_select_where(
        self,
        table_name: str,
        where_clause: str,
        where_params: List[Any],
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> Dict[str, Any]:
        """Mock SELECT com WHERE simples (apenas coluna = valor)"""
        mock_data = {
            'FC07000': [
                {'CDCLI': 1, 'NOMECLI': 'João Silva', 'EMAIL': 'joao@email.com', 'TELEFONE': '11999999999'},
                {'CDCLI': 2, 'NOMECLI': 'Maria Santos', 'EMAIL': 'maria@email.com', 'TELEFONE': '11888888888'},
                {'CDCLI': 3, 'NOMECLI': 'Pedro Costa', 'EMAIL': 'pedro@email.com', 'TELEFONE': '11777777777'}
            ],
            'FC08000': [
                {'NUMPEDIDO': 1001, 'CDCLI': 1, 'DATAPEDIDO': '2024-01-15', 'VALOR': 150.50},
                {'NUMPEDIDO': 1002, 'CDCLI': 2, 'DATAPEDIDO': '2024-01-16', 'VALOR': 275.80},
                {'NUMPEDIDO': 1003, 'CDCLI': 1, 'DATAPEDIDO': '2024-01-17', 'VALOR': 89.90}
            ]
        }
        
        data = mock_data.get(table_name.upper(), [])
        
        # Tenta extrair coluna de where_clause no formato "COLUNA OP ?"
        try:
            col = where_clause.split()[0].upper()
            op = where_clause.split()[1].upper()
            val = where_params[0] if where_params else None
            
            def match(d):
                if col not in d:
                    return False
                dv = d[col]
                if op == '=':
                    return dv == val
                if op == '<>':
                    return dv != val
                if op == '>':
                    return isinstance(dv, (int, float)) and dv > val
                if op == '<':
                    return isinstance(dv, (int, float)) and dv < val
                if op == '>=':
                    return isinstance(dv, (int, float)) and dv >= val
                if op == '<=':
                    return isinstance(dv, (int, float)) and dv <= val
                if op == 'LIKE':
                    return isinstance(dv, str) and str(val).replace('%', '') in dv
                return False
            
            filtered = [r for r in data if match(r)]
        except Exception:
            filtered = data
        
        if limit:
            filtered = filtered[:limit]
        
        columns = list(filtered[0].keys()) if filtered else []
        return {
            'table': table_name,
            'columns': columns,
            'data': filtered,
            'count': len(filtered)
        }
    
    def execute_insert(self, table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock insert"""
        return {'message': f'Mock: Registro inserido com sucesso na tabela {table_name}'}
    
    def execute_update(self, table_name: str, data: Dict[str, Any], where_clause: str, where_params: List[Any]) -> Dict[str, Any]:
        """Mock update"""
        return {'message': f'Mock: Registro(s) atualizado(s) com sucesso na tabela {table_name}'}
    
    def execute_delete(self, table_name: str, where_clause: str, where_params: List[Any]) -> Dict[str, Any]:
        """Mock delete"""
        return {'message': f'Mock: Registro(s) deletado(s) com sucesso da tabela {table_name}'}
    
    def execute_custom_query(self, query: str) -> Dict[str, Any]:
        """Mock custom query"""
        return {
            'columns': ['RESULTADO'],
            'data': [{'RESULTADO': f'Mock result for: {query[:50]}...'}],
            'count': 1,
            'query': query
        }
    
    def execute_custom_query_params(self, query: str, params: List[Any]) -> Dict[str, Any]:
        """Mock custom query com parâmetros"""
        return {
            'columns': ['RESULTADO', 'PARAMS'],
            'data': [{'RESULTADO': f'Mock result for: {query[:50]}...', 'PARAMS': params}],
            'count': 1,
            'query': query
        }

try:
    import fdb
except Exception:
    fdb = None
try:
    import firebirdsql
except Exception:
    firebirdsql = None
import os
import re
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
        self._driver = None  # 'fdb' ou 'firebirdsql'
        
    def get_connection(self):
        """Estabelece conexão com o banco Firebird"""
        try:
            dsn = f"{self.host}/{self.port}:{self.database_path}"
            
            # Tenta com FDB primeiro, se disponível
            if fdb is not None:
                try:
                    connection = fdb.connect(
                        dsn=dsn,
                        user=self.username,
                        password=self.password,
                        charset=self.charset
                    )
                    self._driver = 'fdb'
                    return connection
                except Exception as e_fdb:
                    # Se falhar por falta de fbclient, tenta fallback
                    err = str(e_fdb).lower()
                    needs_fbclient = ('fbclient' in err) or ('gds32' in err) or ('library' in err)
                    if not needs_fbclient:
                        # Tenta outros charsets com FDB
                        charsets_fallback = ['WIN1252', 'ISO8859_1', 'UTF8', 'NONE']
                        for charset in charsets_fallback:
                            if charset == self.charset:
                                continue
                            try:
                                connection = fdb.connect(
                                    dsn=dsn,
                                    user=self.username,
                                    password=self.password,
                                    charset=charset
                                )
                                self._driver = 'fdb'
                                print(f"⚠️  Usando charset fallback: {charset}")
                                return connection
                            except Exception:
                                continue
                    # Continua para tentar firebirdsql abaixo
            
            # Fallback: tentar firebirdsql (driver puro Python)
            if firebirdsql is not None:
                try:
                    connection = firebirdsql.connect(
                        host=self.host,
                        database=self.database_path,
                        user=self.username,
                        password=self.password,
                        port=self.port,
                        charset=self.charset
                    )
                    self._driver = 'firebirdsql'
                    return connection
                except Exception as e_fbsql:
                    # Tenta charsets alternativos
                    charsets_fallback = ['WIN1252', 'ISO8859_1', 'UTF8', 'NONE']
                    try:
                        for charset in charsets_fallback:
                            if charset == self.charset:
                                continue
                            connection = firebirdsql.connect(
                                host=self.host,
                                database=self.database_path,
                                user=self.username,
                                password=self.password,
                                port=self.port,
                                charset=charset
                            )
                            self._driver = 'firebirdsql'
                            print(f"⚠️  Usando charset fallback (firebirdsql): {charset}")
                            return connection
                    except Exception:
                        pass
            
            raise Exception("Não foi possível conectar com nenhum driver (fdb/firebirdsql) e charset")
                    
        except Exception as e:
            raise Exception(f"Erro ao conectar com o banco: {str(e)}")
    
    def get_all_tables(self) -> List[str]:
        """Retorna lista de todas as tabelas do banco"""
        connection = self.get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT RDB$RELATION_NAME 
                FROM RDB$RELATIONS 
                WHERE RDB$VIEW_BLR IS NULL 
                AND (RDB$SYSTEM_FLAG IS NULL OR RDB$SYSTEM_FLAG = 0)
                ORDER BY RDB$RELATION_NAME
            """)
            tables = [row[0].strip() for row in cursor.fetchall()]
            tables = [t for t in tables if re.fullmatch(r'FC\d{5}', t)]
            return tables
        finally:
            connection.close()
    
    def get_table_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """Retorna informações das colunas de uma tabela"""
        connection = self.get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT 
                    rf.RDB$FIELD_NAME as field_name,
                    f.RDB$FIELD_TYPE as field_type,
                    f.RDB$FIELD_LENGTH as field_length,
                    rf.RDB$NULL_FLAG as null_flag
                FROM RDB$RELATION_FIELDS rf
                JOIN RDB$FIELDS f ON rf.RDB$FIELD_SOURCE = f.RDB$FIELD_NAME
                WHERE rf.RDB$RELATION_NAME = ?
                ORDER BY rf.RDB$FIELD_POSITION
            """, (table_name.upper(),))
            
            columns = []
            for row in cursor.fetchall():
                columns.append({
                    'name': row[0].strip() if row[0] else '',
                    'type': self._get_field_type_name(row[1]),
                    'length': row[2],
                    'nullable': row[3] is None
                })
            return columns
        finally:
            connection.close()
    
    def _get_field_type_name(self, field_type: int) -> str:
        """Converte código do tipo de campo para nome"""
        type_mapping = {
            7: 'SMALLINT',
            8: 'INTEGER',
            10: 'FLOAT',
            12: 'DATE',
            13: 'TIME',
            14: 'CHAR',
            16: 'BIGINT',
            27: 'DOUBLE',
            35: 'TIMESTAMP',
            37: 'VARCHAR',
            261: 'BLOB'
        }
        return type_mapping.get(field_type, 'UNKNOWN')
    
    def execute_select(self, table_name: str, limit: Optional[int] = None, offset: Optional[int] = None) -> Dict[str, Any]:
        """Executa SELECT em uma tabela com paginação"""
        connection = self.get_connection()
        try:
            cursor = connection.cursor()
            
            # Query base
            query = f"SELECT * FROM {table_name.upper()}"
            
            # Adiciona paginação se especificada (usando FIRST/SKIP do Firebird)
            if limit is not None:
                if offset and offset > 0:
                    query = query.replace("SELECT", f"SELECT FIRST {limit} SKIP {offset}")
                else:
                    query = query.replace("SELECT", f"SELECT FIRST {limit}")
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            # Pega os nomes das colunas
            columns = [desc[0] for desc in cursor.description]
            
            # Converte para lista de dicionários
            data = []
            for row in rows:
                row_dict = {}
                for i, value in enumerate(row):
                    # Converte valores especiais para JSON serializável
                    if hasattr(value, 'isoformat'):  # datetime objects
                        row_dict[columns[i]] = value.isoformat()
                    elif value is None:
                        row_dict[columns[i]] = None
                    elif isinstance(value, bytes):
                        # Tenta decodificar bytes com diferentes encodings
                        try:
                            row_dict[columns[i]] = value.decode('utf-8')
                        except UnicodeDecodeError:
                            try:
                                row_dict[columns[i]] = value.decode('latin1')
                            except UnicodeDecodeError:
                                try:
                                    row_dict[columns[i]] = value.decode('cp1252')
                                except UnicodeDecodeError:
                                    row_dict[columns[i]] = str(value, errors='ignore')
                    elif isinstance(value, str):
                        # Limpa caracteres especiais de strings
                        row_dict[columns[i]] = value.strip()
                    else:
                        row_dict[columns[i]] = value if isinstance(value, (int, float, bool)) else str(value)
                data.append(row_dict)
            
            return {
                'table': table_name,
                'columns': columns,
                'data': data,
                'count': len(data)
            }
        finally:
            connection.close()
    
    def execute_select_where(
        self, 
        table_name: str, 
        where_clause: str, 
        where_params: List[Any], 
        limit: Optional[int] = None, 
        offset: Optional[int] = None
    ) -> Dict[str, Any]:
        """Executa SELECT com WHERE parametrizado e paginação"""
        connection = self.get_connection()
        try:
            cursor = connection.cursor()
            
            # Monta SELECT com paginação
            base_select = "SELECT *"
            if limit is not None:
                if offset and offset > 0:
                    base_select = f"SELECT FIRST {limit} SKIP {offset} *"
                else:
                    base_select = f"SELECT FIRST {limit} *"
            
            query = f"{base_select} FROM {table_name.upper()} WHERE {where_clause}"
            cursor.execute(query, where_params)
            rows = cursor.fetchall()
            
            columns = [desc[0] for desc in cursor.description]
            data = []
            for row in rows:
                row_dict = {}
                for i, value in enumerate(row):
                    if hasattr(value, 'isoformat'):
                        row_dict[columns[i]] = value.isoformat()
                    elif value is None:
                        row_dict[columns[i]] = None
                    elif isinstance(value, bytes):
                        try:
                            row_dict[columns[i]] = value.decode('utf-8')
                        except UnicodeDecodeError:
                            try:
                                row_dict[columns[i]] = value.decode('latin1')
                            except UnicodeDecodeError:
                                try:
                                    row_dict[columns[i]] = value.decode('cp1252')
                                except UnicodeDecodeError:
                                    row_dict[columns[i]] = str(value, errors='ignore')
                    elif isinstance(value, str):
                        row_dict[columns[i]] = value.strip()
                    else:
                        row_dict[columns[i]] = value if isinstance(value, (int, float, bool)) else str(value)
                data.append(row_dict)
            
            return {
                'table': table_name,
                'columns': columns,
                'data': data,
                'count': len(data)
            }
        finally:
            connection.close()
    
    def execute_insert(self, table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Executa INSERT em uma tabela"""
        connection = self.get_connection()
        try:
            cursor = connection.cursor()
            
            columns = [col.upper() for col in data.keys()]
            values = list(data.values())
            placeholders = ', '.join(['?' for _ in values])
            
            query = f"INSERT INTO {table_name.upper()} ({', '.join(columns)}) VALUES ({placeholders})"
            cursor.execute(query, values)
            connection.commit()
            
            return {'message': f'Registro inserido com sucesso na tabela {table_name}'}
        finally:
            connection.close()
    
    def execute_update(self, table_name: str, data: Dict[str, Any], where_clause: str, where_params: List[Any]) -> Dict[str, Any]:
        """Executa UPDATE em uma tabela"""
        connection = self.get_connection()
        try:
            cursor = connection.cursor()
            
            set_clause = ', '.join([f"{col.upper()} = ?" for col in data.keys()])
            query = f"UPDATE {table_name.upper()} SET {set_clause} WHERE {where_clause}"
            
            params = list(data.values()) + where_params
            cursor.execute(query, params)
            connection.commit()
            
            return {'message': f'Registro(s) atualizado(s) com sucesso na tabela {table_name}'}
        finally:
            connection.close()
    
    def execute_delete(self, table_name: str, where_clause: str, where_params: List[Any]) -> Dict[str, Any]:
        """Executa DELETE em uma tabela"""
        connection = self.get_connection()
        try:
            cursor = connection.cursor()
            
            query = f"DELETE FROM {table_name.upper()} WHERE {where_clause}"
            cursor.execute(query, where_params)
            connection.commit()
            
            return {'message': f'Registro(s) deletado(s) com sucesso da tabela {table_name}'}
        finally:
            connection.close()
    
    def execute_custom_query(self, query: str) -> Dict[str, Any]:
        """Executa uma query customizada com tratamento de encoding melhorado"""
        connection = self.get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            
            # Pega os nomes das colunas
            columns = [desc[0].strip() if desc[0] else f'col_{i}' for i, desc in enumerate(cursor.description)]
            
            # Converte para lista de dicionários com tratamento de encoding
            data = []
            for row in rows:
                row_dict = {}
                for i, value in enumerate(row):
                    column_name = columns[i]
                    
                    if hasattr(value, 'isoformat'):  # datetime objects
                        row_dict[column_name] = value.isoformat()
                    elif value is None:
                        row_dict[column_name] = None
                    elif isinstance(value, bytes):
                        # Tenta decodificar bytes com diferentes encodings
                        try:
                            row_dict[column_name] = value.decode('utf-8').strip()
                        except UnicodeDecodeError:
                            try:
                                row_dict[column_name] = value.decode('latin1').strip()
                            except UnicodeDecodeError:
                                try:
                                    row_dict[column_name] = value.decode('cp1252').strip()
                                except UnicodeDecodeError:
                                    row_dict[column_name] = str(value, errors='replace').strip()
                    elif isinstance(value, str):
                        # Limpa caracteres especiais e espaços
                        cleaned_value = value.strip()
                        # Remove caracteres de controle
                        cleaned_value = ''.join(char for char in cleaned_value if ord(char) >= 32 or char in '\n\r\t')
                        row_dict[column_name] = cleaned_value
                    else:
                        row_dict[column_name] = value if isinstance(value, (int, float, bool)) else str(value)
                        
                data.append(row_dict)
            
            return {
                'columns': columns,
                'data': data,
                'count': len(data),
                'query': query
            }
        finally:
            connection.close()
    
    def execute_custom_query_params(self, query: str, params: List[Any]) -> Dict[str, Any]:
        """Executa uma query customizada parametrizada (apenas SELECT)"""
        connection = self.get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(query, params or [])
            rows = cursor.fetchall()
            
            columns = [desc[0].strip() if desc[0] else f'col_{i}' for i, desc in enumerate(cursor.description)]
            
            data = []
            for row in rows:
                row_dict = {}
                for i, value in enumerate(row):
                    column_name = columns[i]
                    if hasattr(value, 'isoformat'):
                        row_dict[column_name] = value.isoformat()
                    elif value is None:
                        row_dict[column_name] = None
                    elif isinstance(value, bytes):
                        try:
                            row_dict[column_name] = value.decode('utf-8').strip()
                        except UnicodeDecodeError:
                            try:
                                row_dict[column_name] = value.decode('latin1').strip()
                            except UnicodeDecodeError:
                                try:
                                    row_dict[column_name] = value.decode('cp1252').strip()
                                except UnicodeDecodeError:
                                    row_dict[column_name] = str(value, errors='replace').strip()
                    elif isinstance(value, str):
                        cleaned_value = value.strip()
                        cleaned_value = ''.join(char for char in cleaned_value if ord(char) >= 32 or char in '\n\r\t')
                        row_dict[column_name] = cleaned_value
                    else:
                        row_dict[column_name] = value if isinstance(value, (int, float, bool)) else str(value)
                data.append(row_dict)
            
            return {
                'columns': columns,
                'data': data,
                'count': len(data),
                'query': query
            }
        finally:
            connection.close()

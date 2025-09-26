"""
Versão simplificada da API sem dependências complexas
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

# Dados mock para demonstração
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

class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        try:
            if path == '/':
                self.send_json_response({
                    "message": "Firebird Database API - Simple Version",
                    "version": "1.0.0-simple",
                    "mode": "mock",
                    "endpoints": {
                        "health": "/health",
                        "tables": "/tables",
                        "table_data": "/tables/{table_name}",
                        "table_schema": "/tables/{table_name}/schema",
                        "docs": "/docs"
                    }
                })
            
            elif path == '/health':
                self.send_json_response({
                    "status": "healthy",
                    "database": "mock",
                    "mode": "simple",
                    "timestamp": time.time()
                })
            
            elif path == '/tables':
                self.send_json_response({
                    "tables": MOCK_TABLES,
                    "count": len(MOCK_TABLES)
                })
            
            elif path.startswith('/tables/') and path.endswith('/schema'):
                table_name = path.split('/')[2]
                if table_name.upper() in MOCK_COLUMNS:
                    self.send_json_response({
                        "table": table_name,
                        "columns": MOCK_COLUMNS[table_name.upper()]
                    })
                else:
                    self.send_error_response(404, f"Tabela '{table_name}' não encontrada")
            
            elif path.startswith('/tables/'):
                table_name = path.split('/')[2]
                if table_name.upper() in MOCK_DATA:
                    data = MOCK_DATA[table_name.upper()]
                    
                    # Aplicar limit se especificado
                    limit = query_params.get('limit', [None])[0]
                    if limit:
                        try:
                            limit = int(limit)
                            data = data[:limit]
                        except ValueError:
                            pass
                    
                    self.send_json_response({
                        "table": table_name,
                        "columns": list(data[0].keys()) if data else [],
                        "data": data,
                        "count": len(data)
                    })
                else:
                    self.send_error_response(404, f"Tabela '{table_name}' não encontrada")
            
            elif path == '/docs':
                self.send_html_response(self.get_docs_html())
            
            else:
                self.send_error_response(404, "Endpoint não encontrado")
                
        except Exception as e:
            self.send_error_response(500, str(e))
    
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            if self.path == '/query':
                try:
                    data = json.loads(post_data.decode('utf-8'))
                    query = data.get('query', '')
                    
                    if not query.upper().startswith('SELECT'):
                        self.send_error_response(400, "Apenas queries SELECT são permitidas")
                        return
                    
                    # Mock query result
                    self.send_json_response({
                        "columns": ["RESULTADO"],
                        "data": [{"RESULTADO": f"Mock result for: {query[:50]}..."}],
                        "count": 1,
                        "query": query
                    })
                except json.JSONDecodeError:
                    self.send_error_response(400, "JSON inválido")
            else:
                self.send_error_response(404, "Endpoint não encontrado")
                
        except Exception as e:
            self.send_error_response(500, str(e))
    
    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
    
    def send_error_response(self, status, message):
        self.send_json_response({"error": message, "status": status}, status)
    
    def send_html_response(self, html):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def get_docs_html(self):
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Firebird API - Simple Version</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .endpoint { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
                .method { background: #007bff; color: white; padding: 5px 10px; border-radius: 3px; }
                .path { font-family: monospace; background: #f8f9fa; padding: 5px; }
                pre { background: #f8f9fa; padding: 10px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>🔥 Firebird Database API - Simple Version</h1>
            <p>Versão simplificada da API sem dependências complexas</p>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <span class="path">/health</span>
                <p>Verifica status da API</p>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <span class="path">/tables</span>
                <p>Lista todas as tabelas disponíveis</p>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <span class="path">/tables/{table_name}</span>
                <p>Retorna dados de uma tabela específica</p>
                <p>Parâmetros: ?limit=10</p>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <span class="path">/tables/{table_name}/schema</span>
                <p>Retorna estrutura de uma tabela</p>
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span>
                <span class="path">/query</span>
                <p>Executa query customizada (apenas SELECT)</p>
                <pre>{"query": "SELECT * FROM FC07000"}</pre>
            </div>
            
            <h2>Exemplos:</h2>
            <ul>
                <li><a href="/tables">Listar tabelas</a></li>
                <li><a href="/tables/FC07000">Dados da FC07000</a></li>
                <li><a href="/tables/FC07000/schema">Schema da FC07000</a></li>
            </ul>
        </body>
        </html>
        """
    
    def log_message(self, format, *args):
        # Log customizado
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

def run_server():
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), APIHandler)
    print(f"🚀 Firebird API Simple rodando na porta {port}")
    print(f"📖 Documentação: http://localhost:{port}/docs")
    server.serve_forever()

if __name__ == '__main__':
    run_server()
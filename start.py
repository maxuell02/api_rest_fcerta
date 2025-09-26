#!/usr/bin/env python3
"""
Script de inicialização que tenta diferentes abordagens
"""

import os
import sys
import subprocess
import time

def log(message):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def try_fastapi():
    """Tenta iniciar com FastAPI"""
    try:
        log("🚀 Tentando iniciar com FastAPI...")
        
        # Tenta importar FastAPI
        import fastapi
        import uvicorn
        log(f"✅ FastAPI {fastapi.__version__} disponível")
        
        # Tenta importar nossa aplicação
        try:
            from main_with_fallback import app
            log("✅ main_with_fallback importado com sucesso")
            
            port = int(os.environ.get('PORT', 8000))
            log(f"🌐 Iniciando FastAPI na porta {port}")
            
            uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
            return True
            
        except ImportError as e:
            log(f"❌ Erro ao importar main_with_fallback: {e}")
            
            try:
                from main import app
                log("✅ main importado como fallback")
                
                port = int(os.environ.get('PORT', 8000))
                uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
                return True
                
            except ImportError as e2:
                log(f"❌ Erro ao importar main: {e2}")
                return False
                
    except ImportError as e:
        log(f"❌ FastAPI não disponível: {e}")
        return False

def try_simple():
    """Tenta iniciar versão simples"""
    try:
        log("🔄 Iniciando versão simples (sem dependências)...")
        
        # Importa e executa versão simples
        from simple_main import run_server
        run_server()
        return True
        
    except Exception as e:
        log(f"❌ Erro na versão simples: {e}")
        return False

def try_gunicorn():
    """Tenta iniciar com Gunicorn"""
    try:
        log("🔧 Tentando Gunicorn...")
        
        port = os.environ.get('PORT', '8000')
        
        # Tenta diferentes aplicações
        apps_to_try = [
            'main_with_fallback:app',
            'main:app'
        ]
        
        for app_module in apps_to_try:
            try:
                log(f"🧪 Testando {app_module}")
                cmd = [
                    'gunicorn', 
                    app_module,
                    '--bind', f'0.0.0.0:{port}',
                    '--workers', '1',
                    '--timeout', '120',
                    '--access-logfile', '-',
                    '--error-logfile', '-'
                ]
                
                subprocess.run(cmd, check=True)
                return True
                
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                log(f"❌ {app_module} falhou: {e}")
                continue
                
        return False
        
    except Exception as e:
        log(f"❌ Gunicorn não disponível: {e}")
        return False

def main():
    log("🚀 Iniciando Firebird API...")
    log(f"🐍 Python {sys.version}")
    log(f"📁 Diretório: {os.getcwd()}")
    log(f"🌐 PORT: {os.environ.get('PORT', 'não definida')}")
    
    # Lista arquivos disponíveis
    files = [f for f in os.listdir('.') if f.endswith('.py')]
    log(f"📄 Arquivos Python: {files}")
    
    # Tenta diferentes abordagens em ordem de preferência
    approaches = [
        ("FastAPI/Uvicorn", try_fastapi),
        ("Gunicorn", try_gunicorn), 
        ("Versão Simples", try_simple)
    ]
    
    for name, func in approaches:
        log(f"🔄 Tentando abordagem: {name}")
        try:
            if func():
                log(f"✅ {name} iniciado com sucesso!")
                return
        except Exception as e:
            log(f"❌ {name} falhou: {e}")
            continue
    
    # Se chegou aqui, nada funcionou
    log("💥 Todas as abordagens falharam!")
    log("🆘 Iniciando servidor HTTP básico como último recurso...")
    
    try:
        # Servidor HTTP básico do Python
        import http.server
        import socketserver
        
        port = int(os.environ.get('PORT', 8000))
        
        class Handler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/health':
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(b'{"status": "emergency", "message": "Basic HTTP server"}')
                else:
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'<h1>Firebird API - Emergency Mode</h1><p>API em modo de emergencia. Verifique os logs.</p>')
        
        with socketserver.TCPServer(("", port), Handler) as httpd:
            log(f"🆘 Servidor de emergência na porta {port}")
            httpd.serve_forever()
            
    except Exception as e:
        log(f"💀 Falha total: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
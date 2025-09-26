#!/usr/bin/env python3
"""
Script para testar a API localmente
"""

import sys
import os

def test_imports():
    """Testa se os imports funcionam"""
    print("🧪 Testando imports...")
    
    # Teste 1: FastAPI
    try:
        import fastapi
        print(f"✅ FastAPI {fastapi.__version__} disponível")
    except ImportError:
        print("❌ FastAPI não disponível")
    
    # Teste 2: Uvicorn
    try:
        import uvicorn
        print(f"✅ Uvicorn disponível")
    except ImportError:
        print("❌ Uvicorn não disponível")
    
    # Teste 3: FDB
    try:
        import fdb
        print(f"✅ FDB disponível")
    except ImportError:
        print("❌ FDB não disponível (esperado)")
    
    # Teste 4: Nossas aplicações
    apps_to_test = [
        'main_simple_fallback',
        'main_with_fallback', 
        'main',
        'simple_main'
    ]
    
    for app_name in apps_to_test:
        try:
            module = __import__(app_name)
            app = getattr(module, 'app', None)
            if app:
                print(f"✅ {app_name} importado com sucesso")
            else:
                print(f"⚠️ {app_name} importado mas sem 'app'")
        except ImportError as e:
            print(f"❌ {app_name} falhou: {e}")
        except Exception as e:
            print(f"⚠️ {app_name} erro: {e}")

def test_simple_server():
    """Testa o servidor simples"""
    print("\n🚀 Testando servidor simples...")
    
    try:
        from simple_main import APIHandler
        print("✅ simple_main pode ser importado")
        
        # Testa se pode criar handler
        handler = APIHandler
        print("✅ APIHandler pode ser criado")
        
    except Exception as e:
        print(f"❌ Erro no servidor simples: {e}")

def main():
    print("🔍 Teste Local da API Firebird")
    print("=" * 50)
    
    print(f"🐍 Python: {sys.version}")
    print(f"📁 Diretório: {os.getcwd()}")
    
    # Lista arquivos Python
    py_files = [f for f in os.listdir('.') if f.endswith('.py')]
    print(f"📄 Arquivos Python: {py_files}")
    
    test_imports()
    test_simple_server()
    
    print("\n" + "=" * 50)
    print("✅ Teste concluído!")
    print("💡 Para iniciar a API: python start.py")

if __name__ == '__main__':
    main()
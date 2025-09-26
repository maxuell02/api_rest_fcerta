#!/usr/bin/env python3
"""
Script de verificação de saúde para o Render
"""

import requests
import sys
import time

def check_health(url, max_attempts=5, delay=10):
    """Verifica se a API está respondendo"""
    
    for attempt in range(max_attempts):
        try:
            print(f"Tentativa {attempt + 1}/{max_attempts}: Verificando {url}")
            
            response = requests.get(f"{url}/health", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API está online!")
                print(f"Status: {data.get('status')}")
                print(f"Database: {data.get('database')}")
                return True
            else:
                print(f"❌ Status code: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de conexão: {e}")
        
        if attempt < max_attempts - 1:
            print(f"⏳ Aguardando {delay} segundos...")
            time.sleep(delay)
    
    return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python health_check.py <URL_DA_API>")
        print("Exemplo: python health_check.py https://sua-api.onrender.com")
        sys.exit(1)
    
    url = sys.argv[1].rstrip('/')
    
    print("🔍 Verificação de Saúde da API")
    print("=" * 50)
    
    if check_health(url):
        print("\n🎉 API está funcionando corretamente!")
        sys.exit(0)
    else:
        print("\n💥 API não está respondendo")
        sys.exit(1)
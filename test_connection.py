#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para testar a conexão com o banco Firebird e identificar o charset correto
"""

import fdb
import os
from dotenv import load_dotenv

load_dotenv()

def test_firebird_connection():
    """Testa diferentes charsets para encontrar o correto"""
    
    host = os.getenv('DATABASE_HOST')
    database_path = os.getenv('DATABASE_PATH')
    username = os.getenv('DATABASE_USERNAME')
    password = os.getenv('DATABASE_PASSWORD')
    port = int(os.getenv('DATABASE_PORT', 3050))
    
    dsn = f"{host}/{port}:{database_path}"
    
    # Lista de charsets para testar
    charsets = [
        'WIN1252',      # Windows-1252 (mais comum no Brasil)
        'ISO8859_1',    # Latin-1
        'UTF8',         # UTF-8
        'NONE',         # Sem conversão
        'WIN1251',      # Windows-1251
        'DOS850',       # DOS 850
        'DOS437'        # DOS 437
    ]
    
    print(f"🔍 Testando conexão com: {dsn}")
    print("=" * 60)
    
    for charset in charsets:
        try:
            print(f"📡 Testando charset: {charset}")
            
            connection = fdb.connect(
                dsn=dsn,
                user=username,
                password=password,
                charset=charset
            )
            
            cursor = connection.cursor()
            
            # Testa uma query simples
            cursor.execute("SELECT FIRST 1 * FROM FC07000")
            row = cursor.fetchone()
            
            if row:
                print(f"✅ Sucesso com {charset}!")
                print(f"   Dados de exemplo: {row[:3]}...")  # Primeiros 3 campos
                
                # Testa se há caracteres especiais
                for i, value in enumerate(row[:5]):  # Primeiros 5 campos
                    if isinstance(value, str) and value.strip():
                        print(f"   Campo {i}: '{value.strip()}'")
                        break
                
                connection.close()
                return charset
            
            connection.close()
            
        except Exception as e:
            print(f"❌ Falhou com {charset}: {str(e)[:100]}...")
    
    print("\n⚠️  Nenhum charset funcionou completamente")
    return None

def test_query_with_charset(charset):
    """Testa a query específica que estava dando erro"""
    
    host = os.getenv('DATABASE_HOST')
    database_path = os.getenv('DATABASE_PATH')
    username = os.getenv('DATABASE_USERNAME')
    password = os.getenv('DATABASE_PASSWORD')
    port = int(os.getenv('DATABASE_PORT', 3050))
    
    dsn = f"{host}/{port}:{database_path}"
    
    try:
        connection = fdb.connect(
            dsn=dsn,
            user=username,
            password=password,
            charset=charset
        )
        
        cursor = connection.cursor()
        
        # Query que estava dando erro
        query = "SELECT FIRST 50 CDCLI, CDFIL, NOMECLI FROM FC07000 ORDER BY NOMECLI ASC"
        
        print(f"\n🚀 Executando query com charset {charset}:")
        print(f"   {query}")
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        print(f"✅ Query executada com sucesso! {len(rows)} registros encontrados")
        
        # Mostra alguns exemplos
        for i, row in enumerate(rows[:3]):
            print(f"   Registro {i+1}: {row}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro na query: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔥 Teste de Conexão Firebird")
    print("=" * 60)
    
    # Testa conexão
    best_charset = test_firebird_connection()
    
    if best_charset:
        print(f"\n🎯 Melhor charset encontrado: {best_charset}")
        
        # Testa a query específica
        print("\n" + "=" * 60)
        test_query_with_charset(best_charset)
        
        print(f"\n💡 Recomendação: Use charset='{best_charset}' na sua aplicação")
    else:
        print("\n❌ Não foi possível estabelecer conexão com nenhum charset")
        print("💡 Verifique as configurações de conexão no arquivo .env")
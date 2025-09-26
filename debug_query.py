#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para debugar problemas de query SQL
"""

import fdb
import os
from dotenv import load_dotenv

load_dotenv()

def test_query_step_by_step():
    """Testa queries passo a passo para identificar o problema"""
    
    host = os.getenv('DATABASE_HOST')
    database_path = os.getenv('DATABASE_PATH')
    username = os.getenv('DATABASE_USERNAME')
    password = os.getenv('DATABASE_PASSWORD')
    port = int(os.getenv('DATABASE_PORT', 3050))
    charset = os.getenv('DATABASE_CHARSET', 'WIN1252')
    
    dsn = f"{host}/{port}:{database_path}"
    
    print("🔍 Debug de Query SQL")
    print("=" * 60)
    
    try:
        connection = fdb.connect(
            dsn=dsn,
            user=username,
            password=password,
            charset=charset
        )
        
        cursor = connection.cursor()
        
        # Testes progressivos
        queries_to_test = [
            # 1. Query mais simples
            "SELECT FIRST 1 * FROM FC07000",
            
            # 2. Com colunas específicas
            "SELECT FIRST 1 CDCLI, NOMECLI FROM FC07000",
            
            # 3. Com ORDER BY
            "SELECT FIRST 1 CDCLI, NOMECLI FROM FC07000 ORDER BY NOMECLI",
            
            # 4. Com ORDER BY e direção
            "SELECT FIRST 1 CDCLI, NOMECLI FROM FC07000 ORDER BY NOMECLI ASC",
            
            # 5. Com mais registros
            "SELECT FIRST 10 CDCLI, NOMECLI FROM FC07000 ORDER BY NOMECLI ASC",
            
            # 6. Com WHERE simples
            "SELECT FIRST 10 CDCLI, NOMECLI FROM FC07000 WHERE CDCLI > 0 ORDER BY NOMECLI ASC",
            
            # 7. Com alias
            "SELECT FIRST 10 fc1.CDCLI, fc1.NOMECLI FROM FC07000 fc1 ORDER BY fc1.NOMECLI ASC",
        ]
        
        for i, query in enumerate(queries_to_test, 1):
            print(f"\n🧪 Teste {i}: {query}")
            print(f"   Tamanho: {len(query)} caracteres")
            
            try:
                cursor.execute(query)
                rows = cursor.fetchall()
                print(f"   ✅ Sucesso! {len(rows)} registros retornados")
                
                if rows:
                    print(f"   📄 Primeiro registro: {rows[0][:3]}...")
                    
            except Exception as e:
                print(f"   ❌ Erro: {str(e)}")
                print(f"   🔍 Analisando posição do erro...")
                
                # Tentar identificar a posição do erro
                error_str = str(e)
                if "column" in error_str and "line" in error_str:
                    try:
                        # Extrair posição do erro
                        parts = error_str.split("column")
                        if len(parts) > 1:
                            col_part = parts[1].strip()
                            col_num = int(col_part.split()[0])
                            print(f"   📍 Erro na coluna {col_num}")
                            if col_num <= len(query):
                                print(f"   🎯 Caractere: '{query[col_num-1]}'")
                                print(f"   📝 Contexto: '{query[max(0, col_num-10):col_num+10]}'")
                    except:
                        pass
                
                break  # Para no primeiro erro
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Erro de conexão: {str(e)}")

def test_specific_problematic_query():
    """Testa uma query específica que está dando problema"""
    
    # Query que provavelmente está causando o erro
    problematic_query = "SELECT FIRST 50 CDCLI, CDFIL, NOMECLI FROM FC07000 ORDER BY NOMECLI ASC"
    
    print(f"\n🎯 Testando query problemática:")
    print(f"Query: {problematic_query}")
    print(f"Tamanho: {len(problematic_query)}")
    print(f"Posição 93: '{problematic_query[92] if len(problematic_query) > 92 else 'N/A'}'")
    print(f"Contexto 85-100: '{problematic_query[84:100]}'")
    
    host = os.getenv('DATABASE_HOST')
    database_path = os.getenv('DATABASE_PATH')
    username = os.getenv('DATABASE_USERNAME')
    password = os.getenv('DATABASE_PASSWORD')
    port = int(os.getenv('DATABASE_PORT', 3050))
    charset = os.getenv('DATABASE_CHARSET', 'WIN1252')
    
    dsn = f"{host}/{port}:{database_path}"
    
    try:
        connection = fdb.connect(
            dsn=dsn,
            user=username,
            password=password,
            charset=charset
        )
        
        cursor = connection.cursor()
        cursor.execute(problematic_query)
        rows = cursor.fetchall()
        
        print(f"✅ Query executada com sucesso! {len(rows)} registros")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        
        # Tentar variações da query
        variations = [
            "SELECT CDCLI, CDFIL, NOMECLI FROM FC07000 ORDER BY NOMECLI ASC",  # Sem FIRST
            "SELECT FIRST 50 CDCLI, CDFIL, NOMECLI FROM FC07000",  # Sem ORDER BY
            "SELECT FIRST 50 * FROM FC07000 ORDER BY NOMECLI ASC",  # Com *
        ]
        
        print("\n🔄 Tentando variações...")
        
        for i, variation in enumerate(variations, 1):
            print(f"\nVariação {i}: {variation}")
            try:
                connection = fdb.connect(dsn=dsn, user=username, password=password, charset=charset)
                cursor = connection.cursor()
                cursor.execute(variation)
                rows = cursor.fetchall()
                print(f"✅ Variação {i} funcionou! {len(rows)} registros")
                connection.close()
            except Exception as ve:
                print(f"❌ Variação {i} falhou: {str(ve)}")

if __name__ == "__main__":
    test_query_step_by_step()
    print("\n" + "=" * 60)
    test_specific_problematic_query()
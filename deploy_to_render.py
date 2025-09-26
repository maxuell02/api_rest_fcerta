#!/usr/bin/env python3
"""
Script automatizado para deploy no Render
"""

import os
import subprocess
import sys
import time

def run_command(cmd, description):
    """Executa comando e mostra resultado"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Sucesso")
            if result.stdout.strip():
                print(f"   {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - Erro")
            if result.stderr.strip():
                print(f"   {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exceção: {e}")
        return False

def check_files():
    """Verifica se arquivos necessários existem"""
    required_files = [
        'start.py',
        'main_simple_fallback.py', 
        'requirements.txt',
        'render.yaml',
        'Procfile'
    ]
    
    print("📋 Verificando arquivos necessários...")
    all_good = True
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - FALTANDO!")
            all_good = False
    
    return all_good

def check_git():
    """Verifica se está em repositório Git"""
    if os.path.exists('.git'):
        print("✅ Repositório Git encontrado")
        return True
    else:
        print("❌ Não é um repositório Git")
        return False

def show_render_config():
    """Mostra configuração para o Render"""
    print("\n" + "="*60)
    print("🔧 CONFIGURAÇÃO PARA O RENDER")
    print("="*60)
    
    print("\n📝 Build Command:")
    print("pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir fdb || echo 'FDB opcional falhou'")
    
    print("\n🚀 Start Command:")
    print("python start.py")
    
    print("\n🔑 Environment Variables:")
    env_vars = [
        ("DATABASE_HOST", "25.90.252.41"),
        ("DATABASE_PATH", "D:\\sistemas\\fcerta\\DB\\ALTERDB.ib"),
        ("DATABASE_USERNAME", "SYSDBA"),
        ("DATABASE_PASSWORD", "masterkey"),
        ("DATABASE_PORT", "3050"),
        ("DATABASE_CHARSET", "WIN1252")
    ]
    
    for key, value in env_vars:
        print(f"   {key} = {value}")

def main():
    print("🚀 Deploy Automatizado para Render")
    print("="*50)
    
    # Verificar arquivos
    if not check_files():
        print("\n❌ Arquivos necessários estão faltando!")
        print("💡 Execute este script na pasta raiz do projeto")
        return False
    
    # Verificar Git
    if not check_git():
        print("\n❌ Não é um repositório Git!")
        print("💡 Execute: git init")
        return False
    
    # Testar imports localmente
    print("\n🧪 Testando imports localmente...")
    if run_command("python test_local.py", "Teste local"):
        print("✅ Testes locais passaram")
    else:
        print("⚠️ Alguns testes falharam, mas continuando...")
    
    # Verificar status Git
    print("\n📝 Verificando mudanças Git...")
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    
    if result.stdout.strip():
        print("📝 Mudanças detectadas, fazendo commit...")
        
        # Add all files
        if not run_command("git add .", "Adicionando arquivos"):
            return False
        
        # Commit
        commit_msg = f"Deploy: Firebird API corrigida - {time.strftime('%Y-%m-%d %H:%M:%S')}"
        if not run_command(f'git commit -m "{commit_msg}"', "Fazendo commit"):
            return False
    else:
        print("ℹ️ Nenhuma mudança para commit")
    
    # Push para GitHub
    print("\n📤 Enviando para GitHub...")
    if not run_command("git push origin main", "Push para GitHub"):
        print("⚠️ Push falhou. Verifique se o remote está configurado:")
        print("   git remote add origin https://github.com/SEU_USUARIO/firebird-api.git")
        return False
    
    # Mostrar configuração do Render
    show_render_config()
    
    print("\n" + "="*60)
    print("✅ PREPARAÇÃO CONCLUÍDA!")
    print("="*60)
    
    print("\n🎯 PRÓXIMOS PASSOS NO RENDER:")
    print("1. Acesse https://render.com")
    print("2. Clique 'New +' → 'Web Service'")
    print("3. Conecte seu repositório GitHub")
    print("4. Use as configurações mostradas acima")
    print("5. Adicione as Environment Variables")
    print("6. Clique 'Create Web Service'")
    
    print("\n⏱️ Deploy levará ~2-3 minutos")
    print("🔗 URL será: https://firebird-api-xxxx.onrender.com")
    
    print("\n🧪 TESTE APÓS DEPLOY:")
    print("curl https://sua-url.onrender.com/health")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 Pronto para deploy no Render!")
        else:
            print("\n💥 Preparação falhou. Verifique os erros acima.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Cancelado pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro inesperado: {e}")
        sys.exit(1)
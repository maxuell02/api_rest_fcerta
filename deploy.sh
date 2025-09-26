#!/bin/bash

# Script de deploy para Render
# Uso: ./deploy.sh

echo "🚀 Deploy da API Firebird para Render"
echo "====================================="

# Verificar se está em um repositório git
if [ ! -d ".git" ]; then
    echo "❌ Não é um repositório Git. Inicializando..."
    git init
    echo "✅ Repositório Git inicializado"
fi

# Verificar se há mudanças para commit
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 Adicionando arquivos ao Git..."
    git add .
    
    echo "💬 Digite a mensagem do commit (ou pressione Enter para usar padrão):"
    read -r commit_message
    
    if [ -z "$commit_message" ]; then
        commit_message="Deploy: $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    
    git commit -m "$commit_message"
    echo "✅ Commit realizado: $commit_message"
else
    echo "ℹ️  Nenhuma mudança detectada"
fi

# Verificar se há remote configurado
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "❌ Remote 'origin' não configurado"
    echo "💡 Configure manualmente:"
    echo "   git remote add origin https://github.com/SEU_USUARIO/firebird-api.git"
    echo "   git push -u origin main"
    exit 1
fi

# Push para GitHub
echo "📤 Enviando para GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo "✅ Deploy enviado com sucesso!"
    echo ""
    echo "🔗 Próximos passos:"
    echo "1. Acesse https://render.com"
    echo "2. Crie um novo Web Service"
    echo "3. Conecte seu repositório GitHub"
    echo "4. Configure as variáveis de ambiente"
    echo "5. Aguarde o build completar"
    echo ""
    echo "📚 Guia completo: DEPLOY_RENDER.md"
else
    echo "❌ Erro no push. Verifique sua configuração Git"
    exit 1
fi
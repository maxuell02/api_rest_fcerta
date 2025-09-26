@echo off
echo 🚀 Deploy da API Firebird para Render
echo =====================================

REM Verificar se está em um repositório git
if not exist ".git" (
    echo ❌ Não é um repositório Git. Inicializando...
    git init
    echo ✅ Repositório Git inicializado
)

REM Adicionar arquivos
echo 📝 Adicionando arquivos ao Git...
git add .

REM Commit
set /p commit_message="💬 Digite a mensagem do commit (ou pressione Enter para usar padrão): "
if "%commit_message%"=="" (
    for /f "tokens=1-4 delims=/ " %%i in ('date /t') do set mydate=%%i-%%j-%%k
    for /f "tokens=1-2 delims=: " %%i in ('time /t') do set mytime=%%i:%%j
    set commit_message=Deploy: !mydate! !mytime!
)

git commit -m "%commit_message%"
echo ✅ Commit realizado: %commit_message%

REM Push para GitHub
echo 📤 Enviando para GitHub...
git push origin main

if %errorlevel% equ 0 (
    echo ✅ Deploy enviado com sucesso!
    echo.
    echo 🔗 Próximos passos:
    echo 1. Acesse https://render.com
    echo 2. Crie um novo Web Service
    echo 3. Conecte seu repositório GitHub
    echo 4. Configure as variáveis de ambiente
    echo 5. Aguarde o build completar
    echo.
    echo 📚 Guia completo: DEPLOY_RENDER.md
) else (
    echo ❌ Erro no push. Verifique sua configuração Git
    pause
)

pause
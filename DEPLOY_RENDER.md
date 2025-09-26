# 🚀 Deploy da API Firebird no Render

## 📋 Pré-requisitos

- ✅ Conta no GitHub
- ✅ Conta no Render (gratuita)
- ✅ Banco Firebird acessível pela internet
- ✅ Código da API pronto

## 🔧 Passo a Passo Completo

### **1. Preparar o Repositório GitHub**

#### 1.1 Criar repositório no GitHub
```bash
# No GitHub, criar novo repositório (ex: firebird-api)
# Não inicializar com README (já temos os arquivos)
```

#### 1.2 Inicializar Git local
```bash
git init
git add .
git commit -m "Initial commit - Firebird API"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/firebird-api.git
git push -u origin main
```

### **2. Configurar o Render**

#### 2.1 Acessar o Render
1. Vá para [render.com](https://render.com)
2. Faça login ou crie conta gratuita
3. Conecte sua conta GitHub

#### 2.2 Criar novo Web Service
1. Clique em **"New +"**
2. Selecione **"Web Service"**
3. Conecte seu repositório GitHub
4. Selecione o repositório `firebird-api`

#### 2.3 Configurar o Service
```yaml
Name: firebird-api
Environment: Python 3
Region: Oregon (US West) # ou mais próximo do seu banco
Branch: main
Build Command: pip install -r requirements.txt
Start Command: gunicorn main:app -c gunicorn.conf.py
```

### **3. Configurar Variáveis de Ambiente**

No painel do Render, adicione as seguintes variáveis:

| Variável | Valor | Descrição |
|----------|-------|-----------|
| `DATABASE_HOST` | `25.90.252.41` | IP do servidor Firebird |
| `DATABASE_PATH` | `D:\sistemas\fcerta\DB\ALTERDB.ib` | Caminho do banco |
| `DATABASE_USERNAME` | `SYSDBA` | Usuário do banco |
| `DATABASE_PASSWORD` | `masterkey` | Senha do banco |
| `DATABASE_PORT` | `3050` | Porta do Firebird |
| `DATABASE_CHARSET` | `WIN1252` | Charset do banco |
| `PORT` | `10000` | Porta do Render |

### **4. Deploy Automático**

#### 4.1 Iniciar Deploy
1. Clique em **"Create Web Service"**
2. O Render iniciará o build automaticamente
3. Acompanhe os logs em tempo real

#### 4.2 Verificar Build
```bash
# Logs esperados:
==> Building...
==> Installing dependencies from requirements.txt
==> Build completed successfully
==> Starting service...
==> Service is live at https://firebird-api-xxxx.onrender.com
```

### **5. Testar a API**

#### 5.1 Verificar Health Check
```bash
# Substitua pela sua URL do Render
curl https://firebird-api-xxxx.onrender.com/health
```

#### 5.2 Usar script de verificação
```bash
python health_check.py https://firebird-api-xxxx.onrender.com
```

#### 5.3 Testar endpoints
```bash
# Listar tabelas
curl https://firebird-api-xxxx.onrender.com/tables

# Documentação automática
https://firebird-api-xxxx.onrender.com/docs
```

## 🔧 Configurações Avançadas

### **Domínio Customizado**
1. No painel do Render, vá em **Settings**
2. Adicione seu domínio em **Custom Domains**
3. Configure DNS conforme instruções

### **Monitoramento**
```bash
# Logs em tempo real
render logs --service firebird-api

# Status do serviço
render status --service firebird-api
```

### **Auto-Deploy**
- ✅ Já configurado automaticamente
- Cada push para `main` faz novo deploy
- Deploy leva ~2-5 minutos

## 🚨 Solução de Problemas

### **Build Failed**
```bash
# Verificar requirements.txt
pip install -r requirements.txt

# Testar localmente
python main.py
```

### **Service Won't Start**
1. Verificar variáveis de ambiente
2. Testar conexão com banco
3. Verificar logs do Render

### **Database Connection Failed**
1. Verificar se IP está correto
2. Testar porta 3050 aberta
3. Verificar firewall do servidor

### **Timeout Issues**
- Render free tier tem timeout de 15min inatividade
- Primeira requisição pode ser lenta (cold start)
- Use plano pago para melhor performance

## 📊 Monitoramento

### **URLs Importantes**
```bash
# API Base
https://firebird-api-xxxx.onrender.com

# Health Check
https://firebird-api-xxxx.onrender.com/health

# Documentação
https://firebird-api-xxxx.onrender.com/docs

# Painel Render
https://dashboard.render.com
```

### **Métricas Disponíveis**
- ✅ CPU Usage
- ✅ Memory Usage  
- ✅ Response Time
- ✅ Request Count
- ✅ Error Rate

## 🔄 Atualizações

### **Deploy Manual**
```bash
git add .
git commit -m "Update API"
git push origin main
# Deploy automático iniciará
```

### **Rollback**
1. No painel Render, vá em **Deploys**
2. Clique em deploy anterior
3. Selecione **"Redeploy"**

## 💰 Custos

### **Plano Free**
- ✅ 750 horas/mês
- ✅ Sleep após 15min inatividade
- ✅ Perfeito para testes

### **Plano Starter ($7/mês)**
- ✅ Sem sleep
- ✅ Melhor performance
- ✅ Recomendado para produção

## 🆘 Suporte

### **Documentação Oficial**
- [Render Docs](https://render.com/docs)
- [Python on Render](https://render.com/docs/deploy-fastapi)

### **Comunidade**
- [Render Community](https://community.render.com)
- [GitHub Issues](https://github.com/render-examples)

### **Logs e Debug**
```bash
# Ver logs em tempo real
https://dashboard.render.com/web/srv-xxxxx/logs

# Download logs
render logs --service firebird-api --download
```

---

## ✅ Checklist Final

- [ ] Repositório GitHub criado e configurado
- [ ] Render Web Service criado
- [ ] Variáveis de ambiente configuradas
- [ ] Build completado com sucesso
- [ ] Health check respondendo
- [ ] Endpoints funcionando
- [ ] Documentação acessível
- [ ] Monitoramento configurado

🎉 **Sua API Firebird está no ar!**
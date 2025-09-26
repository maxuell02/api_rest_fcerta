# ⚡ Render - Guia Rápido (5 minutos)

## 🚀 Passo 1: Preparar (2 min)

### **Executar script automático:**
```bash
python deploy_to_render.py
```

**OU manualmente:**
```bash
git add .
git commit -m "Deploy: API Firebird corrigida"
git push origin main
```

---

## 🔧 Passo 2: Render (2 min)

### **1. Acessar Render**
- Vá para [render.com](https://render.com)
- Login/Cadastro gratuito
- Conectar GitHub

### **2. Criar Web Service**
- **New +** → **Web Service**
- Selecionar repositório `firebird-api`
- **Connect**

### **3. Configuração Rápida**
```
Name: firebird-api
Environment: Python 3
Branch: main

Build Command:
pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir fdb || echo "FDB opcional"

Start Command:
python start.py
```

### **4. Environment Variables**
```
DATABASE_HOST = 25.90.252.41
DATABASE_PATH = D:\sistemas\fcerta\DB\ALTERDB.ib
DATABASE_USERNAME = SYSDBA
DATABASE_PASSWORD = masterkey
DATABASE_PORT = 3050
DATABASE_CHARSET = WIN1252
```

### **5. Deploy**
- **Create Web Service**
- Aguardar 2-3 minutos

---

## ✅ Passo 3: Testar (1 min)

### **Health Check:**
```bash
curl https://firebird-api-xxxx.onrender.com/health
```

### **Resposta esperada:**
```json
{
  "status": "healthy",
  "mode": "simple-fastapi", 
  "database": "mock"
}
```

### **Documentação:**
```
https://firebird-api-xxxx.onrender.com/docs
```

---

## 🎯 Resultado

**✅ API funcionando em 5 minutos!**

- 🔗 URL pública disponível
- 📊 Dados mock funcionando
- 📖 Documentação automática
- 🔄 Deploy automático configurado

---

## 🚨 Se algo der errado

### **Build Failed:**
- Verificar se `requirements.txt` existe
- Logs no painel Render

### **Service Won't Start:**
- Verificar se `start.py` existe
- Confirmar start command: `python start.py`

### **API não responde:**
- Aguardar 2-3 minutos (cold start)
- Testar `/health` primeiro

### **Modo emergência:**
- Normal no primeiro deploy
- Verificar logs detalhados

---

## 📞 Suporte Rápido

**Comandos úteis:**
```bash
# Testar local
python start.py

# Verificar arquivos
python test_local.py

# Novo deploy
git add . && git commit -m "Update" && git push
```

**Links úteis:**
- [Dashboard Render](https://dashboard.render.com)
- [Logs em tempo real](https://dashboard.render.com/web/srv-xxxxx/logs)
- [Documentação Render](https://render.com/docs)

---

## 🎉 Pronto!

**Sua API Firebird está no ar!** 🚀

**Próximos passos:**
1. Testar todos os endpoints
2. Configurar domínio customizado (opcional)
3. Upgrade para plano pago (opcional)
4. Integrar com aplicações frontend
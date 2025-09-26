# 🚨 Solução de Problemas - Render Deploy

## ❌ Erro: Pydantic Build Failed

### **Problema:**
```
error: metadata-generation-failed
× Encountered error while generating package metadata.
pydantic_core-2.14.1.tar.gz
Read-only file system (os error 30)
```

### **Causa:**
Pydantic v2 precisa compilar código Rust, mas o Render não tem permissões de escrita.

### **✅ Solução:**
Use versões compatíveis no `requirements.txt`:

```txt
fastapi==0.88.0
uvicorn==0.20.0
fdb==2.0.2
python-dotenv==1.0.0
pydantic==1.10.4
gunicorn==20.1.0
```

---

## ❌ Erro: FDB Installation Failed

### **Problema:**
```
ERROR: Failed building wheel for fdb
```

### **Causa:**
FDB precisa de bibliotecas C++ do Firebird que podem não estar disponíveis.

### **✅ Soluções:**

#### **Opção 1: Usar versão com fallback**
```yaml
# render.yaml
startCommand: gunicorn main_with_fallback:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

#### **Opção 2: Requirements alternativos**
```txt
# requirements-alternative.txt
fastapi==0.88.0
uvicorn==0.20.0
firebirdsql==1.2.2  # Alternativa ao FDB
python-dotenv==1.0.0
pydantic==1.10.4
gunicorn==20.1.0
```

#### **Opção 3: Usar Docker**
```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y firebird-dev gcc g++
COPY requirements.txt .
RUN pip install -r requirements.txt
```

---

## ❌ Erro: Service Won't Start

### **Problema:**
```
==> Build completed successfully
==> Starting service...
==> Service failed to start
```

### **Causa:**
Erro na inicialização da aplicação.

### **✅ Diagnóstico:**

#### **1. Verificar logs:**
```bash
# No painel Render
Dashboard > Service > Logs
```

#### **2. Testar localmente:**
```bash
python main_with_fallback.py
# Deve mostrar: "✅ Usando database real" ou "🔄 Usando database mock"
```

#### **3. Verificar variáveis:**
```bash
# No Render, verificar se todas estão definidas:
DATABASE_HOST=25.90.252.41
DATABASE_PATH=D:\sistemas\fcerta\DB\ALTERDB.ib
DATABASE_USERNAME=SYSDBA
DATABASE_PASSWORD=masterkey
DATABASE_PORT=3050
DATABASE_CHARSET=WIN1252
```

---

## ❌ Erro: Database Connection Failed

### **Problema:**
```
Database connection failed: Error connecting to database
```

### **Causa:**
Banco Firebird não acessível ou configuração incorreta.

### **✅ Soluções:**

#### **1. Verificar conectividade:**
```bash
# Testar se porta está aberta
telnet 25.90.252.41 3050
```

#### **2. Verificar firewall:**
- Liberar porta 3050 no servidor Firebird
- Permitir conexões externas

#### **3. Usar modo mock temporário:**
```python
# Força uso do mock para teste
from database_mock import FirebirdDatabase
```

---

## ❌ Erro: Build Timeout

### **Problema:**
```
==> Build timed out after 15 minutes
```

### **Causa:**
Build muito lento ou travado.

### **✅ Soluções:**

#### **1. Otimizar requirements:**
```txt
# Versões específicas e leves
fastapi==0.88.0
uvicorn==0.20.0
gunicorn==20.1.0
```

#### **2. Usar cache:**
```yaml
buildCommand: |
  pip install --upgrade pip
  pip install --no-cache-dir -r requirements.txt
```

#### **3. Build em etapas:**
```yaml
buildCommand: |
  pip install fastapi uvicorn gunicorn
  pip install -r requirements.txt
```

---

## 🔧 Configurações Recomendadas

### **render.yaml otimizado:**
```yaml
services:
  - type: web
    name: firebird-api
    env: python
    plan: free
    buildCommand: |
      pip install --upgrade pip
      pip install --no-cache-dir fastapi==0.88.0 uvicorn==0.20.0 gunicorn==20.1.0
      pip install --no-cache-dir python-dotenv pydantic==1.10.4
      pip install --no-cache-dir fdb || echo "FDB failed, using fallback"
    startCommand: gunicorn main_with_fallback:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.5
```

### **runtime.txt:**
```
python-3.11.5
```

---

## 🧪 Testes de Validação

### **1. Health Check:**
```bash
curl https://sua-api.onrender.com/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "database": "connected",
  "mode": "real"  // ou "mock"
}
```

### **2. Listar tabelas:**
```bash
curl https://sua-api.onrender.com/tables
```

### **3. Documentação:**
```
https://sua-api.onrender.com/docs
```

---

## 🚀 Deploy Alternativo

### **Se nada funcionar, use Heroku:**

#### **1. Criar Procfile:**
```
web: gunicorn main_with_fallback:app --bind 0.0.0.0:$PORT
```

#### **2. Deploy:**
```bash
heroku create firebird-api
git push heroku main
```

### **Ou use Railway:**

#### **1. Conectar GitHub**
#### **2. Deploy automático**
#### **3. Configurar variáveis**

---

## 📞 Suporte

### **Logs úteis:**
```bash
# Render Dashboard
https://dashboard.render.com/web/srv-xxxxx/logs

# Download logs
render logs --service firebird-api --download
```

### **Comunidade:**
- [Render Community](https://community.render.com)
- [FastAPI Discord](https://discord.gg/VQjSZaeJmf)
- [GitHub Issues](https://github.com/render-examples)

### **Alternativas:**
- **Heroku** (mais estável, pago)
- **Railway** (similar ao Render)
- **Vercel** (para APIs simples)
- **DigitalOcean App Platform**

---

## ✅ Checklist de Deploy

- [ ] Python 3.11 especificado
- [ ] Pydantic v1.x (não v2)
- [ ] FDB com fallback para mock
- [ ] Variáveis de ambiente configuradas
- [ ] Health check funcionando
- [ ] Logs sem erros
- [ ] Endpoints respondendo
- [ ] Documentação acessível

🎉 **Deploy bem-sucedido!**
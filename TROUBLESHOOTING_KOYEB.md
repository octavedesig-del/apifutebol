# 🔧 GUIA DE SOLUÇÃO DE ERROS - KOYEB DEPLOY

## ❌ Erro: "Falha ao compilar aplicativo"

### SOLUÇÃO RÁPIDA - Checklist

1. **Arquivos Necessários** ✅
   ```
   ✓ app.py (não api.py!)
   ✓ requirements.txt
   ✓ Procfile
   ✓ runtime.txt (opcional)
   ✓ .gitignore
   ```

2. **Estrutura Mínima do Repositório**
   ```
   seu-repo/
   ├── app.py              ← IMPORTANTE: nome correto!
   ├── requirements.txt    ← Sem flashscore
   ├── Procfile           ← Referência: app:app
   └── runtime.txt        ← python-3.11.7
   ```

3. **Conteúdo Correto dos Arquivos**

### ✅ requirements.txt (CORRETO)
```
Flask==3.0.0
Flask-CORS==4.0.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
requests==2.31.0
gunicorn==21.2.0
```

**IMPORTANTE**: 
- ❌ NÃO incluir `flashscore` (não existe no PyPI)
- ✅ Usar versões específicas (não `>=`)

### ✅ Procfile (CORRETO)
```
web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --log-level info
```

**Detalhes**:
- `app:app` significa: arquivo `app.py`, objeto `app`
- `$PORT` é fornecido automaticamente pelo Koyeb
- `--workers 2` para tier gratuito

### ✅ runtime.txt (OPCIONAL mas recomendado)
```
python-3.11.7
```

### ✅ .gitignore
```
__pycache__/
*.pyc
.env
*.log
venv/
```

---

## 🔍 DIAGNÓSTICO DO ERRO

### Erro 1: "Package not found"
**Causa**: Pacote no requirements.txt não existe ou nome errado

**Solução**:
```bash
# Remover flashscore do requirements.txt
# Ele não existe no PyPI oficial

# requirements.txt correto:
Flask==3.0.0
Flask-CORS==4.0.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
requests==2.31.0
gunicorn==21.2.0
```

### Erro 2: "Application failed to start"
**Causa**: Nome do arquivo ou objeto Flask incorreto

**Solução**:
```python
# Arquivo: app.py (não api.py)
from flask import Flask

app = Flask(__name__)  # Nome deve ser 'app'

@app.route('/')
def home():
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run()
```

### Erro 3: "No module named 'api'"
**Causa**: Procfile referencia arquivo errado

**Solução**:
```
# Procfile correto:
web: gunicorn app:app --bind 0.0.0.0:$PORT
```

### Erro 4: "Could not detect buildpack"
**Causa**: Falta requirements.txt ou está em local errado

**Solução**:
- Certifique-se que `requirements.txt` está na **raiz** do repositório
- Não em subpastas

---

## 🚀 PASSO A PASSO PARA CORRIGIR

### 1. Verificar Estrutura Local

```bash
# No seu projeto local
ls -la

# Deve mostrar:
# app.py
# requirements.txt
# Procfile
# runtime.txt
```

### 2. Renomear Arquivo (se necessário)

```bash
# Se você tem api.py, renomeie para app.py
mv api.py app.py

# Atualize o Procfile
echo "web: gunicorn app:app --bind 0.0.0.0:\$PORT" > Procfile
```

### 3. Validar requirements.txt

```bash
# Testar instalação local
pip install -r requirements.txt

# Se flashscore falhar, remova do requirements.txt
# Você pode coletar dados localmente e popular o banco
```

### 4. Testar Localmente

```bash
# Testar se a app inicia
python app.py

# Testar com gunicorn (como no Koyeb)
gunicorn app:app --bind 0.0.0.0:8000

# Acessar: http://localhost:8000
```

### 5. Commit e Push

```bash
git add .
git commit -m "Fix: Configuração correta para Koyeb"
git push origin main
```

### 6. Redeploy no Koyeb

1. Vá no dashboard do Koyeb
2. Selecione seu serviço
3. Clique em "Redeploy"
4. Aguarde o build (~3-5 minutos)

---

## 🎯 CONFIGURAÇÃO KOYEB CORRETA

### Build Settings
```
Builder: Buildpack
Build command: (deixe vazio)
Run command: (será lido do Procfile)
```

### Environment Variables
```
DATABASE_URL = postgresql://user:pass@host.neon.tech/db?sslmode=require
ENVIRONMENT = production
PORT = (deixe vazio - Koyeb configura automaticamente)
```

### Instance Settings
```
Region: Washington DC (ou mais próximo)
Instance type: Nano (gratuito)
Scaling: 1 instance
```

---

## 📝 CHECKLIST PRÉ-DEPLOY

Antes de fazer deploy, verifique:

- [ ] Arquivo principal é `app.py` (não `api.py`)
- [ ] `requirements.txt` não tem `flashscore`
- [ ] `requirements.txt` tem versões específicas
- [ ] `Procfile` referencia `app:app`
- [ ] `runtime.txt` tem versão Python válida
- [ ] `.gitignore` não bloqueia arquivos importantes
- [ ] Testado localmente com `python app.py`
- [ ] Testado com gunicorn: `gunicorn app:app`
- [ ] DATABASE_URL configurada no Koyeb
- [ ] Repositório no GitHub atualizado

---

## 🗄️ SOBRE O FLASHSCORE

**Por que não usar flashscore no deploy?**

1. `flashscore` não está disponível no PyPI oficial
2. Coleta de dados é intensiva e pode exceder limites
3. Melhor estratégia: coletar dados **localmente** e popular o banco

**Workflow Recomendado**:

```bash
# Local - Coletar dados
pip install flashscore  # Instalar de fonte alternativa
python populate_database.py  # Popular banco Neon

# Deploy - Apenas servir dados
# requirements.txt sem flashscore
# API apenas lê do banco PostgreSQL
```

---

## 🆘 AINDA TEM ERRO?

### Ver Logs do Koyeb

1. Dashboard → Seu Serviço
2. Aba "Logs"
3. Procure por:
   - `ERROR`
   - `FAILED`
   - `could not find`

### Testar Connection String

```python
# test_db.py
import psycopg2
import os

DATABASE_URL = "sua_connection_string"

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("✓ Conexão OK!")
    conn.close()
except Exception as e:
    print(f"✗ Erro: {e}")
```

### Validar Estrutura do Banco

```sql
-- No console do Neon.tech
SELECT COUNT(*) FROM matches;
SELECT COUNT(*) FROM leagues;

-- Se retornar 0, precisa popular o banco
```

---

## 💡 DICAS FINAIS

1. **Mantenha Simples**: API básica primeiro, features depois
2. **Teste Local**: Sempre teste antes de fazer push
3. **Logs São Seus Amigos**: Leia os logs do Koyeb
4. **Versões Específicas**: Sempre use versões fixas no requirements.txt
5. **Um Arquivo por Vez**: Faça mudanças incrementais

---

## ✅ CONFIGURAÇÃO FUNCIONANDO

Se tudo estiver correto, você verá no Koyeb:

```
✓ Building...
✓ Installing dependencies...
✓ Starting web process...
✓ Health check passed
✓ Service is healthy
```

E ao acessar `https://seu-app.koyeb.app`:

```json
{
  "name": "Football Data API",
  "version": "1.0.0",
  "status": "online"
}
```

---

## 📞 PRECISA DE MAIS AJUDA?

1. Verifique logs do Koyeb
2. Teste cada arquivo individualmente
3. Compare com os arquivos de exemplo fornecidos
4. Use versão mínima primeiro (só Flask + PostgreSQL)

Boa sorte! 🚀

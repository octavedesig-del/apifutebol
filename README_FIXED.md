# ⚽ Football Data API - Deploy Koyeb (VERSÃO CORRIGIDA)

> **SOLUÇÃO PARA ERRO DE BUILD NO KOYEB** ✅

## 🎯 O QUE FOI CORRIGIDO

### Problema Original
❌ Erro ao compilar aplicativo no Koyeb devido a:
- `flashscore` não disponível no PyPI
- Nome de arquivo incorreto (`api.py` vs `app.py`)
- Dependências incompatíveis

### Solução Implementada
✅ API otimizada para Koyeb com:
- Arquivo `app.py` (padrão Flask)
- `requirements.txt` apenas com pacotes oficiais
- Configuração testada e funcional

---

## 📦 ARQUIVOS ESSENCIAIS

### 1. app.py
API Flask completa que **apenas serve dados** do PostgreSQL (não coleta).

### 2. requirements.txt
```
Flask==3.0.0
Flask-CORS==4.0.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
requests==2.31.0
gunicorn==21.2.0
```
**SEM `flashscore`** - coleta é feita localmente!

### 3. Procfile
```
web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --log-level info
```

### 4. runtime.txt
```
python-3.11.7
```

---

## 🚀 DEPLOY EM 3 PASSOS

### PASSO 1: Preparar Banco de Dados (LOCALMENTE)

```bash
# 1. Criar banco no Neon.tech e copiar connection string

# 2. Criar .env local
echo "DATABASE_URL=postgresql://user:pass@host.neon.tech/db" > .env

# 3. Instalar dependências locais (incluindo flashscore)
pip install Flask Flask-CORS psycopg2-binary python-dotenv flashscore

# 4. Criar schema
python create_database.py

# 5. Popular banco (30-60 min)
python populate_database.py
```

### PASSO 2: Preparar Código para Deploy

```bash
# 1. Certifique-se que tem estes arquivos:
ls -la
# Deve mostrar:
# - app.py (não api.py!)
# - requirements.txt (sem flashscore)
# - Procfile
# - runtime.txt
# - .gitignore

# 2. Testar localmente
python app.py
# Deve iniciar em http://localhost:8000

# 3. Testar com gunicorn
gunicorn app:app --bind 0.0.0.0:8000
```

### PASSO 3: Deploy no Koyeb

```bash
# 1. Criar repositório GitHub
git init
git add app.py requirements.txt Procfile runtime.txt .gitignore
git commit -m "Deploy: Football Data API"
git remote add origin https://github.com/SEU_USER/SEU_REPO.git
git push -u origin main

# 2. No Koyeb:
# - Create Service
# - GitHub source
# - Selecione repositório
# - Configure ENV vars:
#   DATABASE_URL = sua_connection_string_neon
#   ENVIRONMENT = production
# - Deploy!
```

---

## ✅ CHECKLIST PRÉ-DEPLOY

- [ ] Banco criado no Neon.tech ✓
- [ ] Schema criado (`create_database.py`) ✓
- [ ] Dados populados (`populate_database.py`) ✓
- [ ] Arquivo principal é `app.py` (não `api.py`) ✓
- [ ] `requirements.txt` **SEM** `flashscore` ✓
- [ ] `Procfile` referencia `app:app` ✓
- [ ] Testado localmente com `python app.py` ✓
- [ ] Testado com `gunicorn app:app` ✓
- [ ] `.gitignore` não bloqueia arquivos importantes ✓
- [ ] Código no GitHub ✓
- [ ] `DATABASE_URL` configurada no Koyeb ✓

---

## 📡 ENDPOINTS DA API

```
GET /                                      → Info da API
GET /health                                → Health check
GET /api/leagues                           → Todas as ligas
GET /api/leagues/<id>/seasons              → Temporadas
GET /api/matches                           → Listar partidas
GET /api/matches?league_id=brasileirao     → Filtrar por liga
GET /api/matches?season=2023               → Filtrar por temporada
GET /api/matches/<id>                      → Detalhes partida
GET /api/standings/<league>/<season>       → Classificação
GET /api/teams                             → Listar times
GET /api/search?q=termo                    → Busca geral
```

---

## 🧪 TESTAR APÓS DEPLOY

```bash
# Substituir pela sua URL do Koyeb
export API_URL="https://seu-app.koyeb.app"

# Health check
curl $API_URL/health

# Listar ligas
curl $API_URL/api/leagues

# Partidas do Brasileirão 2023
curl "$API_URL/api/matches?league_id=brasileirao&season=2023&limit=5"

# Classificação
curl $API_URL/api/standings/brasileirao/2023
```

---

## ⚠️ IMPORTANTE: ESTRATÉGIA DE DADOS

### Por que NÃO coletar no deploy?

1. **flashscore não está no PyPI** - dificulta build
2. **Coleta é lenta** - timeout no Koyeb
3. **Limites do free tier** - pode exceder
4. **Melhor separar** - coleta local, deploy só serve dados

### Workflow Recomendado

```
LOCAL (seu computador)
  ├─ Instalar flashscore
  ├─ Coletar dados (populate_database.py)
  └─ Popular banco Neon ✓

KOYEB (cloud)
  ├─ Apenas app.py (sem flashscore)
  ├─ Conecta ao Neon
  └─ Serve dados via API ✓
```

---

## 🐛 AINDA TEM ERRO?

Veja o guia completo: **TROUBLESHOOTING_KOYEB.md**

### Erros Comuns

**Build Failed**
→ Verifique `requirements.txt` (sem flashscore)
→ Arquivo deve ser `app.py` (não `api.py`)

**App Crashed**
→ Verifique logs no Koyeb
→ Teste `DATABASE_URL` está correta

**404 Not Found**
→ Verifique Procfile: `app:app`
→ Arquivo `app.py` existe?

---

## 💻 ESTRUTURA DO PROJETO

```
football-api/
├── app.py                       ← API Flask principal
├── requirements.txt             ← Dependências (sem flashscore)
├── Procfile                     ← Config Koyeb
├── runtime.txt                  ← Versão Python
├── .gitignore                   ← Arquivos ignorados
├── create_database.py           ← Criar schema (local)
├── populate_database.py         ← Popular dados (local)
├── TROUBLESHOOTING_KOYEB.md    ← Guia de erros
└── README.md                    ← Este arquivo
```

---

## 📊 DADOS DISPONÍVEIS

Após popular o banco localmente:

- **11 Campeonatos**: Brasileirão, Copa do Brasil, Paulista, Carioca, Premier League, La Liga, Serie A, Bundesliga, Ligue 1, Champions, Europa League
- **3 Anos**: 2022, 2023, 2024
- **Milhares de partidas** com estatísticas completas

---

## 🎉 SUCESSO!

Se tudo funcionou, você verá:

```bash
$ curl https://seu-app.koyeb.app/health

{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-02-11T22:00:00"
}
```

**Sua API está no ar!** 🚀

URL: `https://seu-app.koyeb.app`

---

## 📚 Documentação Adicional

- `TROUBLESHOOTING_KOYEB.md` - Solução de problemas
- `DEPLOY_GUIDE.md` - Guia completo passo a passo
- `create_database.py` - Script criação banco
- `populate_database.py` - Script população dados

---

## 🤝 Contribuindo

Encontrou um bug? Abra uma issue!
Melhorias? Pull requests são bem-vindos!

---

**Desenvolvido para ser simples, funcional e gratuito** ⚽🚀

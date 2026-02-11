# 🚀 GUIA DE DEPLOY - KOYEB + NEON.TECH

## 📋 Visão Geral

Este guia vai te ensinar a fazer deploy da sua API REST de dados de futebol usando:
- **Koyeb**: Hospedagem da API (gratuito)
- **Neon.tech**: Banco de dados PostgreSQL (gratuito)
- **FlashscoreApi**: Coleta de dados de futebol

---

## 🗄️ PARTE 1: Configurar Neon.tech (Banco de Dados)

### Passo 1: Criar conta no Neon.tech

1. Acesse: https://neon.tech
2. Clique em "Sign Up" e crie sua conta (use GitHub para facilitar)
3. Confirme seu email

### Passo 2: Criar um novo projeto

1. No dashboard, clique em "Create Project"
2. Escolha:
   - **Project name**: `football-data-db` (ou outro nome)
   - **Region**: Escolha o mais próximo (ex: US East)
   - **PostgreSQL version**: 16 (recomendado)
3. Clique em "Create Project"

### Passo 3: Obter connection string

1. Após criar o projeto, você verá a connection string
2. Copie a connection string que começa com `postgresql://`
3. Exemplo:
   ```
   postgresql://neondb_owner:npg_XXXXXXXXXXXX@ep-XXXXXXXX.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
4. **GUARDE ESSA STRING** - você vai precisar dela!

### Passo 4: Criar arquivo .env local

Crie um arquivo `.env` na raiz do projeto:

```bash
DATABASE_URL=postgresql://sua_connection_string_aqui
PORT=8000
ENVIRONMENT=development
```

---

## 🏗️ PARTE 2: Criar o Schema do Banco de Dados

### Passo 1: Instalar dependências localmente

```bash
pip install -r requirements_deploy.txt
```

### Passo 2: Criar as tabelas

Execute o script de criação do banco:

```bash
python create_database.py
```

Você verá:
```
Criando schema do banco de dados...
✓ Tabela 'leagues' criada
✓ Tabela 'teams' criada
✓ Tabela 'matches' criada
✓ Tabela 'match_stats' criada
✓ Tabela 'standings' criada
✓ Tabela 'team_stats' criada
✓ Índices criados
✅ Schema do banco de dados criado com sucesso!
```

---

## 📊 PARTE 3: Popular o Banco com Dados

### Passo 1: Executar script de população

```bash
python populate_database.py
```

Este processo vai:
- Coletar dados de 2022, 2023 e 2024
- De todos os 11 campeonatos
- Inserir no banco de dados Neon

**IMPORTANTE**: Esse processo pode levar 30-60 minutos! Deixe rodando.

### Passo 2: Verificar dados

Acesse o console do Neon.tech e execute:

```sql
SELECT COUNT(*) FROM matches;
SELECT COUNT(*) FROM teams;
SELECT COUNT(*) FROM leagues;
```

---

## ☁️ PARTE 4: Deploy no Koyeb

### Passo 1: Preparar seu código

1. Certifique-se de que todos os arquivos estão prontos:
   - `api.py`
   - `requirements_deploy.txt`
   - `Procfile`
   - `runtime.txt`

2. Crie um repositório no GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/seu-usuario/seu-repo.git
   git push -u origin main
   ```

### Passo 2: Criar conta no Koyeb

1. Acesse: https://www.koyeb.com
2. Clique em "Sign Up" (use GitHub para facilitar)
3. Confirme sua conta

### Passo 3: Criar um novo serviço

1. No dashboard do Koyeb, clique em "Create Service"
2. Escolha "GitHub" como fonte
3. Selecione seu repositório
4. Configure:
   - **Builder**: Buildpack
   - **Build command**: (deixe vazio)
   - **Run command**: (será lido do Procfile)

### Passo 4: Configurar variáveis de ambiente

Na seção "Environment Variables", adicione:

```
DATABASE_URL = sua_connection_string_do_neon
ENVIRONMENT = production
```

### Passo 5: Configurar região e instância

- **Region**: Escolha o mais próximo (ex: Washington, D.C.)
- **Instance**: Escolha o tier gratuito (Nano)

### Passo 6: Deploy!

1. Clique em "Deploy"
2. Aguarde o build (3-5 minutos)
3. Quando estiver pronto, você verá "Healthy" ✅

### Passo 7: Testar sua API

Acesse a URL fornecida pelo Koyeb (ex: `https://seu-app.koyeb.app`)

Teste os endpoints:
```
https://seu-app.koyeb.app/
https://seu-app.koyeb.app/health
https://seu-app.koyeb.app/api/leagues
https://seu-app.koyeb.app/api/matches?league_id=brasileirao&season=2023
```

---

## 🔧 PARTE 5: Manutenção e Atualizações

### Atualizar dados do banco

Para adicionar mais dados (por exemplo, 2025):

```bash
# Localmente
python populate_database.py
```

### Fazer deploy de alterações

```bash
git add .
git commit -m "Descrição das alterações"
git push
```

O Koyeb vai automaticamente fazer redeploy!

### Monitorar logs

No dashboard do Koyeb:
1. Clique no seu serviço
2. Vá em "Logs" para ver o que está acontecendo

---

## 📡 ENDPOINTS DA API

### Informações Gerais
- `GET /` - Informações da API
- `GET /health` - Health check

### Ligas/Campeonatos
- `GET /api/leagues` - Lista todas as ligas
- `GET /api/leagues?country=brazil` - Filtra por país
- `GET /api/leagues/{league_id}/seasons` - Temporadas de uma liga

### Partidas
- `GET /api/matches` - Lista partidas
- `GET /api/matches?league_id=brasileirao` - Filtra por liga
- `GET /api/matches?season=2023` - Filtra por temporada
- `GET /api/matches?team=Palmeiras` - Filtra por time
- `GET /api/matches/{match_id}` - Detalhes de uma partida

### Classificação
- `GET /api/standings/{league_id}/{season}` - Tabela de classificação

### Times
- `GET /api/teams` - Lista times
- `GET /api/teams?league_id=brasileirao` - Filtra por liga
- `GET /api/teams/{team_id}/stats` - Estatísticas do time

### Busca
- `GET /api/search?q=Palmeiras` - Busca geral
- `GET /api/search?q=brasil&type=leagues` - Busca específica

---

## 🎯 Exemplos de Uso da API

### JavaScript (Fetch)
```javascript
// Buscar partidas do Brasileirão 2023
fetch('https://seu-app.koyeb.app/api/matches?league_id=brasileirao&season=2023')
  .then(response => response.json())
  .then(data => console.log(data));
```

### Python (Requests)
```python
import requests

# Buscar classificação
response = requests.get(
    'https://seu-app.koyeb.app/api/standings/brasileirao/2023'
)
data = response.json()
print(data)
```

### cURL
```bash
# Health check
curl https://seu-app.koyeb.app/health

# Buscar ligas
curl https://seu-app.koyeb.app/api/leagues

# Buscar partidas
curl "https://seu-app.koyeb.app/api/matches?league_id=premier_league&season=2023-2024"
```

---

## ⚠️ IMPORTANTE: Limites do Plano Gratuito

### Neon.tech (Free Tier)
- ✅ 512 MB de armazenamento
- ✅ 10 GB de transferência/mês
- ✅ 1 projeto
- ✅ Até 100 horas de computação/mês

### Koyeb (Free Tier)
- ✅ 512 MB RAM
- ✅ 2 GB disco
- ✅ 100 GB largura de banda/mês
- ✅ 1 serviço web

**Dica**: Para projetos maiores, considere os planos pagos!

---

## 🐛 Solução de Problemas

### Erro: "Could not connect to database"
- Verifique se a DATABASE_URL está correta
- Confirme que o Neon.tech está ativo
- Teste a conexão localmente primeiro

### Erro: "Application failed to start"
- Verifique os logs no Koyeb
- Confirme que requirements_deploy.txt está correto
- Teste localmente com: `gunicorn api:app`

### API lenta
- O tier gratuito tem recursos limitados
- Considere adicionar cache
- Limite o número de resultados por página

### Dados não aparecem
- Confirme que populate_database.py foi executado
- Verifique se há dados no banco via console Neon
- Teste os endpoints diretamente

---

## 📚 Recursos Adicionais

- **Documentação Neon**: https://neon.tech/docs
- **Documentação Koyeb**: https://www.koyeb.com/docs
- **Flask Docs**: https://flask.palletsprojects.com/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

---

## ✅ Checklist de Deploy

- [ ] Conta criada no Neon.tech
- [ ] Banco de dados criado no Neon
- [ ] Connection string copiada
- [ ] Arquivo .env configurado localmente
- [ ] Script create_database.py executado
- [ ] Script populate_database.py executado
- [ ] Código testado localmente
- [ ] Repositório GitHub criado
- [ ] Conta criada no Koyeb
- [ ] Serviço configurado no Koyeb
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy realizado com sucesso
- [ ] Endpoints testados e funcionando

---

## 🎉 Pronto!

Sua API está no ar! Agora você tem:
- ✅ API REST hospedada gratuitamente
- ✅ Banco de dados PostgreSQL na nuvem
- ✅ Dados de 11 campeonatos (2022-2024)
- ✅ Endpoints documentados e funcionais

**URL da sua API**: `https://seu-app.koyeb.app`

Compartilhe, use em projetos, e divirta-se! ⚽🚀

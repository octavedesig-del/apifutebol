# ⚽ Football Data API - REST API + PostgreSQL

API REST completa para dados históricos de futebol com deploy em Koyeb e banco de dados PostgreSQL no Neon.tech.

## 🎯 Visão Geral

Esta API fornece acesso a dados completos de **11 campeonatos de futebol** das temporadas **2022, 2023 e 2024**:

### 🇧🇷 Brasil
- Brasileirão Série A
- Copa do Brasil
- Campeonato Paulista
- Campeonato Carioca

### 🇪🇺 Europa
- Premier League (Inglaterra)
- La Liga (Espanha)
- Serie A (Itália)
- Bundesliga (Alemanha)
- Ligue 1 (França)

### 🌍 Internacional
- UEFA Champions League
- UEFA Europa League

## 🚀 Tecnologias

- **Backend**: Python + Flask
- **Banco de Dados**: PostgreSQL (Neon.tech)
- **Deploy**: Koyeb (gratuito)
- **Fonte de Dados**: FlashscoreApi

## 📋 Pré-requisitos

- Python 3.11+
- Conta no Neon.tech (gratuita)
- Conta no Koyeb (gratuita)
- Git e GitHub

## ⚡ Início Rápido

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/football-data-api.git
cd football-data-api
```

### 2. Instale as dependências

```bash
pip install -r requirements_deploy.txt
```

### 3. Configure as variáveis de ambiente

Copie o arquivo de exemplo e configure:

```bash
cp .env.example .env
```

Edite `.env` e adicione sua connection string do Neon.tech:

```
DATABASE_URL=postgresql://seu_usuario:senha@host.neon.tech/dbname?sslmode=require
PORT=8000
ENVIRONMENT=development
```

### 4. Crie o schema do banco

```bash
python create_database.py
```

### 5. Popule o banco com dados

```bash
python populate_database.py
```

**⚠️ Atenção**: Este processo coleta dados de 3 anos (2022-2024) de 11 campeonatos e pode levar 30-60 minutos!

### 6. Execute a API localmente

```bash
python api.py
```

A API estará disponível em: `http://localhost:8000`

## 📡 Endpoints da API

### Informações
- `GET /` - Informações gerais da API
- `GET /health` - Health check

### Ligas
- `GET /api/leagues` - Listar todas as ligas
- `GET /api/leagues?country=brazil` - Filtrar por país
- `GET /api/leagues/{league_id}/seasons` - Temporadas disponíveis

### Partidas
- `GET /api/matches` - Listar partidas (paginado)
- `GET /api/matches?league_id=brasileirao` - Filtrar por liga
- `GET /api/matches?season=2023` - Filtrar por temporada
- `GET /api/matches?team=Palmeiras` - Filtrar por time
- `GET /api/matches/{match_id}` - Detalhes de uma partida

### Classificação
- `GET /api/standings/{league_id}/{season}` - Tabela de classificação

### Times
- `GET /api/teams` - Listar times
- `GET /api/teams?search=Flamengo` - Buscar time
- `GET /api/teams/{team_id}/stats` - Estatísticas do time

### Busca
- `GET /api/search?q=termo` - Busca geral
- `GET /api/search?q=termo&type=teams` - Busca específica

## 🔧 Exemplos de Uso

### JavaScript
```javascript
// Buscar partidas do Brasileirão 2023
const response = await fetch(
  'https://sua-api.koyeb.app/api/matches?league_id=brasileirao&season=2023'
);
const data = await response.json();
console.log(data);
```

### Python
```python
import requests

# Buscar classificação
response = requests.get(
    'https://sua-api.koyeb.app/api/standings/brasileirao/2023'
)
print(response.json())
```

### cURL
```bash
# Health check
curl https://sua-api.koyeb.app/health

# Buscar partidas do Palmeiras
curl "https://sua-api.koyeb.app/api/matches?team=Palmeiras&limit=10"
```

## 🌐 Deploy

Siga o guia completo de deploy em **[DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)**

### Resumo do processo:

1. **Criar banco no Neon.tech**
   - Criar conta e projeto
   - Copiar connection string

2. **Popular banco de dados**
   - Executar `create_database.py`
   - Executar `populate_database.py`

3. **Deploy no Koyeb**
   - Push para GitHub
   - Conectar repositório no Koyeb
   - Configurar variáveis de ambiente
   - Deploy automático!

## 📊 Estrutura do Banco de Dados

```
leagues          → Campeonatos
├── teams        → Times
├── matches      → Partidas
│   └── match_stats → Estatísticas de partidas
├── standings    → Classificações
└── team_stats   → Estatísticas de times
```

## 📁 Estrutura do Projeto

```
football-data-api/
├── api.py                    # API REST Flask
├── create_database.py        # Criação do schema
├── populate_database.py      # População do banco
├── requirements_deploy.txt   # Dependências
├── Procfile                  # Configuração Koyeb
├── runtime.txt              # Versão Python
├── .env.example             # Exemplo de variáveis
├── DEPLOY_GUIDE.md          # Guia de deploy
└── README.md                # Este arquivo
```

## 🔑 Variáveis de Ambiente

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `DATABASE_URL` | Connection string PostgreSQL | `postgresql://user:pass@host/db` |
| `PORT` | Porta da aplicação | `8000` |
| `ENVIRONMENT` | Ambiente de execução | `production` |

## 📈 Dados Disponíveis

- **Temporadas**: 2022, 2023, 2024
- **Campeonatos**: 11 ligas diferentes
- **Partidas**: Milhares de jogos
- **Times**: Centenas de equipes
- **Estatísticas**: Completas por time e partida

## ⚙️ Scripts Disponíveis

| Script | Descrição |
|--------|-----------|
| `create_database.py` | Cria schema do banco |
| `populate_database.py` | Popula com dados do Flashscore |
| `api.py` | Executa a API Flask |

## 🐛 Solução de Problemas

### Erro de conexão com banco
```bash
# Verifique a DATABASE_URL
python -c "import os; print(os.getenv('DATABASE_URL'))"
```

### API não inicia
```bash
# Teste localmente
python api.py

# Ou com gunicorn
gunicorn api:app --bind 0.0.0.0:8000
```

### Dados não aparecem
```sql
-- Conecte ao Neon e verifique
SELECT COUNT(*) FROM matches;
SELECT COUNT(*) FROM teams;
```

## 📝 TODO

- [ ] Adicionar autenticação JWT
- [ ] Implementar cache Redis
- [ ] Adicionar testes unitários
- [ ] Documentação Swagger/OpenAPI
- [ ] Rate limiting
- [ ] Websockets para dados ao vivo

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é de código aberto e está disponível sob a licença MIT.

## 🙏 Agradecimentos

- **FlashscoreApi** - Fonte de dados
- **Neon.tech** - Banco de dados PostgreSQL
- **Koyeb** - Hospedagem da API

## 📧 Contato

Dúvidas ou sugestões? Abra uma issue no GitHub!

---

**Desenvolvido com ⚽ para análise de dados de futebol**

🌟 Se este projeto foi útil, dê uma estrela no GitHub!

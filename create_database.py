"""
Script para criar o schema do banco de dados PostgreSQL (Neon.tech)
Execute este script ANTES de popular o banco com dados
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def create_database_schema():
    """Cria todas as tabelas necessárias no banco de dados"""
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("Criando schema do banco de dados...")
    
    # Tabela de Ligas/Campeonatos
    cur.execute('''
        CREATE TABLE IF NOT EXISTS leagues (
            league_id VARCHAR(100) PRIMARY KEY,
            league_name VARCHAR(200) NOT NULL,
            country VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    print("✓ Tabela 'leagues' criada")
    
    # Tabela de Times
    cur.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            team_id SERIAL PRIMARY KEY,
            team_name VARCHAR(200) NOT NULL,
            league_id VARCHAR(100) REFERENCES leagues(league_id),
            season VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(team_name, league_id, season)
        );
    ''')
    print("✓ Tabela 'teams' criada")
    
    # Tabela de Partidas
    cur.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            match_id VARCHAR(100) PRIMARY KEY,
            league_id VARCHAR(100) REFERENCES leagues(league_id),
            season VARCHAR(20) NOT NULL,
            match_date DATE,
            match_time TIME,
            home_team VARCHAR(200) NOT NULL,
            away_team VARCHAR(200) NOT NULL,
            home_score INTEGER,
            away_score INTEGER,
            status VARCHAR(50),
            round VARCHAR(100),
            stadium VARCHAR(200),
            referee VARCHAR(200),
            attendance INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    print("✓ Tabela 'matches' criada")
    
    # Tabela de Estatísticas de Partidas
    cur.execute('''
        CREATE TABLE IF NOT EXISTS match_stats (
            id SERIAL PRIMARY KEY,
            match_id VARCHAR(100) REFERENCES matches(match_id) ON DELETE CASCADE,
            stat_type VARCHAR(100) NOT NULL,
            home_value VARCHAR(50),
            away_value VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    print("✓ Tabela 'match_stats' criada")
    
    # Tabela de Classificação
    cur.execute('''
        CREATE TABLE IF NOT EXISTS standings (
            id SERIAL PRIMARY KEY,
            league_id VARCHAR(100) REFERENCES leagues(league_id),
            season VARCHAR(20) NOT NULL,
            team_name VARCHAR(200) NOT NULL,
            position INTEGER NOT NULL,
            played INTEGER,
            wins INTEGER,
            draws INTEGER,
            losses INTEGER,
            goals_for INTEGER,
            goals_against INTEGER,
            goal_difference INTEGER,
            points INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(league_id, season, team_name)
        );
    ''')
    print("✓ Tabela 'standings' criada")
    
    # Tabela de Estatísticas de Times
    cur.execute('''
        CREATE TABLE IF NOT EXISTS team_stats (
            id SERIAL PRIMARY KEY,
            team_id INTEGER REFERENCES teams(team_id),
            league_id VARCHAR(100) REFERENCES leagues(league_id),
            season VARCHAR(20) NOT NULL,
            total_matches INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            draws INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            goals_for INTEGER DEFAULT 0,
            goals_against INTEGER DEFAULT 0,
            goal_difference INTEGER DEFAULT 0,
            win_rate DECIMAL(5,4),
            home_wins INTEGER DEFAULT 0,
            away_wins INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(team_id, league_id, season)
        );
    ''')
    print("✓ Tabela 'team_stats' criada")
    
    # Criar índices para melhor performance
    print("\nCriando índices...")
    
    cur.execute('CREATE INDEX IF NOT EXISTS idx_matches_league ON matches(league_id);')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_matches_season ON matches(season);')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(match_date);')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_matches_home ON matches(home_team);')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_matches_away ON matches(away_team);')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_standings_league ON standings(league_id, season);')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_teams_name ON teams(team_name);')
    
    print("✓ Índices criados")
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("\n✅ Schema do banco de dados criado com sucesso!")
    print("\nTabelas criadas:")
    print("  1. leagues - Campeonatos")
    print("  2. teams - Times")
    print("  3. matches - Partidas")
    print("  4. match_stats - Estatísticas de partidas")
    print("  5. standings - Classificação")
    print("  6. team_stats - Estatísticas de times")


def drop_all_tables():
    """CUIDADO: Remove todas as tabelas do banco de dados"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("⚠️  REMOVENDO TODAS AS TABELAS...")
    
    cur.execute('DROP TABLE IF EXISTS match_stats CASCADE;')
    cur.execute('DROP TABLE IF EXISTS team_stats CASCADE;')
    cur.execute('DROP TABLE IF EXISTS standings CASCADE;')
    cur.execute('DROP TABLE IF EXISTS matches CASCADE;')
    cur.execute('DROP TABLE IF EXISTS teams CASCADE;')
    cur.execute('DROP TABLE IF EXISTS leagues CASCADE;')
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("✅ Todas as tabelas foram removidas")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--drop':
        confirm = input("⚠️  Tem certeza que deseja DELETAR todas as tabelas? (sim/não): ")
        if confirm.lower() == 'sim':
            drop_all_tables()
        else:
            print("Operação cancelada")
    else:
        create_database_schema()

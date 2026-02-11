"""
Script para popular o banco de dados PostgreSQL com dados do FlashscoreApi
Coleta dados de 2022, 2023 e 2024 e insere no Neon.tech
"""

from flashscore import Flashscore
import psycopg2
import os
from dotenv import load_dotenv
import time
import logging
from datetime import datetime

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv('DATABASE_URL')

# Configuração dos campeonatos
LEAGUES = {
    'brasileirao': {
        'name': 'Brasileirão Série A',
        'country': 'brazil',
        'league_id': 'brasileirao'
    },
    'copa_brasil': {
        'name': 'Copa do Brasil',
        'country': 'brazil',
        'league_id': 'copa_brasil'
    },
    'paulista': {
        'name': 'Campeonato Paulista',
        'country': 'brazil',
        'league_id': 'paulista'
    },
    'carioca': {
        'name': 'Campeonato Carioca',
        'country': 'brazil',
        'league_id': 'carioca'
    },
    'premier_league': {
        'name': 'Premier League',
        'country': 'england',
        'league_id': 'premier_league'
    },
    'la_liga': {
        'name': 'La Liga',
        'country': 'spain',
        'league_id': 'la_liga'
    },
    'serie_a': {
        'name': 'Serie A',
        'country': 'italy',
        'league_id': 'serie_a'
    },
    'bundesliga': {
        'name': 'Bundesliga',
        'country': 'germany',
        'league_id': 'bundesliga'
    },
    'ligue_1': {
        'name': 'Ligue 1',
        'country': 'france',
        'league_id': 'ligue_1'
    },
    'champions_league': {
        'name': 'UEFA Champions League',
        'country': 'europe',
        'league_id': 'champions_league'
    },
    'europa_league': {
        'name': 'UEFA Europa League',
        'country': 'europe',
        'league_id': 'europa_league'
    }
}


class DatabasePopulator:
    """Classe para popular o banco de dados com dados do Flashscore"""
    
    def __init__(self):
        self.flashscore = Flashscore()
        self.conn = psycopg2.connect(DATABASE_URL)
        self.cur = self.conn.cursor()
        logger.info("Conexão com banco de dados estabelecida")
    
    def insert_league(self, league_id, league_name, country):
        """Insere uma liga no banco de dados"""
        try:
            self.cur.execute('''
                INSERT INTO leagues (league_id, league_name, country)
                VALUES (%s, %s, %s)
                ON CONFLICT (league_id) DO NOTHING
            ''', (league_id, league_name, country))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Erro ao inserir liga {league_id}: {e}")
            self.conn.rollback()
    
    def insert_team(self, team_name, league_id, season):
        """Insere um time no banco de dados"""
        try:
            self.cur.execute('''
                INSERT INTO teams (team_name, league_id, season)
                VALUES (%s, %s, %s)
                ON CONFLICT (team_name, league_id, season) DO NOTHING
                RETURNING team_id
            ''', (team_name, league_id, season))
            
            result = self.cur.fetchone()
            if result:
                self.conn.commit()
                return result[0]
            else:
                # Time já existe, buscar ID
                self.cur.execute('''
                    SELECT team_id FROM teams
                    WHERE team_name = %s AND league_id = %s AND season = %s
                ''', (team_name, league_id, season))
                result = self.cur.fetchone()
                return result[0] if result else None
                
        except Exception as e:
            logger.error(f"Erro ao inserir time {team_name}: {e}")
            self.conn.rollback()
            return None
    
    def insert_match(self, match_data):
        """Insere uma partida no banco de dados"""
        try:
            self.cur.execute('''
                INSERT INTO matches (
                    match_id, league_id, season, match_date, match_time,
                    home_team, away_team, home_score, away_score,
                    status, round, stadium, referee, attendance
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (match_id) DO UPDATE SET
                    home_score = EXCLUDED.home_score,
                    away_score = EXCLUDED.away_score,
                    status = EXCLUDED.status
            ''', (
                match_data.get('match_id'),
                match_data.get('league_id'),
                match_data.get('season'),
                match_data.get('date'),
                match_data.get('time'),
                match_data.get('home_team'),
                match_data.get('away_team'),
                match_data.get('home_score'),
                match_data.get('away_score'),
                match_data.get('status'),
                match_data.get('round'),
                match_data.get('stadium'),
                match_data.get('referee'),
                match_data.get('attendance')
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Erro ao inserir partida {match_data.get('match_id')}: {e}")
            self.conn.rollback()
            return False
    
    def insert_match_stats(self, match_id, stats):
        """Insere estatísticas de uma partida"""
        if not stats:
            return
        
        try:
            for stat_type, values in stats.items():
                self.cur.execute('''
                    INSERT INTO match_stats (match_id, stat_type, home_value, away_value)
                    VALUES (%s, %s, %s, %s)
                ''', (match_id, stat_type, values.get('home'), values.get('away')))
            
            self.conn.commit()
        except Exception as e:
            logger.error(f"Erro ao inserir estatísticas da partida {match_id}: {e}")
            self.conn.rollback()
    
    def insert_standings(self, league_id, season, standings_data):
        """Insere tabela de classificação"""
        try:
            for position, team_data in enumerate(standings_data, 1):
                self.cur.execute('''
                    INSERT INTO standings (
                        league_id, season, team_name, position,
                        played, wins, draws, losses,
                        goals_for, goals_against, goal_difference, points
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (league_id, season, team_name) DO UPDATE SET
                        position = EXCLUDED.position,
                        played = EXCLUDED.played,
                        wins = EXCLUDED.wins,
                        draws = EXCLUDED.draws,
                        losses = EXCLUDED.losses,
                        goals_for = EXCLUDED.goals_for,
                        goals_against = EXCLUDED.goals_against,
                        goal_difference = EXCLUDED.goal_difference,
                        points = EXCLUDED.points
                ''', (
                    league_id, season,
                    team_data.get('team'),
                    position,
                    team_data.get('played', 0),
                    team_data.get('wins', 0),
                    team_data.get('draws', 0),
                    team_data.get('losses', 0),
                    team_data.get('goals_for', 0),
                    team_data.get('goals_against', 0),
                    team_data.get('goal_difference', 0),
                    team_data.get('points', 0)
                ))
            
            self.conn.commit()
        except Exception as e:
            logger.error(f"Erro ao inserir classificação: {e}")
            self.conn.rollback()
    
    def calculate_team_stats(self, team_name, league_id, season):
        """Calcula estatísticas de um time baseado nas partidas"""
        try:
            # Buscar partidas do time
            self.cur.execute('''
                SELECT * FROM matches
                WHERE (home_team = %s OR away_team = %s)
                AND league_id = %s AND season = %s
            ''', (team_name, team_name, league_id, season))
            
            matches = self.cur.fetchall()
            
            stats = {
                'total_matches': 0,
                'wins': 0,
                'draws': 0,
                'losses': 0,
                'goals_for': 0,
                'goals_against': 0,
                'home_wins': 0,
                'away_wins': 0
            }
            
            for match in matches:
                stats['total_matches'] += 1
                
                # Determinar se é casa ou visitante
                is_home = match[5] == team_name  # home_team column
                team_score = match[7] if is_home else match[8]  # home_score or away_score
                opponent_score = match[8] if is_home else match[7]
                
                if team_score is not None and opponent_score is not None:
                    stats['goals_for'] += team_score
                    stats['goals_against'] += opponent_score
                    
                    if team_score > opponent_score:
                        stats['wins'] += 1
                        if is_home:
                            stats['home_wins'] += 1
                        else:
                            stats['away_wins'] += 1
                    elif team_score == opponent_score:
                        stats['draws'] += 1
                    else:
                        stats['losses'] += 1
            
            # Calcular taxa de vitória
            stats['win_rate'] = stats['wins'] / stats['total_matches'] if stats['total_matches'] > 0 else 0
            stats['goal_difference'] = stats['goals_for'] - stats['goals_against']
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas do time: {e}")
            return None
    
    def populate_league_season(self, league_key, season):
        """Popula dados de uma liga/temporada"""
        league_info = LEAGUES[league_key]
        league_id = league_info['league_id']
        
        logger.info(f"="*80)
        logger.info(f"Coletando {league_info['name']} - Temporada {season}")
        logger.info(f"="*80)
        
        # Inserir liga
        self.insert_league(league_id, league_info['name'], league_info['country'])
        
        try:
            # Coletar partidas do Flashscore
            logger.info("Coletando partidas...")
            matches = self.flashscore.get_league_matches(
                league_id=league_id,
                season=season
            )
            
            match_count = 0
            for match in matches:
                match_data = {
                    'match_id': getattr(match, 'id', f"{league_id}_{season}_{match_count}"),
                    'league_id': league_id,
                    'season': season,
                    'date': getattr(match, 'date', None),
                    'time': getattr(match, 'time', None),
                    'home_team': getattr(match, 'home_team', None),
                    'away_team': getattr(match, 'away_team', None),
                    'home_score': getattr(match, 'home_score', None),
                    'away_score': getattr(match, 'away_score', None),
                    'status': getattr(match, 'status', None),
                    'round': getattr(match, 'round', None),
                    'stadium': getattr(match, 'stadium', None),
                    'referee': getattr(match, 'referee', None),
                    'attendance': getattr(match, 'attendance', None)
                }
                
                # Inserir partida
                if self.insert_match(match_data):
                    match_count += 1
                    
                    # Inserir times
                    if match_data['home_team']:
                        self.insert_team(match_data['home_team'], league_id, season)
                    if match_data['away_team']:
                        self.insert_team(match_data['away_team'], league_id, season)
                
                # Delay para não sobrecarregar
                time.sleep(0.5)
            
            logger.info(f"✓ {match_count} partidas inseridas")
            
            # Coletar classificação
            try:
                logger.info("Coletando classificação...")
                table = self.flashscore.get_league_table(
                    league_id=league_id,
                    season=season
                )
                self.insert_standings(league_id, season, table)
                logger.info("✓ Classificação inserida")
            except Exception as e:
                logger.warning(f"Não foi possível coletar classificação: {e}")
            
            logger.info(f"✅ {league_info['name']} {season} concluído!")
            
        except Exception as e:
            logger.error(f"Erro ao coletar {league_key} {season}: {e}")
    
    def populate_all(self, years=[2022, 2023, 2024]):
        """Popula o banco com todos os campeonatos e anos"""
        logger.info("="*80)
        logger.info("INICIANDO POPULAÇÃO DO BANCO DE DADOS")
        logger.info("="*80)
        
        start_time = datetime.now()
        
        for league_key in LEAGUES:
            for year in years:
                # Determinar formato da temporada
                if league_key in ['brasileirao', 'copa_brasil', 'paulista', 'carioca']:
                    season = str(year)
                else:
                    season = f"{year}-{year+1}"
                
                self.populate_league_season(league_key, season)
                time.sleep(2)  # Delay entre ligas
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("="*80)
        logger.info("POPULAÇÃO CONCLUÍDA!")
        logger.info(f"Tempo total: {duration/60:.1f} minutos")
        logger.info("="*80)
    
    def close(self):
        """Fecha conexão com banco de dados"""
        self.cur.close()
        self.conn.close()
        logger.info("Conexão com banco fechada")


if __name__ == "__main__":
    populator = DatabasePopulator()
    
    try:
        # Popular banco com dados de 2022, 2023 e 2024
        populator.populate_all(years=[2022, 2023, 2024])
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Processo interrompido pelo usuário")
    except Exception as e:
        logger.error(f"\n❌ Erro durante população: {e}")
    finally:
        populator.close()

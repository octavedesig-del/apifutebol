"""
Football Data REST API - Versão para Deploy Koyeb
API REST simplificada para servir dados já coletados
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuração do banco de dados
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    logger.warning("DATABASE_URL não configurada! Usando valores padrão para desenvolvimento.")
    DATABASE_URL = "postgresql://localhost/football_db"

def get_db_connection():
    """Cria conexão com PostgreSQL"""
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar: {e}")
        return None


@app.route('/')
def home():
    """Endpoint raiz com informações da API"""
    return jsonify({
        'name': 'Football Data API',
        'version': '1.0.0',
        'status': 'online',
        'description': 'API REST para dados de futebol - 11 campeonatos (2022-2024)',
        'documentation': 'https://github.com/seu-usuario/football-api',
        'endpoints': {
            'health': '/health',
            'leagues': '/api/leagues',
            'seasons': '/api/leagues/<league_id>/seasons',
            'matches': '/api/matches',
            'match_details': '/api/matches/<match_id>',
            'standings': '/api/standings/<league_id>/<season>',
            'teams': '/api/teams',
            'team_stats': '/api/teams/<team_id>/stats',
            'search': '/api/search'
        },
        'examples': {
            'get_leagues': '/api/leagues',
            'get_brazilian_matches': '/api/matches?league_id=brasileirao&season=2023',
            'get_standings': '/api/standings/brasileirao/2023',
            'search_team': '/api/search?q=Palmeiras'
        }
    })


@app.route('/health')
def health():
    """Health check para Koyeb"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'status': 'unhealthy',
                'database': 'disconnected',
                'timestamp': datetime.now().isoformat()
            }), 503
        
        cur = conn.cursor()
        cur.execute('SELECT 1')
        cur.close()
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503


@app.route('/api/leagues', methods=['GET'])
def get_leagues():
    """Lista todas as ligas"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        cur = conn.cursor()
        country = request.args.get('country')
        
        if country:
            cur.execute('''
                SELECT DISTINCT league_id, league_name, country 
                FROM leagues 
                WHERE country = %s
                ORDER BY league_name
            ''', (country,))
        else:
            cur.execute('''
                SELECT DISTINCT league_id, league_name, country 
                FROM leagues 
                ORDER BY country, league_name
            ''')
        
        leagues = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(leagues),
            'data': leagues
        })
    except Exception as e:
        logger.error(f"Error fetching leagues: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/leagues/<league_id>/seasons', methods=['GET'])
def get_league_seasons(league_id):
    """Retorna temporadas disponíveis de uma liga"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        cur = conn.cursor()
        cur.execute('''
            SELECT DISTINCT season 
            FROM matches 
            WHERE league_id = %s 
            ORDER BY season DESC
        ''', (league_id,))
        
        seasons = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'league_id': league_id,
            'count': len(seasons),
            'data': seasons
        })
    except Exception as e:
        logger.error(f"Error fetching seasons: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/matches', methods=['GET'])
def get_matches():
    """Lista partidas com filtros e paginação"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        cur = conn.cursor()
        
        # Parâmetros
        league_id = request.args.get('league_id')
        season = request.args.get('season')
        team = request.args.get('team')
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = int(request.args.get('offset', 0))
        
        # Query dinâmica
        query = 'SELECT * FROM matches WHERE 1=1'
        params = []
        
        if league_id:
            query += ' AND league_id = %s'
            params.append(league_id)
        
        if season:
            query += ' AND season = %s'
            params.append(season)
        
        if team:
            query += ' AND (home_team ILIKE %s OR away_team ILIKE %s)'
            params.extend([f'%{team}%', f'%{team}%'])
        
        query += ' ORDER BY match_date DESC LIMIT %s OFFSET %s'
        params.extend([limit, offset])
        
        cur.execute(query, params)
        matches = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(matches),
            'limit': limit,
            'offset': offset,
            'data': matches
        })
    except Exception as e:
        logger.error(f"Error fetching matches: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/matches/<match_id>', methods=['GET'])
def get_match_details(match_id):
    """Detalhes de uma partida específica"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        cur = conn.cursor()
        cur.execute('SELECT * FROM matches WHERE match_id = %s', (match_id,))
        match = cur.fetchone()
        
        if not match:
            cur.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Match not found'}), 404
        
        # Buscar estatísticas
        cur.execute('SELECT * FROM match_stats WHERE match_id = %s', (match_id,))
        stats = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'match': match,
                'stats': stats
            }
        })
    except Exception as e:
        logger.error(f"Error fetching match details: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/standings/<league_id>/<season>', methods=['GET'])
def get_standings(league_id, season):
    """Tabela de classificação"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        cur = conn.cursor()
        cur.execute('''
            SELECT * FROM standings 
            WHERE league_id = %s AND season = %s 
            ORDER BY position
        ''', (league_id, season))
        
        standings = cur.fetchall()
        cur.close()
        conn.close()
        
        if not standings:
            return jsonify({'success': False, 'error': 'Standings not found'}), 404
        
        return jsonify({
            'success': True,
            'league_id': league_id,
            'season': season,
            'count': len(standings),
            'data': standings
        })
    except Exception as e:
        logger.error(f"Error fetching standings: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/teams', methods=['GET'])
def get_teams():
    """Lista times com filtros"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        cur = conn.cursor()
        
        league_id = request.args.get('league_id')
        season = request.args.get('season')
        search = request.args.get('search')
        
        query = 'SELECT DISTINCT team_id, team_name FROM teams WHERE 1=1'
        params = []
        
        if league_id:
            query += ' AND league_id = %s'
            params.append(league_id)
        
        if season:
            query += ' AND season = %s'
            params.append(season)
        
        if search:
            query += ' AND team_name ILIKE %s'
            params.append(f'%{search}%')
        
        query += ' ORDER BY team_name'
        
        cur.execute(query, params)
        teams = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(teams),
            'data': teams
        })
    except Exception as e:
        logger.error(f"Error fetching teams: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/search', methods=['GET'])
def search():
    """Busca geral"""
    try:
        query_term = request.args.get('q', '')
        
        if not query_term:
            return jsonify({'success': False, 'error': 'Query parameter "q" required'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        cur = conn.cursor()
        results = {}
        
        # Buscar times
        cur.execute('''
            SELECT DISTINCT team_id, team_name 
            FROM teams 
            WHERE team_name ILIKE %s 
            LIMIT 10
        ''', (f'%{query_term}%',))
        results['teams'] = cur.fetchall()
        
        # Buscar ligas
        cur.execute('''
            SELECT DISTINCT league_id, league_name, country 
            FROM leagues 
            WHERE league_name ILIKE %s 
            LIMIT 10
        ''', (f'%{query_term}%',))
        results['leagues'] = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'query': query_term,
            'results': results
        })
    except Exception as e:
        logger.error(f"Error searching: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('ENVIRONMENT', 'production') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)

"""
Football Data REST API
API REST para servir dados de futebol com Flask + PostgreSQL (Neon.tech)
Deploy: Koyeb
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
CORS(app)  # Permitir requisições de qualquer origem

# Configuração do banco de dados Neon.tech
DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    """Cria conexão com o banco de dados PostgreSQL (Neon)"""
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {e}")
        raise


# ============================================================================
# ROTAS DE SAÚDE E INFO
# ============================================================================

@app.route('/')
def home():
    """Endpoint raiz com informações da API"""
    return jsonify({
        'name': 'Football Data API',
        'version': '1.0.0',
        'status': 'online',
        'description': 'API REST para dados de futebol',
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
        }
    })


@app.route('/health')
def health():
    """Health check para o Koyeb"""
    try:
        conn = get_db_connection()
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
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503


# ============================================================================
# ROTAS DE LIGAS/CAMPEONATOS
# ============================================================================

@app.route('/api/leagues', methods=['GET'])
def get_leagues():
    """
    Retorna todas as ligas disponíveis
    
    Query params:
    - country: filtrar por país (opcional)
    """
    try:
        conn = get_db_connection()
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
        logger.error(f"Erro ao buscar ligas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/leagues/<league_id>/seasons', methods=['GET'])
def get_league_seasons(league_id):
    """Retorna todas as temporadas disponíveis de uma liga"""
    try:
        conn = get_db_connection()
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
        logger.error(f"Erro ao buscar temporadas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# ROTAS DE PARTIDAS
# ============================================================================

@app.route('/api/matches', methods=['GET'])
def get_matches():
    """
    Retorna partidas com filtros
    
    Query params:
    - league_id: filtrar por liga
    - season: filtrar por temporada
    - team: filtrar por time (casa ou visitante)
    - date_from: data inicial (YYYY-MM-DD)
    - date_to: data final (YYYY-MM-DD)
    - limit: quantidade de resultados (padrão: 100)
    - offset: paginação (padrão: 0)
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Parâmetros de filtro
        league_id = request.args.get('league_id')
        season = request.args.get('season')
        team = request.args.get('team')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        # Construir query dinâmica
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
        
        if date_from:
            query += ' AND match_date >= %s'
            params.append(date_from)
        
        if date_to:
            query += ' AND match_date <= %s'
            params.append(date_to)
        
        query += ' ORDER BY match_date DESC LIMIT %s OFFSET %s'
        params.extend([limit, offset])
        
        cur.execute(query, params)
        matches = cur.fetchall()
        
        # Contar total
        count_query = query.split('ORDER BY')[0].replace('SELECT *', 'SELECT COUNT(*)')
        cur.execute(count_query, params[:-2])  # Remover limit e offset
        total = cur.fetchone()['count']
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(matches),
            'total': total,
            'limit': limit,
            'offset': offset,
            'data': matches
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar partidas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/matches/<match_id>', methods=['GET'])
def get_match_details(match_id):
    """Retorna detalhes completos de uma partida específica"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM matches WHERE match_id = %s', (match_id,))
        match = cur.fetchone()
        
        if not match:
            return jsonify({
                'success': False,
                'error': 'Partida não encontrada'
            }), 404
        
        # Buscar estatísticas se existirem
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
        logger.error(f"Erro ao buscar detalhes da partida: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# ROTAS DE CLASSIFICAÇÃO
# ============================================================================

@app.route('/api/standings/<league_id>/<season>', methods=['GET'])
def get_standings(league_id, season):
    """Retorna a tabela de classificação de uma liga/temporada"""
    try:
        conn = get_db_connection()
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
            return jsonify({
                'success': False,
                'error': 'Tabela não encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'league_id': league_id,
            'season': season,
            'count': len(standings),
            'data': standings
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar classificação: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# ROTAS DE TIMES
# ============================================================================

@app.route('/api/teams', methods=['GET'])
def get_teams():
    """
    Retorna lista de times
    
    Query params:
    - league_id: filtrar por liga
    - season: filtrar por temporada
    - search: buscar por nome
    """
    try:
        conn = get_db_connection()
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
        logger.error(f"Erro ao buscar times: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/teams/<team_id>/stats', methods=['GET'])
def get_team_stats(team_id):
    """
    Retorna estatísticas de um time
    
    Query params:
    - season: filtrar por temporada (opcional)
    - league_id: filtrar por liga (opcional)
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        season = request.args.get('season')
        league_id = request.args.get('league_id')
        
        query = '''
            SELECT * FROM team_stats 
            WHERE team_id = %s
        '''
        params = [team_id]
        
        if season:
            query += ' AND season = %s'
            params.append(season)
        
        if league_id:
            query += ' AND league_id = %s'
            params.append(league_id)
        
        cur.execute(query, params)
        stats = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'team_id': team_id,
            'count': len(stats),
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas do time: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# ROTA DE BUSCA
# ============================================================================

@app.route('/api/search', methods=['GET'])
def search():
    """
    Busca geral na API
    
    Query params:
    - q: termo de busca
    - type: tipo de busca (teams, matches, leagues)
    """
    try:
        query_term = request.args.get('q', '')
        search_type = request.args.get('type', 'all')
        
        if not query_term:
            return jsonify({
                'success': False,
                'error': 'Parâmetro de busca "q" é obrigatório'
            }), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        results = {}
        
        # Buscar times
        if search_type in ['all', 'teams']:
            cur.execute('''
                SELECT DISTINCT team_id, team_name 
                FROM teams 
                WHERE team_name ILIKE %s 
                LIMIT 10
            ''', (f'%{query_term}%',))
            results['teams'] = cur.fetchall()
        
        # Buscar ligas
        if search_type in ['all', 'leagues']:
            cur.execute('''
                SELECT DISTINCT league_id, league_name, country 
                FROM leagues 
                WHERE league_name ILIKE %s 
                LIMIT 10
            ''', (f'%{query_term}%',))
            results['leagues'] = cur.fetchall()
        
        # Buscar partidas
        if search_type in ['all', 'matches']:
            cur.execute('''
                SELECT * FROM matches 
                WHERE home_team ILIKE %s OR away_team ILIKE %s 
                ORDER BY match_date DESC 
                LIMIT 10
            ''', (f'%{query_term}%', f'%{query_term}%'))
            results['matches'] = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'query': query_term,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# TRATAMENTO DE ERROS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint não encontrado'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Erro interno do servidor'
    }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)

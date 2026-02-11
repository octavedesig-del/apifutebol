"""
Script de testes para validar a API Football Data
Execute este script para testar todos os endpoints
"""

import requests
import json
from datetime import datetime

# Configuração
BASE_URL = "http://localhost:8000"  # Altere para sua URL do Koyeb quando em produção

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.END} {msg}")

def print_error(msg):
    print(f"{Colors.RED}✗{Colors.END} {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.END} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.END} {msg}")

def test_endpoint(name, url, expected_keys=None):
    """Testa um endpoint específico"""
    print(f"\n{Colors.BLUE}Testing:{Colors.END} {name}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print_success(f"Status: {response.status_code}")
            
            data = response.json()
            
            # Verificar chaves esperadas
            if expected_keys:
                for key in expected_keys:
                    if key in data:
                        print_success(f"Key '{key}' found")
                    else:
                        print_error(f"Key '{key}' NOT found")
            
            # Mostrar amostra dos dados
            print_info(f"Response sample: {json.dumps(data, indent=2)[:200]}...")
            
            return True
        else:
            print_error(f"Status: {response.status_code}")
            print_error(f"Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Request timed out")
        return False
    except requests.exceptions.ConnectionError:
        print_error("Connection error - Is the API running?")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def run_tests():
    """Executa todos os testes"""
    print("="*80)
    print(f"{Colors.BLUE}FOOTBALL DATA API - TEST SUITE{Colors.END}")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    results = {}
    
    # Test 1: Root endpoint
    results['root'] = test_endpoint(
        "Root Endpoint",
        f"{BASE_URL}/",
        expected_keys=['name', 'version', 'status', 'endpoints']
    )
    
    # Test 2: Health check
    results['health'] = test_endpoint(
        "Health Check",
        f"{BASE_URL}/health",
        expected_keys=['status', 'database', 'timestamp']
    )
    
    # Test 3: List leagues
    results['leagues'] = test_endpoint(
        "List All Leagues",
        f"{BASE_URL}/api/leagues",
        expected_keys=['success', 'count', 'data']
    )
    
    # Test 4: Filter leagues by country
    results['leagues_br'] = test_endpoint(
        "Filter Leagues by Country (Brazil)",
        f"{BASE_URL}/api/leagues?country=brazil",
        expected_keys=['success', 'count', 'data']
    )
    
    # Test 5: Get seasons for a league
    results['seasons'] = test_endpoint(
        "Get Seasons for Brasileirao",
        f"{BASE_URL}/api/leagues/brasileirao/seasons",
        expected_keys=['success', 'league_id', 'data']
    )
    
    # Test 6: List matches
    results['matches'] = test_endpoint(
        "List Matches (paginated)",
        f"{BASE_URL}/api/matches?limit=10",
        expected_keys=['success', 'count', 'total', 'data']
    )
    
    # Test 7: Filter matches by league
    results['matches_brasileirao'] = test_endpoint(
        "Filter Matches by League (Brasileirao)",
        f"{BASE_URL}/api/matches?league_id=brasileirao&limit=5",
        expected_keys=['success', 'count', 'data']
    )
    
    # Test 8: Filter matches by season
    results['matches_2023'] = test_endpoint(
        "Filter Matches by Season (2023)",
        f"{BASE_URL}/api/matches?season=2023&limit=5",
        expected_keys=['success', 'count', 'data']
    )
    
    # Test 9: Get standings
    results['standings'] = test_endpoint(
        "Get Standings (Brasileirao 2023)",
        f"{BASE_URL}/api/standings/brasileirao/2023",
        expected_keys=['success', 'league_id', 'season', 'data']
    )
    
    # Test 10: List teams
    results['teams'] = test_endpoint(
        "List Teams",
        f"{BASE_URL}/api/teams",
        expected_keys=['success', 'count', 'data']
    )
    
    # Test 11: Search teams
    results['search_teams'] = test_endpoint(
        "Search Teams (Palmeiras)",
        f"{BASE_URL}/api/teams?search=Palmeiras",
        expected_keys=['success', 'count', 'data']
    )
    
    # Test 12: Global search
    results['search'] = test_endpoint(
        "Global Search",
        f"{BASE_URL}/api/search?q=brasil",
        expected_keys=['success', 'query', 'results']
    )
    
    # Resultados finais
    print("\n" + "="*80)
    print(f"{Colors.BLUE}TEST RESULTS SUMMARY{Colors.END}")
    print("="*80)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    print("\n" + "="*80)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("ALL TESTS PASSED! 🎉")
    elif passed > 0:
        print_warning(f"SOME TESTS FAILED ({total - passed} failures)")
    else:
        print_error("ALL TESTS FAILED! ❌")
    
    print("="*80)
    
    return passed, total


def test_specific_match():
    """Teste específico para detalhes de uma partida"""
    print("\n" + "="*80)
    print("ADVANCED TEST: Match Details")
    print("="*80)
    
    # Primeiro, buscar uma partida para obter um ID
    print_info("Fetching a match ID first...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/matches?limit=1")
        if response.status_code == 200:
            data = response.json()
            if data['data']:
                match_id = data['data'][0].get('match_id')
                print_success(f"Found match ID: {match_id}")
                
                # Agora testar os detalhes
                test_endpoint(
                    "Get Match Details",
                    f"{BASE_URL}/api/matches/{match_id}",
                    expected_keys=['success', 'data']
                )
            else:
                print_warning("No matches found in database")
        else:
            print_error("Failed to fetch matches")
    except Exception as e:
        print_error(f"Error: {e}")


if __name__ == "__main__":
    import sys
    
    # Verificar se foi passada uma URL customizada
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
        print(f"Using custom base URL: {BASE_URL}")
    
    try:
        # Executar testes básicos
        passed, total = run_tests()
        
        # Teste avançado
        test_specific_match()
        
        # Exit code baseado nos resultados
        sys.exit(0 if passed == total else 1)
        
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)

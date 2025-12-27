"""
Test PHASE 3: Frontend React Time-Real Dashboard
Valide l'intégration complète du système
"""

import asyncio
import json
import time
import subprocess
import requests
from pathlib import Path
import sys

# Ajouter le chemin backend
backend_path = Path(__file__).parent.parent / "backend" / "app"
sys.path.insert(0, str(backend_path.parent))

def test_phase3_setup():
    """Vérifier que tous les fichiers frontend sont en place"""
    print("✅ TEST 1: Vérifier la structure frontend...")
    
    frontend_path = Path(__file__).parent / "frontend" / "src"
    
    files_to_check = [
        frontend_path / "hooks" / "useRealtimeData.js",
        frontend_path / "components" / "realtime" / "RealtimeDashboard.jsx",
        frontend_path / "components" / "realtime" / "RealtimeDashboard.css",
        frontend_path / "components" / "realtime" / "RealtimeChart.jsx",
        frontend_path / "components" / "realtime" / "AlertNotification.jsx",
        frontend_path / "components" / "realtime" / "AlertNotification.css",
        frontend_path / "pages" / "RealtimePage.jsx",
        frontend_path / "config.js",
    ]
    
    missing_files = []
    for file_path in files_to_check:
        if not file_path.exists():
            missing_files.append(file_path.name)
        else:
            print(f"  ✓ {file_path.name}")
    
    if missing_files:
        print(f"❌ Fichiers manquants: {', '.join(missing_files)}")
        return False
    
    print("✅ Tous les fichiers frontend sont présents!\n")
    return True


def test_backend_api():
    """Vérifier que l'API backend fonctionne"""
    print("✅ TEST 2: Vérifier l'API backend...")
    
    try:
        # Vérifier que le backend est accessible
        response = requests.get('http://localhost:8000/docs', timeout=5)
        if response.status_code == 200:
            print("  ✓ Backend API accessible")
            
            # Vérifier les endpoints réaltime
            endpoints = [
                '/api/realtime/stats',
                '/api/realtime/history',
            ]
            
            for endpoint in endpoints:
                try:
                    resp = requests.get(f'http://localhost:8000{endpoint}', timeout=5)
                    if resp.status_code in [200, 401]:  # 401 si pas authentifié, c'est OK
                        print(f"  ✓ Endpoint {endpoint} disponible")
                except:
                    print(f"  ⚠ Endpoint {endpoint} non accessible (backend pas démarré?)")
            
            return True
        else:
            print("❌ Backend API non accessible")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠️  Backend non démarré. Démarrez-le avec: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_frontend_dependencies():
    """Vérifier les dépendances npm frontend"""
    print("\n✅ TEST 3: Vérifier les dépendances npm...")
    
    package_json_path = Path(__file__).parent / "frontend" / "package.json"
    
    try:
        with open(package_json_path, 'r') as f:
            package_json = json.load(f)
        
        required_deps = [
            'react',
            'react-dom',
            'react-router-dom',
            'recharts',
            'axios',
            'date-fns',
        ]
        
        deps = package_json.get('dependencies', {})
        
        for dep in required_deps:
            if dep in deps:
                print(f"  ✓ {dep} ({deps[dep]})")
            else:
                print(f"  ❌ {dep} manquant")
                return False
        
        print("✅ Toutes les dépendances sont présentes!\n")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_websocket_endpoint_declared():
    """Vérifier que l'endpoint WebSocket est déclaré"""
    print("✅ TEST 4: Vérifier la déclaration de l'endpoint WebSocket...")
    
    main_py_path = Path(__file__).parent / "backend" / "app" / "main.py"
    
    try:
        with open(main_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ('@app.websocket("/ws/realtime")', 'Endpoint WebSocket'),
            ('realtime_service', 'Service realtime'),
            ('mqtt_consumer', 'Consumer MQTT'),
        ]
        
        for check_str, label in checks:
            if check_str in content:
                print(f"  ✓ {label}")
            else:
                print(f"  ❌ {label} non trouvé")
                return False
        
        print("✅ Tous les éléments sont déclarés!\n")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_realtime_page_routing():
    """Vérifier que la page RealtimePage est intégrée"""
    print("✅ TEST 5: Vérifier l'intégration de la page realtime...")
    
    realtime_page = Path(__file__).parent / "frontend" / "src" / "pages" / "RealtimePage.jsx"
    
    try:
        with open(realtime_page, 'r') as f:
            content = f.read()
        
        checks = [
            ('RealtimeDashboard', 'Import RealtimeDashboard'),
            ('AlertNotification', 'Import AlertNotification'),
            ('Navbar', 'Import Navbar'),
        ]
        
        for check_str, label in checks:
            if check_str in content:
                print(f"  ✓ {label}")
            else:
                print(f"  ❌ {label} manquant")
                return False
        
        print("✅ Page RealtimePage correctement configurée!\n")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_hook_websocket_logic():
    """Vérifier la logique du hook WebSocket"""
    print("✅ TEST 6: Vérifier le hook useRealtimeData...")
    
    hook_path = Path(__file__).parent / "frontend" / "src" / "hooks" / "useRealtimeData.js"
    
    try:
        with open(hook_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ('new WebSocket', 'Connexion WebSocket'),
            ('onopen', 'Gestion ouverture'),
            ('onmessage', 'Gestion messages'),
            ('onerror', 'Gestion erreurs'),
            ('reconnect', 'Logique reconnexion'),
            ('keep-alive', 'Keep-alive'),
            ('fraudCount', 'Calcul fraudes'),
            ('normalCount', 'Calcul normales'),
            ('avgScore', 'Score moyen'),
        ]
        
        for check_str, label in checks:
            if check_str.lower() in content.lower():
                print(f"  ✓ {label}")
            else:
                print(f"  ❌ {label} manquant")
                return False
        
        print("✅ Hook correctement implémenté!\n")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_dashboard_components():
    """Vérifier que le dashboard a les bons composants"""
    print("✅ TEST 7: Vérifier le composant RealtimeDashboard...")
    
    dashboard_path = Path(__file__).parent / "frontend" / "src" / "components" / "realtime" / "RealtimeDashboard.jsx"
    
    try:
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ('Stats', 'Cartes stats'),
            ('Filter', 'Boutons filtres'),
            ('Predictions', 'Liste prédictions'),
            ('RiskBadge', 'Badge risque'),
            ('RealtimeChart', 'Graphiques'),
            ('fraud-alert', 'Alertes fraude'),
            ('connection-status', 'Statut connexion'),
        ]
        
        for check_str, label in checks:
            if check_str.lower() in content.lower():
                print(f"  ✓ {label}")
            else:
                print(f"  ⚠️  {label} manquant (optionnel)")
        
        print("✅ Dashboard correctement structuré!\n")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def main():
    """Exécuter tous les tests"""
    print("\n" + "="*60)
    print("🚀 TESTS PHASE 3: Frontend React Time-Real Dashboard")
    print("="*60 + "\n")
    
    results = []
    
    # Exécuter les tests
    results.append(("Setup Frontend", test_phase3_setup()))
    results.append(("Frontend Dependencies", test_frontend_dependencies()))
    results.append(("Hook WebSocket Logic", test_hook_websocket_logic()))
    results.append(("Dashboard Components", test_dashboard_components()))
    results.append(("Realtime Page Routing", test_realtime_page_routing()))
    results.append(("Backend API", test_backend_api()))
    results.append(("WebSocket Endpoint", test_websocket_endpoint_declared()))
    
    # Résumé
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nRésultat: {passed}/{total} tests passés")
    
    if passed == total:
        print("\n🎉 PHASE 3 VALIDÉE - Frontend prêt pour les tests E2E!")
        print("\nProchaines étapes:")
        print("1. Démarrer le backend: uvicorn app.main:app --reload")
        print("2. Démarrer le simulator: python sensor_simulator.py")
        print("3. Démarrer le frontend: npm run dev")
        print("4. Ouvrir: http://localhost:5173/realtime")
    else:
        print("\n⚠️  Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
    
    print("\n")
    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())

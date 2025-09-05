#!/usr/bin/env python3

import requests
import sys
import json
import time
from datetime import datetime

class RegistrationFixTester:
    def __init__(self, base_url="http://localhost:8001/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.auth_token = None
        self.user_data = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, auth_required=False):
        """Run a single API test"""
        if endpoint == "/":
            url = self.base_url + "/"
        elif endpoint:
            url = f"{self.base_url}/{endpoint}"
        else:
            url = self.base_url
        headers = {'Content-Type': 'application/json'}
        
        # Add auth header if required and available
        if auth_required and self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:300]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_api_status(self):
        """Test endpoint de base - GET /api/ pour confirmer l'API est accessible"""
        return self.run_test("API Status Check", "GET", "/", 200)

    def test_new_user_registration(self):
        """Test d'inscription basique - POST /api/auth/register avec nouvel utilisateur"""
        timestamp = int(time.time())
        user_data = {
            "email": f"nouveau_utilisateur_test_{timestamp}@usexplo.com",
            "username": f"nouveau_utilisateur_test_{timestamp}",
            "password": "MonMotDePasse2025!"
        }
        
        success, response = self.run_test("New User Registration", "POST", "auth/register", 200, data=user_data)
        if success and 'access_token' in response:
            self.auth_token = response['access_token']
            self.user_data = response['user']
            print(f"   ✅ Utilisateur enregistré: {self.user_data['username']}")
            print(f"   ✅ Token reçu: {self.auth_token[:20]}...")
        return success

    def test_user_login(self):
        """Test de connexion - POST /api/auth/login avec l'utilisateur créé"""
        if not self.user_data:
            print("❌ Aucune donnée utilisateur disponible pour le test de connexion")
            return False
            
        login_data = {
            "email": self.user_data['email'],
            "password": "MonMotDePasse2025!"
        }
        
        success, response = self.run_test("User Login", "POST", "auth/login", 200, data=login_data)
        if success and 'access_token' in response:
            print(f"   ✅ Connexion réussie pour: {response['user']['username']}")
        return success

    def test_validation_invalid_email(self):
        """Test de validation - Email invalide"""
        timestamp = int(time.time())
        invalid_user_data = {
            "email": f"email_invalide_sans_arobase_{timestamp}",
            "username": f"test_validation_user_{timestamp}",
            "password": "MonMotDePasse2025!"
        }
        
        # Should fail with 422 (validation error) or 400 (bad request)
        success, response = self.run_test("Invalid Email Validation", "POST", "auth/register", 422, data=invalid_user_data)
        if not success:
            # Try 400 status code as alternative
            success, response = self.run_test("Invalid Email Validation (400)", "POST", "auth/register", 400, data=invalid_user_data)
        return success

    def test_validation_short_password(self):
        """Test de validation - Mot de passe trop court"""
        timestamp = int(time.time())
        short_password_data = {
            "email": f"test_short_password_{timestamp}@usexplo.com",
            "username": f"test_short_password_{timestamp}",
            "password": "123"  # Trop court
        }
        
        # Should fail with 422 (validation error) or 400 (bad request)
        success, response = self.run_test("Short Password Validation", "POST", "auth/register", 422, data=short_password_data)
        if not success:
            # Try 400 status code as alternative
            success, response = self.run_test("Short Password Validation (400)", "POST", "auth/register", 400, data=short_password_data)
        return success

    def test_duplicate_email_registration(self):
        """Test cas d'erreur - Inscription avec email déjà existant"""
        if not self.user_data:
            print("❌ Aucune donnée utilisateur disponible pour le test de duplication")
            return False
            
        duplicate_user_data = {
            "email": self.user_data['email'],  # Same email as first test
            "username": "autre_nom_utilisateur",
            "password": "AutreMotDePasse2025!"
        }
        
        return self.run_test("Duplicate Email Registration", "POST", "auth/register", 400, data=duplicate_user_data)

    def run_all_tests(self):
        """Exécuter tous les tests de correctif d'inscription"""
        print("🎵 DÉMARRAGE DES TESTS DE CORRECTIF D'INSCRIPTION US EXPLO")
        print("=" * 60)
        
        # Test 1: Endpoint de base
        print("\n📍 TEST 1: Vérification de l'accessibilité de l'API")
        self.test_api_status()
        
        # Test 2: Inscription basique
        print("\n📍 TEST 2: Inscription d'un nouvel utilisateur")
        self.test_new_user_registration()
        
        # Test 3: Connexion
        print("\n📍 TEST 3: Connexion avec l'utilisateur créé")
        self.test_user_login()
        
        # Test 4: Validation email invalide
        print("\n📍 TEST 4: Validation - Email invalide")
        self.test_validation_invalid_email()
        
        # Test 5: Validation mot de passe court
        print("\n📍 TEST 5: Validation - Mot de passe trop court")
        self.test_validation_short_password()
        
        # Test 6: Email déjà existant
        print("\n📍 TEST 6: Cas d'erreur - Email déjà existant")
        self.test_duplicate_email_registration()
        
        # Résumé
        print("\n" + "=" * 60)
        print(f"🎯 RÉSUMÉ DES TESTS DE CORRECTIF D'INSCRIPTION")
        print(f"   Tests exécutés: {self.tests_run}")
        print(f"   Tests réussis: {self.tests_passed}")
        print(f"   Taux de réussite: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 TOUS LES TESTS SONT PASSÉS - CORRECTIF D'INSCRIPTION VALIDÉ!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} test(s) ont échoué")
            return False

if __name__ == "__main__":
    # Get backend URL from environment
    backend_url = "http://localhost:8001/api"
    
    # Check if frontend .env exists to get the correct URL
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    base_url = line.split('=')[1].strip()
                    backend_url = f"{base_url}/api"
                    break
    except:
        pass
    
    print(f"🌐 URL Backend utilisée: {backend_url}")
    
    tester = RegistrationFixTester(backend_url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)
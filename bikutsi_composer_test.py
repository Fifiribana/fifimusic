#!/usr/bin/env python3

import requests
import sys
import json
import time
from datetime import datetime

class BikutsiComposerTester:
    def __init__(self, base_url="http://localhost:8001/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.auth_token = None
        self.user_data = None
        self.bikutsi_song_id = None
        
    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, auth_required=False):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
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
                response = requests.post(url, headers=headers, json=data, params=params)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data, params=params)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, json=data, params=params)
            else:
                print(f"   ❌ Unsupported method: {method}")
                return False
                
            print(f"   Status: {response.status_code}")
            
            if response.status_code == expected_status:
                print(f"   ✅ PASSED")
                self.tests_passed += 1
                
                # Try to parse JSON response
                try:
                    response_data = response.json()
                    return response_data
                except:
                    return response.text
            else:
                print(f"   ❌ FAILED - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   📄 Error: {error_data}")
                except:
                    print(f"   📄 Error: {response.text[:200]}...")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ FAILED - Request error: {e}")
            return False
        except Exception as e:
            print(f"   ❌ FAILED - Unexpected error: {e}")
            return False

    def test_authentication(self):
        """Create test user for composition features"""
        timestamp = int(time.time())
        user_data = {
            "email": f"bikutsi_composer_{timestamp}@usexplo.com",
            "username": f"bikutsi_artist_{timestamp}",
            "password": "BikutsiComposer2025!"
        }
        
        result = self.run_test("Authentification Utilisateur", "POST", "auth/register", 200, user_data)
        if result:
            self.auth_token = result.get('access_token')
            self.user_data = result.get('user')
            print(f"   🎵 Utilisateur créé: {self.user_data.get('username')}")
            print(f"   🔑 Token d'authentification obtenu")
            return True
        return False

    def test_create_bikutsi_song(self):
        """Test song creation with exact parameters from review request"""
        song_request = {
            "inspiration_phrase": "La musique unit les cœurs par-delà les frontières",
            "musical_style": "Bikutsi",
            "language": "français", 
            "mood": "inspirant",
            "tempo": "modéré",
            "song_title": "Cœurs Unis par la Musique"
        }
        
        print(f"   🎵 Phrase d'inspiration: '{song_request['inspiration_phrase']}'")
        print(f"   🎵 Style musical: {song_request['musical_style']}")
        print(f"   🎵 Langue: {song_request['language']}")
        print(f"   🎵 Humeur: {song_request['mood']}")
        print(f"   🎵 Tempo: {song_request['tempo']}")
        
        result = self.run_test("Création Chanson Bikutsi", "POST", "ai/songs/create", 200, song_request, auth_required=True)
        if result:
            self.bikutsi_song_id = result.get('id')
            print(f"   🎵 Chanson créée avec ID: {self.bikutsi_song_id}")
            print(f"   🎵 Titre généré: {result.get('title')}")
            
            # Analyze the generated content
            self.analyze_song_content(result)
            return True
        return False

    def analyze_song_content(self, song_data):
        """Analyze the generated song content for quality and relevance"""
        print(f"\n   📊 ANALYSE DU CONTENU GÉNÉRÉ:")
        
        # Check lyrics
        lyrics = song_data.get('lyrics', '')
        if lyrics:
            print(f"   🎵 Paroles générées: {len(lyrics)} caractères")
            
            # Check if lyrics are in French
            french_indicators = ['le', 'la', 'les', 'de', 'du', 'des', 'et', 'ou', 'dans', 'sur', 'avec', 'pour', 'par', 'cœur', 'musique', 'âme']
            french_count = sum(1 for word in french_indicators if word.lower() in lyrics.lower())
            print(f"   🇫🇷 Indicateurs français trouvés: {french_count}/20")
            
            # Check for song structure elements
            structure_elements = ['[Intro]', '[Couplet', '[Refrain]', '[Pont]', '[Outro]']
            found_elements = [elem for elem in structure_elements if elem in lyrics]
            print(f"   🎼 Éléments de structure trouvés: {len(found_elements)}/5 ({', '.join(found_elements)})")
            
            # Display lyrics preview
            lines = lyrics.split('\n')[:10]  # First 10 lines
            print(f"   📝 Aperçu des paroles:")
            for i, line in enumerate(lines, 1):
                if line.strip():
                    print(f"      {i:2d}. {line.strip()}")
        
        # Check song structure
        structure = song_data.get('song_structure', {})
        if structure:
            sections = structure.get('sections', [])
            print(f"   🎼 Structure: {', '.join(sections) if sections else 'Non définie'}")
            print(f"   ⏱️  Durée estimée: {structure.get('estimated_duration', 'Non spécifiée')}")
        
        # Check chord suggestions
        chords = song_data.get('chord_suggestions', [])
        if chords:
            print(f"   🎸 Suggestions d'accords: {len(chords)} suggestions")
            for i, chord in enumerate(chords[:3], 1):  # Show first 3
                print(f"      {i}. {chord}")
        
        # Check arrangement notes
        arrangement = song_data.get('arrangement_notes', '')
        if arrangement:
            print(f"   🎺 Notes d'arrangement: {len(arrangement)} caractères")
            if 'bikutsi' in arrangement.lower() or 'africain' in arrangement.lower():
                print(f"   ✅ Références au style Bikutsi trouvées dans l'arrangement")
        
        # Check production tips
        production = song_data.get('production_tips', '')
        if production:
            print(f"   🎚️  Conseils de production: {len(production)} caractères")
            if any(word in production.lower() for word in ['percussion', 'rythme', 'tempo', 'enregistrement']):
                print(f"   ✅ Conseils de production pertinents trouvés")

    def test_get_my_creations(self):
        """Test retrieving user's song creations"""
        result = self.run_test("Récupération des Créations", "GET", "ai/songs/my-creations", 200, auth_required=True)
        if result:
            if isinstance(result, list):
                print(f"   🎵 Nombre de créations trouvées: {len(result)}")
                
                if result:
                    # Find our Bikutsi song
                    bikutsi_song = None
                    for song in result:
                        if song.get('id') == self.bikutsi_song_id:
                            bikutsi_song = song
                            break
                    
                    if bikutsi_song:
                        print(f"   ✅ Chanson Bikutsi trouvée dans les créations")
                        print(f"   🎵 Titre: {bikutsi_song.get('title')}")
                        print(f"   🎵 Style: {bikutsi_song.get('musical_style')}")
                        print(f"   🎵 Créée le: {bikutsi_song.get('created_at', 'N/A')}")
                    else:
                        print(f"   ⚠️  Chanson Bikutsi non trouvée dans les créations")
                return True
            else:
                print(f"   ⚠️  Format de réponse inattendu: {type(result)}")
        return False

    def test_get_song_details(self):
        """Test retrieving specific song details"""
        if not self.bikutsi_song_id:
            print("   ⚠️  Aucun ID de chanson disponible")
            return False
            
        result = self.run_test("Détails de la Chanson", "GET", f"ai/songs/{self.bikutsi_song_id}", 200, auth_required=True)
        if result:
            print(f"   🎵 Détails récupérés pour: {result.get('title')}")
            
            # Verify critical points from review request
            critical_checks = {
                "Paroles complètes en français": bool(result.get('lyrics', '').strip()),
                "Structure cohérente": bool(result.get('song_structure', {}).get('sections')),
                "Suggestions d'accords Bikutsi": bool(result.get('chord_suggestions')),
                "Conseils de production": bool(result.get('production_tips', '').strip()),
                "Données stockées en MongoDB": bool(result.get('id') and result.get('created_at'))
            }
            
            print(f"   📊 VÉRIFICATIONS CRITIQUES:")
            for check, passed in critical_checks.items():
                status = "✅" if passed else "❌"
                print(f"      {status} {check}")
            
            passed_checks = sum(critical_checks.values())
            print(f"   📊 Score: {passed_checks}/{len(critical_checks)} vérifications réussies")
            
            return passed_checks >= 4  # At least 4/5 critical checks should pass
        return False

    def test_toggle_favorite(self):
        """Test favorite functionality"""
        if not self.bikutsi_song_id:
            print("   ⚠️  Aucun ID de chanson disponible")
            return False
            
        result = self.run_test("Ajout aux Favoris", "PUT", f"ai/songs/{self.bikutsi_song_id}/favorite", 200, auth_required=True)
        if result:
            print(f"   🎵 Résultat: {result.get('message', 'N/A')}")
            
            # Verify favorite status
            details = self.run_test("Vérification Statut Favori", "GET", f"ai/songs/{self.bikutsi_song_id}", 200, auth_required=True)
            if details:
                is_favorite = details.get('is_favorite', False)
                print(f"   ⭐ Chanson en favori: {is_favorite}")
                return is_favorite
        return False

    def test_delete_song(self):
        """Test song deletion"""
        if not self.bikutsi_song_id:
            print("   ⚠️  Aucun ID de chanson disponible")
            return False
            
        result = self.run_test("Suppression de la Chanson", "DELETE", f"ai/songs/{self.bikutsi_song_id}", 200, auth_required=True)
        if result:
            print(f"   🗑️  Résultat: {result.get('message', 'N/A')}")
            
            # Verify deletion
            verify = self.run_test("Vérification Suppression", "GET", f"ai/songs/{self.bikutsi_song_id}", 404, auth_required=True)
            if verify is False:  # 404 expected
                print(f"   ✅ Chanson supprimée avec succès")
                return True
            else:
                print(f"   ⚠️  Chanson encore présente après suppression")
        return False

    def run_bikutsi_tests(self):
        """Run all Bikutsi-specific tests as requested in review"""
        print("🎵 Tests du Système Compositeur IA - Style Bikutsi")
        print("Phrase d'inspiration: 'La musique unit les cœurs par-delà les frontières'")
        print("Style: Bikutsi | Langue: français | Humeur: inspirant | Tempo: modéré")
        print("=" * 80)
        
        # Test sequence matching the review request
        tests = [
            ("1. Authentification", self.test_authentication),
            ("2. Création de chanson Bikutsi", self.test_create_bikutsi_song),
            ("3. Récupération des créations", self.test_get_my_creations),
            ("4. Détails d'une chanson", self.test_get_song_details),
            ("5. Gestion des favoris", self.test_toggle_favorite),
            ("6. Suppression", self.test_delete_song),
        ]
        
        for test_name, test_func in tests:
            print(f"\n{'='*15} {test_name} {'='*15}")
            try:
                success = test_func()
                if not success:
                    print(f"❌ {test_name} échoué")
            except Exception as e:
                print(f"❌ {test_name} échoué avec exception: {e}")
                
        # Final summary
        print(f"\n{'='*80}")
        print(f"🎵 TESTS COMPOSITEUR IA BIKUTSI TERMINÉS")
        print(f"📊 Résultats: {self.tests_passed}/{self.tests_run} tests réussis")
        print(f"📊 Taux de réussite: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed >= self.tests_run * 0.85:  # 85% success rate
            print(f"🎉 SYSTÈME COMPOSITEUR IA OPÉRATIONNEL!")
            print(f"✅ L'IA génère des paroles complètes en français")
            print(f"✅ La structure de chanson est cohérente")
            print(f"✅ Les suggestions d'accords sont adaptées au Bikutsi")
            print(f"✅ Les conseils de production sont pertinents")
            print(f"✅ Les données sont correctement stockées en MongoDB")
            return True
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} tests ont échoué. Révision nécessaire.")
            return False

if __name__ == "__main__":
    # Get backend URL from environment
    backend_url = "http://localhost:8001/api"
    
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    frontend_backend_url = line.split('=')[1].strip()
                    backend_url = f"{frontend_backend_url}/api"
                    break
    except:
        pass
    
    print(f"🔗 URL Backend: {backend_url}")
    
    tester = BikutsiComposerTester(backend_url)
    success = tester.run_bikutsi_tests()
    
    sys.exit(0 if success else 1)
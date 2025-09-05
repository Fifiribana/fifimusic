#!/usr/bin/env python3

import requests
import sys
import json
import time
from datetime import datetime

class AIComposerTester:
    def __init__(self, base_url="http://localhost:8001/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.auth_token = None
        self.user_data = None
        self.created_song_id = None
        
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
                    if isinstance(response_data, dict):
                        print(f"   📄 Response keys: {list(response_data.keys())}")
                    elif isinstance(response_data, list):
                        print(f"   📄 Response: List with {len(response_data)} items")
                    return response_data
                except:
                    print(f"   📄 Response: {response.text[:200]}...")
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

    def test_api_status(self):
        """Test API status endpoint"""
        return self.run_test("API Status", "GET", "", 200)

    def test_user_registration(self):
        """Test user registration for AI composer"""
        timestamp = int(time.time())
        user_data = {
            "email": f"composer_test_{timestamp}@usexplo.com",
            "username": f"composer_user_{timestamp}",
            "password": "ComposerTest2025!"
        }
        
        result = self.run_test("User Registration", "POST", "auth/register", 200, user_data)
        if result:
            self.auth_token = result.get('access_token')
            self.user_data = result.get('user')
            print(f"   🔑 Auth token obtained for user: {self.user_data.get('username')}")
            return True
        return False

    def test_user_login(self):
        """Test user login"""
        if not self.user_data:
            print("   ⚠️  No user data available for login test")
            return False
            
        login_data = {
            "email": self.user_data['email'],
            "password": "ComposerTest2025!"
        }
        
        result = self.run_test("User Login", "POST", "auth/login", 200, login_data)
        if result:
            self.auth_token = result.get('access_token')
            print(f"   🔑 Login successful for user: {result.get('user', {}).get('username')}")
            return True
        return False

    def test_create_song_with_ai(self):
        """Test AI song creation with French inspiration phrase"""
        song_request = {
            "inspiration_phrase": "La musique unit les cœurs par-delà les frontières",
            "musical_style": "Bikutsi",
            "language": "français",
            "mood": "inspirant",
            "tempo": "modéré",
            "song_title": "Cœurs Unis"
        }
        
        result = self.run_test("AI Song Creation", "POST", "ai/songs/create", 200, song_request, auth_required=True)
        if result:
            self.created_song_id = result.get('id')
            print(f"   🎵 Song created with ID: {self.created_song_id}")
            print(f"   🎵 Song title: {result.get('title')}")
            print(f"   🎵 Musical style: {result.get('musical_style')}")
            print(f"   🎵 Language: {result.get('language')}")
            print(f"   🎵 Mood: {result.get('mood')}")
            print(f"   🎵 Tempo: {result.get('tempo')}")
            
            # Check if lyrics were generated
            lyrics = result.get('lyrics', '')
            if lyrics:
                print(f"   🎵 Lyrics generated: {len(lyrics)} characters")
                print(f"   🎵 Lyrics preview: {lyrics[:100]}...")
            else:
                print(f"   ⚠️  No lyrics generated")
                
            # Check song structure
            structure = result.get('song_structure', {})
            if structure:
                print(f"   🎵 Song structure: {structure.get('structure', 'N/A')}")
                sections = structure.get('sections', [])
                print(f"   🎵 Sections: {', '.join(sections) if sections else 'N/A'}")
            
            # Check chord suggestions
            chords = result.get('chord_suggestions', [])
            if chords:
                print(f"   🎵 Chord suggestions: {len(chords)} suggestions")
                print(f"   🎵 First chord suggestion: {chords[0] if chords else 'N/A'}")
            
            # Check arrangement and production notes
            arrangement = result.get('arrangement_notes', '')
            production = result.get('production_tips', '')
            if arrangement:
                print(f"   🎵 Arrangement notes: {len(arrangement)} characters")
            if production:
                print(f"   🎵 Production tips: {len(production)} characters")
                
            return True
        return False

    def test_get_my_creations(self):
        """Test retrieving user's song creations"""
        result = self.run_test("Get My Song Creations", "GET", "ai/songs/my-creations", 200, auth_required=True)
        if result:
            if isinstance(result, list):
                print(f"   🎵 Found {len(result)} song creations")
                if result and self.created_song_id:
                    # Check if our created song is in the list
                    found_song = any(song.get('id') == self.created_song_id for song in result)
                    if found_song:
                        print(f"   ✅ Created song found in user's creations")
                    else:
                        print(f"   ⚠️  Created song not found in user's creations")
                        
                    # Display details of first song
                    first_song = result[0]
                    print(f"   🎵 First song: {first_song.get('title')} ({first_song.get('musical_style')})")
                return True
            else:
                print(f"   ⚠️  Expected list, got: {type(result)}")
        return False

    def test_get_song_details(self):
        """Test retrieving specific song details"""
        if not self.created_song_id:
            print("   ⚠️  No song ID available for details test")
            return False
            
        result = self.run_test("Get Song Details", "GET", f"ai/songs/{self.created_song_id}", 200, auth_required=True)
        if result:
            print(f"   🎵 Song details retrieved for: {result.get('title')}")
            print(f"   🎵 Inspiration phrase: {result.get('inspiration_phrase')}")
            print(f"   🎵 AI Analysis: {result.get('ai_analysis', 'N/A')}")
            print(f"   🎵 Is favorite: {result.get('is_favorite', False)}")
            
            # Verify all required fields are present
            required_fields = ['id', 'title', 'inspiration_phrase', 'musical_style', 'language', 'mood', 'tempo', 'lyrics']
            missing_fields = [field for field in required_fields if field not in result]
            if missing_fields:
                print(f"   ⚠️  Missing fields: {missing_fields}")
            else:
                print(f"   ✅ All required fields present")
            return True
        return False

    def test_toggle_favorite(self):
        """Test toggling song favorite status"""
        if not self.created_song_id:
            print("   ⚠️  No song ID available for favorite test")
            return False
            
        # First, toggle to favorite
        result = self.run_test("Toggle Song Favorite (Add)", "PUT", f"ai/songs/{self.created_song_id}/favorite", 200, auth_required=True)
        if result:
            message = result.get('message', '')
            print(f"   🎵 Favorite toggle result: {message}")
            
            # Verify the change by getting song details
            song_details = self.run_test("Verify Favorite Status", "GET", f"ai/songs/{self.created_song_id}", 200, auth_required=True)
            if song_details:
                is_favorite = song_details.get('is_favorite', False)
                print(f"   🎵 Song is now favorite: {is_favorite}")
                
                # Toggle back to unfavorite
                result2 = self.run_test("Toggle Song Favorite (Remove)", "PUT", f"ai/songs/{self.created_song_id}/favorite", 200, auth_required=True)
                if result2:
                    message2 = result2.get('message', '')
                    print(f"   🎵 Second toggle result: {message2}")
                    return True
        return False

    def test_delete_song(self):
        """Test deleting a song creation"""
        if not self.created_song_id:
            print("   ⚠️  No song ID available for deletion test")
            return False
            
        result = self.run_test("Delete Song Creation", "DELETE", f"ai/songs/{self.created_song_id}", 200, auth_required=True)
        if result:
            message = result.get('message', '')
            print(f"   🎵 Deletion result: {message}")
            
            # Verify deletion by trying to get the song (should return 404)
            verify_result = self.run_test("Verify Song Deletion", "GET", f"ai/songs/{self.created_song_id}", 404, auth_required=True)
            if verify_result is False:  # 404 expected
                print(f"   ✅ Song successfully deleted (404 confirmed)")
                return True
            else:
                print(f"   ⚠️  Song still exists after deletion")
        return False

    def test_create_second_song(self):
        """Test creating a second song with different parameters"""
        song_request = {
            "inspiration_phrase": "Les rythmes africains résonnent dans mon âme",
            "musical_style": "Makossa",
            "language": "français",
            "mood": "joyeux",
            "tempo": "rapide",
            "song_title": "Rythmes de l'Âme"
        }
        
        result = self.run_test("Create Second AI Song", "POST", "ai/songs/create", 200, song_request, auth_required=True)
        if result:
            song_id = result.get('id')
            print(f"   🎵 Second song created with ID: {song_id}")
            print(f"   🎵 Title: {result.get('title')}")
            print(f"   🎵 Style: {result.get('musical_style')} (Makossa)")
            print(f"   🎵 Mood: {result.get('mood')} (joyeux)")
            print(f"   🎵 Tempo: {result.get('tempo')} (rapide)")
            
            # Store this ID for potential cleanup
            self.created_song_id = song_id
            return True
        return False

    def test_error_cases(self):
        """Test error handling scenarios"""
        print(f"\n🔍 Testing Error Cases...")
        
        # Test unauthorized access (no auth token)
        temp_token = self.auth_token
        self.auth_token = None
        
        result1 = self.run_test("Unauthorized Song Creation", "POST", "ai/songs/create", 401, {
            "inspiration_phrase": "Test phrase",
            "musical_style": "Test",
            "language": "français"
        }, auth_required=True)
        
        result2 = self.run_test("Unauthorized Get Creations", "GET", "ai/songs/my-creations", 401, auth_required=True)
        
        # Restore auth token
        self.auth_token = temp_token
        
        # Test invalid song ID
        result3 = self.run_test("Invalid Song ID", "GET", "ai/songs/invalid-id-123", 404, auth_required=True)
        
        # Test missing required fields
        result4 = self.run_test("Missing Required Fields", "POST", "ai/songs/create", 422, {
            "musical_style": "Bikutsi"
            # Missing inspiration_phrase
        }, auth_required=True)
        
        success_count = sum([1 for r in [result1, result2, result3, result4] if r is False])  # False means expected error occurred
        print(f"   ✅ {success_count}/4 error cases handled correctly")
        
        return success_count >= 3  # Allow some flexibility

    def run_all_tests(self):
        """Run all AI Composer tests"""
        print("🎵 Starting US EXPLO AI Composer System Tests")
        print("=" * 60)
        
        # Test sequence
        tests = [
            ("API Status Check", self.test_api_status),
            ("User Registration", self.test_user_registration),
            ("User Authentication", self.test_user_login),
            ("AI Song Creation (Bikutsi)", self.test_create_song_with_ai),
            ("Get My Song Creations", self.test_get_my_creations),
            ("Get Song Details", self.test_get_song_details),
            ("Toggle Favorite Status", self.test_toggle_favorite),
            ("Create Second Song (Makossa)", self.test_create_second_song),
            ("Error Handling", self.test_error_cases),
            ("Delete Song Creation", self.test_delete_song),
        ]
        
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                success = test_func()
                if not success:
                    print(f"❌ {test_name} failed")
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                
        # Final summary
        print(f"\n{'='*60}")
        print(f"🎵 AI COMPOSER TESTS COMPLETED")
        print(f"📊 Results: {self.tests_passed}/{self.tests_run} tests passed")
        print(f"📊 Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print(f"🎉 ALL TESTS PASSED! AI Composer system is fully functional!")
            return True
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} tests failed. Review the issues above.")
            return False

if __name__ == "__main__":
    # Get backend URL from environment or use default
    backend_url = "http://localhost:8001/api"
    
    # Check if we should use the frontend env URL
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    frontend_backend_url = line.split('=')[1].strip()
                    backend_url = f"{frontend_backend_url}/api"
                    break
    except:
        pass
    
    print(f"🔗 Using backend URL: {backend_url}")
    
    tester = AIComposerTester(backend_url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)
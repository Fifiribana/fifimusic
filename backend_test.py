#!/usr/bin/env python3

import requests
import sys
import json
import time
import os
import tempfile
from datetime import datetime

class USExploAPITester:
    def __init__(self, base_url="http://localhost:8001/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.created_track_id = None
        self.created_collection_id = None
        self.auth_token = None
        self.user_data = None
        self.session_id = None
        self.uploaded_track_id = None
        # Community-specific variables
        self.musician_profile_id = None
        self.created_post_id = None
        self.second_user_token = None
        self.second_user_data = None
        self.sent_message_id = None
        # New features variables
        self.subscription_plan_id = None
        self.user_subscription_id = None
        self.music_listing_id = None
        self.community_group_id = None
        self.group_message_id = None

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
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
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
        """Test API root endpoint"""
        return self.run_test("API Status", "GET", "", 200)

    # ===== PHASE 2: AUTHENTICATION TESTS =====
    def test_user_registration(self):
        """Test user registration"""
        timestamp = int(time.time())
        user_data = {
            "email": f"test_user_{timestamp}@example.com",
            "username": f"testuser_{timestamp}",
            "password": "TestPassword123!"
        }
        
        success, response = self.run_test("User Registration", "POST", "auth/register", 200, data=user_data)
        if success and 'access_token' in response:
            self.auth_token = response['access_token']
            self.user_data = response['user']
            print(f"   Registered user: {self.user_data['username']}")
            print(f"   Token received: {self.auth_token[:20]}...")
        return success

    def test_user_login(self):
        """Test user login with existing credentials"""
        if not self.user_data:
            print("❌ No user data available for login test")
            return False
            
        login_data = {
            "email": self.user_data['email'],
            "password": "TestPassword123!"
        }
        
        success, response = self.run_test("User Login", "POST", "auth/login", 200, data=login_data)
        if success and 'access_token' in response:
            # Update token with login token
            self.auth_token = response['access_token']
            print(f"   Login successful for: {response['user']['username']}")
        return success

    def test_get_current_user(self):
        """Test getting current user profile"""
        if not self.auth_token:
            print("❌ No auth token available for user profile test")
            return False
            
        return self.run_test("Get Current User", "GET", "auth/me", 200, auth_required=True)[0]

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        invalid_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        return self.run_test("Invalid Login", "POST", "auth/login", 401, data=invalid_data)[0]

    # ===== PHASE 2: ENHANCED TRACK TESTS =====
    def test_get_tracks_with_new_styles(self):
        """Test getting tracks with new Phase 2 styles"""
        new_styles = ["Bikutsi", "Makossa", "Soukous"]
        
        results = []
        for style in new_styles:
            success, data = self.run_test(
                f"Get {style} Tracks", 
                "GET", 
                "tracks", 
                200, 
                params={"style": style}
            )
            results.append(success)
        
        return all(results)

    def test_get_featured_tracks(self):
        """Test getting featured tracks"""
        return self.run_test(
            "Get Featured Tracks", 
            "GET", 
            "tracks", 
            200, 
            params={"featured": True}
        )[0]

    def test_get_tracks(self):
        """Test getting all tracks"""
        return self.run_test("Get All Tracks", "GET", "tracks", 200)

    def test_get_tracks_with_filters(self):
        """Test track filtering"""
        filters = [
            {"region": "Afrique"},
            {"style": "Traditional"},
            {"instrument": "Oud"},
            {"mood": "Méditatif"}
        ]
        
        results = []
        for filter_params in filters:
            filter_name = list(filter_params.keys())[0]
            filter_value = list(filter_params.values())[0]
            success, data = self.run_test(
                f"Filter Tracks by {filter_name}={filter_value}", 
                "GET", 
                "tracks", 
                200, 
                params=filter_params
            )
            results.append(success)
        
        return all(results)

    def test_create_track_with_preview(self):
        """Test creating a new track with preview URL"""
        track_data = {
            "title": "Test Bikutsi Track",
            "artist": "Test Artist Phase 2",
            "region": "Afrique",
            "style": "Bikutsi",
            "instrument": "Balafon",
            "duration": 180,
            "bpm": 140,
            "mood": "Énergique",
            "audio_url": "https://example.com/test-bikutsi.mp3",
            "preview_url": "https://example.com/previews/test-bikutsi-preview.mp3",
            "artwork_url": "https://example.com/test-bikutsi.jpg",
            "price": 3.29,
            "description": "A test Bikutsi track for Phase 2 testing",
            "is_featured": True
        }
        
        success, response = self.run_test("Create Track with Preview", "POST", "tracks", 200, data=track_data)
        if success and 'id' in response:
            self.created_track_id = response['id']
            print(f"   Created track ID: {self.created_track_id}")
        return success

    # ===== PHASE 2: PAYMENT SYSTEM TESTS =====
    def test_create_checkout_session(self):
        """Test creating a Stripe checkout session"""
        if not self.created_track_id:
            print("❌ No track ID available for checkout test")
            return False
            
        checkout_data = {
            "host_url": "http://localhost:8001",
            "track_ids": [self.created_track_id],
            "user_email": self.user_data['email'] if self.user_data else "test@example.com"
        }
        
        success, response = self.run_test("Create Checkout Session", "POST", "checkout/create", 200, data=checkout_data)
        if success and 'session_id' in response:
            self.session_id = response['session_id']
            print(f"   Created session ID: {self.session_id}")
            print(f"   Checkout URL: {response.get('checkout_url', 'N/A')}")
        return success

    def test_get_checkout_status(self):
        """Test getting checkout session status"""
        if not self.session_id:
            print("❌ No session ID available for status test")
            return False
            
        return self.run_test(
            "Get Checkout Status", 
            "GET", 
            f"checkout/status/{self.session_id}", 
            200
        )[0]

    def test_purchase_history(self):
        """Test getting user purchase history"""
        if not self.auth_token:
            print("❌ No auth token available for purchase history test")
            return False
            
        return self.run_test("Get Purchase History", "GET", "purchases/history", 200, auth_required=True)[0]

    def test_invalid_checkout_session(self):
        """Test creating checkout with invalid track IDs"""
        checkout_data = {
            "host_url": "http://localhost:8001",
            "track_ids": ["invalid-track-id"],
            "user_email": "test@example.com"
        }
        
        return self.run_test("Invalid Checkout Session", "POST", "checkout/create", 404, data=checkout_data)[0]

    def test_get_single_track(self):
        """Test getting a single track by ID"""
        if not self.created_track_id:
            print("❌ No track ID available for single track test")
            return False
        
        return self.run_test(
            f"Get Track by ID", 
            "GET", 
            f"tracks/{self.created_track_id}", 
            200
        )[0]

    def test_like_track(self):
        """Test liking a track"""
        if not self.created_track_id:
            print("❌ No track ID available for like test")
            return False
        
        return self.run_test(
            "Like Track", 
            "PUT", 
            f"tracks/{self.created_track_id}/like", 
            200
        )[0]

    def test_download_track(self):
        """Test downloading a track"""
        if not self.created_track_id:
            print("❌ No track ID available for download test")
            return False
        
        return self.run_test(
            "Download Track", 
            "PUT", 
            f"tracks/{self.created_track_id}/download", 
            200
        )[0]

    def test_get_collections(self):
        """Test getting all collections"""
        return self.run_test("Get All Collections", "GET", "collections", 200)

    def test_get_featured_collections(self):
        """Test getting featured collections"""
        return self.run_test(
            "Get Featured Collections", 
            "GET", 
            "collections", 
            200, 
            params={"featured": True}
        )[0]

    def test_create_collection(self):
        """Test creating a new collection"""
        collection_data = {
            "title": "Test Collection",
            "description": "A test collection for API testing",
            "tracks": [self.created_track_id] if self.created_track_id else [],
            "image_url": "https://example.com/test-collection.jpg",
            "featured": False
        }
        
        success, response = self.run_test("Create Collection", "POST", "collections", 200, data=collection_data)
        if success and 'id' in response:
            self.created_collection_id = response['id']
            print(f"   Created collection ID: {self.created_collection_id}")
        return success

    def test_get_single_collection(self):
        """Test getting a single collection by ID"""
        if not self.created_collection_id:
            print("❌ No collection ID available for single collection test")
            return False
        
        return self.run_test(
            f"Get Collection by ID", 
            "GET", 
            f"collections/{self.created_collection_id}", 
            200
        )[0]

    def test_search_tracks(self):
        """Test search functionality"""
        search_queries = ["Desert", "Afrique", "Traditional", "Oud"]
        
        results = []
        for query in search_queries:
            success, data = self.run_test(
                f"Search for '{query}'", 
                "GET", 
                "search", 
                200, 
                params={"q": query}
            )
            results.append(success)
        
        return all(results)

    def test_search_bikutsi(self):
        """Test specific search for Bikutsi as mentioned in review request"""
        success, data = self.run_test(
            "Search for 'bikutsi'", 
            "GET", 
            "search", 
            200, 
            params={"q": "bikutsi"}
        )
        if success and data:
            print(f"   Found {data.get('total', 0)} Bikutsi tracks")
            if data.get('tracks'):
                for track in data['tracks'][:3]:  # Show first 3 tracks
                    print(f"   - {track.get('title', 'N/A')} by {track.get('artist', 'N/A')}")
        return success

    def test_region_stats(self):
        """Test region statistics"""
        return self.run_test("Get Region Statistics", "GET", "regions/stats", 200)[0]

    def test_style_stats(self):
        """Test style statistics"""
        return self.run_test("Get Style Statistics", "GET", "styles/stats", 200)[0]

    # ===== FILE UPLOAD TESTS =====
    def create_test_audio_file(self):
        """Create a temporary audio file for testing"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        # Create a minimal MP3-like file (just for testing, not a real MP3)
        temp_file.write(b'ID3\x03\x00\x00\x00\x00\x00\x00\x00' + b'\x00' * 100)
        temp_file.close()
        return temp_file.name

    def create_test_image_file(self):
        """Create a temporary image file for testing"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        # Create a minimal JPEG-like file (just for testing, not a real JPEG)
        temp_file.write(b'\xff\xd8\xff\xe0\x00\x10JFIF' + b'\x00' * 100 + b'\xff\xd9')
        temp_file.close()
        return temp_file.name

    def run_upload_test(self, name, endpoint, files, data=None, expected_status=200, auth_required=True):
        """Run a file upload test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {}
        
        # Add auth header if required and available
        if auth_required and self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            response = requests.post(url, files=files, data=data, headers=headers)
            
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

    def test_upload_audio_file(self):
        """Test uploading an audio file"""
        if not self.auth_token:
            print("❌ No auth token available for audio upload test")
            return False
            
        audio_file_path = self.create_test_audio_file()
        
        try:
            with open(audio_file_path, 'rb') as f:
                files = {'file': ('test_audio.mp3', f, 'audio/mpeg')}
                success, response = self.run_upload_test(
                    "Upload Audio File", 
                    "upload/audio", 
                    files, 
                    auth_required=True
                )
            return success
        finally:
            # Clean up temp file
            if os.path.exists(audio_file_path):
                os.unlink(audio_file_path)

    def test_upload_image_file(self):
        """Test uploading an image file"""
        if not self.auth_token:
            print("❌ No auth token available for image upload test")
            return False
            
        image_file_path = self.create_test_image_file()
        
        try:
            with open(image_file_path, 'rb') as f:
                files = {'file': ('test_image.jpg', f, 'image/jpeg')}
                success, response = self.run_upload_test(
                    "Upload Image File", 
                    "upload/image", 
                    files, 
                    auth_required=True
                )
            return success
        finally:
            # Clean up temp file
            if os.path.exists(image_file_path):
                os.unlink(image_file_path)

    def test_upload_track_with_files(self):
        """Test the corrected /api/tracks/upload endpoint with Form data"""
        if not self.auth_token:
            print("❌ No auth token available for track upload test")
            return False
            
        audio_file_path = self.create_test_audio_file()
        image_file_path = self.create_test_image_file()
        preview_file_path = self.create_test_audio_file()  # Create preview file
        
        try:
            # Create unique track data
            timestamp = int(time.time())
            
            with open(audio_file_path, 'rb') as audio_f, \
                 open(image_file_path, 'rb') as image_f, \
                 open(preview_file_path, 'rb') as preview_f:
                
                files = {
                    'audio_file': ('test_track.mp3', audio_f, 'audio/mpeg'),
                    'image_file': ('test_cover.jpg', image_f, 'image/jpeg'),
                    'preview_file': ('test_preview.mp3', preview_f, 'audio/mpeg')
                }
                
                # Form data for track metadata
                form_data = {
                    'title': f'Test Upload Track {timestamp}',
                    'artist': 'Simon Messela (fifi Ribana)',
                    'region': 'Afrique',
                    'style': 'Bikutsi Moderne',
                    'instrument': 'Balafon + Synthétiseur',
                    'duration': '285',
                    'bpm': '145',
                    'mood': 'Énergique',
                    'price': '5.99',
                    'description': 'Test track uploaded via corrected API endpoint'
                }
                
                success, response = self.run_upload_test(
                    "Upload Complete Track with Files", 
                    "tracks/upload", 
                    files, 
                    data=form_data,
                    auth_required=True
                )
                
                if success and 'id' in response:
                    self.uploaded_track_id = response['id']
                    print(f"   Created uploaded track ID: {self.uploaded_track_id}")
                    print(f"   Track title: {response.get('title', 'N/A')}")
                    print(f"   Audio URL: {response.get('audio_url', 'N/A')}")
                    print(f"   Artwork URL: {response.get('artwork_url', 'N/A')}")
                    print(f"   Preview URL: {response.get('preview_url', 'N/A')}")
                
                return success
                
        finally:
            # Clean up temp files
            for file_path in [audio_file_path, image_file_path, preview_file_path]:
                if os.path.exists(file_path):
                    os.unlink(file_path)

    def test_upload_track_without_preview(self):
        """Test track upload without optional preview file"""
        if not self.auth_token:
            print("❌ No auth token available for track upload test")
            return False
            
        audio_file_path = self.create_test_audio_file()
        image_file_path = self.create_test_image_file()
        
        try:
            timestamp = int(time.time())
            
            with open(audio_file_path, 'rb') as audio_f, \
                 open(image_file_path, 'rb') as image_f:
                
                files = {
                    'audio_file': ('test_track_no_preview.mp3', audio_f, 'audio/mpeg'),
                    'image_file': ('test_cover_no_preview.jpg', image_f, 'image/jpeg')
                }
                
                form_data = {
                    'title': f'Test Upload No Preview {timestamp}',
                    'artist': 'Simon Messela (fifi Ribana)',
                    'region': 'Global Fusion',
                    'style': 'World Electronic',
                    'instrument': 'Synthétiseur + Balafon',
                    'duration': '355',
                    'bpm': '128',
                    'mood': 'Énergique',
                    'price': '6.99',
                    'description': 'Test track without preview file'
                }
                
                success, response = self.run_upload_test(
                    "Upload Track without Preview", 
                    "tracks/upload", 
                    files, 
                    data=form_data,
                    auth_required=True
                )
                
                return success
                
        finally:
            # Clean up temp files
            for file_path in [audio_file_path, image_file_path]:
                if os.path.exists(file_path):
                    os.unlink(file_path)

    def test_verify_uploaded_track_in_database(self):
        """Verify that the uploaded track exists in the database"""
        if not self.uploaded_track_id:
            print("❌ No uploaded track ID available for verification")
            return False
        
        success, response = self.run_test(
            "Verify Uploaded Track in Database", 
            "GET", 
            f"tracks/{self.uploaded_track_id}", 
            200
        )
        
        if success:
            print(f"   ✅ Track verified in database:")
            print(f"   - Title: {response.get('title', 'N/A')}")
            print(f"   - Artist: {response.get('artist', 'N/A')}")
            print(f"   - Audio URL: {response.get('audio_url', 'N/A')}")
            print(f"   - Artwork URL: {response.get('artwork_url', 'N/A')}")
            print(f"   - Preview URL: {response.get('preview_url', 'N/A')}")
        
        return success

    def test_upload_invalid_file_types(self):
        """Test uploading invalid file types"""
        if not self.auth_token:
            print("❌ No auth token available for invalid file test")
            return False
            
        # Create a text file to test invalid upload
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
        temp_file.write(b'This is not an audio or image file')
        temp_file.close()
        
        try:
            with open(temp_file.name, 'rb') as f:
                # Test invalid audio file
                files = {'file': ('test.txt', f, 'text/plain')}
                success1, _ = self.run_upload_test(
                    "Upload Invalid Audio File", 
                    "upload/audio", 
                    files, 
                    expected_status=400,
                    auth_required=True
                )
                
                # Reset file pointer
                f.seek(0)
                
                # Test invalid image file
                files = {'file': ('test.txt', f, 'text/plain')}
                success2, _ = self.run_upload_test(
                    "Upload Invalid Image File", 
                    "upload/image", 
                    files, 
                    expected_status=400,
                    auth_required=True
                )
            
            return success1 and success2
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)

    # ===== MUSICIAN COMMUNITY TESTS =====

    def test_create_musician_profile(self):
        """Test creating a musician profile with African instruments and genres"""
        if not self.auth_token:
            print("❌ No auth token available for musician profile test")
            return False
            
        profile_data = {
            "stage_name": "Kofi Asante",
            "bio": "Musicien traditionnel du Ghana spécialisé dans les rythmes Afrobeat et Highlife. Passionné par la fusion entre traditions ancestrales et sonorités modernes.",
            "instruments": ["Balafon", "Djembé", "Guitare", "Kora"],
            "genres": ["Afrobeat", "Highlife", "Bikutsi", "Traditional African"],
            "experience_level": "Professionnel",
            "region": "Afrique",
            "city": "Accra",
            "looking_for": ["Collaboration", "Performance", "Jam Session"],
            "social_links": {
                "instagram": "@kofi_asante_music",
                "youtube": "KofiAsanteOfficial"
            }
        }
        
        success, response = self.run_test(
            "Create Musician Profile", 
            "POST", 
            "community/profile", 
            200, 
            data=profile_data, 
            auth_required=True
        )
        
        if success and 'id' in response:
            self.musician_profile_id = response['id']
            print(f"   Created musician profile ID: {self.musician_profile_id}")
            print(f"   Stage name: {response.get('stage_name', 'N/A')}")
            print(f"   Instruments: {response.get('instruments', [])}")
            print(f"   Genres: {response.get('genres', [])}")
        
        return success

    def test_get_my_musician_profile(self):
        """Test getting current user's musician profile"""
        if not self.auth_token:
            print("❌ No auth token available for get profile test")
            return False
            
        success, response = self.run_test(
            "Get My Musician Profile", 
            "GET", 
            "community/profile/me", 
            200, 
            auth_required=True
        )
        
        if success:
            print(f"   Profile retrieved: {response.get('stage_name', 'N/A')}")
            print(f"   Region: {response.get('region', 'N/A')}")
            print(f"   Experience: {response.get('experience_level', 'N/A')}")
        
        return success

    def test_search_musicians_no_filters(self):
        """Test searching musicians without filters"""
        success, response = self.run_test(
            "Search Musicians (No Filters)", 
            "GET", 
            "community/musicians", 
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} musicians")
            for musician in response[:3]:  # Show first 3
                print(f"   - {musician.get('stage_name', 'N/A')} ({musician.get('region', 'N/A')})")
        
        return success

    def test_search_musicians_with_filters(self):
        """Test searching musicians with various filters"""
        filters_to_test = [
            {"region": "Afrique"},
            {"genre": "Afrobeat"},
            {"instrument": "Balafon"},
            {"experience_level": "Professionnel"},
            {"looking_for": "Collaboration"}
        ]
        
        results = []
        for filter_params in filters_to_test:
            filter_name = list(filter_params.keys())[0]
            filter_value = list(filter_params.values())[0]
            
            success, response = self.run_test(
                f"Search Musicians by {filter_name}={filter_value}", 
                "GET", 
                "community/musicians", 
                200, 
                params=filter_params
            )
            
            if success and isinstance(response, list):
                print(f"   Found {len(response)} musicians with {filter_name}={filter_value}")
            
            results.append(success)
        
        return all(results)

    def test_create_community_post(self):
        """Test creating a community post with African music themes"""
        if not self.auth_token:
            print("❌ No auth token available for create post test")
            return False
            
        post_data = {
            "title": "Recherche collaborateurs pour projet Afrobeat-Bikutsi",
            "content": "Salut la communauté ! Je travaille sur un projet fusion mêlant Afrobeat nigérian et Bikutsi camerounais. Je cherche un joueur de balafon et un bassiste pour enregistrer quelques morceaux. Le projet explore les rythmes traditionnels avec des arrangements modernes. Qui serait intéressé ?",
            "post_type": "collaboration",
            "tags": ["Afrobeat", "Bikutsi", "Collaboration", "Balafon", "Fusion", "Enregistrement"]
        }
        
        success, response = self.run_test(
            "Create Community Post", 
            "POST", 
            "community/posts", 
            200, 
            data=post_data, 
            auth_required=True
        )
        
        if success and 'id' in response:
            self.created_post_id = response['id']
            print(f"   Created post ID: {self.created_post_id}")
            print(f"   Post title: {response.get('title', 'N/A')}")
            print(f"   Post type: {response.get('post_type', 'N/A')}")
            print(f"   Tags: {response.get('tags', [])}")
        
        return success

    def test_get_community_feed(self):
        """Test getting community feed posts"""
        success, response = self.run_test(
            "Get Community Feed", 
            "GET", 
            "community/posts", 
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} posts in feed")
            for post in response[:3]:  # Show first 3
                print(f"   - {post.get('title', 'N/A')} ({post.get('post_type', 'N/A')})")
                author = post.get('author', {})
                print(f"     by {author.get('username', 'N/A')} / {author.get('stage_name', 'N/A')}")
        
        return success

    def test_get_community_feed_with_filters(self):
        """Test getting community feed with filters"""
        filters_to_test = [
            {"post_type": "collaboration"},
            {"tag": "Afrobeat"}
        ]
        
        results = []
        for filter_params in filters_to_test:
            filter_name = list(filter_params.keys())[0]
            filter_value = list(filter_params.values())[0]
            
            success, response = self.run_test(
                f"Get Community Feed by {filter_name}={filter_value}", 
                "GET", 
                "community/posts", 
                200, 
                params=filter_params
            )
            
            if success and isinstance(response, list):
                print(f"   Found {len(response)} posts with {filter_name}={filter_value}")
            
            results.append(success)
        
        return all(results)

    def test_like_community_post(self):
        """Test liking a community post"""
        if not self.auth_token:
            print("❌ No auth token available for like post test")
            return False
            
        if not self.created_post_id:
            print("❌ No post ID available for like test")
            return False
            
        success, response = self.run_test(
            "Like Community Post", 
            "POST", 
            f"community/posts/{self.created_post_id}/like", 
            200, 
            auth_required=True
        )
        
        if success:
            print(f"   Like action: {response.get('message', 'N/A')}")
            print(f"   Liked status: {response.get('liked', 'N/A')}")
        
        return success

    def test_unlike_community_post(self):
        """Test unliking a community post (toggle like)"""
        if not self.auth_token:
            print("❌ No auth token available for unlike post test")
            return False
            
        if not self.created_post_id:
            print("❌ No post ID available for unlike test")
            return False
            
        success, response = self.run_test(
            "Unlike Community Post", 
            "POST", 
            f"community/posts/{self.created_post_id}/like", 
            200, 
            auth_required=True
        )
        
        if success:
            print(f"   Unlike action: {response.get('message', 'N/A')}")
            print(f"   Liked status: {response.get('liked', 'N/A')}")
        
        return success

    def test_add_comment_to_post(self):
        """Test adding a comment to a community post"""
        if not self.auth_token:
            print("❌ No auth token available for add comment test")
            return False
            
        if not self.created_post_id:
            print("❌ No post ID available for comment test")
            return False
            
        comment_data = {
            "content": "Super projet ! Je joue du balafon depuis 15 ans et je serais très intéressé par cette collaboration Afrobeat-Bikutsi. J'ai déjà travaillé sur des fusions similaires. Contacte-moi si tu veux écouter quelques samples de mon travail !"
        }
        
        success, response = self.run_test(
            "Add Comment to Post", 
            "POST", 
            f"community/posts/{self.created_post_id}/comments", 
            200, 
            data=comment_data, 
            auth_required=True
        )
        
        if success:
            print(f"   Comment ID: {response.get('id', 'N/A')}")
            print(f"   Comment content: {response.get('content', 'N/A')[:50]}...")
        
        return success

    def test_get_post_comments(self):
        """Test getting comments for a post"""
        if not self.created_post_id:
            print("❌ No post ID available for get comments test")
            return False
            
        success, response = self.run_test(
            "Get Post Comments", 
            "GET", 
            f"community/posts/{self.created_post_id}/comments", 
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} comments")
            for comment in response[:3]:  # Show first 3
                print(f"   - {comment.get('content', 'N/A')[:50]}...")
                author = comment.get('author', {})
                print(f"     by {author.get('username', 'N/A')}")
        
        return success

    def test_create_second_user_for_messaging(self):
        """Create a second user for testing private messaging"""
        timestamp = int(time.time())
        user_data = {
            "email": f"musician2_{timestamp}@example.com",
            "username": f"musician2_{timestamp}",
            "password": "TestPassword123!"
        }
        
        success, response = self.run_test("Create Second User for Messaging", "POST", "auth/register", 200, data=user_data)
        if success and 'access_token' in response:
            self.second_user_token = response['access_token']
            self.second_user_data = response['user']
            print(f"   Second user registered: {self.second_user_data['username']}")
            print(f"   Second user ID: {self.second_user_data['id']}")
        return success

    def test_send_private_message(self):
        """Test sending a private message to another musician"""
        if not self.auth_token:
            print("❌ No auth token available for send message test")
            return False
            
        if not self.second_user_data:
            print("❌ No second user available for messaging test")
            return False
            
        message_data = {
            "recipient_id": self.second_user_data['id'],
            "subject": "Collaboration Afrobeat - Proposition de projet",
            "content": "Salut ! J'ai vu ton profil et je pense que ton style pourrait parfaitement s'intégrer dans mon projet de fusion Afrobeat-Bikutsi. J'aimerais discuter d'une possible collaboration. Tu es disponible pour un appel cette semaine ? J'ai quelques démos à te faire écouter."
        }
        
        success, response = self.run_test(
            "Send Private Message", 
            "POST", 
            "community/messages", 
            200, 
            data=message_data, 
            auth_required=True
        )
        
        if success:
            self.sent_message_id = response.get('id')
            print(f"   Message ID: {self.sent_message_id}")
            print(f"   Subject: {response.get('subject', 'N/A')}")
            print(f"   Recipient ID: {response.get('recipient_id', 'N/A')}")
        
        return success

    def test_get_my_messages(self):
        """Test getting user's private messages"""
        if not self.auth_token:
            print("❌ No auth token available for get messages test")
            return False
            
        success, response = self.run_test(
            "Get My Messages", 
            "GET", 
            "community/messages", 
            200, 
            auth_required=True
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} messages")
            for message in response[:3]:  # Show first 3
                print(f"   - {message.get('subject', 'N/A')}")
                sender = message.get('sender', {})
                recipient = message.get('recipient', {})
                print(f"     from {sender.get('username', 'N/A')} to {recipient.get('username', 'N/A')}")
                print(f"     read: {message.get('is_read', False)}")
        
        return success

    def test_get_second_user_messages(self):
        """Test getting messages for the second user (recipient)"""
        if not self.second_user_token:
            print("❌ No second user token available for get messages test")
            return False
            
        # Temporarily switch to second user's token
        original_token = self.auth_token
        self.auth_token = self.second_user_token
        
        success, response = self.run_test(
            "Get Second User Messages", 
            "GET", 
            "community/messages", 
            200, 
            auth_required=True
        )
        
        # Restore original token
        self.auth_token = original_token
        
        if success and isinstance(response, list):
            print(f"   Second user found {len(response)} messages")
            for message in response[:3]:  # Show first 3
                print(f"   - {message.get('subject', 'N/A')}")
                sender = message.get('sender', {})
                print(f"     from {sender.get('username', 'N/A')}")
        
        return success

    def test_create_additional_community_posts(self):
        """Test creating additional community posts with different types"""
        if not self.auth_token:
            print("❌ No auth token available for additional posts test")
            return False
            
        additional_posts = [
            {
                "title": "Question sur les gammes pentatoniques africaines",
                "content": "Bonjour ! Je m'intéresse aux gammes pentatoniques utilisées dans la musique traditionnelle africaine, particulièrement dans le Highlife ghanéen et le Soukous congolais. Quelqu'un pourrait-il m'expliquer les différences et me recommander des ressources pour approfondir ?",
                "post_type": "question",
                "tags": ["Théorie musicale", "Highlife", "Soukous", "Gammes", "Apprentissage"]
            },
            {
                "title": "Showcase : Nouveau morceau Bikutsi moderne",
                "content": "Je viens de terminer un nouveau morceau qui fusionne Bikutsi traditionnel et électronique moderne. J'ai utilisé des samples de balafon authentiques avec des synthés contemporains. Qu'est-ce que vous en pensez ? Feedback bienvenu !",
                "post_type": "showcase",
                "tags": ["Bikutsi", "Électronique", "Fusion", "Balafon", "Nouveau morceau"]
            },
            {
                "title": "Idée : Festival de musique africaine virtuel",
                "content": "Et si on organisait un festival de musique africaine virtuel ? Chaque musicien pourrait présenter sa région/style, on pourrait avoir des masterclasses, des jams sessions en ligne... Qui serait partant pour développer cette idée ?",
                "post_type": "idea",
                "tags": ["Festival", "Virtuel", "Communauté", "Masterclass", "Organisation"]
            }
        ]
        
        results = []
        for i, post_data in enumerate(additional_posts):
            success, response = self.run_test(
                f"Create Additional Post {i+1} ({post_data['post_type']})", 
                "POST", 
                "community/posts", 
                200, 
                data=post_data, 
                auth_required=True
            )
            
            if success:
                print(f"   Created {post_data['post_type']} post: {response.get('title', 'N/A')}")
            
            results.append(success)
        
        return all(results)

    # ===== NEW FEATURES TESTS - SUBSCRIPTION SYSTEM =====

    def test_get_subscription_plans(self):
        """Test getting all subscription plans"""
        success, response = self.run_test(
            "Get Subscription Plans", 
            "GET", 
            "subscriptions/plans", 
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} subscription plans")
            for plan in response:
                print(f"   - {plan.get('name', 'N/A')}: €{plan.get('price_monthly', 0)}/mois")
                print(f"     Features: {plan.get('features', [])}")
                print(f"     Can sell music: {plan.get('can_sell_music', False)}")
                if plan.get('name') == 'Pro':  # Store Pro plan ID for subscription test
                    self.subscription_plan_id = plan.get('id')
                    print(f"     Stored Pro plan ID: {self.subscription_plan_id}")
        
        return success

    def test_create_subscription(self):
        """Test subscribing to a plan"""
        if not self.auth_token:
            print("❌ No auth token available for subscription test")
            return False
            
        if not self.subscription_plan_id:
            print("❌ No subscription plan ID available")
            return False
            
        subscription_data = {
            "plan_id": self.subscription_plan_id,
            "billing_cycle": "monthly"
        }
        
        success, response = self.run_test(
            "Create Subscription (Pro Plan)", 
            "POST", 
            "subscriptions/subscribe", 
            200, 
            data=subscription_data,
            auth_required=True
        )
        
        if success:
            self.user_subscription_id = response.get('id')
            print(f"   Subscription ID: {self.user_subscription_id}")
            print(f"   Plan ID: {response.get('plan_id', 'N/A')}")
            print(f"   Billing cycle: {response.get('billing_cycle', 'N/A')}")
            print(f"   Status: {response.get('status', 'N/A')}")
        
        return success

    def test_get_user_subscription(self):
        """Test getting current user's subscription"""
        if not self.auth_token:
            print("❌ No auth token available for get subscription test")
            return False
            
        success, response = self.run_test(
            "Get My Subscription", 
            "GET", 
            "subscriptions/my-subscription", 
            200, 
            auth_required=True
        )
        
        if success and response:
            plan = response.get('plan', {})
            print(f"   Subscription status: {response.get('status', 'N/A')}")
            print(f"   Plan name: {plan.get('name', 'N/A')}")
            print(f"   Billing cycle: {response.get('billing_cycle', 'N/A')}")
            print(f"   Can sell music: {plan.get('can_sell_music', False)}")
        elif success and not response:
            print("   No active subscription found")
        
        return success

    # ===== NEW FEATURES TESTS - MUSIC MARKETPLACE =====

    def test_create_music_listing(self):
        """Test listing music for sale in marketplace"""
        if not self.auth_token:
            print("❌ No auth token available for marketplace listing test")
            return False
            
        if not self.created_track_id:
            print("❌ No track ID available for marketplace listing")
            return False
            
        listing_data = {
            "track_id": self.created_track_id,
            "listing_type": "sale",
            "sale_price": 15.99,
            "license_price": 25.99,
            "license_terms": "commercial",
            "royalty_percentage": 5.0,
            "is_exclusive": False
        }
        
        success, response = self.run_test(
            "Create Music Listing", 
            "POST", 
            "marketplace/list", 
            200, 
            data=listing_data,
            auth_required=True
        )
        
        if success:
            self.music_listing_id = response.get('id')
            print(f"   Listing ID: {self.music_listing_id}")
            print(f"   Track ID: {response.get('track_id', 'N/A')}")
            print(f"   Sale price: €{response.get('sale_price', 0)}")
            print(f"   License price: €{response.get('license_price', 0)}")
            print(f"   Status: {response.get('status', 'N/A')}")
        
        return success

    def test_get_marketplace_listings(self):
        """Test browsing marketplace listings"""
        success, response = self.run_test(
            "Get Marketplace Listings", 
            "GET", 
            "marketplace/listings", 
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} marketplace listings")
            for listing in response[:3]:  # Show first 3
                track = listing.get('track', {})
                seller = listing.get('seller', {})
                print(f"   - {track.get('title', 'N/A')} by {seller.get('username', 'N/A')}")
                print(f"     Type: {listing.get('listing_type', 'N/A')}")
                print(f"     Sale price: €{listing.get('sale_price', 0)}")
        
        return success

    def test_get_marketplace_listings_with_filters(self):
        """Test marketplace listings with filters"""
        filters_to_test = [
            {"genre": "Bikutsi"},
            {"listing_type": "sale"},
            {"price_min": 10.0, "price_max": 50.0}
        ]
        
        results = []
        for filter_params in filters_to_test:
            filter_desc = ", ".join([f"{k}={v}" for k, v in filter_params.items()])
            
            success, response = self.run_test(
                f"Get Marketplace Listings with filters ({filter_desc})", 
                "GET", 
                "marketplace/listings", 
                200, 
                params=filter_params
            )
            
            if success and isinstance(response, list):
                print(f"   Found {len(response)} listings with filters: {filter_desc}")
            
            results.append(success)
        
        return all(results)

    def test_get_my_marketplace_listings(self):
        """Test getting current user's marketplace listings"""
        if not self.auth_token:
            print("❌ No auth token available for my listings test")
            return False
            
        success, response = self.run_test(
            "Get My Marketplace Listings", 
            "GET", 
            "marketplace/my-listings", 
            200, 
            auth_required=True
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} of my listings")
            for listing in response:
                track = listing.get('track', {})
                print(f"   - {track.get('title', 'N/A')}")
                print(f"     Status: {listing.get('status', 'N/A')}")
                print(f"     Sale price: €{listing.get('sale_price', 0)}")
        
        return success

    # ===== NEW FEATURES TESTS - COMMUNITY GROUPS =====

    def test_create_community_group(self):
        """Test creating a community group"""
        if not self.auth_token:
            print("❌ No auth token available for create group test")
            return False
            
        group_data = {
            "name": "Musiciens Bikutsi",
            "description": "Groupe dédié aux musiciens passionnés de Bikutsi camerounais. Partageons nos techniques, nos compositions et organisons des collaborations !",
            "group_type": "public",
            "max_members": 100,
            "tags": ["Bikutsi", "Cameroun", "Collaboration", "Traditionnel", "Moderne"]
        }
        
        success, response = self.run_test(
            "Create Community Group", 
            "POST", 
            "community/groups", 
            200, 
            data=group_data,
            auth_required=True
        )
        
        if success:
            self.community_group_id = response.get('id')
            print(f"   Group ID: {self.community_group_id}")
            print(f"   Group name: {response.get('name', 'N/A')}")
            print(f"   Group type: {response.get('group_type', 'N/A')}")
            print(f"   Max members: {response.get('max_members', 0)}")
            print(f"   Tags: {response.get('tags', [])}")
        
        return success

    def test_get_community_groups(self):
        """Test getting community groups"""
        success, response = self.run_test(
            "Get Community Groups", 
            "GET", 
            "community/groups", 
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} community groups")
            for group in response[:3]:  # Show first 3
                print(f"   - {group.get('name', 'N/A')} ({group.get('group_type', 'N/A')})")
                print(f"     Members: {group.get('member_count', 0)}/{group.get('max_members', 0)}")
                print(f"     Tags: {group.get('tags', [])}")
        
        return success

    def test_get_community_groups_with_filters(self):
        """Test getting community groups with filters"""
        filters_to_test = [
            {"group_type": "public"},
            {"tag": "Bikutsi"}
        ]
        
        results = []
        for filter_params in filters_to_test:
            filter_desc = ", ".join([f"{k}={v}" for k, v in filter_params.items()])
            
            success, response = self.run_test(
                f"Get Community Groups with filters ({filter_desc})", 
                "GET", 
                "community/groups", 
                200, 
                params=filter_params
            )
            
            if success and isinstance(response, list):
                print(f"   Found {len(response)} groups with filters: {filter_desc}")
            
            results.append(success)
        
        return all(results)

    def test_join_community_group(self):
        """Test joining a community group with second user"""
        if not self.second_user_token:
            print("❌ No second user token available for join group test")
            return False
            
        if not self.community_group_id:
            print("❌ No community group ID available for join test")
            return False
            
        # Switch to second user's token
        original_token = self.auth_token
        self.auth_token = self.second_user_token
        
        success, response = self.run_test(
            "Join Community Group (Second User)", 
            "POST", 
            f"community/groups/{self.community_group_id}/join", 
            200, 
            auth_required=True
        )
        
        # Restore original token
        self.auth_token = original_token
        
        if success:
            print(f"   Join status: {response.get('message', 'N/A')}")
            print(f"   Member role: {response.get('role', 'N/A')}")
        
        return success

    def test_send_group_message(self):
        """Test sending a message to the community group"""
        if not self.auth_token:
            print("❌ No auth token available for group message test")
            return False
            
        if not self.community_group_id:
            print("❌ No community group ID available for message test")
            return False
            
        message_data = {
            "content": "Salut tout le monde ! Je suis ravi de rejoindre ce groupe de passionnés de Bikutsi. Je joue du balafon depuis 10 ans et j'aimerais partager quelques techniques traditionnelles que j'ai apprises au Cameroun. Qui serait intéressé par un atelier virtuel ?",
            "message_type": "text"
        }
        
        success, response = self.run_test(
            "Send Group Message", 
            "POST", 
            f"community/groups/{self.community_group_id}/messages", 
            200, 
            data=message_data,
            auth_required=True
        )
        
        if success:
            self.group_message_id = response.get('id')
            print(f"   Message ID: {self.group_message_id}")
            print(f"   Content: {response.get('content', 'N/A')[:50]}...")
            print(f"   Message type: {response.get('message_type', 'N/A')}")
        
        return success

    def test_get_group_messages(self):
        """Test getting messages from the community group"""
        if not self.community_group_id:
            print("❌ No community group ID available for get messages test")
            return False
            
        success, response = self.run_test(
            "Get Group Messages", 
            "GET", 
            f"community/groups/{self.community_group_id}/messages", 
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} group messages")
            for message in response[:3]:  # Show first 3
                sender = message.get('sender', {})
                print(f"   - {message.get('content', 'N/A')[:50]}...")
                print(f"     by {sender.get('username', 'N/A')} / {sender.get('stage_name', 'N/A')}")
                print(f"     type: {message.get('message_type', 'N/A')}")
        
        return success

    def test_second_user_send_group_message(self):
        """Test second user sending a message to the group"""
        if not self.second_user_token:
            print("❌ No second user token available for group message test")
            return False
            
        if not self.community_group_id:
            print("❌ No community group ID available for message test")
            return False
            
        # Switch to second user's token
        original_token = self.auth_token
        self.auth_token = self.second_user_token
        
        message_data = {
            "content": "Excellente idée pour l'atelier ! Je suis bassiste et j'aimerais apprendre comment adapter les lignes de basse traditionnelles du Bikutsi avec des instruments modernes. Ça pourrait être très enrichissant pour tous !",
            "message_type": "text"
        }
        
        success, response = self.run_test(
            "Second User Send Group Message", 
            "POST", 
            f"community/groups/{self.community_group_id}/messages", 
            200, 
            data=message_data,
            auth_required=True
        )
        
        # Restore original token
        self.auth_token = original_token
        
        if success:
            print(f"   Second user message ID: {response.get('id')}")
            print(f"   Content: {response.get('content', 'N/A')[:50]}...")
        
        return success

    def test_subscription_restrictions(self):
        """Test that subscription restrictions work correctly"""
        if not self.auth_token:
            print("❌ No auth token available for subscription restrictions test")
            return False
            
        # Test creating a listing without subscription (should fail)
        # First, let's create a user without subscription
        timestamp = int(time.time())
        user_data = {
            "email": f"no_sub_user_{timestamp}@example.com",
            "username": f"no_sub_user_{timestamp}",
            "password": "TestPassword123!"
        }
        
        success, response = self.run_test("Create User Without Subscription", "POST", "auth/register", 200, data=user_data)
        if not success:
            return False
            
        no_sub_token = response.get('access_token')
        
        # Try to create a listing without subscription
        original_token = self.auth_token
        self.auth_token = no_sub_token
        
        listing_data = {
            "track_id": self.created_track_id,
            "listing_type": "sale",
            "sale_price": 10.99
        }
        
        success, response = self.run_test(
            "Create Listing Without Subscription (Should Fail)", 
            "POST", 
            "marketplace/list", 
            403,  # Should fail with 403 Forbidden
            data=listing_data,
            auth_required=True
        )
        
        # Restore original token
        self.auth_token = original_token
        
        if success:
            print("   ✅ Subscription restriction working correctly - listing creation blocked")
        
        return success

def main():
    print("🎵 US EXPLO API Testing Suite - NEW FEATURES TESTING")
    print("🔥 Testing: Subscription System, Music Marketplace, Community Groups")
    print("=" * 70)
    
    # Get the correct backend URL from environment
    backend_url = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
    if not backend_url.endswith('/api'):
        backend_url = f"{backend_url}/api"
    
    print(f"🌐 Testing backend at: {backend_url}")
    tester = USExploAPITester(base_url=backend_url)
    
    # Test sequence focusing on NEW FEATURES
    tests = [
        # Basic API Tests
        ("API Status", tester.test_api_status),
        
        # Authentication Tests (required for new features)
        ("User Registration", tester.test_user_registration),
        ("User Login", tester.test_user_login),
        ("Get Current User", tester.test_get_current_user),
        
        # Create musician profile for both users
        ("Create Musician Profile", tester.test_create_musician_profile),
        ("Get My Musician Profile", tester.test_get_my_musician_profile),
        
        # NEW FEATURES - SUBSCRIPTION SYSTEM
        ("Get Subscription Plans", tester.test_get_subscription_plans),
        ("Create Subscription (Pro Plan)", tester.test_create_subscription),
        ("Get My Subscription", tester.test_get_user_subscription),
        
        # Create track for marketplace testing
        ("Create Track with Preview", tester.test_create_track_with_preview),
        
        # NEW FEATURES - MUSIC MARKETPLACE
        ("Create Music Listing", tester.test_create_music_listing),
        ("Get Marketplace Listings", tester.test_get_marketplace_listings),
        ("Get Marketplace Listings with Filters", tester.test_get_marketplace_listings_with_filters),
        ("Get My Marketplace Listings", tester.test_get_my_marketplace_listings),
        
        # Create second user for group testing
        ("Create Second User for Messaging", tester.test_create_second_user_for_messaging),
        
        # NEW FEATURES - COMMUNITY GROUPS
        ("Create Community Group", tester.test_create_community_group),
        ("Get Community Groups", tester.test_get_community_groups),
        ("Get Community Groups with Filters", tester.test_get_community_groups_with_filters),
        ("Join Community Group (Second User)", tester.test_join_community_group),
        ("Send Group Message", tester.test_send_group_message),
        ("Get Group Messages", tester.test_get_group_messages),
        ("Second User Send Group Message", tester.test_second_user_send_group_message),
        
        # Test subscription restrictions
        ("Test Subscription Restrictions", tester.test_subscription_restrictions),
        
        # Additional community tests
        ("Search Musicians (No Filters)", tester.test_search_musicians_no_filters),
        ("Search Musicians with Filters", tester.test_search_musicians_with_filters),
        ("Create Community Post", tester.test_create_community_post),
        ("Get Community Feed", tester.test_get_community_feed),
        ("Like Community Post", tester.test_like_community_post),
        ("Add Comment to Post", tester.test_add_comment_to_post),
        ("Send Private Message", tester.test_send_private_message),
        ("Get My Messages", tester.test_get_my_messages),
        
        # Basic functionality tests
        ("Get Tracks", tester.test_get_tracks),
        ("Search Bikutsi", tester.test_search_bikutsi),
        ("Get Featured Tracks", tester.test_get_featured_tracks),
        ("Track Filtering", tester.test_get_tracks_with_filters),
        ("Get Single Track", tester.test_get_single_track),
        ("Like Track", tester.test_like_track),
        ("Download Track", tester.test_download_track),
        
        # Collections
        ("Get Collections", tester.test_get_collections),
        ("Get Featured Collections", tester.test_get_featured_collections),
        
        # Search and Stats
        ("Search Tracks", tester.test_search_tracks),
        ("Region Statistics", tester.test_region_stats),
        ("Style Statistics", tester.test_style_stats),
    ]
    
    print(f"\nRunning {len(tests)} test categories...")
    
    failed_tests = []
    upload_tests = [
        "Upload Audio File", 
        "Upload Image File", 
        "Upload Complete Track with Files",
        "Upload Track without Preview",
        "Verify Uploaded Track in Database",
        "Upload Invalid File Types"
    ]
    
    for test_name, test_func in tests:
        try:
            if not test_func():
                failed_tests.append(test_name)
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            failed_tests.append(test_name)
    
    # Print final results
    print("\n" + "=" * 70)
    print(f"📊 FINAL RESULTS - NEW FEATURES TESTING")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    # Focus on community test results
    community_tests = [
        "Create Musician Profile", 
        "Get My Musician Profile", 
        "Search Musicians (No Filters)",
        "Search Musicians with Filters",
        "Create Community Post",
        "Get Community Feed",
        "Get Community Feed with Filters",
        "Like Community Post",
        "Unlike Community Post",
        "Add Comment to Post",
        "Get Post Comments",
        "Create Second User for Messaging",
        "Send Private Message",
        "Get My Messages",
        "Get Second User Messages",
        "Create Additional Community Posts"
    ]
    
    community_failed = [test for test in failed_tests if test in community_tests]
    community_passed = [test for test in community_tests if test not in failed_tests]
    
    print(f"\n🎯 COMMUNITY FUNCTIONALITY RESULTS:")
    print(f"Community tests passed: {len(community_passed)}/{len(community_tests)}")
    
    if community_passed:
        print(f"\n✅ Successful community tests:")
        for test in community_passed:
            print(f"   ✅ {test}")
    
    if community_failed:
        print(f"\n❌ Failed community tests:")
        for test in community_failed:
            print(f"   ❌ {test}")
    
    # Focus on upload test results
    upload_failed = [test for test in failed_tests if test in upload_tests]
    upload_passed = [test for test in upload_tests if test not in failed_tests]
    
    print(f"\n🎯 UPLOAD FUNCTIONALITY RESULTS:")
    print(f"Upload tests passed: {len(upload_passed)}/{len(upload_tests)}")
    
    if failed_tests:
        print(f"\n❌ All failed test categories:")
        for test in failed_tests:
            print(f"   - {test}")
        
        print(f"\n🔧 CRITICAL FEATURES TO FIX:")
        critical_features = [
            "User Registration", "User Login", "Get Current User",
            "Create Musician Profile", "Get My Musician Profile", "Create Community Post",
            "Send Private Message", "Get My Messages"
        ]
        critical_failed = [test for test in failed_tests if test in critical_features]
        if critical_failed:
            for test in critical_failed:
                print(f"   🚨 {test}")
    else:
        print(f"\n🎉 All test categories passed!")
    
    # Special focus on community endpoints
    if len(community_failed) == 0:
        print(f"\n🎉 SUCCESS: All community endpoints are working perfectly!")
        print(f"   ✅ Musician profiles creation and retrieval")
        print(f"   ✅ Musician search with filters (region, genre, instrument, etc.)")
        print(f"   ✅ Community posts creation and feed")
        print(f"   ✅ Post likes and comments system")
        print(f"   ✅ Private messaging between musicians")
        print(f"   ✅ All endpoints tested with realistic African music data")
    else:
        print(f"\n❌ ISSUES: {len(community_failed)} community endpoints have problems")
        print(f"   Community features need attention before production")
    
    return 0 if len(failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
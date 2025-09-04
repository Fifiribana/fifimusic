#!/usr/bin/env python3

import requests
import sys
import json
import time
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

def main():
    print("🎵 US EXPLO API Testing Suite - Phase 2")
    print("=" * 50)
    
    tester = USExploAPITester()
    
    # Test sequence - Phase 2 comprehensive testing
    tests = [
        # Basic API Tests
        ("API Status", tester.test_api_status),
        
        # Phase 2: Authentication Tests
        ("User Registration", tester.test_user_registration),
        ("User Login", tester.test_user_login),
        ("Get Current User", tester.test_get_current_user),
        ("Invalid Login", tester.test_invalid_login),
        
        # Phase 2: Enhanced Track Tests
        ("Get Tracks", tester.test_get_tracks),
        ("New Styles (Bikutsi/Makossa/Soukous)", tester.test_get_tracks_with_new_styles),
        ("Get Featured Tracks", tester.test_get_featured_tracks),
        ("Track Filtering", tester.test_get_tracks_with_filters),
        ("Create Track with Preview", tester.test_create_track_with_preview),
        ("Get Single Track", tester.test_get_single_track),
        ("Like Track", tester.test_like_track),
        ("Download Track", tester.test_download_track),
        
        # Phase 2: Payment System Tests
        ("Create Checkout Session", tester.test_create_checkout_session),
        ("Get Checkout Status", tester.test_get_checkout_status),
        ("Purchase History", tester.test_purchase_history),
        ("Invalid Checkout Session", tester.test_invalid_checkout_session),
        
        # Collection Tests
        ("Get Collections", tester.test_get_collections),
        ("Get Featured Collections", tester.test_get_featured_collections),
        ("Create Collection", tester.test_create_collection),
        ("Get Single Collection", tester.test_get_single_collection),
        
        # Search and Stats Tests
        ("Search Tracks", tester.test_search_tracks),
        ("Search Bikutsi", tester.test_search_bikutsi),
        ("Region Statistics", tester.test_region_stats),
        ("Style Statistics", tester.test_style_stats),
    ]
    
    print(f"\nRunning {len(tests)} test categories...")
    
    failed_tests = []
    for test_name, test_func in tests:
        try:
            if not test_func():
                failed_tests.append(test_name)
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            failed_tests.append(test_name)
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 FINAL RESULTS - PHASE 2")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if failed_tests:
        print(f"\n❌ Failed test categories:")
        for test in failed_tests:
            print(f"   - {test}")
        print(f"\n🔧 PHASE 2 CRITICAL FEATURES TO FIX:")
        critical_features = [
            "User Registration", "User Login", "Get Current User",
            "Create Checkout Session", "Get Checkout Status",
            "New Styles (Bikutsi/Makossa/Soukous)", "Get Featured Tracks"
        ]
        critical_failed = [test for test in failed_tests if test in critical_features]
        if critical_failed:
            for test in critical_failed:
                print(f"   🚨 {test}")
    else:
        print(f"\n🎉 All Phase 2 test categories passed!")
    
    return 0 if len(failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
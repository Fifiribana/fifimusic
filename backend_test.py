#!/usr/bin/env python3

import requests
import sys
import json
import time
from datetime import datetime

class USExploAPITester:
    def __init__(self, base_url="https://beatvoyage-1.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.created_track_id = None
        self.created_collection_id = None
        self.auth_token = None
        self.user_data = None
        self.session_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        headers = {'Content-Type': 'application/json'}

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

    def test_create_track(self):
        """Test creating a new track"""
        track_data = {
            "title": "Test Track",
            "artist": "Test Artist",
            "region": "Test Region",
            "style": "Test Style",
            "instrument": "Test Instrument",
            "duration": 180,
            "bpm": 120,
            "mood": "Test Mood",
            "audio_url": "https://example.com/test.mp3",
            "artwork_url": "https://example.com/test.jpg",
            "price": 2.99,
            "description": "A test track for API testing"
        }
        
        success, response = self.run_test("Create Track", "POST", "tracks", 200, data=track_data)
        if success and 'id' in response:
            self.created_track_id = response['id']
            print(f"   Created track ID: {self.created_track_id}")
        return success

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

    def test_region_stats(self):
        """Test region statistics"""
        return self.run_test("Get Region Statistics", "GET", "regions/stats", 200)[0]

    def test_style_stats(self):
        """Test style statistics"""
        return self.run_test("Get Style Statistics", "GET", "styles/stats", 200)[0]

def main():
    print("🎵 US EXPLO API Testing Suite")
    print("=" * 50)
    
    tester = USExploAPITester()
    
    # Test sequence
    tests = [
        ("API Status", tester.test_api_status),
        ("Get Tracks", tester.test_get_tracks),
        ("Track Filtering", tester.test_get_tracks_with_filters),
        ("Create Track", tester.test_create_track),
        ("Get Single Track", tester.test_get_single_track),
        ("Like Track", tester.test_like_track),
        ("Download Track", tester.test_download_track),
        ("Get Collections", tester.test_get_collections),
        ("Get Featured Collections", tester.test_get_featured_collections),
        ("Create Collection", tester.test_create_collection),
        ("Get Single Collection", tester.test_get_single_collection),
        ("Search Tracks", tester.test_search_tracks),
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
    print(f"📊 FINAL RESULTS")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if failed_tests:
        print(f"\n❌ Failed test categories:")
        for test in failed_tests:
            print(f"   - {test}")
    else:
        print(f"\n🎉 All test categories passed!")
    
    return 0 if len(failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
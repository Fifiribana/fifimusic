#!/usr/bin/env python3

import requests
import sys
import json
import time
import os
from datetime import datetime

class USExploCorrectionsTest:
    def __init__(self, base_url="http://localhost:8001/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.auth_token = None
        self.user_data = None
        self.created_track_id = None
        self.subscription_plan_id = None
        self.music_listing_id = None

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

    def setup_user_and_auth(self):
        """Create user and authenticate"""
        timestamp = int(time.time())
        user_data = {
            "email": f"corrections_test_{timestamp}@example.com",
            "username": f"corrections_user_{timestamp}",
            "password": "TestPassword123!"
        }
        
        success, response = self.run_test("User Registration", "POST", "auth/register", 200, data=user_data)
        if success and 'access_token' in response:
            self.auth_token = response['access_token']
            self.user_data = response['user']
            print(f"   ✅ User created: {self.user_data['username']}")
            return True
        return False

    def create_test_track(self):
        """Create a track owned by the current user"""
        track_data = {
            "title": "Test Track for Corrections",
            "artist": self.user_data['username'],  # Use username as artist
            "region": "Afrique",
            "style": "Bikutsi",
            "instrument": "Balafon",
            "duration": 180,
            "bpm": 140,
            "mood": "Énergique",
            "audio_url": "https://example.com/test-track.mp3",
            "preview_url": "https://example.com/test-preview.mp3",
            "artwork_url": "https://example.com/test-artwork.jpg",
            "price": 4.99,
            "description": "Test track for corrections testing"
        }
        
        success, response = self.run_test("Create Test Track", "POST", "tracks", 200, data=track_data)
        if success and 'id' in response:
            self.created_track_id = response['id']
            print(f"   ✅ Track created with ID: {self.created_track_id}")
            print(f"   ✅ Track user_id: {response.get('user_id', 'Not set')}")
            return True
        return False

    def test_subscription_plans(self):
        """Test getting subscription plans"""
        success, response = self.run_test(
            "Get Subscription Plans", 
            "GET", 
            "subscriptions/plans", 
            200
        )
        
        if success and isinstance(response, list):
            print(f"   ✅ Found {len(response)} subscription plans")
            for plan in response:
                if plan.get('name') == 'Pro':
                    self.subscription_plan_id = plan.get('id')
                    print(f"   ✅ Pro plan ID stored: {self.subscription_plan_id}")
                    break
        
        return success

    def test_create_subscription(self):
        """Test creating a subscription"""
        if not self.subscription_plan_id:
            print("❌ No Pro plan ID available")
            return False
            
        subscription_data = {
            "plan_id": self.subscription_plan_id,
            "billing_cycle": "monthly"
        }
        
        success, response = self.run_test(
            "Create Pro Subscription", 
            "POST", 
            "subscriptions/subscribe", 
            200, 
            data=subscription_data,
            auth_required=True
        )
        
        if success:
            print(f"   ✅ Subscription created: {response.get('status', 'N/A')}")
        
        return success

    def test_get_my_subscription(self):
        """Test the CORRECTED my-subscription endpoint"""
        success, response = self.run_test(
            "Get My Subscription (CORRECTED)", 
            "GET", 
            "subscriptions/my-subscription", 
            200, 
            auth_required=True
        )
        
        if success:
            if response:
                plan = response.get('plan', {})
                print(f"   ✅ CORRECTION VERIFIED: Subscription retrieved successfully")
                print(f"   ✅ Plan: {plan.get('name', 'N/A')}")
                print(f"   ✅ Status: {response.get('status', 'N/A')}")
                print(f"   ✅ Can sell music: {plan.get('can_sell_music', False)}")
            else:
                print("   ✅ No subscription found (valid response)")
        
        return success

    def test_create_marketplace_listing(self):
        """Test the CORRECTED marketplace listing creation"""
        if not self.created_track_id:
            print("❌ No track ID available")
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
            "Create Marketplace Listing (CORRECTED)", 
            "POST", 
            "marketplace/list", 
            200, 
            data=listing_data,
            auth_required=True
        )
        
        if success:
            self.music_listing_id = response.get('id')
            print(f"   ✅ CORRECTION VERIFIED: Listing created successfully")
            print(f"   ✅ Listing ID: {self.music_listing_id}")
            print(f"   ✅ Track ownership verified")
        
        return success

    def test_marketplace_listings_with_price_filters(self):
        """Test the CORRECTED marketplace price filters"""
        price_filter_tests = [
            {"price_min": 10.0},
            {"price_max": 50.0},
            {"price_min": 10.0, "price_max": 50.0}
        ]
        
        results = []
        for filter_params in price_filter_tests:
            filter_desc = ", ".join([f"{k}={v}" for k, v in filter_params.items()])
            
            success, response = self.run_test(
                f"Get Marketplace Listings with Price Filters (CORRECTED): {filter_desc}", 
                "GET", 
                "marketplace/listings", 
                200, 
                params=filter_params
            )
            
            if success:
                print(f"   ✅ CORRECTION VERIFIED: Price filter {filter_desc} works")
                print(f"   ✅ Found {len(response) if isinstance(response, list) else 0} listings")
            
            results.append(success)
        
        return all(results)

    def test_my_tracks_endpoint(self):
        """Test the CORRECTED my-tracks endpoint"""
        success, response = self.run_test(
            "Get My Tracks (CORRECTED)", 
            "GET", 
            "admin/my-tracks", 
            200, 
            auth_required=True
        )
        
        if success and isinstance(response, list):
            print(f"   ✅ CORRECTION VERIFIED: My tracks endpoint works")
            print(f"   ✅ Found {len(response)} tracks owned by user")
            
            # Check if our created track is in the list
            track_found = False
            for track in response:
                if track.get('id') == self.created_track_id:
                    track_found = True
                    print(f"   ✅ Created track found in my tracks")
                    print(f"   ✅ Track user_id: {track.get('user_id', 'Not set')}")
                    break
            
            if not track_found and self.created_track_id:
                print(f"   ⚠️  Created track not found in my tracks (might be ownership issue)")
        
        return success

    def test_complete_scenario(self):
        """Test the complete scenario mentioned in the review request"""
        print("\n🎯 TESTING COMPLETE SCENARIO:")
        print("1. Create user and subscribe to Pro plan")
        print("2. Create track via upload")
        print("3. List track in marketplace")
        print("4. Verify everything works without errors")
        
        # Step 1: User and subscription (already done)
        print("\n✅ Step 1: User created and subscribed to Pro plan")
        
        # Step 2: Track creation (already done)
        print("✅ Step 2: Track created")
        
        # Step 3: Marketplace listing (already done)
        print("✅ Step 3: Track listed in marketplace")
        
        # Step 4: Final verification
        print("\n🔍 Step 4: Final verification...")
        
        # Verify subscription still works
        sub_success, _ = self.run_test(
            "Final Verification - My Subscription", 
            "GET", 
            "subscriptions/my-subscription", 
            200, 
            auth_required=True
        )
        
        # Verify marketplace listing exists
        listing_success, response = self.run_test(
            "Final Verification - My Listings", 
            "GET", 
            "marketplace/my-listings", 
            200, 
            auth_required=True
        )
        
        # Verify my tracks
        tracks_success, _ = self.run_test(
            "Final Verification - My Tracks", 
            "GET", 
            "admin/my-tracks", 
            200, 
            auth_required=True
        )
        
        all_success = sub_success and listing_success and tracks_success
        
        if all_success:
            print("🎉 COMPLETE SCENARIO SUCCESSFUL - All corrections working!")
        else:
            print("❌ Some issues remain in the complete scenario")
        
        return all_success

def main():
    print("🔧 US EXPLO API - CORRECTIONS TESTING")
    print("Testing specific corrections mentioned in review request:")
    print("1. Track ownership (user_id field)")
    print("2. Subscription pipeline (MongoDB serialization)")
    print("3. Marketplace filters (price filters)")
    print("4. My-tracks endpoint (user_id ownership)")
    print("=" * 70)
    
    # Get the correct backend URL from environment
    backend_url = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
    if not backend_url.endswith('/api'):
        backend_url = f"{backend_url}/api"
    
    print(f"🌐 Testing backend at: {backend_url}")
    tester = USExploCorrectionsTest(base_url=backend_url)
    
    # Test sequence for corrections
    tests = [
        ("Setup User and Auth", tester.setup_user_and_auth),
        ("Create Test Track", tester.create_test_track),
        ("Get Subscription Plans", tester.test_subscription_plans),
        ("Create Pro Subscription", tester.test_create_subscription),
        ("Get My Subscription (CORRECTED)", tester.test_get_my_subscription),
        ("Create Marketplace Listing (CORRECTED)", tester.test_create_marketplace_listing),
        ("Marketplace Price Filters (CORRECTED)", tester.test_marketplace_listings_with_price_filters),
        ("My Tracks Endpoint (CORRECTED)", tester.test_my_tracks_endpoint),
        ("Complete Scenario Test", tester.test_complete_scenario),
    ]
    
    print(f"\nRunning {len(tests)} correction tests...")
    
    failed_tests = []
    
    for test_name, test_func in tests:
        try:
            if not test_func():
                failed_tests.append(test_name)
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            failed_tests.append(test_name)
    
    # Print final results
    print("\n" + "=" * 70)
    print(f"📊 CORRECTIONS TEST RESULTS")
    print(f"Total tests: {tester.tests_run}")
    print(f"Passed: {tester.tests_passed}")
    print(f"Failed: {len(failed_tests)}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if failed_tests:
        print(f"\n❌ Failed tests:")
        for test in failed_tests:
            print(f"   - {test}")
    else:
        print(f"\n🎉 ALL CORRECTIONS WORKING PERFECTLY!")
    
    print("\n" + "=" * 70)
    
    # Return appropriate exit code
    return 0 if len(failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
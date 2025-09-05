#!/usr/bin/env python3

import requests
import sys
import json
import time
import os
import traceback
from datetime import datetime

class FocusedUSExploAPITester:
    def __init__(self, base_url="http://localhost:8001/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.auth_token = None
        self.user_data = None
        self.subscription_plan_id = None
        self.created_track_id = None
        self.community_group_id = None
        self.second_user_token = None
        self.second_user_data = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, auth_required=False):
        """Run a single API test with detailed error capture"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        headers = {'Content-Type': 'application/json'}
        
        # Add auth header if required and available
        if auth_required and self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        if params:
            print(f"   Params: {params}")
        
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
                    print(f"   Response: {json.dumps(response_data, indent=2)[:500]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error Response: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error Text: {response.text}")
                
                # Capture full stack trace for 500 errors
                if response.status_code == 500:
                    print(f"   🚨 SERVER ERROR 500 - Full response:")
                    print(f"   Headers: {dict(response.headers)}")
                    print(f"   Content: {response.text}")
                
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Exception: {str(e)}")
            print(f"   Exception traceback: {traceback.format_exc()}")
            return False, {}

    def setup_test_user(self):
        """Create and authenticate a test user"""
        timestamp = int(time.time())
        user_data = {
            "email": f"focused_test_user_{timestamp}@example.com",
            "username": f"focuseduser_{timestamp}",
            "password": "TestPassword123!"
        }
        
        success, response = self.run_test("User Registration", "POST", "auth/register", 200, data=user_data)
        if success and 'access_token' in response:
            self.auth_token = response['access_token']
            self.user_data = response['user']
            print(f"   ✅ User created: {self.user_data['username']} (ID: {self.user_data['id']})")
            return True
        return False

    def setup_second_user(self):
        """Create a second test user for group testing"""
        timestamp = int(time.time())
        user_data = {
            "email": f"focused_test_user2_{timestamp}@example.com",
            "username": f"focuseduser2_{timestamp}",
            "password": "TestPassword123!"
        }
        
        success, response = self.run_test("Second User Registration", "POST", "auth/register", 200, data=user_data)
        if success and 'access_token' in response:
            self.second_user_token = response['access_token']
            self.second_user_data = response['user']
            print(f"   ✅ Second user created: {self.second_user_data['username']} (ID: {self.second_user_data['id']})")
            return True
        return False

    def create_test_track(self):
        """Create a test track for marketplace testing"""
        track_data = {
            "title": "Test Bikutsi Track for Marketplace",
            "artist": self.user_data['username'],  # Use current user's username
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
            "description": "A test Bikutsi track for marketplace testing"
        }
        
        success, response = self.run_test("Create Test Track", "POST", "tracks", 200, data=track_data)
        if success and 'id' in response:
            self.created_track_id = response['id']
            print(f"   ✅ Track created: {self.created_track_id}")
            return True
        return False

    # ===== FOCUSED TEST 1: SUBSCRIPTION SYSTEM =====
    
    def test_subscription_system(self):
        """Test the complete subscription flow focusing on the problematic GET endpoint"""
        print("\n" + "="*60)
        print("🎯 FOCUSED TEST 1: SYSTÈME D'ABONNEMENTS")
        print("="*60)
        
        # Step 1: Get subscription plans
        success, plans_response = self.run_test(
            "Get Subscription Plans", 
            "GET", 
            "subscriptions/plans", 
            200
        )
        
        if not success or not plans_response:
            print("❌ Cannot proceed - no subscription plans available")
            return False
        
        # Find Pro plan
        pro_plan = None
        for plan in plans_response:
            if plan.get('name') == 'Pro':
                pro_plan = plan
                self.subscription_plan_id = plan.get('id')
                break
        
        if not pro_plan:
            print("❌ Cannot find Pro plan")
            return False
        
        print(f"   ✅ Found Pro plan: {pro_plan.get('name')} - €{pro_plan.get('price_monthly')}/mois")
        print(f"   Plan ID: {self.subscription_plan_id}")
        
        # Step 2: Create subscription
        subscription_data = {
            "plan_id": self.subscription_plan_id,
            "billing_cycle": "monthly"
        }
        
        success, sub_response = self.run_test(
            "Create Subscription (Pro Plan)", 
            "POST", 
            "subscriptions/subscribe", 
            200, 
            data=subscription_data,
            auth_required=True
        )
        
        if not success:
            print("❌ Failed to create subscription")
            return False
        
        print(f"   ✅ Subscription created: {sub_response.get('id')}")
        print(f"   Status: {sub_response.get('status')}")
        print(f"   Billing cycle: {sub_response.get('billing_cycle')}")
        
        # Step 3: THE PROBLEMATIC ENDPOINT - Get user subscription
        print(f"\n🎯 TESTING PROBLEMATIC ENDPOINT: GET /api/subscriptions/my-subscription")
        success, my_sub_response = self.run_test(
            "Get My Subscription (PROBLEMATIC ENDPOINT)", 
            "GET", 
            "subscriptions/my-subscription", 
            200, 
            auth_required=True
        )
        
        if success:
            print(f"   ✅ SUCCESS! Subscription retrieved successfully")
            if my_sub_response:
                plan = my_sub_response.get('plan', {})
                print(f"   Subscription status: {my_sub_response.get('status')}")
                print(f"   Plan name: {plan.get('name')}")
                print(f"   Billing cycle: {my_sub_response.get('billing_cycle')}")
                print(f"   Can sell music: {plan.get('can_sell_music')}")
            else:
                print(f"   ⚠️  Empty response but status 200")
            return True
        else:
            print(f"   ❌ FAILED! This is the problematic endpoint mentioned in test_result.md")
            return False

    # ===== FOCUSED TEST 2: MARKETPLACE MUSICALE =====
    
    def test_marketplace_system(self):
        """Test the marketplace system focusing on the problematic POST endpoint"""
        print("\n" + "="*60)
        print("🎯 FOCUSED TEST 2: MARKETPLACE MUSICALE")
        print("="*60)
        
        # Ensure we have a subscription (required for marketplace)
        if not self.subscription_plan_id:
            print("❌ No subscription available - running subscription test first")
            if not self.test_subscription_system():
                print("❌ Cannot test marketplace without subscription")
                return False
        
        # Ensure we have a track to list
        if not self.created_track_id:
            print("❌ No track available - creating test track")
            if not self.create_test_track():
                print("❌ Cannot test marketplace without track")
                return False
        
        # Step 1: THE PROBLEMATIC ENDPOINT - Create music listing
        print(f"\n🎯 TESTING PROBLEMATIC ENDPOINT: POST /api/marketplace/list")
        listing_data = {
            "track_id": self.created_track_id,
            "listing_type": "sale",
            "sale_price": 15.99,
            "license_price": 25.99,
            "license_terms": "commercial",
            "royalty_percentage": 5.0,
            "is_exclusive": False
        }
        
        success, listing_response = self.run_test(
            "Create Music Listing (PROBLEMATIC ENDPOINT)", 
            "POST", 
            "marketplace/list", 
            200, 
            data=listing_data,
            auth_required=True
        )
        
        if success:
            print(f"   ✅ SUCCESS! Music listing created successfully")
            print(f"   Listing ID: {listing_response.get('id')}")
            print(f"   Track ID: {listing_response.get('track_id')}")
            print(f"   Sale price: €{listing_response.get('sale_price')}")
        else:
            print(f"   ❌ FAILED! This is the problematic endpoint mentioned in test_result.md")
            print(f"   Expected issue: ownership check or artist mismatch")
        
        # Step 2: Test marketplace listings (basic)
        success2, listings_response = self.run_test(
            "Get Marketplace Listings", 
            "GET", 
            "marketplace/listings", 
            200
        )
        
        if success2:
            print(f"   ✅ Marketplace listings retrieved: {len(listings_response)} listings")
        
        # Step 3: THE PROBLEMATIC FILTERS - Test with price filters
        print(f"\n🎯 TESTING PROBLEMATIC FILTERS: price_min/price_max")
        success3, filtered_response = self.run_test(
            "Get Marketplace Listings with Price Filters (PROBLEMATIC)", 
            "GET", 
            "marketplace/listings", 
            200,
            params={"price_min": 10.0, "price_max": 50.0}
        )
        
        if success3:
            print(f"   ✅ SUCCESS! Price filters working")
            print(f"   Filtered listings: {len(filtered_response)} listings")
        else:
            print(f"   ❌ FAILED! This is the problematic filter mentioned in test_result.md")
            print(f"   Expected issue: MongoDB '$or array vide' error")
        
        # Step 4: Test my listings
        success4, my_listings_response = self.run_test(
            "Get My Marketplace Listings", 
            "GET", 
            "marketplace/my-listings", 
            200,
            auth_required=True
        )
        
        if success4:
            print(f"   ✅ My listings retrieved: {len(my_listings_response)} listings")
        
        return success and success3  # Both problematic endpoints must work

    # ===== FOCUSED TEST 3: GROUPES COMMUNAUTAIRES =====
    
    def test_community_groups_system(self):
        """Test the community groups system focusing on the problematic GET messages endpoint"""
        print("\n" + "="*60)
        print("🎯 FOCUSED TEST 3: GROUPES COMMUNAUTAIRES")
        print("="*60)
        
        # Ensure we have a second user
        if not self.second_user_data:
            print("❌ No second user available - creating second user")
            if not self.setup_second_user():
                print("❌ Cannot test groups without second user")
                return False
        
        # Step 1: Create community group
        group_data = {
            "name": "Musiciens Bikutsi Test",
            "description": "Groupe de test pour les musiciens Bikutsi",
            "group_type": "public",
            "max_members": 100,
            "tags": ["Bikutsi", "Test", "Collaboration"]
        }
        
        success, group_response = self.run_test(
            "Create Community Group", 
            "POST", 
            "community/groups", 
            200, 
            data=group_data,
            auth_required=True
        )
        
        if not success:
            print("❌ Failed to create community group")
            return False
        
        self.community_group_id = group_response.get('id')
        print(f"   ✅ Group created: {self.community_group_id}")
        print(f"   Group name: {group_response.get('name')}")
        
        # Step 2: Get community groups
        success2, groups_response = self.run_test(
            "Get Community Groups", 
            "GET", 
            "community/groups", 
            200
        )
        
        if success2:
            print(f"   ✅ Groups retrieved: {len(groups_response)} groups")
        
        # Step 3: Join group with second user
        original_token = self.auth_token
        self.auth_token = self.second_user_token
        
        success3, join_response = self.run_test(
            "Join Community Group (Second User)", 
            "POST", 
            f"community/groups/{self.community_group_id}/join", 
            200, 
            auth_required=True
        )
        
        if success3:
            print(f"   ✅ Second user joined group successfully")
            print(f"   Join message: {join_response.get('message')}")
        else:
            print(f"   ❌ Failed to join group")
            self.auth_token = original_token
            return False
        
        # Step 4: Send message to group (as second user)
        message_data = {
            "content": "Salut ! Message de test dans le groupe Bikutsi.",
            "message_type": "text"
        }
        
        success4, message_response = self.run_test(
            "Send Group Message (Second User)", 
            "POST", 
            f"community/groups/{self.community_group_id}/messages", 
            200, 
            data=message_data,
            auth_required=True
        )
        
        if success4:
            print(f"   ✅ Message sent successfully")
            print(f"   Message ID: {message_response.get('id')}")
        else:
            print(f"   ❌ Failed to send message")
        
        # Restore original token
        self.auth_token = original_token
        
        # Step 5: Send another message as original user
        message_data2 = {
            "content": "Réponse du créateur du groupe ! Bienvenue !",
            "message_type": "text"
        }
        
        success5, message_response2 = self.run_test(
            "Send Group Message (Original User)", 
            "POST", 
            f"community/groups/{self.community_group_id}/messages", 
            200, 
            data=message_data2,
            auth_required=True
        )
        
        if success5:
            print(f"   ✅ Second message sent successfully")
        
        # Step 6: THE PROBLEMATIC ENDPOINT - Get group messages
        print(f"\n🎯 TESTING PROBLEMATIC ENDPOINT: GET /api/community/groups/{self.community_group_id}/messages")
        success6, messages_response = self.run_test(
            "Get Group Messages (PROBLEMATIC ENDPOINT)", 
            "GET", 
            f"community/groups/{self.community_group_id}/messages", 
            200,
            auth_required=True
        )
        
        if success6:
            print(f"   ✅ SUCCESS! Group messages retrieved successfully")
            print(f"   Messages count: {len(messages_response)}")
            for i, message in enumerate(messages_response[:3]):
                sender = message.get('sender', {})
                print(f"   Message {i+1}: {message.get('content', 'N/A')[:50]}...")
                print(f"     by {sender.get('username', 'N/A')}")
            return True
        else:
            print(f"   ❌ FAILED! This is the problematic endpoint mentioned in test_result.md")
            print(f"   Expected issue: 403 'Not authenticated' - membership verification problem")
            return False

def main():
    print("🎯 US EXPLO API - FOCUSED TESTING FOR 3 PROBLEMATIC ENDPOINTS")
    print("🔥 Testing specific issues identified in test_result.md")
    print("=" * 80)
    
    # Get the correct backend URL from environment
    backend_url = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
    if not backend_url.endswith('/api'):
        backend_url = f"{backend_url}/api"
    
    print(f"🌐 Testing backend at: {backend_url}")
    tester = FocusedUSExploAPITester(base_url=backend_url)
    
    # Setup phase
    print("\n📋 SETUP PHASE")
    print("-" * 40)
    
    if not tester.setup_test_user():
        print("❌ Failed to setup test user - aborting")
        sys.exit(1)
    
    # Run the 3 focused tests
    results = {}
    
    try:
        # Test 1: Subscription System
        results['subscriptions'] = tester.test_subscription_system()
        
        # Test 2: Marketplace System  
        results['marketplace'] = tester.test_marketplace_system()
        
        # Test 3: Community Groups System
        results['groups'] = tester.test_community_groups_system()
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
    
    # Final results
    print("\n" + "=" * 80)
    print("📊 FOCUSED TESTING RESULTS")
    print("=" * 80)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    print(f"\n🎯 SPECIFIC PROBLEMATIC ENDPOINTS TESTED:")
    print(f"   1. Système d'abonnements (GET /api/subscriptions/my-subscription): {'✅ FIXED' if results.get('subscriptions') else '❌ STILL BROKEN'}")
    print(f"   2. Marketplace musicale (POST /api/marketplace/list + filters): {'✅ FIXED' if results.get('marketplace') else '❌ STILL BROKEN'}")
    print(f"   3. Groupes communautaires (GET /api/community/groups/{{id}}/messages): {'✅ FIXED' if results.get('groups') else '❌ STILL BROKEN'}")
    
    print(f"\n📈 SUMMARY:")
    print(f"   Total focused tests: {total_tests}")
    print(f"   Tests passed: {passed_tests}")
    print(f"   Tests failed: {total_tests - passed_tests}")
    print(f"   Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print(f"\n🎉 ALL PROBLEMATIC ENDPOINTS ARE NOW WORKING!")
        sys.exit(0)
    else:
        print(f"\n⚠️  SOME ENDPOINTS STILL HAVE ISSUES - See detailed logs above")
        sys.exit(1)

if __name__ == "__main__":
    main()
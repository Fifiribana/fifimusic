#!/usr/bin/env python3

import requests
import sys
import json
import time
import os
from datetime import datetime

class SolidaritySystemTester:
    def __init__(self, base_url="http://localhost:8001/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.auth_token = None
        self.user_data = None
        self.campaign_id = None
        self.donation_id = None
        self.advice_id = None
        self.support_request_id = None

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
                response = requests.delete(url, headers=headers, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")

            print(f"   Status: {response.status_code}")
            
            if response.status_code == expected_status:
                print(f"   ✅ PASS")
                self.tests_passed += 1
                
                # Try to parse JSON response
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2, default=str)[:500]}...")
                    return response_data
                except:
                    print(f"   Response: {response.text[:200]}...")
                    return response.text
            else:
                print(f"   ❌ FAIL - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            return None

    def test_authentication(self):
        """Test user authentication for solidarity system"""
        print("\n" + "="*60)
        print("🎵 TESTING SOLIDARITY SYSTEM AUTHENTICATION")
        print("="*60)
        
        # Create a test musician user
        user_data = {
            "email": f"musicien_solidaire_{int(time.time())}@usexplo.com",
            "username": f"musicien_solidaire_{int(time.time())}",
            "password": "SolidariteMusicale2025!"
        }
        
        response = self.run_test(
            "User Registration for Solidarity",
            "POST", 
            "auth/register",
            200,
            user_data
        )
        
        if response:
            self.auth_token = response.get('access_token')
            self.user_data = response.get('user')
            print(f"✅ Authenticated user: {self.user_data.get('username')}")
            return True
        return False

    def test_solidarity_stats(self):
        """Test global solidarity statistics (no auth required)"""
        print("\n" + "="*60)
        print("📊 TESTING SOLIDARITY STATISTICS")
        print("="*60)
        
        response = self.run_test(
            "Global Solidarity Statistics",
            "GET",
            "solidarity/stats",
            200,
            auth_required=False
        )
        
        if response:
            print(f"📈 Campaigns: {response.get('campaigns', {})}")
            print(f"💰 Donations: {response.get('donations', {})}")
            print(f"🤝 Community: {response.get('community', {})}")
            return True
        return False

    def test_solidarity_campaigns(self):
        """Test solidarity campaigns listing (public)"""
        print("\n" + "="*60)
        print("🎯 TESTING SOLIDARITY CAMPAIGNS")
        print("="*60)
        
        # Test public campaigns list
        response = self.run_test(
            "Public Campaigns List",
            "GET",
            "solidarity/campaigns",
            200,
            auth_required=False
        )
        
        if response:
            print(f"📋 Found {len(response)} campaigns")
            return True
        return False

    def test_campaign_creation(self):
        """Test creating a new solidarity campaign"""
        print("\n" + "="*60)
        print("🎼 TESTING CAMPAIGN CREATION")
        print("="*60)
        
        # Create campaign with suggested parameters
        campaign_data = {
            "title": "Album Bikutsi Solidaire",
            "description": "Un projet musical pour unir les communautés à travers la musique bikutsi traditionnelle",
            "project_type": "album",
            "goal_amount": 2500.0,
            "deadline_days": 45,
            "story": "Je crée un album pour unir les communautés à travers la musique bikutsi traditionnelle. Cette musique ancestrale du Cameroun porte en elle les valeurs de solidarité et d'entraide qui nous rassemblent. Ensemble nous sommes très forts ! 🎵",
            "needs": [
                "Studio d'enregistrement",
                "Instruments traditionnels",
                "Mixage professionnel"
            ],
            "region": "Afrique",
            "music_style": "Bikutsi",
            "image_url": "https://example.com/bikutsi-album-cover.jpg",
            "video_url": "https://example.com/bikutsi-teaser.mp4"
        }
        
        response = self.run_test(
            "Create Bikutsi Album Campaign",
            "POST",
            "solidarity/campaigns",
            200,
            campaign_data,
            auth_required=True
        )
        
        if response:
            self.campaign_id = response.get('id')
            print(f"🎯 Created campaign: {response.get('title')}")
            print(f"💰 Goal: €{response.get('goal_amount')}")
            print(f"📅 Deadline: {response.get('deadline')}")
            return True
        return False

    def test_campaign_details(self):
        """Test getting campaign details"""
        print("\n" + "="*60)
        print("📋 TESTING CAMPAIGN DETAILS")
        print("="*60)
        
        if not self.campaign_id:
            print("❌ No campaign ID available for testing")
            return False
        
        response = self.run_test(
            "Get Campaign Details",
            "GET",
            f"solidarity/campaigns/{self.campaign_id}",
            200,
            auth_required=False
        )
        
        if response:
            print(f"📊 Campaign: {response.get('title')}")
            print(f"💰 Current: €{response.get('current_amount', 0)}")
            print(f"🎯 Goal: €{response.get('goal_amount')}")
            print(f"📈 Progress: {response.get('progress_percentage', 0):.1f}%")
            print(f"👥 Donors: {response.get('donors_count', 0)}")
            return True
        return False

    def test_donation(self):
        """Test making a donation (anonymous possible)"""
        print("\n" + "="*60)
        print("💝 TESTING DONATION SYSTEM")
        print("="*60)
        
        if not self.campaign_id:
            print("❌ No campaign ID available for testing")
            return False
        
        # Test donation with suggested parameters
        donation_data = {
            "campaign_id": self.campaign_id,
            "amount": 50.0,
            "donor_name": "Ami de la Musique Bikutsi",
            "message": "Ensemble nous sommes très forts ! 🎵 Votre projet musical va unir nos cœurs.",
            "is_anonymous": False
        }
        
        response = self.run_test(
            "Make Donation to Campaign",
            "POST",
            "solidarity/donate",
            200,
            donation_data,
            auth_required=False  # Anonymous donations allowed
        )
        
        if response:
            self.donation_id = response.get('donation_id')
            print(f"💰 Donation successful: €{donation_data['amount']}")
            print(f"💝 New total: €{response.get('new_total', 0)}")
            print(f"💌 Message: {donation_data['message']}")
            return True
        return False

    def test_community_advice(self):
        """Test community advice system"""
        print("\n" + "="*60)
        print("🧘 TESTING COMMUNITY ADVICE")
        print("="*60)
        
        # Test getting existing advice
        response = self.run_test(
            "Get Community Advice",
            "GET",
            "solidarity/advice",
            200,
            params={"category": "spiritual"},
            auth_required=False
        )
        
        if response:
            print(f"📚 Found {len(response)} advice posts")
        
        # Test creating new advice with suggested parameters
        advice_data = {
            "category": "spiritual",
            "title": "La méditation avant création musicale",
            "content": "Avant chaque session de création musicale, prenez quelques minutes pour méditer. Connectez-vous à votre essence créative et laissez la musique couler naturellement. La spiritualité nourrit l'art et l'art nourrit l'âme. Ensemble nous sommes très forts dans cette démarche créative ! 🎵✨",
            "advice_type": "general",
            "target_audience": "all",
            "tags": ["méditation", "création", "spiritualité", "bikutsi", "musique"]
        }
        
        response = self.run_test(
            "Create Spiritual Advice",
            "POST",
            "solidarity/advice",
            200,
            advice_data,
            auth_required=True
        )
        
        if response:
            self.advice_id = response.get('id')
            print(f"🧘 Created advice: {response.get('title')}")
            print(f"📂 Category: {response.get('category')}")
            return True
        return False

    def test_support_requests(self):
        """Test support request system"""
        print("\n" + "="*60)
        print("🆘 TESTING SUPPORT REQUESTS")
        print("="*60)
        
        # Test creating a support request
        support_data = {
            "category": "creative",
            "title": "Besoin d'aide pour arrangement Bikutsi moderne",
            "description": "Je travaille sur un projet d'album Bikutsi et j'aimerais moderniser les arrangements tout en gardant l'authenticité traditionnelle. Quelqu'un pourrait-il me conseiller sur l'équilibre entre tradition et modernité ? Ensemble nous sommes très forts pour préserver notre patrimoine musical ! 🎵",
            "urgency": "normal"
        }
        
        response = self.run_test(
            "Create Support Request",
            "POST",
            "solidarity/support-request",
            200,
            support_data,
            auth_required=True
        )
        
        if response:
            self.support_request_id = response.get('id')
            print(f"🆘 Created support request: {response.get('title')}")
            print(f"📂 Category: {response.get('category')}")
            print(f"⚡ Urgency: {response.get('urgency')}")
        
        # Test getting support requests
        response = self.run_test(
            "Get Support Requests",
            "GET",
            "solidarity/support-requests",
            200,
            params={"category": "creative", "status": "open"},
            auth_required=False
        )
        
        if response:
            print(f"📋 Found {len(response)} support requests")
            return True
        return False

    def test_anonymous_donation(self):
        """Test anonymous donation functionality"""
        print("\n" + "="*60)
        print("🕶️ TESTING ANONYMOUS DONATION")
        print("="*60)
        
        if not self.campaign_id:
            print("❌ No campaign ID available for testing")
            return False
        
        # Test anonymous donation
        anonymous_donation_data = {
            "campaign_id": self.campaign_id,
            "amount": 25.0,
            "donor_name": "Anonyme",
            "message": "La musique unit les cœurs ! Continuez votre beau projet. 🎵",
            "is_anonymous": True
        }
        
        response = self.run_test(
            "Make Anonymous Donation",
            "POST",
            "solidarity/donate",
            200,
            anonymous_donation_data,
            auth_required=False  # No authentication for anonymous
        )
        
        if response:
            print(f"🕶️ Anonymous donation successful: €{anonymous_donation_data['amount']}")
            print(f"💝 New total: €{response.get('new_total', 0)}")
            return True
        return False

    def run_all_tests(self):
        """Run all solidarity system tests"""
        print("\n" + "🎵"*20)
        print("🎵 US EXPLO - SYSTÈME DE SOLIDARITÉ MUSICALE 🎵")
        print("🎵 Testing Musical Solidarity & Support System 🎵")
        print("🎵"*20)
        
        # Test sequence following the review request
        tests = [
            ("Authentication", self.test_authentication),
            ("Global Statistics", self.test_solidarity_stats),
            ("Campaigns List", self.test_solidarity_campaigns),
            ("Campaign Creation", self.test_campaign_creation),
            ("Campaign Details", self.test_campaign_details),
            ("Donation System", self.test_donation),
            ("Community Advice", self.test_community_advice),
            ("Support Requests", self.test_support_requests),
            ("Anonymous Donation", self.test_anonymous_donation),
        ]
        
        for test_name, test_func in tests:
            try:
                success = test_func()
                if not success:
                    print(f"\n⚠️ Test '{test_name}' had issues but continuing...")
            except Exception as e:
                print(f"\n❌ Test '{test_name}' failed with error: {str(e)}")
        
        # Final summary
        print("\n" + "="*60)
        print("🎵 SOLIDARITY SYSTEM TEST SUMMARY 🎵")
        print("="*60)
        print(f"📊 Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 TOUS LES TESTS RÉUSSIS ! SYSTÈME DE SOLIDARITÉ OPÉRATIONNEL ! 🎉")
            print("🎵 'Ensemble nous sommes très forts !' - Objectif atteint ! 🎵")
        else:
            print(f"\n⚠️ {self.tests_run - self.tests_passed} tests ont échoué. Vérification nécessaire.")
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    # Get backend URL from environment or use default
    backend_url = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
    api_url = f"{backend_url}/api"
    
    print(f"🔗 Testing Solidarity System at: {api_url}")
    
    tester = SolidaritySystemTester(api_url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)
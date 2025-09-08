#!/usr/bin/env python3

import requests
import sys
import json
import time
import os
from datetime import datetime

class TranslationDonationTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.auth_token = None
        self.user_data = None

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

    # ===== AUTHENTICATION SETUP =====
    def test_user_registration(self):
        """Test user registration for authenticated endpoints"""
        timestamp = int(time.time())
        user_data = {
            "email": f"translation_test_user_{timestamp}@usexplo.com",
            "username": f"translationuser_{timestamp}",
            "password": "TestPassword123!"
        }
        
        success, response = self.run_test("User Registration", "POST", "api/auth/register", 200, data=user_data)
        if success and 'access_token' in response:
            self.auth_token = response['access_token']
            self.user_data = response['user']
            print(f"   Registered user: {self.user_data['username']}")
            print(f"   Token received: {self.auth_token[:20]}...")
        return success

    # ===== TRANSLATION ENDPOINTS TESTS =====
    
    def test_basic_translation_french_to_english(self):
        """Test POST /translate - Basic text translation from French to English"""
        translation_data = {
            "text": "Découvrez la Musique du Monde",
            "target_language": "en",
            "source_language": "fr"
        }
        
        success, response = self.run_test(
            "Basic Translation (French to English)", 
            "POST", 
            "translate", 
            200, 
            data=translation_data
        )
        
        if success:
            print(f"   Original: {response.get('original_text', 'N/A')}")
            print(f"   Translated: {response.get('translated_text', 'N/A')}")
            print(f"   Source Language: {response.get('source_language', 'N/A')}")
            print(f"   Target Language: {response.get('target_language', 'N/A')}")
            print(f"   Confidence: {response.get('confidence', 'N/A')}")
        
        return success

    def test_translation_french_to_spanish(self):
        """Test POST /translate - French to Spanish translation"""
        translation_data = {
            "text": "Écoutez des aperçus de 30 secondes",
            "target_language": "es",
            "source_language": "fr"
        }
        
        success, response = self.run_test(
            "Translation (French to Spanish)", 
            "POST", 
            "translate", 
            200, 
            data=translation_data
        )
        
        if success:
            print(f"   Original: {response.get('original_text', 'N/A')}")
            print(f"   Translated: {response.get('translated_text', 'N/A')}")
        
        return success

    def test_translation_french_to_chinese(self):
        """Test POST /translate - French to Chinese translation"""
        translation_data = {
            "text": "Aucune inscription requise",
            "target_language": "zh",
            "source_language": "fr"
        }
        
        success, response = self.run_test(
            "Translation (French to Chinese)", 
            "POST", 
            "translate", 
            200, 
            data=translation_data
        )
        
        if success:
            print(f"   Original: {response.get('original_text', 'N/A')}")
            print(f"   Translated: {response.get('translated_text', 'N/A')}")
        
        return success

    def test_get_supported_languages(self):
        """Test GET /languages - Verify supported languages list"""
        success, response = self.run_test(
            "Get Supported Languages", 
            "GET", 
            "languages", 
            200
        )
        
        if success and isinstance(response, dict):
            print(f"   Found {len(response)} supported languages")
            # Show first 10 languages
            languages_list = list(response.items())[:10]
            for code, name in languages_list:
                print(f"   - {code}: {name}")
            print("   ...")
        
        return success

    def test_translated_tracks_english(self):
        """Test GET /tracks/translated?lang=en - Test translated track metadata"""
        success, response = self.run_test(
            "Get Translated Tracks (English)", 
            "GET", 
            "tracks/translated", 
            200,
            params={"lang": "en", "limit": 5}
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} translated tracks")
            for track in response[:3]:  # Show first 3 tracks
                print(f"   - {track.get('title', 'N/A')} by {track.get('artist', 'N/A')}")
                print(f"     Region: {track.get('region', 'N/A')} -> {track.get('region_translated', 'N/A')}")
                if track.get('description'):
                    print(f"     Description: {track.get('description', 'N/A')[:50]}...")
        
        return success

    def test_translated_tracks_spanish(self):
        """Test GET /tracks/translated?lang=es - Test Spanish translation"""
        success, response = self.run_test(
            "Get Translated Tracks (Spanish)", 
            "GET", 
            "tracks/translated", 
            200,
            params={"lang": "es", "limit": 3}
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} tracks translated to Spanish")
            for track in response[:2]:  # Show first 2 tracks
                print(f"   - {track.get('title', 'N/A')}")
                print(f"     Region: {track.get('region', 'N/A')} -> {track.get('region_translated', 'N/A')}")
        
        return success

    def test_batch_translation(self):
        """Test POST /translate/batch - Test batch translation functionality"""
        batch_data = {
            "texts": [
                "Accueil",
                "Explorer", 
                "Communauté",
                "Collections",
                "Premium"
            ],
            "target_language": "en",
            "source_language": "fr"
        }
        
        success, response = self.run_test(
            "Batch Translation (French to English)", 
            "POST", 
            "translate/batch", 
            200, 
            data=batch_data
        )
        
        if success:
            translations = response.get('translations', [])
            print(f"   Batch ID: {response.get('batch_id', 'N/A')}")
            print(f"   Processing time: {response.get('processing_time', 'N/A')}s")
            print(f"   Translated {len(translations)} texts:")
            for translation in translations:
                print(f"   - '{translation.get('original_text', 'N/A')}' -> '{translation.get('translated_text', 'N/A')}'")
        
        return success

    # ===== DONATION ENDPOINTS TESTS =====
    
    def test_donation_stats(self):
        """Test GET /donation/stats - Test donation statistics endpoint"""
        success, response = self.run_test(
            "Get Donation Statistics", 
            "GET", 
            "donation/stats", 
            200
        )
        
        if success:
            print(f"   Total Donated: €{response.get('total_donated', 0)}")
            print(f"   Monthly Donors: {response.get('monthly_donors', 0)}")
            print(f"   YouTube Views: {response.get('youtube_views', 0):,}")
            print(f"   Supported Artists: {response.get('supported_artists', 0)}")
        
        return success

    def test_create_donation_session_one_time(self):
        """Test POST /create-donation-session - Test one-time donation session creation"""
        donation_data = {
            "amount": 25.0,
            "currency": "EUR",
            "type": "one-time",
            "donor_email": "test@example.com",
            "payment_method": "stripe",
            "donor_name": "Test Donor",
            "message": "Supporting US EXPLO platform!",
            "is_anonymous": False,
            "purpose": "youtube_maintenance"
        }
        
        success, response = self.run_test(
            "Create One-Time Donation Session", 
            "POST", 
            "create-donation-session", 
            200, 
            data=donation_data
        )
        
        if success:
            print(f"   Checkout URL: {response.get('checkout_url', 'N/A')[:50]}...")
            print(f"   Session ID: {response.get('session_id', 'N/A')}")
            print(f"   Donation ID: {response.get('donation_id', 'N/A')}")
        
        return success

    def test_create_donation_session_monthly(self):
        """Test POST /create-donation-session - Test monthly donation session creation"""
        donation_data = {
            "amount": 10.0,
            "currency": "EUR",
            "type": "monthly",
            "donor_email": "monthly_supporter@example.com",
            "payment_method": "stripe",
            "donor_name": "Monthly Supporter",
            "message": "Monthly support for the platform",
            "is_anonymous": False,
            "purpose": "youtube_maintenance"
        }
        
        success, response = self.run_test(
            "Create Monthly Donation Session", 
            "POST", 
            "create-donation-session", 
            200, 
            data=donation_data
        )
        
        if success:
            print(f"   Monthly Checkout URL: {response.get('checkout_url', 'N/A')[:50]}...")
            print(f"   Session ID: {response.get('session_id', 'N/A')}")
            print(f"   Donation ID: {response.get('donation_id', 'N/A')}")
        
        return success

    def test_create_anonymous_donation_session(self):
        """Test POST /create-donation-session - Test anonymous donation"""
        donation_data = {
            "amount": 15.0,
            "currency": "EUR",
            "type": "one-time",
            "donor_email": "anonymous@example.com",
            "payment_method": "stripe",
            "is_anonymous": True,
            "purpose": "youtube_maintenance"
        }
        
        success, response = self.run_test(
            "Create Anonymous Donation Session", 
            "POST", 
            "create-donation-session", 
            200, 
            data=donation_data
        )
        
        if success:
            print(f"   Anonymous Checkout URL: {response.get('checkout_url', 'N/A')[:50]}...")
            print(f"   Session ID: {response.get('session_id', 'N/A')}")
        
        return success

    def test_recent_donors(self):
        """Test GET /recent-donors - Test recent donors list"""
        success, response = self.run_test(
            "Get Recent Donors", 
            "GET", 
            "recent-donors", 
            200,
            params={"limit": 10}
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} recent donors")
            for donor in response[:5]:  # Show first 5 donors
                print(f"   - {donor.get('name', 'N/A')}: €{donor.get('amount', 0)}")
                if donor.get('message'):
                    print(f"     Message: {donor.get('message', 'N/A')[:50]}...")
                print(f"     Date: {donor.get('date', 'N/A')}")
        
        return success

    # ===== ERROR HANDLING TESTS =====
    
    def test_translation_invalid_language(self):
        """Test translation with invalid target language"""
        translation_data = {
            "text": "Test text",
            "target_language": "invalid_lang",
            "source_language": "fr"
        }
        
        # This should still work with mock service, but may return error with real service
        success, response = self.run_test(
            "Translation with Invalid Language", 
            "POST", 
            "translate", 
            200,  # Mock service will handle this gracefully
            data=translation_data
        )
        
        return success

    def test_donation_invalid_amount(self):
        """Test donation with invalid amount"""
        donation_data = {
            "amount": -10.0,  # Invalid negative amount
            "currency": "EUR",
            "type": "one-time",
            "donor_email": "test@example.com",
            "payment_method": "stripe"
        }
        
        # This should fail validation
        success, response = self.run_test(
            "Donation with Invalid Amount", 
            "POST", 
            "create-donation-session", 
            500,  # Expecting error
            data=donation_data
        )
        
        return success

def main():
    print("🌍 US EXPLO Translation & Donation API Testing Suite")
    print("🔥 Testing: Translation Service & Donation System")
    print("=" * 70)
    
    # Get the correct backend URL from environment or use default
    backend_url = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
    if backend_url.endswith('/api'):
        backend_url = backend_url[:-4]  # Remove /api suffix for these endpoints
    
    print(f"🌐 Testing backend at: {backend_url}")
    tester = TranslationDonationTester(base_url=backend_url)
    
    # Test sequence for Translation and Donation endpoints
    tests = [
        # Authentication setup
        ("User Registration", tester.test_user_registration),
        
        # Translation Endpoints
        ("Basic Translation (French to English)", tester.test_basic_translation_french_to_english),
        ("Translation (French to Spanish)", tester.test_translation_french_to_spanish),
        ("Translation (French to Chinese)", tester.test_translation_french_to_chinese),
        ("Get Supported Languages", tester.test_get_supported_languages),
        ("Get Translated Tracks (English)", tester.test_translated_tracks_english),
        ("Get Translated Tracks (Spanish)", tester.test_translated_tracks_spanish),
        ("Batch Translation", tester.test_batch_translation),
        
        # Donation Endpoints
        ("Get Donation Statistics", tester.test_donation_stats),
        ("Create One-Time Donation Session", tester.test_create_donation_session_one_time),
        ("Create Monthly Donation Session", tester.test_create_donation_session_monthly),
        ("Create Anonymous Donation Session", tester.test_create_anonymous_donation_session),
        ("Get Recent Donors", tester.test_recent_donors),
        
        # Error Handling Tests
        ("Translation with Invalid Language", tester.test_translation_invalid_language),
        ("Donation with Invalid Amount", tester.test_donation_invalid_amount),
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
    print("\n" + "=" * 70)
    print(f"📊 FINAL RESULTS - TRANSLATION & DONATION TESTING")
    print(f"Tests run: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    print(f"Tests failed: {len(failed_tests)}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if failed_tests:
        print(f"\n❌ Failed tests:")
        for test in failed_tests:
            print(f"   - {test}")
    else:
        print(f"\n🎉 All tests passed!")
    
    print("\n" + "=" * 70)
    
    # Return appropriate exit code
    return 0 if len(failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
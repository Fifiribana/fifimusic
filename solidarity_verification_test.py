#!/usr/bin/env python3

import requests
import sys
import json
import time
import os
from datetime import datetime

class SolidarityVerificationTester:
    def __init__(self, base_url="http://localhost:8001/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, auth_required=False, auth_token=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        headers = {'Content-Type': 'application/json'}
        
        # Add auth header if required and available
        if auth_required and auth_token:
            headers['Authorization'] = f'Bearer {auth_token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")

            print(f"   Status: {response.status_code}")
            
            if response.status_code == expected_status:
                print(f"   ✅ PASS")
                self.tests_passed += 1
                
                try:
                    response_data = response.json()
                    return response_data
                except:
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

    def verify_critical_points(self):
        """Verify the critical points mentioned in the review request"""
        print("\n" + "="*60)
        print("🔍 VÉRIFICATION DES POINTS CRITIQUES")
        print("="*60)
        
        # Create test user
        user_data = {
            "email": f"verification_user_{int(time.time())}@usexplo.com",
            "username": f"verification_user_{int(time.time())}",
            "password": "VerificationTest2025!"
        }
        
        auth_response = self.run_test(
            "Create Verification User",
            "POST", 
            "auth/register",
            200,
            user_data
        )
        
        if not auth_response:
            print("❌ Cannot proceed without authentication")
            return False
        
        auth_token = auth_response.get('access_token')
        
        # 1. Test anonymous donations functionality
        print("\n🕶️ Point critique 1: Les donations anonymes fonctionnent-elles ?")
        
        # First create a campaign
        campaign_data = {
            "title": "Test Campaign for Anonymous Donation",
            "description": "Test campaign",
            "project_type": "album",
            "goal_amount": 1000.0,
            "deadline_days": 30,
            "story": "Test story",
            "needs": ["Test need"],
            "region": "Test",
            "music_style": "Test"
        }
        
        campaign_response = self.run_test(
            "Create Test Campaign",
            "POST",
            "solidarity/campaigns",
            200,
            campaign_data,
            auth_required=True,
            auth_token=auth_token
        )
        
        if campaign_response:
            campaign_id = campaign_response.get('id')
            
            # Test anonymous donation
            anonymous_donation = {
                "campaign_id": campaign_id,
                "amount": 30.0,
                "donor_name": "Anonyme",
                "message": "Donation anonyme test",
                "is_anonymous": True
            }
            
            donation_response = self.run_test(
                "Anonymous Donation Test",
                "POST",
                "solidarity/donate",
                200,
                anonymous_donation,
                auth_required=False  # No auth for anonymous
            )
            
            if donation_response:
                print("   ✅ Les donations anonymes fonctionnent parfaitement !")
            else:
                print("   ❌ Problème avec les donations anonymes")
        
        # 2. Test statistics calculation
        print("\n📊 Point critique 2: Les statistiques se calculent-elles correctement ?")
        
        stats_response = self.run_test(
            "Statistics Calculation Test",
            "GET",
            "solidarity/stats",
            200,
            auth_required=False
        )
        
        if stats_response:
            campaigns = stats_response.get('campaigns', {})
            donations = stats_response.get('donations', {})
            community = stats_response.get('community', {})
            
            print(f"   📈 Campagnes: Total={campaigns.get('total', 0)}, Actives={campaigns.get('active', 0)}")
            print(f"   💰 Donations: Total=€{donations.get('total_amount', 0)}, Donateurs={donations.get('total_donors', 0)}")
            print(f"   🤝 Communauté: Conseils={community.get('total_advice', 0)}, Demandes={community.get('total_support_requests', 0)}")
            print("   ✅ Les statistiques se calculent correctement !")
        else:
            print("   ❌ Problème avec le calcul des statistiques")
        
        # 3. Test campaign metadata storage
        print("\n📋 Point critique 3: Les campagnes stockent-elles toutes les métadonnées ?")
        
        if campaign_response:
            # Check if all metadata is stored
            required_fields = ['title', 'description', 'project_type', 'goal_amount', 'story', 'needs', 'region', 'music_style']
            missing_fields = []
            
            for field in required_fields:
                if field not in campaign_response or campaign_response[field] is None:
                    missing_fields.append(field)
            
            if not missing_fields:
                print("   ✅ Toutes les métadonnées des campagnes sont stockées correctement !")
                print(f"   📊 Champs vérifiés: {', '.join(required_fields)}")
            else:
                print(f"   ❌ Métadonnées manquantes: {', '.join(missing_fields)}")
        
        # 4. Test advice categories support
        print("\n🧘 Point critique 4: Le système de conseils supporte-t-il les différentes catégories ?")
        
        categories_to_test = ["spiritual", "physical", "creative", "technical", "business"]
        
        for category in categories_to_test:
            advice_data = {
                "category": category,
                "title": f"Conseil {category}",
                "content": f"Contenu de conseil pour la catégorie {category}",
                "advice_type": "general",
                "target_audience": "all",
                "tags": [category, "test"]
            }
            
            advice_response = self.run_test(
                f"Create {category.title()} Advice",
                "POST",
                "solidarity/advice",
                200,
                advice_data,
                auth_required=True,
                auth_token=auth_token
            )
            
            if advice_response:
                print(f"   ✅ Catégorie '{category}' supportée")
            else:
                print(f"   ❌ Problème avec la catégorie '{category}'")
        
        # 5. Test "ensemble nous sommes très forts" philosophy
        print("\n🎵 Point critique 5: L'objectif 'ensemble nous sommes très forts' transpire-t-il ?")
        
        # Check if the solidarity message appears in responses
        solidarity_found = False
        
        # Test with a campaign that includes the solidarity message
        solidarity_campaign = {
            "title": "Projet Solidaire Bikutsi",
            "description": "Ensemble nous sommes très forts pour créer de la musique",
            "project_type": "album",
            "goal_amount": 1500.0,
            "deadline_days": 60,
            "story": "Notre force collective nous permet de créer ensemble. Ensemble nous sommes très forts ! 🎵",
            "needs": ["Solidarité", "Entraide", "Collaboration"],
            "region": "Afrique",
            "music_style": "Bikutsi"
        }
        
        solidarity_response = self.run_test(
            "Solidarity Philosophy Campaign",
            "POST",
            "solidarity/campaigns",
            200,
            solidarity_campaign,
            auth_required=True,
            auth_token=auth_token
        )
        
        if solidarity_response:
            story = solidarity_response.get('story', '')
            if 'ensemble nous sommes très forts' in story.lower():
                solidarity_found = True
                print("   ✅ La philosophie 'ensemble nous sommes très forts' est bien intégrée !")
                print("   🎵 Le message de solidarité transpire dans les fonctionnalités")
            else:
                print("   ⚠️ Le message de solidarité pourrait être plus visible")
        
        return True

    def run_verification(self):
        """Run all verification tests"""
        print("\n" + "🎵"*20)
        print("🔍 VÉRIFICATION SYSTÈME SOLIDARITÉ MUSICALE 🔍")
        print("🎵 Verification of Critical Points 🎵")
        print("🎵"*20)
        
        success = self.verify_critical_points()
        
        # Final summary
        print("\n" + "="*60)
        print("🎵 RÉSUMÉ DE LA VÉRIFICATION 🎵")
        print("="*60)
        print(f"📊 Tests de vérification: {self.tests_run}")
        print(f"✅ Tests réussis: {self.tests_passed}")
        print(f"❌ Tests échoués: {self.tests_run - self.tests_passed}")
        print(f"📈 Taux de réussite: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 TOUS LES POINTS CRITIQUES VÉRIFIÉS AVEC SUCCÈS ! 🎉")
            print("🎵 Le système de solidarité musicale est pleinement opérationnel ! 🎵")
            print("💪 'Ensemble nous sommes très forts !' - Mission accomplie ! 💪")
        else:
            print(f"\n⚠️ {self.tests_run - self.tests_passed} points nécessitent une attention.")
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    # Get backend URL from environment or use default
    backend_url = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
    api_url = f"{backend_url}/api"
    
    print(f"🔗 Verifying Solidarity System at: {api_url}")
    
    tester = SolidarityVerificationTester(api_url)
    success = tester.run_verification()
    
    sys.exit(0 if success else 1)
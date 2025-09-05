#!/usr/bin/env python3

import requests
import sys
import json
import time
from datetime import datetime

class USExploAITester:
    def __init__(self, base_url="http://localhost:8001/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.auth_token = None
        self.user_data = None
        self.session_id = None
        self.automation_task_id = None

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
                response = requests.put(url, headers=headers, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == expected_status:
                print(f"✅ Passed - {name}")
                self.tests_passed += 1
                return response.json() if response.content else None
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                if response.content:
                    print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return None

    def test_user_registration(self):
        """Test user registration for AI testing"""
        timestamp = int(time.time())
        user_data = {
            "username": f"ai_testuser_{timestamp}",
            "email": f"ai_test_{timestamp}@usexplo.com",
            "password": "TestPassword123!"
        }
        
        result = self.run_test("User Registration for AI Tests", "POST", "auth/register", 200, user_data)
        if result:
            self.auth_token = result.get('access_token')
            self.user_data = result.get('user')
            print(f"   ✅ User created: {self.user_data['username']}")
            print(f"   ✅ Auth token obtained")
        return result

    def test_ai_chat_simple(self):
        """Test AI chat with simple French question"""
        if not self.auth_token:
            print("❌ No auth token available for AI chat test")
            return None
            
        chat_data = {
            "content": "Bonjour, peux-tu me recommander de la musique africaine?"
        }
        
        result = self.run_test("AI Chat - Simple French Question", "POST", "ai/chat", 200, chat_data, auth_required=True)
        if result:
            self.session_id = result.get('session_id')
            print(f"   ✅ Session ID: {self.session_id}")
            print(f"   ✅ AI Response: {result.get('content', '')[:100]}...")
            
            # Verify response is in French
            response_content = result.get('content', '').lower()
            french_indicators = ['bonjour', 'salut', 'musique', 'africaine', 'recommande', 'je', 'vous', 'tu', 'peux']
            has_french = any(indicator in response_content for indicator in french_indicators)
            if has_french:
                print("   ✅ Response appears to be in French")
            else:
                print("   ⚠️  Response may not be in French")
                
        return result

    def test_ai_chat_marketplace_question(self):
        """Test AI chat about US EXPLO marketplace"""
        if not self.auth_token:
            print("❌ No auth token available for marketplace question test")
            return None
            
        chat_data = {
            "content": "Comment utiliser la marketplace de US EXPLO?",
            "session_id": self.session_id
        }
        
        result = self.run_test("AI Chat - Marketplace Question", "POST", "ai/chat", 200, chat_data, auth_required=True)
        if result:
            print(f"   ✅ AI Response: {result.get('content', '')[:150]}...")
            
            # Check if response mentions US EXPLO context
            response_content = result.get('content', '').lower()
            us_explo_indicators = ['us explo', 'marketplace', 'plateforme', 'vendre', 'acheter', 'musique']
            has_context = any(indicator in response_content for indicator in us_explo_indicators)
            if has_context:
                print("   ✅ Response includes US EXPLO context")
            else:
                print("   ⚠️  Response may lack US EXPLO context")
                
        return result

    def test_ai_chat_premium_question(self):
        """Test AI chat about Premium subscriptions"""
        if not self.auth_token:
            print("❌ No auth token available for premium question test")
            return None
            
        chat_data = {
            "content": "Quels sont les avantages des abonnements Premium?",
            "session_id": self.session_id
        }
        
        result = self.run_test("AI Chat - Premium Subscription Question", "POST", "ai/chat", 200, chat_data, auth_required=True)
        if result:
            print(f"   ✅ AI Response: {result.get('content', '')[:150]}...")
            
            # Check if response mentions subscription benefits
            response_content = result.get('content', '').lower()
            premium_indicators = ['premium', 'abonnement', 'avantages', 'fonctionnalités', 'accès', 'exclusif']
            has_premium_info = any(indicator in response_content for indicator in premium_indicators)
            if has_premium_info:
                print("   ✅ Response includes Premium subscription info")
            else:
                print("   ⚠️  Response may lack Premium subscription details")
                
        return result

    def test_get_chat_sessions(self):
        """Test getting user's chat sessions"""
        if not self.auth_token:
            print("❌ No auth token available for chat sessions test")
            return None
            
        result = self.run_test("Get Chat Sessions", "GET", "ai/sessions", 200, auth_required=True)
        if result:
            print(f"   ✅ Found {len(result)} chat sessions")
            if result and len(result) > 0:
                session = result[0]
                print(f"   ✅ Latest session: {session.get('title', 'No title')}")
                print(f"   ✅ Session ID: {session.get('id', 'No ID')}")
                
        return result

    def test_get_chat_messages(self):
        """Test getting messages from a chat session"""
        if not self.auth_token or not self.session_id:
            print("❌ No auth token or session ID available for chat messages test")
            return None
            
        result = self.run_test("Get Chat Messages", "GET", f"ai/sessions/{self.session_id}/messages", 200, auth_required=True)
        if result:
            print(f"   ✅ Found {len(result)} messages in session")
            if result and len(result) > 0:
                # Check for user and assistant messages
                user_messages = [msg for msg in result if msg.get('message_type') == 'user']
                ai_messages = [msg for msg in result if msg.get('message_type') == 'assistant']
                print(f"   ✅ User messages: {len(user_messages)}")
                print(f"   ✅ AI messages: {len(ai_messages)}")
                
        return result

    def test_generate_ai_recommendations(self):
        """Test generating AI recommendations"""
        if not self.auth_token:
            print("❌ No auth token available for AI recommendations test")
            return None
            
        result = self.run_test("Generate AI Recommendations", "POST", "ai/recommendations/generate", 200, auth_required=True)
        if result:
            print(f"   ✅ Recommendations generated successfully")
            ai_analysis = result.get('ai_analysis', '')
            recommendations = result.get('recommendations', [])
            
            print(f"   ✅ AI Analysis: {ai_analysis[:100]}...")
            print(f"   ✅ Number of recommendations: {len(recommendations)}")
            
            if recommendations:
                for i, rec in enumerate(recommendations[:2]):  # Show first 2
                    content = rec.get('content', {})
                    print(f"   ✅ Rec {i+1}: {content.get('title', 'No title')} - {content.get('style', 'No style')}")
                    
        return result

    def test_get_ai_recommendations(self):
        """Test getting user's AI recommendations"""
        if not self.auth_token:
            print("❌ No auth token available for get recommendations test")
            return None
            
        result = self.run_test("Get AI Recommendations", "GET", "ai/recommendations", 200, auth_required=True)
        if result:
            print(f"   ✅ Found {len(result)} recommendations")
            if result and len(result) > 0:
                rec = result[0]
                content = rec.get('content', {})
                print(f"   ✅ Latest recommendation: {content.get('title', 'No title')}")
                print(f"   ✅ Reason: {rec.get('reason', 'No reason')}")
                print(f"   ✅ Confidence: {rec.get('confidence_score', 0)}")
                
        return result

    def test_create_automation_task(self):
        """Test creating an automation task"""
        if not self.auth_token:
            print("❌ No auth token available for automation task test")
            return None
            
        task_data = {
            "task_type": "recommendation",
            "task_name": "Recommandations musicales hebdomadaires",
            "description": "Générer des recommandations de musique africaine chaque semaine",
            "schedule": "weekly",
            "config": {
                "preferred_genres": ["Afrobeat", "Bikutsi", "Makossa"],
                "max_recommendations": 5
            }
        }
        
        result = self.run_test("Create Automation Task", "POST", "ai/automation/tasks", 200, task_data, auth_required=True)
        if result:
            self.automation_task_id = result.get('id')
            print(f"   ✅ Task created: {result.get('task_name')}")
            print(f"   ✅ Task ID: {self.automation_task_id}")
            print(f"   ✅ Schedule: {result.get('schedule')}")
            print(f"   ✅ Active: {result.get('is_active')}")
            
        return result

    def test_get_automation_tasks(self):
        """Test getting user's automation tasks"""
        if not self.auth_token:
            print("❌ No auth token available for get automation tasks test")
            return None
            
        result = self.run_test("Get Automation Tasks", "GET", "ai/automation/tasks", 200, auth_required=True)
        if result:
            print(f"   ✅ Found {len(result)} automation tasks")
            if result and len(result) > 0:
                task = result[0]
                print(f"   ✅ Latest task: {task.get('task_name')}")
                print(f"   ✅ Type: {task.get('task_type')}")
                print(f"   ✅ Schedule: {task.get('schedule')}")
                print(f"   ✅ Active: {task.get('is_active')}")
                
        return result

    def run_all_ai_tests(self):
        """Run all AI system tests"""
        print("🎵 Starting US EXPLO AI System Tests...")
        print("=" * 60)
        
        # Authentication
        print("\n🔐 AUTHENTICATION TESTS")
        self.test_user_registration()
        
        # AI Chat Tests
        print("\n🤖 AI CHAT TESTS")
        self.test_ai_chat_simple()
        self.test_ai_chat_marketplace_question()
        self.test_ai_chat_premium_question()
        
        # Chat Sessions Tests
        print("\n💬 CHAT SESSIONS TESTS")
        self.test_get_chat_sessions()
        self.test_get_chat_messages()
        
        # AI Recommendations Tests
        print("\n🎯 AI RECOMMENDATIONS TESTS")
        self.test_generate_ai_recommendations()
        self.test_get_ai_recommendations()
        
        # Automation Tests
        print("\n⚙️ AUTOMATION TESTS")
        self.test_create_automation_task()
        self.test_get_automation_tasks()
        
        # Final Results
        print("\n" + "=" * 60)
        print(f"🎵 AI SYSTEM TEST RESULTS")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL AI TESTS PASSED! The AI system is fully operational!")
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed. Check the issues above.")
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    # Use the backend URL from environment or default
    backend_url = "http://localhost:8001/api"
    
    tester = USExploAITester(backend_url)
    success = tester.run_all_ai_tests()
    
    sys.exit(0 if success else 1)
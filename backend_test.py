#!/usr/bin/env python3
"""
Tests complets pour l'API ChatMe
Teste tous les endpoints backend avec des scénarios réels
"""

import requests
import sys
import json
from datetime import datetime
import time

class ChatMeAPITester:
    def __init__(self, base_url="https://local-environment.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_messages = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")
        return success

    def test_welcome_endpoint(self):
        """Test GET /api/ - Message de bienvenue"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            if success:
                data = response.json()
                success = "message" in data and "ChatMe" in data["message"]
                return self.log_test("Welcome Endpoint", success, f"- Response: {data}")
            else:
                return self.log_test("Welcome Endpoint", False, f"- Status: {response.status_code}")
        except Exception as e:
            return self.log_test("Welcome Endpoint", False, f"- Error: {str(e)}")

    def test_send_message(self, sender, receiver, content):
        """Test POST /api/messages - Envoyer un message"""
        try:
            payload = {
                "sender_name": sender,
                "receiver_name": receiver,
                "content": content
            }
            response = requests.post(f"{self.api_url}/messages", json=payload, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ["id", "sender_name", "receiver_name", "content", "timestamp", "is_read"]
                success = all(field in data for field in required_fields)
                if success:
                    self.created_messages.append(data["id"])
                    return self.log_test(f"Send Message ({sender} -> {receiver})", True, f"- ID: {data['id']}")
                else:
                    return self.log_test(f"Send Message ({sender} -> {receiver})", False, "- Missing required fields")
            else:
                return self.log_test(f"Send Message ({sender} -> {receiver})", False, f"- Status: {response.status_code}")
        except Exception as e:
            return self.log_test(f"Send Message ({sender} -> {receiver})", False, f"- Error: {str(e)}")

    def test_get_conversation(self, user1, user2):
        """Test GET /api/messages/conversation/{user1}/{user2}"""
        try:
            response = requests.get(f"{self.api_url}/messages/conversation/{user1}/{user2}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = isinstance(data, list)
                if success and len(data) > 0:
                    # Vérifier la structure du premier message
                    msg = data[0]
                    required_fields = ["id", "sender_name", "receiver_name", "content", "timestamp", "is_read"]
                    success = all(field in msg for field in required_fields)
                    return self.log_test(f"Get Conversation ({user1} <-> {user2})", success, f"- Messages: {len(data)}")
                else:
                    return self.log_test(f"Get Conversation ({user1} <-> {user2})", success, "- Empty conversation")
            else:
                return self.log_test(f"Get Conversation ({user1} <-> {user2})", False, f"- Status: {response.status_code}")
        except Exception as e:
            return self.log_test(f"Get Conversation ({user1} <-> {user2})", False, f"- Error: {str(e)}")

    def test_get_users(self):
        """Test GET /api/users - Liste des utilisateurs actifs"""
        try:
            response = requests.get(f"{self.api_url}/users", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = isinstance(data, list)
                return self.log_test("Get Active Users", success, f"- Users count: {len(data)}, Users: {data}")
            else:
                return self.log_test("Get Active Users", False, f"- Status: {response.status_code}")
        except Exception as e:
            return self.log_test("Get Active Users", False, f"- Error: {str(e)}")

    def test_mark_message_read(self, message_id):
        """Test PUT /api/messages/{message_id}/read"""
        try:
            response = requests.put(f"{self.api_url}/messages/{message_id}/read", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = "message" in data
                return self.log_test(f"Mark Message Read ({message_id[:8]}...)", success, f"- Response: {data}")
            else:
                return self.log_test(f"Mark Message Read ({message_id[:8]}...)", False, f"- Status: {response.status_code}")
        except Exception as e:
            return self.log_test(f"Mark Message Read ({message_id[:8]}...)", False, f"- Error: {str(e)}")

    def test_get_unread_messages(self, username):
        """Test GET /api/messages/unread/{username}"""
        try:
            response = requests.get(f"{self.api_url}/messages/unread/{username}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = isinstance(data, list)
                return self.log_test(f"Get Unread Messages ({username})", success, f"- Unread count: {len(data)}")
            else:
                return self.log_test(f"Get Unread Messages ({username})", False, f"- Status: {response.status_code}")
        except Exception as e:
            return self.log_test(f"Get Unread Messages ({username})", False, f"- Error: {str(e)}")

    def run_comprehensive_tests(self):
        """Exécuter tous les tests dans un scénario réaliste"""
        print("🚀 Démarrage des tests ChatMe API")
        print(f"📡 URL de base: {self.base_url}")
        print("=" * 60)

        # Test 1: Message de bienvenue
        self.test_welcome_endpoint()

        # Test 2: Créer plusieurs utilisateurs et messages
        test_users = ["Alice", "Bob", "Charlie"]
        
        # Alice envoie des messages à Bob
        self.test_send_message("Alice", "Bob", "Salut Bob! Comment ça va?")
        self.test_send_message("Bob", "Alice", "Salut Alice! Ça va bien, merci!")
        self.test_send_message("Alice", "Bob", "Super! Tu veux qu'on se retrouve plus tard?")
        
        # Charlie rejoint la conversation
        self.test_send_message("Charlie", "Alice", "Salut Alice! 👋")
        self.test_send_message("Alice", "Charlie", "Hey Charlie! Comment tu vas?")
        
        # Bob et Charlie discutent
        self.test_send_message("Bob", "Charlie", "Salut Charlie!")
        self.test_send_message("Charlie", "Bob", "Salut Bob! Ça roule?")

        # Test 3: Récupérer les utilisateurs actifs
        self.test_get_users()

        # Test 4: Récupérer les conversations
        self.test_get_conversation("Alice", "Bob")
        self.test_get_conversation("Alice", "Charlie")
        self.test_get_conversation("Bob", "Charlie")

        # Test 5: Messages non lus
        self.test_get_unread_messages("Alice")
        self.test_get_unread_messages("Bob")
        self.test_get_unread_messages("Charlie")

        # Test 6: Marquer des messages comme lus
        if self.created_messages:
            # Marquer le premier message comme lu
            self.test_mark_message_read(self.created_messages[0])
            
            # Vérifier que les messages non lus ont diminué
            self.test_get_unread_messages("Bob")

        # Test 7: Tests d'erreur
        print("\n🔍 Tests de gestion d'erreur:")
        
        # Message avec ID inexistant
        fake_id = "00000000-0000-0000-0000-000000000000"
        try:
            response = requests.put(f"{self.api_url}/messages/{fake_id}/read", timeout=10)
            success = response.status_code == 404
            self.log_test("Mark Non-existent Message", success, f"- Status: {response.status_code}")
        except Exception as e:
            self.log_test("Mark Non-existent Message", False, f"- Error: {str(e)}")

        # Conversation avec utilisateurs inexistants
        self.test_get_conversation("NonExistentUser1", "NonExistentUser2")

    def print_summary(self):
        """Afficher le résumé des tests"""
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES TESTS")
        print("=" * 60)
        print(f"Tests exécutés: {self.tests_run}")
        print(f"Tests réussis: {self.tests_passed}")
        print(f"Tests échoués: {self.tests_run - self.tests_passed}")
        print(f"Taux de réussite: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 Tous les tests sont passés!")
            return 0
        else:
            print("⚠️  Certains tests ont échoué")
            return 1

def main():
    tester = ChatMeAPITester()
    tester.run_comprehensive_tests()
    return tester.print_summary()

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""
Tests complets pour l'API TuneMe (TM)
Teste tous les endpoints backend de la plateforme vidéo publicitaire avancée
"""

import requests
import sys
import json
from datetime import datetime
import time
import io

class TuneMeAPITester:
    def __init__(self, base_url="https://local-environment.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.user_tokens = {}
        self.created_videos = []
        self.created_comments = []

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
        """Test GET /api/ - Message de bienvenue TuneMe"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            if success:
                data = response.json()
                success = "message" in data and "TuneMe" in data["message"]
                return self.log_test("Welcome Endpoint", success, f"- Response: {data}")
            else:
                return self.log_test("Welcome Endpoint", False, f"- Status: {response.status_code}")
        except Exception as e:
            return self.log_test("Welcome Endpoint", False, f"- Error: {str(e)}")

    def test_user_registration(self, username, email, password, display_name, bio=""):
        """Test POST /api/auth/register - Inscription utilisateur"""
        try:
            payload = {
                "username": username,
                "email": email,
                "password": password,
                "display_name": display_name,
                "bio": bio
            }
            response = requests.post(f"{self.api_url}/auth/register", json=payload, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ["message", "token", "user"]
                success = all(field in data for field in required_fields)
                if success:
                    self.user_tokens[username] = data["token"]
                    return self.log_test(f"Register User ({username})", True, f"- User ID: {data['user']['id']}")
                else:
                    return self.log_test(f"Register User ({username})", False, "- Missing required fields")
            else:
                error_msg = ""
                try:
                    error_data = response.json()
                    error_msg = f"- Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    error_msg = f"- Status: {response.status_code}"
                return self.log_test(f"Register User ({username})", False, error_msg)
        except Exception as e:
            return self.log_test(f"Register User ({username})", False, f"- Error: {str(e)}")

    def test_user_login(self, email, password, username_for_token):
        """Test POST /api/auth/login - Connexion utilisateur"""
        try:
            payload = {
                "email": email,
                "password": password
            }
            response = requests.post(f"{self.api_url}/auth/login", json=payload, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ["message", "token", "user"]
                success = all(field in data for field in required_fields)
                if success:
                    self.user_tokens[username_for_token] = data["token"]
                    return self.log_test(f"Login User ({email})", True, f"- Token received")
                else:
                    return self.log_test(f"Login User ({email})", False, "- Missing required fields")
            else:
                return self.log_test(f"Login User ({email})", False, f"- Status: {response.status_code}")
        except Exception as e:
            return self.log_test(f"Login User ({email})", False, f"- Error: {str(e)}")

    def test_get_user_profile(self, username):
        """Test GET /api/users/me - Profil utilisateur actuel"""
        try:
            if username not in self.user_tokens:
                return self.log_test(f"Get Profile ({username})", False, "- No token available")
            
            headers = {"Authorization": f"Bearer {self.user_tokens[username]}"}
            response = requests.get(f"{self.api_url}/users/me", headers=headers, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ["id", "username", "display_name", "email"]
                success = all(field in data for field in required_fields)
                return self.log_test(f"Get Profile ({username})", success, f"- Display name: {data.get('display_name', 'N/A')}")
            else:
                return self.log_test(f"Get Profile ({username})", False, f"- Status: {response.status_code}")
        except Exception as e:
            return self.log_test(f"Get Profile ({username})", False, f"- Error: {str(e)}")

    def test_upload_avatar(self, username, file_size_mb=1, file_type="image/jpeg"):
        """Test POST /api/users/me/avatar - Upload avatar/profile picture"""
        try:
            if username not in self.user_tokens:
                return self.log_test(f"Upload Avatar ({username})", False, "- No token available")
            
            headers = {"Authorization": f"Bearer {self.user_tokens[username]}"}
            
            # Create fake image content
            fake_image_size = int(file_size_mb * 1024 * 1024)  # Convert MB to bytes
            fake_image_content = b"fake image content" * (fake_image_size // 18 + 1)
            fake_image_content = fake_image_content[:fake_image_size]
            
            files = {"file": ("test_avatar.jpg", io.BytesIO(fake_image_content), file_type)}
            
            response = requests.post(f"{self.api_url}/users/me/avatar", files=files, headers=headers, timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ["message", "avatar_url", "file_size", "file_type"]
                success = all(field in data for field in required_fields)
                if success:
                    avatar_url = data.get("avatar_url", "")
                    return self.log_test(f"Upload Avatar ({username})", True, f"- Avatar URL: {avatar_url[:50]}...")
                else:
                    return self.log_test(f"Upload Avatar ({username})", False, "- Missing required fields")
            else:
                error_msg = ""
                try:
                    error_data = response.json()
                    error_msg = f"- Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    error_msg = f"- Status: {response.status_code}"
                return self.log_test(f"Upload Avatar ({username})", False, error_msg)
        except Exception as e:
            return self.log_test(f"Upload Avatar ({username})", False, f"- Error: {str(e)}")

    def test_upload_avatar_invalid_file(self, username, file_type="text/plain"):
        """Test POST /api/users/me/avatar with invalid file type"""
        try:
            if username not in self.user_tokens:
                return self.log_test(f"Upload Invalid Avatar ({username})", False, "- No token available")
            
            headers = {"Authorization": f"Bearer {self.user_tokens[username]}"}
            
            # Create fake non-image content
            fake_content = b"This is not an image file"
            files = {"file": ("test_file.txt", io.BytesIO(fake_content), file_type)}
            
            response = requests.post(f"{self.api_url}/users/me/avatar", files=files, headers=headers, timeout=15)
            success = response.status_code == 400  # Should fail with 400 Bad Request
            
            if success:
                return self.log_test(f"Upload Invalid Avatar ({username})", True, "- Correctly rejected non-image file")
            else:
                return self.log_test(f"Upload Invalid Avatar ({username})", False, f"- Status: {response.status_code} (expected 400)")
        except Exception as e:
            return self.log_test(f"Upload Invalid Avatar ({username})", False, f"- Error: {str(e)}")

    def test_upload_avatar_too_large(self, username, file_size_mb=6):
        """Test POST /api/users/me/avatar with file too large (>5MB)"""
        try:
            if username not in self.user_tokens:
                return self.log_test(f"Upload Large Avatar ({username})", False, "- No token available")
            
            headers = {"Authorization": f"Bearer {self.user_tokens[username]}"}
            
            # Create fake large image content (6MB)
            fake_image_size = int(file_size_mb * 1024 * 1024)
            fake_image_content = b"fake large image content" * (fake_image_size // 24 + 1)
            fake_image_content = fake_image_content[:fake_image_size]
            
            files = {"file": ("large_avatar.jpg", io.BytesIO(fake_image_content), "image/jpeg")}
            
            response = requests.post(f"{self.api_url}/users/me/avatar", files=files, headers=headers, timeout=15)
            success = response.status_code == 400  # Should fail with 400 Bad Request
            
            if success:
                return self.log_test(f"Upload Large Avatar ({username})", True, "- Correctly rejected large file")
            else:
                return self.log_test(f"Upload Large Avatar ({username})", False, f"- Status: {response.status_code} (expected 400)")
        except Exception as e:
            return self.log_test(f"Upload Large Avatar ({username})", False, f"- Error: {str(e)}")

    def test_remove_avatar(self, username):
        """Test DELETE /api/users/me/avatar - Remove user avatar"""
        try:
            if username not in self.user_tokens:
                return self.log_test(f"Remove Avatar ({username})", False, "- No token available")
            
            headers = {"Authorization": f"Bearer {self.user_tokens[username]}"}
            response = requests.delete(f"{self.api_url}/users/me/avatar", headers=headers, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ["message", "avatar_url"]
                success = all(field in data for field in required_fields)
                if success:
                    avatar_url = data.get("avatar_url", "")
                    return self.log_test(f"Remove Avatar ({username})", True, f"- Default avatar: {avatar_url[:50]}...")
                else:
                    return self.log_test(f"Remove Avatar ({username})", False, "- Missing required fields")
            else:
                return self.log_test(f"Remove Avatar ({username})", False, f"- Status: {response.status_code}")
        except Exception as e:
            return self.log_test(f"Remove Avatar ({username})", False, f"- Error: {str(e)}")

    def test_update_user_profile(self, username, display_name=None, bio=None):
        """Test PUT /api/users/me/profile - Update user profile"""
        try:
            if username not in self.user_tokens:
                return self.log_test(f"Update Profile ({username})", False, "- No token available")
            
            headers = {"Authorization": f"Bearer {self.user_tokens[username]}"}
            
            # Prepare form data
            data = {}
            if display_name:
                data["display_name"] = display_name
            if bio is not None:
                data["bio"] = bio
            
            response = requests.put(f"{self.api_url}/users/me/profile", data=data, headers=headers, timeout=10)
            success = response.status_code == 200
            
            if success:
                profile_data = response.json()
                required_fields = ["id", "username", "display_name", "bio"]
                success = all(field in profile_data for field in required_fields)
                if success:
                    updated_name = profile_data.get("display_name", "")
                    return self.log_test(f"Update Profile ({username})", True, f"- New name: {updated_name}")
                else:
                    return self.log_test(f"Update Profile ({username})", False, "- Missing required fields")
            else:
                return self.log_test(f"Update Profile ({username})", False, f"- Status: {response.status_code}")
        except Exception as e:
            return self.log_test(f"Update Profile ({username})", False, f"- Error: {str(e)}")

    def test_get_user_subscriptions(self, username):
        """Test GET /api/users/me/subscriptions - Get user subscriptions"""
        try:
            if username not in self.user_tokens:
                return self.log_test(f"Get Subscriptions ({username})", False, "- No token available")
            
            headers = {"Authorization": f"Bearer {self.user_tokens[username]}"}
            response = requests.get(f"{self.api_url}/users/me/subscriptions", headers=headers, timeout=10)
            success = response.status_code == 200
            
            if success:
                subscriptions = response.json()
                success = isinstance(subscriptions, list)
                return self.log_test(f"Get Subscriptions ({username})", success, f"- Count: {len(subscriptions)}")
            else:
                return self.log_test(f"Get Subscriptions ({username})", False, f"- Status: {response.status_code}")
        except Exception as e:
            return self.log_test(f"Get Subscriptions ({username})", False, f"- Error: {str(e)}")

    def test_video_upload(self, username, title, description, category, tags="", is_ad=False, ad_type=None):
        """Test POST /api/videos/upload - Upload vidéo avec analyse IA"""
        try:
            if username not in self.user_tokens:
                return self.log_test(f"Upload Video ({username})", False, "- No token available")
            
            headers = {"Authorization": f"Bearer {self.user_tokens[username]}"}
            
            # Créer un fichier factice pour le test
            fake_video_content = b"fake video content for testing"
            files = {"file": ("test_video.mp4", io.BytesIO(fake_video_content), "video/mp4")}
            
            data = {
                "title": title,
                "description": description,
                "category": category,
                "tags": tags,
                "is_ad": str(is_ad).lower(),
                "ad_type": ad_type or "",
                "target_audience": "test audience"
            }
            
            response = requests.post(f"{self.api_url}/videos/upload", files=files, data=data, headers=headers, timeout=30)
            success = response.status_code == 200
            
            if success:
                video_data = response.json()
                required_fields = ["id", "title", "creator_username", "ai_analysis"]
                success = all(field in video_data for field in required_fields)
                if success:
                    self.created_videos.append(video_data["id"])
                    ai_score = video_data.get("ai_analysis", {}).get("engagement_prediction", "N/A")
                    return self.log_test(f"Upload Video ({title})", True, f"- ID: {video_data['id'][:8]}..., AI Score: {ai_score}")
                else:
                    return self.log_test(f"Upload Video ({title})", False, "- Missing required fields")
            else:
                return self.log_test(f"Upload Video ({title})", False, f"- Status: {response.status_code}")
        except Exception as e:
            return self.log_test(f"Upload Video ({title})", False, f"- Error: {str(e)}")

    def test_get_videos(self, filter_category=None, is_ad=None):
        """Test GET /api/videos - Récupérer les vidéos avec filtres"""
        try:
            params = {}
            if filter_category:
                params["category"] = filter_category
            if is_ad is not None:
                params["is_ad"] = str(is_ad).lower()
            
            response = requests.get(f"{self.api_url}/videos", params=params, timeout=10)
            success = response.status_code == 200
            
            if success:
                videos = response.json()
                success = isinstance(videos, list)
                filter_desc = f"category={filter_category}, is_ad={is_ad}" if filter_category or is_ad is not None else "no filters"
                return self.log_test(f"Get Videos ({filter_desc})", success, f"- Count: {len(videos)}")
            else:
                return self.log_test("Get Videos", False, f"- Status: {response.status_code}")
        except Exception as e:
            return self.log_test("Get Videos", False, f"- Error: {str(e)}")

    def test_get_video_by_id(self, video_id):
        """Test GET /api/videos/{video_id} - Récupérer une vidéo spécifique"""
        try:
            response = requests.get(f"{self.api_url}/videos/{video_id}", timeout=10)
            success = response.status_code == 200
            
            if success:
                video = response.json()
                required_fields = ["id", "title", "views_count", "ai_analysis"]
                success = all(field in video for field in required_fields)
                return self.log_test(f"Get Video by ID", success, f"- Title: {video.get('title', 'N/A')[:30]}...")
            else:
                return self.log_test("Get Video by ID", False, f"- Status: {response.status_code}")
        except Exception as e:
            return self.log_test("Get Video by ID", False, f"- Error: {str(e)}")

    def test_like_video(self, username, video_id):
        """Test POST /api/videos/{video_id}/like - Liker une vidéo"""
        try:
            if username not in self.user_tokens:
                return self.log_test(f"Like Video ({username})", False, "- No token available")
            
            headers = {"Authorization": f"Bearer {self.user_tokens[username]}"}
            response = requests.post(f"{self.api_url}/videos/{video_id}/like", headers=headers, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = "message" in data
                return self.log_test(f"Like Video ({username})", success, f"- Response: {data.get('message', 'N/A')}")
            else:
                return self.log_test(f"Like Video ({username})", False, f"- Status: {response.status_code}")
        except Exception as e:
            return self.log_test(f"Like Video ({username})", False, f"- Error: {str(e)}")

    def test_create_comment(self, username, video_id, content):
        """Test POST /api/comments - Créer un commentaire avec analyse sentiment IA"""
        try:
            if username not in self.user_tokens:
                return self.log_test(f"Create Comment ({username})", False, "- No token available")
            
            headers = {"Authorization": f"Bearer {self.user_tokens[username]}"}
            payload = {
                "video_id": video_id,
                "content": content
            }
            
            response = requests.post(f"{self.api_url}/comments", json=payload, headers=headers, timeout=15)
            success = response.status_code == 200
            
            if success:
                comment = response.json()
                required_fields = ["id", "content", "ai_sentiment"]
                success = all(field in comment for field in required_fields)
                if success:
                    self.created_comments.append(comment["id"])
                    sentiment = comment.get("ai_sentiment", "N/A")
                    return self.log_test(f"Create Comment ({username})", True, f"- Sentiment: {sentiment}")
                else:
                    return self.log_test(f"Create Comment ({username})", False, "- Missing required fields")
            else:
                return self.log_test(f"Create Comment ({username})", False, f"- Status: {response.status_code}")
        except Exception as e:
            return self.log_test(f"Create Comment ({username})", False, f"- Error: {str(e)}")

    def test_get_video_comments(self, video_id):
        """Test GET /api/videos/{video_id}/comments - Récupérer les commentaires"""
        try:
            response = requests.get(f"{self.api_url}/videos/{video_id}/comments", timeout=10)
            success = response.status_code == 200
            
            if success:
                comments = response.json()
                success = isinstance(comments, list)
                return self.log_test("Get Video Comments", success, f"- Count: {len(comments)}")
            else:
                return self.log_test("Get Video Comments", False, f"- Status: {response.status_code}")
        except Exception as e:
            return self.log_test("Get Video Comments", False, f"- Error: {str(e)}")

    def test_get_recommendations(self, username):
        """Test GET /api/recommendations - Recommandations IA personnalisées"""
        try:
            if username not in self.user_tokens:
                return self.log_test(f"Get Recommendations ({username})", False, "- No token available")
            
            headers = {"Authorization": f"Bearer {self.user_tokens[username]}"}
            response = requests.get(f"{self.api_url}/recommendations", headers=headers, timeout=15)
            success = response.status_code == 200
            
            if success:
                recommendations = response.json()
                success = isinstance(recommendations, list)
                return self.log_test(f"Get Recommendations ({username})", success, f"- Count: {len(recommendations)}")
            else:
                return self.log_test(f"Get Recommendations ({username})", False, f"- Status: {response.status_code}")
        except Exception as e:
            return self.log_test(f"Get Recommendations ({username})", False, f"- Error: {str(e)}")

    def test_get_channel_analytics(self, username, user_id):
        """Test GET /api/analytics/channel/{user_id} - Analytics créateur"""
        try:
            if username not in self.user_tokens:
                return self.log_test(f"Get Analytics ({username})", False, "- No token available")
            
            headers = {"Authorization": f"Bearer {self.user_tokens[username]}"}
            response = requests.get(f"{self.api_url}/analytics/channel/{user_id}", headers=headers, timeout=10)
            success = response.status_code == 200
            
            if success:
                analytics = response.json()
                required_fields = ["total_videos", "total_views", "total_revenue", "avg_engagement_rate"]
                success = all(field in analytics for field in required_fields)
                if success:
                    revenue = analytics.get("total_revenue", 0)
                    engagement = analytics.get("avg_engagement_rate", 0)
                    return self.log_test(f"Get Analytics ({username})", True, f"- Revenue: ${revenue}, Engagement: {engagement}%")
                else:
                    return self.log_test(f"Get Analytics ({username})", False, "- Missing required fields")
            else:
                return self.log_test(f"Get Analytics ({username})", False, f"- Status: {response.status_code}")
        except Exception as e:
            return self.log_test(f"Get Analytics ({username})", False, f"- Error: {str(e)}")

    def test_get_marketplace_ad_spaces(self):
        """Test GET /api/marketplace/ad-spaces - Espaces publicitaires disponibles"""
        try:
            response = requests.get(f"{self.api_url}/marketplace/ad-spaces", timeout=10)
            success = response.status_code == 200
            
            if success:
                ad_spaces = response.json()
                success = isinstance(ad_spaces, list)
                if success and len(ad_spaces) > 0:
                    first_space = ad_spaces[0]
                    required_fields = ["id", "creator", "category", "cpm_rate", "estimated_views"]
                    success = all(field in first_space for field in required_fields)
                return self.log_test("Get Marketplace Ad Spaces", success, f"- Available spaces: {len(ad_spaces)}")
            else:
                return self.log_test("Get Marketplace Ad Spaces", False, f"- Status: {response.status_code}")
        except Exception as e:
            return self.log_test("Get Marketplace Ad Spaces", False, f"- Error: {str(e)}")

    def test_subscribe_to_channel(self, subscriber_username, channel_user_id):
        """Test POST /api/users/{user_id}/subscribe - S'abonner à une chaîne"""
        try:
            if subscriber_username not in self.user_tokens:
                return self.log_test(f"Subscribe ({subscriber_username})", False, "- No token available")
            
            headers = {"Authorization": f"Bearer {self.user_tokens[subscriber_username]}"}
            response = requests.post(f"{self.api_url}/users/{channel_user_id}/subscribe", headers=headers, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = "message" in data
                return self.log_test(f"Subscribe ({subscriber_username})", success, f"- Response: {data.get('message', 'N/A')}")
            else:
                return self.log_test(f"Subscribe ({subscriber_username})", False, f"- Status: {response.status_code}")
        except Exception as e:
            return self.log_test(f"Subscribe ({subscriber_username})", False, f"- Error: {str(e)}")

    def run_comprehensive_tests(self):
        """Exécuter tous les tests TuneMe dans un scénario réaliste"""
        print("🎬 Démarrage des tests TuneMe (TM) API")
        print(f"📡 URL de base: {self.base_url}")
        print("=" * 70)

        # Test 1: Message de bienvenue
        self.test_welcome_endpoint()

        # Test 2: Inscription des utilisateurs
        print("\n👥 Tests d'authentification:")
        self.test_user_registration("creator1", "creator1@tuneme.com", "password123", "Créateur Pro", "Expert en publicités vidéo")
        self.test_user_registration("creator2", "creator2@tuneme.com", "password123", "Vidéaste Créatif", "Spécialiste contenu viral")
        self.test_user_registration("viewer1", "viewer1@tuneme.com", "password123", "Spectateur Actif", "Amateur de publicités créatives")

        # Test 3: Connexion des utilisateurs
        self.test_user_login("creator1@tuneme.com", "password123", "creator1")
        self.test_user_login("creator2@tuneme.com", "password123", "creator2")

        # Test 4: Profils utilisateurs
        print("\n👤 Tests de profils:")
        self.test_get_user_profile("creator1")
        self.test_get_user_profile("creator2")

        # Test 5: Upload de vidéos avec analyse IA
        print("\n📹 Tests d'upload vidéo avec IA:")
        self.test_video_upload("creator1", "Publicité iPhone 16 Pro", "Nouvelle campagne publicitaire pour l'iPhone 16 Pro avec des effets visuels époustouflants", "Technology", "iphone,apple,smartphone,tech", True, "tv_commercial")
        self.test_video_upload("creator1", "Tutoriel Marketing Digital", "Guide complet pour créer des campagnes publicitaires efficaces", "Business", "marketing,digital,publicité,stratégie", False)
        self.test_video_upload("creator2", "Coca-Cola Summer Campaign", "Campagne estivale rafraîchissante pour Coca-Cola", "Entertainment", "coca-cola,été,rafraîchissant", True, "social_media")
        
        # Attendre l'analyse IA
        print("⏳ Attente de l'analyse IA...")
        time.sleep(3)

        # Test 6: Récupération des vidéos
        print("\n🎥 Tests de récupération vidéos:")
        self.test_get_videos()
        self.test_get_videos(filter_category="Technology")
        self.test_get_videos(is_ad=True)
        self.test_get_videos(is_ad=False)

        # Test 7: Détails vidéo et interactions
        if self.created_videos:
            print("\n👍 Tests d'interactions vidéo:")
            first_video = self.created_videos[0]
            self.test_get_video_by_id(first_video)
            self.test_like_video("creator2", first_video)
            self.test_like_video("viewer1", first_video)  # Devrait échouer car pas connecté

        # Test 8: Système de commentaires avec IA
        if self.created_videos:
            print("\n💬 Tests de commentaires avec analyse sentiment:")
            video_id = self.created_videos[0]
            self.test_create_comment("creator2", video_id, "Excellente publicité! Très créative et engageante!")
            self.test_create_comment("creator1", video_id, "Merci pour ce retour positif!")
            self.test_create_comment("creator2", video_id, "Cette pub est vraiment nulle, ça ne me plaît pas du tout.")
            
            # Attendre l'analyse de sentiment
            time.sleep(2)
            self.test_get_video_comments(video_id)

        # Test 9: Recommandations IA
        print("\n🤖 Tests de recommandations IA:")
        self.test_get_recommendations("creator1")
        self.test_get_recommendations("creator2")

        # Test 10: Analytics créateur
        print("\n📊 Tests d'analytics:")
        # Note: Nous aurions besoin des IDs utilisateur pour ce test
        # Pour l'instant, on teste avec des IDs factices
        
        # Test 11: Marketplace publicitaire
        print("\n💰 Tests marketplace publicitaire:")
        self.test_get_marketplace_ad_spaces()

        # Test 12: Système d'abonnements
        print("\n🔔 Tests d'abonnements:")
        # Note: Nécessiterait les vrais IDs utilisateur

        # Test 13: Tests d'erreur
        print("\n🔍 Tests de gestion d'erreur:")
        
        # Vidéo inexistante
        fake_video_id = "00000000-0000-0000-0000-000000000000"
        self.test_get_video_by_id(fake_video_id)
        
        # Like sans authentification
        try:
            response = requests.post(f"{self.api_url}/videos/{fake_video_id}/like", timeout=10)
            success = response.status_code == 401 or response.status_code == 403
            self.log_test("Like Without Auth", success, f"- Status: {response.status_code}")
        except Exception as e:
            self.log_test("Like Without Auth", False, f"- Error: {str(e)}")

        # Inscription avec email existant
        self.test_user_registration("creator1", "creator1@tuneme.com", "password123", "Duplicate User")

    def print_summary(self):
        """Afficher le résumé des tests"""
        print("\n" + "=" * 70)
        print("📊 RÉSUMÉ DES TESTS TUNEME (TM)")
        print("=" * 70)
        print(f"Tests exécutés: {self.tests_run}")
        print(f"Tests réussis: {self.tests_passed}")
        print(f"Tests échoués: {self.tests_run - self.tests_passed}")
        print(f"Taux de réussite: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        print(f"\n🎬 Vidéos créées: {len(self.created_videos)}")
        print(f"💬 Commentaires créés: {len(self.created_comments)}")
        print(f"👥 Utilisateurs enregistrés: {len(self.user_tokens)}")
        
        if self.tests_passed == self.tests_run:
            print("🎉 Tous les tests sont passés! TuneMe fonctionne parfaitement!")
            return 0
        else:
            print("⚠️  Certains tests ont échoué - Vérifiez les détails ci-dessus")
            return 1

def main():
    tester = TuneMeAPITester()
    tester.run_comprehensive_tests()
    return tester.print_summary()

if __name__ == "__main__":
    sys.exit(main())
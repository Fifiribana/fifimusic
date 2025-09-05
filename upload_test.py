#!/usr/bin/env python3

import requests
import sys
import json
import time
import io
import os
from datetime import datetime

class USExploUploadTester:
    def __init__(self, base_url="https://ae586f29-8094-4784-91e4-f1b7e4d11a65.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.auth_token = None
        self.user_data = None
        self.uploaded_track_id = None

    def run_test(self, name, test_func):
        """Run a single test"""
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            success, message = test_func()
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - {message}")
                return True
            else:
                print(f"❌ Failed - {message}")
                return False
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False

    def create_test_audio_file(self):
        """Create a small test audio file"""
        # Create a minimal WAV file (44 bytes header + some data)
        wav_header = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
        audio_data = b'\x00' * 1000  # 1000 bytes of silence
        return wav_header + audio_data

    def create_test_image_file(self):
        """Create a small test image file (1x1 pixel PNG)"""
        # Minimal PNG file (1x1 pixel, black)
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
        return png_data

    def test_user_registration(self):
        """Test user registration for upload testing"""
        timestamp = int(time.time())
        user_data = {
            "email": f"upload_test_{timestamp}@example.com",
            "username": f"uploaduser_{timestamp}",
            "password": "UploadTest123!"
        }
        
        try:
            response = requests.post(f"{self.base_url}/auth/register", json=user_data)
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data['access_token']
                self.user_data = data['user']
                return True, f"User registered: {self.user_data['username']}"
            else:
                return False, f"Registration failed with status {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"Registration error: {str(e)}"

    def test_audio_upload(self):
        """Test individual audio file upload"""
        if not self.auth_token:
            return False, "No auth token available"

        try:
            audio_data = self.create_test_audio_file()
            files = {
                'file': ('test_audio.wav', io.BytesIO(audio_data), 'audio/wav')
            }
            headers = {'Authorization': f'Bearer {self.auth_token}'}
            
            response = requests.post(f"{self.base_url}/upload/audio", files=files, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return True, f"Audio uploaded: {data['filename']} ({data['size']} bytes)"
            else:
                return False, f"Audio upload failed with status {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"Audio upload error: {str(e)}"

    def test_image_upload(self):
        """Test individual image file upload"""
        if not self.auth_token:
            return False, "No auth token available"

        try:
            image_data = self.create_test_image_file()
            files = {
                'file': ('test_image.png', io.BytesIO(image_data), 'image/png')
            }
            headers = {'Authorization': f'Bearer {self.auth_token}'}
            
            response = requests.post(f"{self.base_url}/upload/image", files=files, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return True, f"Image uploaded: {data['filename']} ({data['size']} bytes)"
            else:
                return False, f"Image upload failed with status {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"Image upload error: {str(e)}"

    def test_track_upload_with_files(self):
        """Test complete track upload with audio and image files"""
        if not self.auth_token:
            return False, "No auth token available"

        try:
            # Prepare track data as JSON
            track_data = {
                "title": "Test Upload Track",
                "region": "Afrique", 
                "style": "Bikutsi",
                "instrument": "Guitare",
                "duration": 180,
                "bpm": 120,
                "mood": "Énergique",
                "price": 4.99,
                "description": "Test d'upload de piste musicale"
            }

            # Prepare files
            audio_data = self.create_test_audio_file()
            image_data = self.create_test_image_file()
            
            files = {
                'audio_file': ('test_track.wav', io.BytesIO(audio_data), 'audio/wav'),
                'image_file': ('test_cover.png', io.BytesIO(image_data), 'image/png')
            }
            
            headers = {
                'Authorization': f'Bearer {self.auth_token}',
                'Content-Type': 'application/json'
            }
            
            # Try sending as multipart with JSON body - this is complex in requests
            # Let's use a different approach - send JSON and files separately
            
            # First approach: try with requests-toolbelt for multipart encoder
            try:
                from requests_toolbelt.multipart.encoder import MultipartEncoder
                
                multipart_data = MultipartEncoder(
                    fields={
                        'track_data': json.dumps(track_data),
                        'audio_file': ('test_track.wav', io.BytesIO(audio_data), 'audio/wav'),
                        'image_file': ('test_cover.png', io.BytesIO(image_data), 'image/png')
                    }
                )
                
                headers = {
                    'Authorization': f'Bearer {self.auth_token}',
                    'Content-Type': multipart_data.content_type
                }
                
                response = requests.post(
                    f"{self.base_url}/tracks/upload", 
                    data=multipart_data,
                    headers=headers
                )
                
            except ImportError:
                # Fallback: use standard requests multipart
                response = requests.post(
                    f"{self.base_url}/tracks/upload", 
                    files=files,
                    json=track_data,
                    headers={'Authorization': f'Bearer {self.auth_token}'}
                )
            
            if response.status_code == 200:
                track = response.json()
                self.uploaded_track_id = track['id']
                return True, f"Track uploaded successfully: {track['title']} (ID: {track['id']})"
            else:
                return False, f"Track upload failed with status {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"Track upload error: {str(e)}"

    def test_get_my_tracks(self):
        """Test retrieving uploaded tracks"""
        if not self.auth_token:
            return False, "No auth token available"

        try:
            headers = {'Authorization': f'Bearer {self.auth_token}'}
            response = requests.get(f"{self.base_url}/admin/my-tracks", headers=headers)
            
            if response.status_code == 200:
                tracks = response.json()
                return True, f"Retrieved {len(tracks)} tracks from my collection"
            else:
                return False, f"Failed to get tracks with status {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"Get tracks error: {str(e)}"

    def test_invalid_file_uploads(self):
        """Test upload with invalid file types"""
        if not self.auth_token:
            return False, "No auth token available"

        try:
            # Test invalid audio file (text file)
            text_data = b"This is not an audio file"
            files = {
                'file': ('fake_audio.txt', io.BytesIO(text_data), 'text/plain')
            }
            headers = {'Authorization': f'Bearer {self.auth_token}'}
            
            response = requests.post(f"{self.base_url}/upload/audio", files=files, headers=headers)
            
            if response.status_code == 400:
                return True, "Correctly rejected invalid audio file type"
            else:
                return False, f"Should have rejected invalid file type, got status {response.status_code}"
        except Exception as e:
            return False, f"Invalid file test error: {str(e)}"

    def test_unauthorized_upload(self):
        """Test upload without authentication"""
        try:
            audio_data = self.create_test_audio_file()
            files = {
                'file': ('test_audio.wav', io.BytesIO(audio_data), 'audio/wav')
            }
            # No Authorization header
            
            response = requests.post(f"{self.base_url}/upload/audio", files=files)
            
            if response.status_code == 401 or response.status_code == 403:
                return True, "Correctly rejected unauthorized upload"
            else:
                return False, f"Should have rejected unauthorized upload, got status {response.status_code}"
        except Exception as e:
            return False, f"Unauthorized test error: {str(e)}"

def main():
    print("🎵 US EXPLO Upload System Testing Suite")
    print("=" * 60)
    
    tester = USExploUploadTester()
    
    # Test sequence for upload functionality
    tests = [
        ("User Registration", tester.test_user_registration),
        ("Audio File Upload", tester.test_audio_upload),
        ("Image File Upload", tester.test_image_upload),
        ("Complete Track Upload", tester.test_track_upload_with_files),
        ("Get My Tracks", tester.test_get_my_tracks),
        ("Invalid File Type Rejection", tester.test_invalid_file_uploads),
        ("Unauthorized Upload Rejection", tester.test_unauthorized_upload),
    ]
    
    print(f"\nRunning {len(tests)} upload tests...")
    
    failed_tests = []
    for test_name, test_func in tests:
        if not tester.run_test(test_name, test_func):
            failed_tests.append(test_name)
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 UPLOAD TESTING RESULTS")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if failed_tests:
        print(f"\n❌ Failed tests:")
        for test in failed_tests:
            print(f"   - {test}")
        print(f"\n🔧 UPLOAD SYSTEM ISSUES TO FIX:")
        critical_features = [
            "User Registration", "Audio File Upload", "Image File Upload", 
            "Complete Track Upload", "Get My Tracks"
        ]
        critical_failed = [test for test in failed_tests if test in critical_features]
        if critical_failed:
            for test in critical_failed:
                print(f"   🚨 {test}")
    else:
        print(f"\n🎉 All upload tests passed!")
    
    return 0 if len(failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
"""
Service de traduction pour US EXPLO avec support multilingue complet
Utilise l'API Google Translate pour la traduction automatique
"""

from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
import logging
import os
from functools import lru_cache
import asyncio
import aioredis
import json
import hashlib
from datetime import datetime, timedelta

# Configuration de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modèles Pydantic
class TranslationRequest(BaseModel):
    text: str
    target_language: str
    source_language: Optional[str] = None

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: Optional[float] = None

class BatchTranslationRequest(BaseModel):
    texts: List[str]
    target_language: str
    source_language: Optional[str] = None

class BatchTranslationResponse(BaseModel):
    translations: List[TranslationResponse]
    batch_id: str
    processing_time: float

class LanguageDetectionRequest(BaseModel):
    text: str

class LanguageDetectionResponse(BaseModel):
    detected_language: str
    confidence: float
    text: str

class TranslationService:
    """Service de traduction avec cache et optimisations"""
    
    def __init__(self):
        self.client = None
        self.redis_client = None
        self.cache_ttl = 86400 * 7  # 7 jours
        self.supported_languages = {}
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialise le client Google Translate"""
        try:
            # Essayer d'importer et initialiser Google Translate
            from google.cloud import translate_v2 as translate
            
            # Vérifier les credentials
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if credentials_path and os.path.exists(credentials_path):
                self.client = translate.Client()
                logger.info("Google Translate client initialized successfully")
            else:
                logger.warning("Google Translate credentials not found, using mock service")
                self.client = MockTranslateClient()
                
        except ImportError:
            logger.warning("Google Cloud Translate not available, using mock service")
            self.client = MockTranslateClient()
        except Exception as e:
            logger.error(f"Error initializing translation client: {e}")
            self.client = MockTranslateClient()
    
    async def initialize_redis(self, redis_url: str = None):
        """Initialise Redis pour le cache"""
        if redis_url:
            try:
                import redis
                # Parse Redis URL
                if redis_url.startswith('redis://'):
                    self.redis_client = redis.from_url(redis_url)
                else:
                    self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
                
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"Redis initialization failed: {e}")
                self.redis_client = None
    
    def _generate_cache_key(self, text: str, target_lang: str, source_lang: str = None) -> str:
        """Génère une clé de cache pour la traduction"""
        key_data = f"{text}:{source_lang or 'auto'}:{target_lang}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def _get_cached_translation(self, cache_key: str) -> Optional[Dict]:
        """Récupère une traduction depuis le cache Redis"""
        if not self.redis_client:
            return None
            
        try:
            cached_data = self.redis_client.get(f"translation:{cache_key}")
            if cached_data:
                return json.loads(cached_data.decode('utf-8'))
        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")
        
        return None
    
    async def _cache_translation(self, cache_key: str, translation_data: Dict):
        """Met en cache une traduction dans Redis"""
        if not self.redis_client:
            return
            
        try:
            self.redis_client.setex(
                f"translation:{cache_key}",
                self.cache_ttl,
                json.dumps(translation_data)
            )
        except Exception as e:
            logger.warning(f"Cache storage error: {e}")
    
    async def translate_text(self, request: TranslationRequest) -> TranslationResponse:
        """Traduit un texte avec cache"""
        try:
            # Vérifier le cache d'abord
            cache_key = self._generate_cache_key(
                request.text, 
                request.target_language, 
                request.source_language
            )
            
            cached_result = await self._get_cached_translation(cache_key)
            if cached_result:
                logger.info(f"Cache hit for translation: {cache_key}")
                return TranslationResponse(**cached_result)
            
            # Effectuer la traduction
            result = self.client.translate(
                request.text,
                target_language=request.target_language,
                source_language=request.source_language
            )
            
            # Créer la réponse
            response_data = {
                'original_text': request.text,
                'translated_text': result['translatedText'],
                'source_language': result.get('detectedSourceLanguage', request.source_language or 'auto'),
                'target_language': request.target_language,
                'confidence': result.get('confidence', 0.95)
            }
            
            # Mettre en cache
            await self._cache_translation(cache_key, response_data)
            
            logger.info(f"Translation completed: {request.target_language}")
            return TranslationResponse(**response_data)
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            # En cas d'erreur, retourner le texte original
            return TranslationResponse(
                original_text=request.text,
                translated_text=request.text,
                source_language=request.source_language or 'unknown',
                target_language=request.target_language,
                confidence=0.0
            )
    
    async def translate_batch(self, request: BatchTranslationRequest) -> BatchTranslationResponse:
        """Traduit un lot de textes de manière optimisée"""
        start_time = datetime.now()
        batch_id = hashlib.md5(f"{len(request.texts)}{start_time}".encode()).hexdigest()[:8]
        
        try:
            translations = []
            
            # Traiter par petits lots pour éviter les timeouts
            batch_size = 10
            for i in range(0, len(request.texts), batch_size):
                batch_texts = request.texts[i:i + batch_size]
                
                # Traiter chaque texte du lot
                batch_tasks = []
                for text in batch_texts:
                    task = self.translate_text(TranslationRequest(
                        text=text,
                        target_language=request.target_language,
                        source_language=request.source_language
                    ))
                    batch_tasks.append(task)
                
                # Attendre que tous les textes du lot soient traduits
                batch_results = await asyncio.gather(*batch_tasks)
                translations.extend(batch_results)
                
                # Petit délai entre les lots
                if i + batch_size < len(request.texts):
                    await asyncio.sleep(0.1)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Batch translation completed: {len(translations)} texts in {processing_time:.2f}s")
            
            return BatchTranslationResponse(
                translations=translations,
                batch_id=batch_id,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Batch translation error: {e}")
            raise HTTPException(status_code=500, detail=f"Batch translation failed: {str(e)}")
    
    async def detect_language(self, request: LanguageDetectionRequest) -> LanguageDetectionResponse:
        """Détecte la langue d'un texte"""
        try:
            result = self.client.detect_language(request.text)
            
            return LanguageDetectionResponse(
                detected_language=result['language'],
                confidence=result['confidence'],
                text=request.text
            )
            
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            # Retourner une détection par défaut
            return LanguageDetectionResponse(
                detected_language='en',
                confidence=0.5,
                text=request.text
            )
    
    @lru_cache(maxsize=1)
    async def get_supported_languages(self) -> Dict[str, str]:
        """Récupère la liste des langues supportées"""
        try:
            if not self.supported_languages:
                languages = self.client.get_languages()
                self.supported_languages = {
                    lang['language']: lang['name'] 
                    for lang in languages
                }
            
            return self.supported_languages
            
        except Exception as e:
            logger.error(f"Error fetching supported languages: {e}")
            # Retourner une liste minimale de langues
            return {
                'fr': 'Français',
                'en': 'English',
                'es': 'Español',
                'de': 'Deutsch',
                'it': 'Italiano',
                'pt': 'Português',
                'zh': '中文',
                'ja': '日本語',
                'ar': 'العربية',
                'ru': 'Русский',
                'hi': 'हिन्दी',
                'ko': '한국어'
            }
    
    async def get_translation_stats(self) -> Dict:
        """Retourne les statistiques de traduction"""
        if not self.redis_client:
            return {'cache_enabled': False, 'cached_translations': 0}
        
        try:
            keys = self.redis_client.keys("translation:*")
            return {
                'cache_enabled': True,
                'cached_translations': len(keys),
                'cache_ttl_days': self.cache_ttl / 86400
            }
        except Exception as e:
            logger.error(f"Error getting translation stats: {e}")
            return {'cache_enabled': False, 'error': str(e)}


class MockTranslateClient:
    """Client de traduction simulé pour les tests et le développement"""
    
    def translate(self, text, target_language=None, source_language=None):
        """Simule une traduction (pour tests)"""
        
        # Traductions simulées pour les langues les plus courantes
        mock_translations = {
            'en': {
                'Découvrez la Musique du Monde Gratuitement': 'Discover World Music for Free',
                'Écoutez des aperçus de 30 secondes': 'Listen to 30-second previews',
                'Aucune inscription requise': 'No registration required',
                'Débloquez l\'Expérience Complète': 'Unlock the Complete Experience',
                'Accueil': 'Home',
                'Explorer': 'Explore',
                'Communauté': 'Community',
                'Collections': 'Collections',
                'Premium': 'Premium',
                'Gratuit': 'Free'
            },
            'es': {
                'Découvrez la Musique du Monde Gratuitement': 'Descubre Música Mundial Gratis',
                'Écoutez des aperçus de 30 secondes': 'Escucha vistas previas de 30 segundos',
                'Aucune inscription requise': 'No se requiere registro',
                'Débloquez l\'Expérience Complète': 'Desbloquea la Experiencia Completa',
                'Accueil': 'Inicio',
                'Explorer': 'Explorar',
                'Communauté': 'Comunidad',
                'Collections': 'Colecciones',
                'Premium': 'Premium',
                'Gratuit': 'Gratis'
            },
            'de': {
                'Découvrez la Musique du Monde Gratuitement': 'Entdecken Sie Weltmusik kostenlos',
                'Écoutez des aperçus de 30 secondes': 'Hören Sie 30-Sekunden-Vorschauen',
                'Aucune inscription requise': 'Keine Anmeldung erforderlich',
                'Débloquez l\'Expérience Complète': 'Schalten Sie das vollständige Erlebnis frei',
                'Accueil': 'Startseite',
                'Explorer': 'Erkunden',
                'Communauté': 'Gemeinschaft',
                'Collections': 'Sammlungen',
                'Premium': 'Premium',
                'Gratuit': 'Kostenlos'
            }
        }
        
        # Si on a une traduction simulée, l'utiliser
        if target_language in mock_translations and text in mock_translations[target_language]:
            translated_text = mock_translations[target_language][text]
        else:
            # Sinon, ajouter un préfixe pour indiquer la langue cible
            translated_text = f"[{target_language.upper()}] {text}"
        
        return {
            'translatedText': translated_text,
            'detectedSourceLanguage': source_language or 'fr',
            'confidence': 0.95
        }
    
    def detect_language(self, text):
        """Simule la détection de langue"""
        # Simple heuristique basée sur des mots clés
        french_words = ['le', 'la', 'les', 'de', 'du', 'des', 'et', 'à', 'un', 'une', 'pour', 'avec']
        english_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        spanish_words = ['el', 'la', 'los', 'las', 'de', 'del', 'y', 'o', 'pero', 'en', 'con', 'por', 'para']
        
        text_lower = text.lower()
        
        french_count = sum(1 for word in french_words if word in text_lower)
        english_count = sum(1 for word in english_words if word in text_lower)
        spanish_count = sum(1 for word in spanish_words if word in text_lower)
        
        if french_count > english_count and french_count > spanish_count:
            return {'language': 'fr', 'confidence': 0.9}
        elif english_count > spanish_count:
            return {'language': 'en', 'confidence': 0.85}
        elif spanish_count > 0:
            return {'language': 'es', 'confidence': 0.8}
        else:
            return {'language': 'fr', 'confidence': 0.5}  # Défaut français
    
    def get_languages(self):
        """Retourne la liste des langues supportées (simulée)"""
        return [
            {'language': 'fr', 'name': 'Français'},
            {'language': 'en', 'name': 'English'},
            {'language': 'es', 'name': 'Español'},
            {'language': 'de', 'name': 'Deutsch'},
            {'language': 'it', 'name': 'Italiano'},
            {'language': 'pt', 'name': 'Português'},
            {'language': 'zh', 'name': '中文'},
            {'language': 'ja', 'name': '日本語'},
            {'language': 'ar', 'name': 'العربية'},
            {'language': 'ru', 'name': 'Русский'},
            {'language': 'hi', 'name': 'हिन्दी'},
            {'language': 'ko', 'name': '한국어'},
            {'language': 'tr', 'name': 'Türkçe'},
            {'language': 'pl', 'name': 'Polski'},
            {'language': 'nl', 'name': 'Nederlands'},
            {'language': 'sv', 'name': 'Svenska'},
            {'language': 'da', 'name': 'Dansk'},
            {'language': 'no', 'name': 'Norsk'},
            {'language': 'fi', 'name': 'Suomi'},
            {'language': 'he', 'name': 'עברית'},
            {'language': 'th', 'name': 'ไทย'},
            {'language': 'vi', 'name': 'Tiếng Việt'},
            {'language': 'uk', 'name': 'Українська'},
            {'language': 'cs', 'name': 'Čeština'},
            {'language': 'hu', 'name': 'Magyar'},
            {'language': 'ro', 'name': 'Română'},
            {'language': 'bg', 'name': 'Български'},
            {'language': 'hr', 'name': 'Hrvatski'},
            {'language': 'sr', 'name': 'Српски'},
            {'language': 'sk', 'name': 'Slovenčina'},
            {'language': 'sl', 'name': 'Slovenščina'},
            {'language': 'et', 'name': 'Eesti'},
            {'language': 'lv', 'name': 'Latviešu'},
            {'language': 'lt', 'name': 'Lietuvių'},
            {'language': 'mt', 'name': 'Malti'},
            {'language': 'ga', 'name': 'Gaeilge'},
            {'language': 'cy', 'name': 'Cymraeg'},
            {'language': 'eu', 'name': 'Euskera'},
            {'language': 'ca', 'name': 'Català'},
            {'language': 'gl', 'name': 'Galego'},
            {'language': 'is', 'name': 'Íslenska'},
            {'language': 'fa', 'name': 'فارسی'},
            {'language': 'ur', 'name': 'اردو'},
            {'language': 'bn', 'name': 'বাংলা'},
            {'language': 'ta', 'name': 'தமிழ்'},
            {'language': 'te', 'name': 'తెలుగు'},
            {'language': 'ml', 'name': 'മലയാളം'},
            {'language': 'kn', 'name': 'ಕನ್ನಡ'},
            {'language': 'gu', 'name': 'ગુજરાતી'},
            {'language': 'pa', 'name': 'ਪੰਜਾਬੀ'},
            {'language': 'mr', 'name': 'मराठी'},
            {'language': 'ne', 'name': 'नेपाली'},
            {'language': 'si', 'name': 'සිංහල'},
            {'language': 'my', 'name': 'မြန်မာ'},
            {'language': 'km', 'name': 'ខ្មែរ'},
            {'language': 'lo', 'name': 'ລາວ'},
            {'language': 'ka', 'name': 'ქართული'},
            {'language': 'hy', 'name': 'Հայերեն'},
            {'language': 'az', 'name': 'Azərbaycan'},
            {'language': 'kk', 'name': 'Қазақ'},
            {'language': 'ky', 'name': 'Кыргыз'},
            {'language': 'uz', 'name': 'O\'zbek'},
            {'language': 'tg', 'name': 'Тоҷикӣ'},
            {'language': 'mn', 'name': 'Монгол'},
            {'language': 'id', 'name': 'Bahasa Indonesia'},
            {'language': 'ms', 'name': 'Bahasa Melayu'},
            {'language': 'tl', 'name': 'Filipino'},
            {'language': 'sw', 'name': 'Kiswahili'},
            {'language': 'am', 'name': 'አማርኛ'},
            {'language': 'zu', 'name': 'isiZulu'},
            {'language': 'xh', 'name': 'isiXhosa'},
            {'language': 'af', 'name': 'Afrikaans'},
            {'language': 'yo', 'name': 'Yorùbá'},
            {'language': 'ig', 'name': 'Igbo'},
            {'language': 'ha', 'name': 'Hausa'}
        ]


# Instance globale du service de traduction
translation_service = TranslationService()
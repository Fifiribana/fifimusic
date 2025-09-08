import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Context pour gérer les traductions
const TranslationContext = createContext();

// Traductions par défaut en français
const defaultTranslations = {
  // Navigation
  'home': 'Accueil',
  'explore': 'Explorer',
  'community': 'Communauté',
  'marketplace': 'Marketplace',
  'subscriptions': 'Abonnements',
  'collections': 'Collections',
  'solidarity': 'Solidarité',
  
  // Section gratuite
  'free_discovery': 'Découverte Gratuite',
  'discover_world_music_free': 'Découvrez la Musique du Monde Gratuitement',
  'free_previews_description': 'Écoutez des aperçus de 30 secondes de notre collection mondiale exceptionnelle',
  'no_registration_needed': 'Aucune inscription requise - Commencez à écouter immédiatement',
  'free_tracks': 'Pistes Gratuites',
  'countries': 'Pays',
  'music_styles': 'Styles Musicaux',
  'access': 'Accès',
  'listen_now_free': 'Écoutez Maintenant - Gratuit',
  '30_second_previews': 'Aperçus de 30 secondes',
  'free': 'GRATUIT',
  'preview_playing': 'Aperçu en cours',
  'preview_available': 'aperçu disponible',
  
  // Section premium
  'premium_content': 'Contenu Premium',
  'unlock_full_experience': 'Débloquez l\'Expérience Complète',
  'premium_benefits_description': 'Accédez à des milliers de pistes HD, des collections exclusives et une expérience sans publicité',
  'unlimited_downloads': 'Téléchargements Illimités',
  'hd_quality_music': 'Musique Qualité HD',
  'exclusive_community': 'Communauté Exclusive',
  'connect_artists': 'Connectez-vous aux Artistes',
  'premium_collections': 'Collections Premium',
  'curated_playlists': 'Playlists Curées',
  'ad_free_experience': 'Expérience Sans Pub',
  'pure_music_enjoyment': 'Pur Plaisir Musical',
  'premium': 'PREMIUM',
  'start_premium_trial': 'Commencer l\'Essai Premium',
  'explore_collections': 'Explorer les Collections',
  'cancel_anytime': 'Annulable à tout moment',
  'first_week_free': 'Première semaine gratuite',
  
  // Interface générale
  'loading_content': 'Chargement du contenu...',
  'search_placeholder': 'Rechercher artistes, chansons, styles...',
  'play': 'Lecture',
  'pause': 'Pause',
  'download': 'Télécharger',
  'like': 'J\'aime',
  'share': 'Partager',
  'add_to_cart': 'Ajouter au Panier',
  'buy_now': 'Acheter Maintenant',
  
  // Hero section
  'discover_pulse_world': 'Découvrez le Pouls du Monde',
  'world_music_description': 'Explorez une carte interactive du patrimoine musical mondial. Écoutez, découvrez et achetez de la musique authentique de tous les continents avec des aperçus audio haute qualité.',
  'start_exploration': 'Commencer l\'Exploration',
  'selected_collections': 'Collections Sélectionnées',
  
  // Statistics
  'countries_stat': 'Pays',
  'tracks_stat': 'Pistes',
  'styles_stat': 'Styles',
  'listening_stat': 'Écoute',
  
  // Formulaires
  'email': 'Email',
  'password': 'Mot de passe',
  'username': 'Nom d\'utilisateur',
  'login': 'Connexion',
  'register': 'Inscription',
  'logout': 'Déconnexion',
  'forgot_password': 'Mot de passe oublié ?',
  'remember_me': 'Se souvenir de moi',
  
  // Messages
  'welcome_back': 'Bon retour',
  'account_created': 'Compte créé avec succès',
  'login_success': 'Connexion réussie',
  'logout_success': 'Déconnexion réussie',
  'error_occurred': 'Une erreur est survenue',
  'try_again': 'Réessayer',
  
  // Musique et artistes
  'artist': 'Artiste',
  'album': 'Album',
  'track': 'Piste',
  'duration': 'Durée',
  'genre': 'Genre',
  'region': 'Région',
  'style': 'Style',
  'mood': 'Ambiance',
  'instrument': 'Instrument',
  'bpm': 'BPM',
  'release_date': 'Date de sortie',
  'price': 'Prix',
  'quality': 'Qualité',
  
  // Regions du monde
  'africa': 'Afrique',
  'asia': 'Asie',
  'europe': 'Europe',
  'north_america': 'Amérique du Nord',
  'south_america': 'Amérique du Sud',
  'oceania': 'Océanie',
  'middle_east': 'Moyen-Orient',
  
  // Genres musicaux
  'bikutsi': 'Bikutsi',
  'makossa': 'Makossa',
  'soukous': 'Soukous',
  'afrobeat': 'Afrobeat',
  'highlife': 'Highlife',
  'rumba': 'Rumba',
  'flamenco': 'Flamenco',
  'bollywood': 'Bollywood',
  'gamelan': 'Gamelan',
  'samba': 'Samba',
  'tango': 'Tango',
  'blues': 'Blues',
  'jazz': 'Jazz',
  'country': 'Country',
  'folk': 'Folk',
  'electronic': 'Électronique',
  
  // États d'humeur
  'energetic': 'Énergique',
  'spiritual': 'Spirituel',
  'dancing': 'Dansant',
  'romantic': 'Romantique',
  'festive': 'Festif',
  'calm': 'Calme',
  'melancholic': 'Mélancolique',
  'uplifting': 'Revigorant',
  
  // Actions
  'search': 'Rechercher',
  'filter': 'Filtrer',
  'sort': 'Trier',
  'view_all': 'Voir tout',
  'load_more': 'Charger plus',
  'go_back': 'Retour',
  'next': 'Suivant',
  'previous': 'Précédent',
  'close': 'Fermer',
  'open': 'Ouvrir',
  'save': 'Sauvegarder',
  'cancel': 'Annuler',
  'confirm': 'Confirmer',
  'delete': 'Supprimer',
  'edit': 'Modifier',
  'update': 'Mettre à jour',
  
  // Footer
  'about_us': 'À propos',
  'contact': 'Contact',
  'privacy_policy': 'Politique de confidentialité',
  'terms_of_service': 'Conditions d\'utilisation',
  'copyright': 'Tous droits réservés',
  'follow_us': 'Suivez-nous',
  
  // Messages d'erreur
  'error_404': 'Page non trouvée',
  'error_500': 'Erreur serveur',
  'network_error': 'Erreur de réseau',
  'timeout_error': 'Délai d\'attente dépassé',
  'validation_error': 'Erreur de validation',
  'authentication_error': 'Erreur d\'authentification',
  'permission_error': 'Permissions insuffisantes',
  
  // Success messages
  'upload_success': 'Téléchargement réussi',
  'download_success': 'Téléchargement terminé',
  'payment_success': 'Paiement réussi',
  'subscription_success': 'Abonnement activé',
  'profile_updated': 'Profil mis à jour',
  'settings_saved': 'Paramètres sauvegardés',
  
  // Premium features
  'premium_only': 'Réservé aux membres Premium',
  'upgrade_to_access': 'Passez au Premium pour accéder',
  'premium_features': 'Fonctionnalités Premium',
  'upgrade_now': 'Passer au Premium',
  'free_trial': 'Essai gratuit',
  'subscription_plans': 'Plans d\'abonnement',
  
  // Community
  'join_community': 'Rejoindre la Communauté',
  'share_music': 'Partager votre Musique',
  'connect_musicians': 'Rencontrer des Musiciens',
  'collaborate': 'Collaborer',
  'discussion': 'Discussion',
  'forum': 'Forum',
  'events': 'Événements',
  
  // AI Features
  'ai_assistant': 'Assistant IA',
  'ai_recommendations': 'Recommandations IA',
  'ai_composer': 'Compositeur IA',
  'chat_with_ai': 'Discuter avec l\'IA',
  'get_suggestions': 'Obtenir des Suggestions',
  'generate_music': 'Générer de la Musique',
  
  // Solidarity
  'solidarity_music': 'Solidarité Musicale',
  'support_artists': 'Soutenir les Artistes',
  'donate': 'Faire un Don',
  'help_community': 'Aider la Communauté',
  'together_stronger': 'Ensemble nous sommes plus forts',
  
  // Social
  'share_facebook': 'Partager sur Facebook',
  'share_twitter': 'Partager sur Twitter',
  'share_instagram': 'Partager sur Instagram',
  'copy_link': 'Copier le lien',
  
  // Time and dates
  'today': 'Aujourd\'hui',
  'yesterday': 'Hier',
  'this_week': 'Cette semaine',
  'this_month': 'Ce mois',
  'this_year': 'Cette année',
  'ago': 'il y a',
  'minutes': 'minutes',
  'hours': 'heures',
  'days': 'jours',
  'weeks': 'semaines',
  'months': 'mois',
  'years': 'années',
  
  // Currency and pricing
  'free_text': 'Gratuit',
  'price_from': 'À partir de',
  'currency_eur': '€',
  'currency_usd': '$',
  'add_to_cart': 'Ajouter au panier',
  'proceed_checkout': 'Procéder au paiement',
  'total': 'Total',
  'subtotal': 'Sous-total',
  'tax': 'Taxe',
  'shipping': 'Livraison',
  
  // Quality and format
  'hd_quality': 'Qualité HD',
  'mp3_format': 'Format MP3',
  'wav_format': 'Format WAV',
  'flac_format': 'Format FLAC',
  '320kbps': '320 kbps',
  'lossless': 'Sans perte',
  
  // Notifications
  'notification': 'Notification',
  'new_music': 'Nouvelle musique',
  'price_drop': 'Baisse de prix',
  'artist_update': 'Mise à jour artiste',
  'system_message': 'Message système',
  'mark_read': 'Marquer comme lu',
  'mark_all_read': 'Tout marquer comme lu',
  
  // Profile and account
  'my_profile': 'Mon Profil',
  'edit_profile': 'Modifier le Profil',
  'account_settings': 'Paramètres du Compte',
  'change_password': 'Changer le Mot de Passe',
  'privacy_settings': 'Paramètres de Confidentialité',
  'notification_settings': 'Paramètres de Notification',
  'language_settings': 'Paramètres de Langue',
  'theme_settings': 'Paramètres de Thème',
  
  // Help and support
  'help': 'Aide',
  'support': 'Support',
  'faq': 'FAQ',
  'contact_support': 'Contacter le Support',
  'report_issue': 'Signaler un Problème',
  'feature_request': 'Demande de Fonctionnalité',
  'feedback': 'Commentaires',
  'rate_app': 'Noter l\'Application',
  
  // Search and discovery
  'popular_searches': 'Recherches Populaires',
  'trending_now': 'Tendances Actuelles',
  'new_releases': 'Nouvelles Sorties',
  'top_charts': 'Top Classements',
  'recommended_for_you': 'Recommandé pour Vous',
  'similar_music': 'Musique Similaire',
  'discover_more': 'Découvrir Plus',
  
  // Player controls
  'play_pause': 'Lecture/Pause',
  'skip_forward': 'Avancer',
  'skip_backward': 'Reculer',
  'volume': 'Volume',
  'mute': 'Muet',
  'repeat': 'Répéter',
  'shuffle': 'Aléatoire',
  'queue': 'File d\'attente',
  'now_playing': 'En cours de lecture',
  
  // Mobile specific
  'install_app': 'Installer l\'App',
  'add_to_homescreen': 'Ajouter à l\'écran d\'accueil',
  'offline_mode': 'Mode Hors Ligne',
  'download_offline': 'Télécharger pour Hors Ligne',
  'sync_settings': 'Paramètres de Synchronisation'
};

export const TranslationProvider = ({ children }) => {
  const [currentLanguage, setCurrentLanguage] = useState('fr');
  const [translations, setTranslations] = useState(defaultTranslations);
  const [isTranslating, setIsTranslating] = useState(false);
  const [translationCache, setTranslationCache] = useState(new Map());

  useEffect(() => {
    // Charger la langue préférée depuis le localStorage
    const savedLanguage = localStorage.getItem('preferred_language');
    if (savedLanguage && savedLanguage !== 'fr') {
      handleLanguageChange(savedLanguage);
    }
  }, []);

  const translateText = async (text, targetLanguage, sourceLanguage = 'fr') => {
    const cacheKey = `${text}:${sourceLanguage}:${targetLanguage}`;
    
    // Vérifier le cache d'abord
    if (translationCache.has(cacheKey)) {
      return translationCache.get(cacheKey);
    }

    try {
      const response = await axios.post(`${API}/translate`, {
        text: text,
        target_language: targetLanguage,
        source_language: sourceLanguage
      });

      const translatedText = response.data.translated_text;
      
      // Mettre en cache le résultat
      setTranslationCache(prev => new Map(prev.set(cacheKey, translatedText)));
      
      return translatedText;
    } catch (error) {
      console.error('Translation error:', error);
      return text; // Retourner le texte original en cas d'erreur
    }
  };

  const translateBatch = async (texts, targetLanguage, sourceLanguage = 'fr') => {
    const uncachedTexts = [];
    const results = {};

    // Vérifier le cache pour chaque texte
    for (const [key, text] of Object.entries(texts)) {
      const cacheKey = `${text}:${sourceLanguage}:${targetLanguage}`;
      if (translationCache.has(cacheKey)) {
        results[key] = translationCache.get(cacheKey);
      } else {
        uncachedTexts.push({ key, text });
      }
    }

    // Traduire les textes non mis en cache par petits lots
    const batchSize = 10;
    for (let i = 0; i < uncachedTexts.length; i += batchSize) {
      const batch = uncachedTexts.slice(i, i + batchSize);
      
      try {
        const promises = batch.map(async ({ key, text }) => {
          const translatedText = await translateText(text, targetLanguage, sourceLanguage);
          return { key, translatedText };
        });

        const batchResults = await Promise.all(promises);
        batchResults.forEach(({ key, translatedText }) => {
          results[key] = translatedText;
        });

        // Petit délai entre les lots pour éviter de surcharger l'API
        if (i + batchSize < uncachedTexts.length) {
          await new Promise(resolve => setTimeout(resolve, 200));
        }
      } catch (error) {
        console.error('Batch translation error:', error);
        // En cas d'erreur, utiliser les textes originaux
        batch.forEach(({ key, text }) => {
          results[key] = text;
        });
      }
    }

    return results;
  };

  const handleLanguageChange = async (newLanguage) => {
    if (newLanguage === currentLanguage) return;

    setIsTranslating(true);

    try {
      let newTranslations = { ...defaultTranslations };

      if (newLanguage !== 'fr') {
        // Traduire toutes les clés de traduction
        newTranslations = await translateBatch(
          defaultTranslations,
          newLanguage,
          'fr'
        );
      }

      setTranslations(newTranslations);
      setCurrentLanguage(newLanguage);
      localStorage.setItem('preferred_language', newLanguage);

      // Mettre à jour l'attribut lang du document
      document.documentElement.lang = newLanguage;

      // Gérer la direction du texte pour les langues RTL
      const rtlLanguages = ['ar', 'he', 'fa', 'ur'];
      if (rtlLanguages.includes(newLanguage)) {
        document.documentElement.dir = 'rtl';
        document.body.classList.add('rtl');
      } else {
        document.documentElement.dir = 'ltr';
        document.body.classList.remove('rtl');
      }

    } catch (error) {
      console.error('Language change failed:', error);
    } finally {
      setIsTranslating(false);
    }
  };

  const t = (key, defaultValue = null) => {
    return translations[key] || defaultValue || key;
  };

  const value = {
    currentLanguage,
    translations,
    isTranslating,
    handleLanguageChange,
    translateText,
    t
  };

  return (
    <TranslationContext.Provider value={value}>
      {children}
    </TranslationContext.Provider>
  );
};

export const useTranslation = () => {
  const context = useContext(TranslationContext);
  if (!context) {
    throw new Error('useTranslation must be used within a TranslationProvider');
  }
  return context;
};
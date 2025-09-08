import React, { useState, useEffect, useRef } from 'react';
import { Globe, ChevronDown, Check, Loader, Sparkles } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Composant de sélection de langue avec traduction automatique
const LanguageSelector = ({ onLanguageChange, currentLanguage = 'fr' }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [languages, setLanguages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [translating, setTranslating] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const dropdownRef = useRef(null);

  // Langues populaires avec leurs données complètes
  const popularLanguages = [
    { code: 'fr', name: 'Français', nativeName: 'Français', flag: '🇫🇷', region: 'Europe' },
    { code: 'en', name: 'English', nativeName: 'English', flag: '🇺🇸', region: 'Americas' },
    { code: 'es', name: 'Español', nativeName: 'Español', flag: '🇪🇸', region: 'Europe' },
    { code: 'de', name: 'Deutsch', nativeName: 'Deutsch', flag: '🇩🇪', region: 'Europe' },
    { code: 'it', name: 'Italiano', nativeName: 'Italiano', flag: '🇮🇹', region: 'Europe' },
    { code: 'pt', name: 'Português', nativeName: 'Português', flag: '🇵🇹', region: 'Europe' },
    { code: 'zh', name: '中文', nativeName: '中文', flag: '🇨🇳', region: 'Asia' },
    { code: 'ja', name: '日本語', nativeName: '日本語', flag: '🇯🇵', region: 'Asia' },
    { code: 'ar', name: 'العربية', nativeName: 'العربية', flag: '🇸🇦', region: 'Middle East', rtl: true },
    { code: 'ru', name: 'Русский', nativeName: 'Русский', flag: '🇷🇺', region: 'Europe' },
    { code: 'hi', name: 'हिन्दी', nativeName: 'हिन्दी', flag: '🇮🇳', region: 'Asia' },
    { code: 'ko', name: '한국어', nativeName: '한국어', flag: '🇰🇷', region: 'Asia' },
    { code: 'tr', name: 'Türkçe', nativeName: 'Türkçe', flag: '🇹🇷', region: 'Europe' },
    { code: 'pl', name: 'Polski', nativeName: 'Polski', flag: '🇵🇱', region: 'Europe' },
    { code: 'nl', name: 'Nederlands', nativeName: 'Nederlands', flag: '🇳🇱', region: 'Europe' },
    { code: 'sv', name: 'Svenska', nativeName: 'Svenska', flag: '🇸🇪', region: 'Europe' },
    { code: 'da', name: 'Dansk', nativeName: 'Dansk', flag: '🇩🇰', region: 'Europe' },
    { code: 'no', name: 'Norsk', nativeName: 'Norsk', flag: '🇳🇴', region: 'Europe' },
    { code: 'fi', name: 'Suomi', nativeName: 'Suomi', flag: '🇫🇮', region: 'Europe' },
    { code: 'he', name: 'עברית', nativeName: 'עברית', flag: '🇮🇱', region: 'Middle East', rtl: true },
    { code: 'th', name: 'ไทย', nativeName: 'ไทย', flag: '🇹🇭', region: 'Asia' },
    { code: 'vi', name: 'Tiếng Việt', nativeName: 'Tiếng Việt', flag: '🇻🇳', region: 'Asia' },
    { code: 'uk', name: 'Українська', nativeName: 'Українська', flag: '🇺🇦', region: 'Europe' },
    { code: 'cs', name: 'Čeština', nativeName: 'Čeština', flag: '🇨🇿', region: 'Europe' },
    { code: 'hu', name: 'Magyar', nativeName: 'Magyar', flag: '🇭🇺', region: 'Europe' },
    { code: 'ro', name: 'Română', nativeName: 'Română', flag: '🇷🇴', region: 'Europe' },
    { code: 'bg', name: 'Български', nativeName: 'Български', flag: '🇧🇬', region: 'Europe' },
    { code: 'hr', name: 'Hrvatski', nativeName: 'Hrvatski', flag: '🇭🇷', region: 'Europe' },
    { code: 'sr', name: 'Српски', nativeName: 'Српски', flag: '🇷🇸', region: 'Europe' },
    { code: 'sk', name: 'Slovenčina', nativeName: 'Slovenčina', flag: '🇸🇰', region: 'Europe' },
    { code: 'sl', name: 'Slovenščina', nativeName: 'Slovenščina', flag: '🇸🇮', region: 'Europe' },
    { code: 'et', name: 'Eesti', nativeName: 'Eesti', flag: '🇪🇪', region: 'Europe' },
    { code: 'lv', name: 'Latviešu', nativeName: 'Latviešu', flag: '🇱🇻', region: 'Europe' },
    { code: 'lt', name: 'Lietuvių', nativeName: 'Lietuvių', flag: '🇱🇹', region: 'Europe' },
    { code: 'mt', name: 'Malti', nativeName: 'Malti', flag: '🇲🇹', region: 'Europe' },
    { code: 'ga', name: 'Gaeilge', nativeName: 'Gaeilge', flag: '🇮🇪', region: 'Europe' },
    { code: 'cy', name: 'Cymraeg', nativeName: 'Cymraeg', flag: '🏴󠁧󠁢󠁷󠁬󠁳󠁿', region: 'Europe' },
    { code: 'eu', name: 'Euskera', nativeName: 'Euskera', flag: '🇪🇸', region: 'Europe' },
    { code: 'ca', name: 'Català', nativeName: 'Català', flag: '🇪🇸', region: 'Europe' },
    { code: 'gl', name: 'Galego', nativeName: 'Galego', flag: '🇪🇸', region: 'Europe' },
    { code: 'is', name: 'Íslenska', nativeName: 'Íslenska', flag: '🇮🇸', region: 'Europe' },
    { code: 'fa', name: 'فارسی', nativeName: 'فارسی', flag: '🇮🇷', region: 'Middle East', rtl: true },
    { code: 'ur', name: 'اردو', nativeName: 'اردو', flag: '🇵🇰', region: 'Asia', rtl: true },
    { code: 'bn', name: 'বাংলা', nativeName: 'বাংলা', flag: '🇧🇩', region: 'Asia' },
    { code: 'ta', name: 'தமிழ்', nativeName: 'தமிழ்', flag: '🇮🇳', region: 'Asia' },
    { code: 'te', name: 'తెలుగు', nativeName: 'తెలుగు', flag: '🇮🇳', region: 'Asia' },
    { code: 'ml', name: 'മലയാളം', nativeName: 'മലയാളം', flag: '🇮🇳', region: 'Asia' },
    { code: 'kn', name: 'ಕನ್ನಡ', nativeName: 'ಕನ್ನಡ', flag: '🇮🇳', region: 'Asia' },
    { code: 'gu', name: 'ગુજરાતી', nativeName: 'ગુજરાતી', flag: '🇮🇳', region: 'Asia' },
    { code: 'pa', name: 'ਪੰਜਾਬੀ', nativeName: 'ਪੰਜਾਬੀ', flag: '🇮🇳', region: 'Asia' },
    { code: 'mr', name: 'मराठी', nativeName: 'मराठी', flag: '🇮🇳', region: 'Asia' },
    { code: 'ne', name: 'नेपाली', nativeName: 'नेपाली', flag: '🇳🇵', region: 'Asia' },
    { code: 'si', name: 'සිංහල', nativeName: 'සිංහල', flag: '🇱🇰', region: 'Asia' },
    { code: 'my', name: 'မြန်မာ', nativeName: 'မြန်မာ', flag: '🇲🇲', region: 'Asia' },
    { code: 'km', name: 'ខ្មែរ', nativeName: 'ខ្មែរ', flag: '🇰🇭', region: 'Asia' },
    { code: 'lo', name: 'ລາວ', nativeName: 'ລາວ', flag: '🇱🇦', region: 'Asia' },
    { code: 'ka', name: 'ქართული', nativeName: 'ქართული', flag: '🇬🇪', region: 'Europe' },
    { code: 'hy', name: 'Հայերեն', nativeName: 'Հայերեն', flag: '🇦🇲', region: 'Europe' },
    { code: 'az', name: 'Azərbaycan', nativeName: 'Azərbaycan', flag: '🇦🇿', region: 'Europe' },
    { code: 'kk', name: 'Қазақ', nativeName: 'Қазақ', flag: '🇰🇿', region: 'Asia' },
    { code: 'ky', name: 'Кыргыз', nativeName: 'Кыргыз', flag: '🇰🇬', region: 'Asia' },
    { code: 'uz', name: 'O\'zbek', nativeName: 'O\'zbek', flag: '🇺🇿', region: 'Asia' },
    { code: 'tg', name: 'Тоҷикӣ', nativeName: 'Тоҷикӣ', flag: '🇹🇯', region: 'Asia' },
    { code: 'mn', name: 'Монгол', nativeName: 'Монгол', flag: '🇲🇳', region: 'Asia' },
    { code: 'id', name: 'Bahasa Indonesia', nativeName: 'Bahasa Indonesia', flag: '🇮🇩', region: 'Asia' },
    { code: 'ms', name: 'Bahasa Melayu', nativeName: 'Bahasa Melayu', flag: '🇲🇾', region: 'Asia' },
    { code: 'tl', name: 'Filipino', nativeName: 'Filipino', flag: '🇵🇭', region: 'Asia' },
    { code: 'sw', name: 'Kiswahili', nativeName: 'Kiswahili', flag: '🇰🇪', region: 'Africa' },
    { code: 'am', name: 'አማርኛ', nativeName: 'አማርኛ', flag: '🇪🇹', region: 'Africa' },
    { code: 'zu', name: 'isiZulu', nativeName: 'isiZulu', flag: '🇿🇦', region: 'Africa' },
    { code: 'xh', name: 'isiXhosa', nativeName: 'isiXhosa', flag: '🇿🇦', region: 'Africa' },
    { code: 'af', name: 'Afrikaans', nativeName: 'Afrikaans', flag: '🇿🇦', region: 'Africa' },
    { code: 'yo', name: 'Yorùbá', nativeName: 'Yorùbá', flag: '🇳🇬', region: 'Africa' },
    { code: 'ig', name: 'Igbo', nativeName: 'Igbo', flag: '🇳🇬', region: 'Africa' },
    { code: 'ha', name: 'Hausa', nativeName: 'Hausa', flag: '🇳🇬', region: 'Africa' }
  ];

  useEffect(() => {
    setLanguages(popularLanguages);
  }, []);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLanguageSelect = async (langCode) => {
    if (langCode === currentLanguage) {
      setIsOpen(false);
      return;
    }

    setTranslating(true);
    setIsOpen(false);

    try {
      // Enregistrer la préférence de langue
      localStorage.setItem('preferred_language', langCode);
      
      // Déclencher la traduction de la page
      await translatePageContent(langCode);
      
      // Notifier le composant parent
      if (onLanguageChange) {
        onLanguageChange(langCode);
      }

      // Mettre à jour l'attribut lang du document
      document.documentElement.lang = langCode;
      
      // Gérer la direction du texte (RTL/LTR)
      const selectedLang = languages.find(lang => lang.code === langCode);
      if (selectedLang?.rtl) {
        document.documentElement.dir = 'rtl';
        document.body.classList.add('rtl');
      } else {
        document.documentElement.dir = 'ltr';
        document.body.classList.remove('rtl');
      }

    } catch (error) {
      console.error('Language change failed:', error);
    } finally {
      setTranslating(false);
    }
  };

  const translatePageContent = async (targetLanguage) => {
    const translatableElements = document.querySelectorAll('[data-translate], h1, h2, h3, h4, h5, h6, p:not(.no-translate), button:not(.no-translate), a:not(.no-translate), span:not(.no-translate)');
    
    const elementsToTranslate = Array.from(translatableElements).filter(element => {
      const text = element.textContent.trim();
      // Ne pas traduire les éléments courts, les URLs, emails, etc.
      return text.length > 2 && 
             !text.match(/^https?:\/\//) && 
             !text.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/) && 
             !text.match(/^\d+(\.\d+)?$/) &&
             !element.closest('.no-translate') &&
             !element.hasAttribute('contenteditable');
    });

    const batchSize = 10;
    for (let i = 0; i < elementsToTranslate.length; i += batchSize) {
      const batch = elementsToTranslate.slice(i, i + batchSize);
      
      const translations = await Promise.all(
        batch.map(async (element) => {
          const originalText = element.dataset.originalText || element.textContent;
          
          // Sauvegarder le texte original
          if (!element.dataset.originalText) {
            element.dataset.originalText = originalText;
          }

          try {
            const response = await axios.post(`${API}/translate`, {
              text: originalText,
              target_language: targetLanguage,
              source_language: 'fr'
            });

            return {
              element,
              translatedText: response.data.translated_text
            };
          } catch (error) {
            console.error('Translation error:', error);
            return {
              element,
              translatedText: originalText
            };
          }
        })
      );

      // Appliquer les traductions
      translations.forEach(({ element, translatedText }) => {
        if (element.tagName === 'INPUT' && element.type === 'text') {
          element.placeholder = translatedText;
        } else {
          element.textContent = translatedText;
        }
      });

      // Petit délai entre les batches pour éviter de surcharger l'API
      if (i + batchSize < elementsToTranslate.length) {
        await new Promise(resolve => setTimeout(resolve, 200));
      }
    }
  };

  const getCurrentLanguage = () => {
    return languages.find(lang => lang.code === currentLanguage) || languages[0];
  };

  const filteredLanguages = languages.filter(lang =>
    lang.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    lang.nativeName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    lang.region.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const groupedLanguages = filteredLanguages.reduce((groups, lang) => {
    const region = lang.region;
    if (!groups[region]) {
      groups[region] = [];
    }
    groups[region].push(lang);
    return groups;
  }, {});

  const currentLang = getCurrentLanguage();

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Indicateur de traduction */}
      {translating && (
        <div className="fixed top-20 right-4 z-50 bg-terracotta text-white px-6 py-3 rounded-full shadow-lg flex items-center space-x-3">
          <Loader className="w-5 h-5 animate-spin" />
          <span className="font-medium">Traduction en cours...</span>
          <Sparkles className="w-5 h-5 text-gold animate-pulse" />
        </div>
      )}

      {/* Bouton de sélection de langue */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`flex items-center space-x-3 px-4 py-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-lg text-white hover:bg-white/20 transition-all ${
          isOpen ? 'ring-2 ring-terracotta' : ''
        }`}
        disabled={translating}
      >
        <Globe className="w-5 h-5" />
        <span className="text-2xl">{currentLang.flag}</span>
        <span className="font-medium">{currentLang.name}</span>
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown menu */}
      {isOpen && (
        <div className="absolute top-full right-0 mt-2 w-96 bg-white rounded-2xl shadow-2xl border border-gray-200 z-50 max-h-96 overflow-hidden">
          {/* Header avec recherche */}
          <div className="p-4 border-b border-gray-100">
            <div className="flex items-center space-x-2 mb-3">
              <Globe className="w-5 h-5 text-terracotta" />
              <span className="font-bold text-charcoal">Choisir une langue</span>
              <Sparkles className="w-4 h-4 text-gold" />
            </div>
            <input
              type="text"
              placeholder="Rechercher une langue..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-terracotta text-sm"
            />
          </div>

          {/* Liste des langues groupées par région */}
          <div className="max-h-80 overflow-y-auto">
            {Object.keys(groupedLanguages).map(region => (
              <div key={region}>
                <div className="px-4 py-2 bg-gray-50 border-b border-gray-100">
                  <span className="text-sm font-semibold text-gray-600">{region}</span>
                </div>
                {groupedLanguages[region].map(lang => (
                  <button
                    key={lang.code}
                    onClick={() => handleLanguageSelect(lang.code)}
                    className={`w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors flex items-center justify-between ${
                      lang.code === currentLanguage ? 'bg-terracotta/10 border-r-4 border-terracotta' : ''
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{lang.flag}</span>
                      <div>
                        <div className="font-medium text-charcoal">{lang.name}</div>
                        <div className="text-sm text-gray-500">{lang.nativeName}</div>
                      </div>
                    </div>
                    {lang.code === currentLanguage && (
                      <Check className="w-5 h-5 text-terracotta" />
                    )}
                  </button>
                ))}
              </div>
            ))}
          </div>

          {/* Footer */}
          <div className="p-3 border-t border-gray-100 bg-gray-50">
            <div className="text-xs text-gray-500 text-center">
              <Sparkles className="w-3 h-3 inline mr-1" />
              Traduction automatique par IA
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LanguageSelector;
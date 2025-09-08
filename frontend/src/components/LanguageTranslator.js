import React, { useState, useEffect, createContext, useContext } from 'react';
import { Globe, ChevronDown, Check, Loader, Sparkles, Languages } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Context for global translation
const TranslationContext = createContext();

// Language configurations with flags and native names
const LANGUAGES = [
  { code: 'fr', name: 'Français', nativeName: 'Français', flag: '🇫🇷', region: 'Europe' },
  { code: 'en', name: 'English', nativeName: 'English', flag: '🇺🇸', region: 'Americas' },
  { code: 'es', name: 'Español', nativeName: 'Español', flag: '🇪🇸', region: 'Europe' },
  { code: 'pt', name: 'Português', nativeName: 'Português', flag: '🇵🇹', region: 'Europe' },
  { code: 'de', name: 'Deutsch', nativeName: 'Deutsch', flag: '🇩🇪', region: 'Europe' },
  { code: 'it', name: 'Italiano', nativeName: 'Italiano', flag: '🇮🇹', region: 'Europe' },
  { code: 'ru', name: 'Русский', nativeName: 'Русский', flag: '🇷🇺', region: 'Europe' },
  { code: 'zh', name: '中文', nativeName: '中文', flag: '🇨🇳', region: 'Asia' },
  { code: 'ja', name: '日本語', nativeName: '日本語', flag: '🇯🇵', region: 'Asia' },
  { code: 'ko', name: '한국어', nativeName: '한국어', flag: '🇰🇷', region: 'Asia' },
  { code: 'ar', name: 'العربية', nativeName: 'العربية', flag: '🇸🇦', region: 'Middle East', rtl: true },
  { code: 'hi', name: 'हिन्दी', nativeName: 'हिन्दी', flag: '🇮🇳', region: 'Asia' },
  { code: 'tr', name: 'Türkçe', nativeName: 'Türkçe', flag: '🇹🇷', region: 'Europe' },
  { code: 'nl', name: 'Nederlands', nativeName: 'Nederlands', flag: '🇳🇱', region: 'Europe' },
  { code: 'pl', name: 'Polski', nativeName: 'Polski', flag: '🇵🇱', region: 'Europe' },
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

// Translation Provider Component
export const GlobalTranslationProvider = ({ children }) => {
  const [currentLanguage, setCurrentLanguage] = useState('fr');
  const [isTranslating, setIsTranslating] = useState(false);
  const [translationCache, setTranslationCache] = useState(new Map());

  useEffect(() => {
    // Load saved language preference
    const savedLanguage = localStorage.getItem('us_explo_language');
    if (savedLanguage && savedLanguage !== 'fr') {
      setCurrentLanguage(savedLanguage);
    }
  }, []);

  const translateText = async (text, targetLanguage) => {
    if (!text || !targetLanguage || targetLanguage === 'fr') {
      return text;
    }

    const cacheKey = `${text}:${targetLanguage}`;
    if (translationCache.has(cacheKey)) {
      return translationCache.get(cacheKey);
    }

    try {
      const response = await axios.post(`${API}/translate`, {
        text: text,
        target_language: targetLanguage,
        source_language: 'fr'
      });

      const translatedText = response.data.translated_text;
      
      // Cache the result
      setTranslationCache(prev => new Map(prev.set(cacheKey, translatedText)));
      
      return translatedText;
    } catch (error) {
      console.error('Translation error:', error);
      return text; // Return original text on error
    }
  };

  const translatePage = async (targetLanguage) => {
    if (targetLanguage === 'fr') {
      // Restore original French text
      const elementsWithOriginal = document.querySelectorAll('[data-original-text]');
      elementsWithOriginal.forEach(element => {
        const originalText = element.dataset.originalText;
        element.textContent = originalText;
      });
      return;
    }

    setIsTranslating(true);

    try {
      // Find all text elements to translate
      const textElements = document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, span, button, a, label, [data-translate]');
      const elementsToTranslate = Array.from(textElements).filter(element => {
        const text = element.textContent.trim();
        return text.length > 1 && 
               !text.match(/^https?:\/\//) && 
               !text.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/) && 
               !text.match(/^\d+(\.\d+)?$/) &&
               !element.closest('.no-translate') &&
               !element.hasAttribute('contenteditable') &&
               !element.querySelector('img, svg, input, textarea, select');
      });

      // Translate in batches
      const batchSize = 5;
      for (let i = 0; i < elementsToTranslate.length; i += batchSize) {
        const batch = elementsToTranslate.slice(i, i + batchSize);
        
        await Promise.all(batch.map(async (element) => {
          const originalText = element.dataset.originalText || element.textContent.trim();
          
          // Save original text if not already saved
          if (!element.dataset.originalText) {
            element.dataset.originalText = originalText;
          }

          try {
            const translatedText = await translateText(originalText, targetLanguage);
            element.textContent = translatedText;
          } catch (error) {
            console.error('Element translation error:', error);
          }
        }));

        // Small delay between batches
        if (i + batchSize < elementsToTranslate.length) {
          await new Promise(resolve => setTimeout(resolve, 100));
        }
      }

      // Handle RTL languages
      const language = LANGUAGES.find(lang => lang.code === targetLanguage);
      if (language?.rtl) {
        document.documentElement.dir = 'rtl';
        document.body.classList.add('rtl');
      } else {
        document.documentElement.dir = 'ltr';
        document.body.classList.remove('rtl');
      }

      // Update document language
      document.documentElement.lang = targetLanguage;

    } catch (error) {
      console.error('Page translation error:', error);
    } finally {
      setIsTranslating(false);
    }
  };

  const changeLanguage = async (languageCode) => {
    if (languageCode === currentLanguage) return;

    setCurrentLanguage(languageCode);
    localStorage.setItem('us_explo_language', languageCode);
    
    await translatePage(languageCode);
  };

  const value = {
    currentLanguage,
    isTranslating,
    translateText,
    translatePage,
    changeLanguage,
    availableLanguages: LANGUAGES
  };

  return (
    <TranslationContext.Provider value={value}>
      {children}
    </TranslationContext.Provider>
  );
};

// Hook to use translation
export const useGlobalTranslation = () => {
  const context = useContext(TranslationContext);
  if (!context) {
    throw new Error('useGlobalTranslation must be used within GlobalTranslationProvider');
  }
  return context;
};

// Main Language Selector Component
export const GlobalLanguageSelector = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const { currentLanguage, isTranslating, changeLanguage, availableLanguages } = useGlobalTranslation();

  const currentLang = availableLanguages.find(lang => lang.code === currentLanguage);
  
  const filteredLanguages = availableLanguages.filter(lang =>
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

  return (
    <div className="relative">
      {/* Translation Progress Indicator */}
      {isTranslating && (
        <div className="fixed top-20 right-4 z-50 bg-gradient-to-r from-terracotta to-gold text-white px-6 py-3 rounded-full shadow-2xl flex items-center space-x-3 border-2 border-white/20">
          <Loader className="w-5 h-5 animate-spin" />
          <span className="font-bold">Traduction en cours...</span>
          <Sparkles className="w-5 h-5 text-yellow-300 animate-pulse" />
        </div>
      )}

      {/* Language Selector Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`flex items-center space-x-3 px-4 py-2 bg-white/15 backdrop-blur-sm border-2 border-white/20 rounded-xl text-white hover:bg-white/25 transition-all duration-300 transform hover:scale-105 shadow-lg ${
          isOpen ? 'ring-2 ring-terracotta scale-105' : ''
        } ${isTranslating ? 'pointer-events-none opacity-75' : ''}`}
        disabled={isTranslating}
      >
        <Globe className="w-5 h-5" />
        <span className="text-2xl">{currentLang?.flag}</span>
        <span className="font-semibold hidden sm:block">{currentLang?.name}</span>
        <ChevronDown className={`w-4 h-4 transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown Menu */}
      {isOpen && !isTranslating && (
        <div className="absolute top-full right-0 mt-3 w-96 bg-white rounded-2xl shadow-2xl border-2 border-gray-200 z-50 max-h-96 overflow-hidden">
          {/* Header */}
          <div className="p-4 bg-gradient-to-r from-terracotta to-gold text-white">
            <div className="flex items-center space-x-2 mb-3">
              <Languages className="w-6 h-6" />
              <span className="font-bold text-lg">Choisir une langue</span>
              <Sparkles className="w-5 h-5 animate-pulse" />
            </div>
            <input
              type="text"
              placeholder="Rechercher une langue..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 rounded-lg border-0 bg-white/20 backdrop-blur-sm text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-white/30"
            />
          </div>

          {/* Languages List */}
          <div className="max-h-80 overflow-y-auto">
            {Object.keys(groupedLanguages).sort().map(region => (
              <div key={region}>
                <div className="px-4 py-2 bg-gradient-to-r from-gray-100 to-gray-50 border-b border-gray-200">
                  <span className="text-sm font-bold text-gray-700 flex items-center">
                    🌍 {region}
                    <span className="ml-2 text-xs text-gray-500">({groupedLanguages[region].length})</span>
                  </span>
                </div>
                {groupedLanguages[region].map(lang => (
                  <button
                    key={lang.code}
                    onClick={() => {
                      changeLanguage(lang.code);
                      setIsOpen(false);
                    }}
                    className={`w-full px-4 py-3 text-left hover:bg-gradient-to-r hover:from-terracotta/10 hover:to-gold/10 transition-all duration-200 flex items-center justify-between border-b border-gray-50 last:border-b-0 ${
                      lang.code === currentLanguage ? 'bg-gradient-to-r from-terracotta/20 to-gold/20 border-l-4 border-l-terracotta' : ''
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <span className="text-3xl">{lang.flag}</span>
                      <div>
                        <div className="font-semibold text-gray-800">{lang.name}</div>
                        <div className="text-sm text-gray-500" dir={lang.rtl ? 'rtl' : 'ltr'}>{lang.nativeName}</div>
                      </div>
                    </div>
                    {lang.code === currentLanguage && (
                      <div className="text-terracotta">
                        <Check className="w-5 h-5" />
                      </div>
                    )}
                  </button>
                ))}
              </div>
            ))}
          </div>

          {/* Footer */}
          <div className="p-3 bg-gradient-to-r from-gray-50 to-gray-100 border-t border-gray-200">
            <div className="text-xs text-gray-600 text-center flex items-center justify-center space-x-1">
              <Sparkles className="w-3 h-3" />
              <span>Traduction automatique propulsée par l'IA</span>
              <span className="text-terracotta font-semibold">• {availableLanguages.length} langues disponibles</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
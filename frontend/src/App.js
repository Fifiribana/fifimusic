import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { Search, Globe, Music, Users, ShoppingCart, User, Menu, X, Play, Pause, Volume2 } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Navigation Component
const Navigation = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-charcoal/95 backdrop-blur-md border-b border-terracotta/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-terracotta to-gold rounded-lg flex items-center justify-center">
              <Music className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">US EXPLO</h1>
              <p className="text-xs text-sage">Universal Sound Exploration</p>
            </div>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <a href="#" className="text-white hover:text-terracotta transition-colors">Accueil</a>
            <div className="relative group">
              <a href="#" className="text-white hover:text-terracotta transition-colors flex items-center">
                Explorer <Globe className="w-4 h-4 ml-1" />
              </a>
            </div>
            <a href="#" className="text-white hover:text-terracotta transition-colors">Artistes</a>
            <a href="#" className="text-white hover:text-terracotta transition-colors">Blog</a>
            <a href="#" className="text-white hover:text-terracotta transition-colors">Boutique</a>
          </div>

          {/* Right side icons */}
          <div className="hidden md:flex items-center space-x-4">
            <button className="p-2 text-white hover:text-terracotta transition-colors">
              <ShoppingCart className="w-5 h-5" />
            </button>
            <button className="p-2 text-white hover:text-terracotta transition-colors">
              <User className="w-5 h-5" />
            </button>
          </div>

          {/* Mobile menu button */}
          <button 
            className="md:hidden p-2 text-white"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden bg-charcoal/98 border-t border-terracotta/20">
            <div className="px-2 pt-2 pb-3 space-y-1">
              <a href="#" className="block px-3 py-2 text-white hover:text-terracotta">Accueil</a>
              <a href="#" className="block px-3 py-2 text-white hover:text-terracotta">Explorer</a>
              <a href="#" className="block px-3 py-2 text-white hover:text-terracotta">Artistes</a>
              <a href="#" className="block px-3 py-2 text-white hover:text-terracotta">Blog</a>
              <a href="#" className="block px-3 py-2 text-white hover:text-terracotta">Boutique</a>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

// Hero Section Component
const HeroSection = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background Image with Overlay */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat"
        style={{
          backgroundImage: `url('https://images.unsplash.com/photo-1528190303099-2408e63c79e3?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHwyfHx3b3JsZCUyMG11c2ljfGVufDB8fHx8MTc1NzAxMTU0MXww&ixlib=rb-4.1.0&q=85')`
        }}
      >
        <div className="absolute inset-0 bg-gradient-to-br from-charcoal/80 via-charcoal/60 to-transparent"></div>
      </div>

      {/* Content */}
      <div className="relative z-10 text-center px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
        <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 tracking-tight">
          US EXPLO
        </h1>
        <p className="text-2xl md:text-3xl text-sage mb-4 font-light">
          Universal Sound Exploration
        </p>
        <p className="text-xl text-white/90 mb-12 max-w-2xl mx-auto leading-relaxed">
          Discover the Pulse of the World. Explorez une carte interactive du patrimoine musical mondial.
        </p>
        
        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <button className="px-8 py-4 bg-terracotta hover:bg-terracotta/90 text-white font-semibold rounded-full transition-all transform hover:scale-105 shadow-lg">
            Commencer l'Exploration
          </button>
          <button className="px-8 py-4 border-2 border-white/30 text-white hover:bg-white/10 font-semibold rounded-full transition-all backdrop-blur-sm">
            Découvrir la Carte
          </button>
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
        <div className="w-6 h-10 border-2 border-white/30 rounded-full flex justify-center">
          <div className="w-1 h-3 bg-white/50 rounded-full mt-2 animate-pulse"></div>
        </div>
      </div>
    </section>
  );
};

// Interactive World Map Component
const InteractiveMap = () => {
  const [selectedRegion, setSelectedRegion] = useState(null);

  const regions = [
    { name: "Afrique", x: 48, y: 60, description: "Afrobeat, Highlife, Soukous" },
    { name: "Europe", x: 48, y: 35, description: "Flamenco, Folk, Electronic" },
    { name: "Asie", x: 70, y: 45, description: "Bollywood, Gamelan, K-Pop" },
    { name: "Amérique du Sud", x: 25, y: 70, description: "Samba, Tango, Cumbia" },
    { name: "Amérique du Nord", x: 20, y: 35, description: "Blues, Jazz, Country" },
    { name: "Océanie", x: 85, y: 75, description: "Didgeridoo, Pacific Islander" }
  ];

  return (
    <section className="py-20 bg-gradient-to-b from-sage/10 to-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-charcoal mb-6">
            Explorez le Monde Musical
          </h2>
          <p className="text-xl text-charcoal/70 max-w-3xl mx-auto leading-relaxed">
            Cliquez sur une région pour découvrir ses richesses musicales
          </p>
        </div>

        <div className="relative max-w-4xl mx-auto bg-white rounded-3xl shadow-2xl p-8 overflow-hidden">
          {/* World Map SVG Background */}
          <div className="relative h-96 bg-gradient-to-br from-sage/20 to-terracotta/20 rounded-2xl flex items-center justify-center">
            <svg viewBox="0 0 100 80" className="w-full h-full">
              {/* Simple world map outlines */}
              <path d="M15,25 Q20,20 30,25 L35,30 Q40,35 35,40 L30,45 Q25,40 20,35 Z" fill="#2d3436" opacity="0.3" />
              <path d="M40,30 Q50,25 60,30 L70,35 Q75,40 70,45 L60,50 Q50,45 45,40 Z" fill="#2d3436" opacity="0.3" />
              <path d="M75,40 Q85,35 90,40 L85,50 Q80,55 75,50 Z" fill="#2d3436" opacity="0.3" />
              <path d="M40,50 Q50,55 60,60 L55,70 Q45,65 40,60 Z" fill="#2d3436" opacity="0.3" />
              <path d="M15,60 Q25,65 35,70 L30,75 Q20,70 15,65 Z" fill="#2d3436" opacity="0.3" />
              <path d="M80,70 Q85,65 90,70 L85,80 Q80,75 80,70 Z" fill="#2d3436" opacity="0.3" />
            </svg>
            
            {/* Interactive Points */}
            {regions.map((region, index) => (
              <button
                key={index}
                className={`absolute w-6 h-6 rounded-full transition-all transform hover:scale-125 ${
                  selectedRegion === region.name 
                    ? 'bg-terracotta shadow-lg shadow-terracotta/50' 
                    : 'bg-gold hover:bg-terracotta'
                } animate-pulse`}
                style={{ left: `${region.x}%`, top: `${region.y}%` }}
                onClick={() => setSelectedRegion(selectedRegion === region.name ? null : region.name)}
              >
                <span className="sr-only">{region.name}</span>
              </button>
            ))}
          </div>

          {/* Region Info */}
          {selectedRegion && (
            <div className="mt-8 p-6 bg-gradient-to-r from-sage/10 to-terracotta/10 rounded-2xl border border-terracotta/20">
              <h3 className="text-2xl font-bold text-charcoal mb-2">{selectedRegion}</h3>
              <p className="text-charcoal/70">
                {regions.find(r => r.name === selectedRegion)?.description}
              </p>
              <button className="mt-4 px-6 py-2 bg-terracotta text-white rounded-full hover:bg-terracotta/90 transition-colors">
                Explorer cette région
              </button>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

// Featured Collections Component
const FeaturedCollections = () => {
  const collections = [
    {
      title: "Découvertes du Mois",
      description: "Les dernières trouvailles musicales du monde entier",
      image: "https://images.unsplash.com/photo-1700419420072-8583b28f2036?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NjZ8MHwxfHNlYXJjaHwzfHxnbG9iYWwlMjBpbnN0cnVtZW50c3xlbnwwfHx8fDE3NTcwMTE1NDZ8MA&ixlib=rb-4.1.0&q=85",
      tracks: 24
    },
    {
      title: "Rythmes Africains",
      description: "L'essence vibrant de l'Afrique musicale",
      image: "https://images.unsplash.com/photo-1565719178004-420e3480e2b5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NjZ8MHwxfHNlYXJjaHw0fHxnbG9iYWwlMjBpbnN0cnVtZW50c3xlbnwwfHx8fDE3NTcwMTE1NDZ8MA&ixlib=rb-4.1.0&q=85",
      tracks: 32
    },
    {
      title: "Mélodies Orientales",
      description: "Les sons mystiques de l'Orient",
      image: "https://images.unsplash.com/photo-1551973732-463437696ab3?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHwxfHx3b3JsZCUyMG11c2ljfGVufDB8fHx8MTc1NzAxMTU0MXww&ixlib=rb-4.1.0&q=85",
      tracks: 18
    }
  ];

  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-charcoal mb-6">
            Collections Sélectionnées
          </h2>
          <p className="text-xl text-charcoal/70 max-w-3xl mx-auto">
            Découvrez nos playlists soigneusement organisées par style et région
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {collections.map((collection, index) => (
            <div 
              key={index} 
              className="group bg-white rounded-3xl shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 overflow-hidden border border-sage/20"
            >
              <div className="relative h-64 overflow-hidden">
                <img 
                  src={collection.image} 
                  alt={collection.title}
                  className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-charcoal/60 via-transparent to-transparent"></div>
                <div className="absolute bottom-4 left-4 text-white">
                  <p className="text-sm opacity-90">{collection.tracks} morceaux</p>
                </div>
              </div>
              <div className="p-6">
                <h3 className="text-2xl font-bold text-charcoal mb-3 group-hover:text-terracotta transition-colors">
                  {collection.title}
                </h3>
                <p className="text-charcoal/70 mb-4">
                  {collection.description}
                </p>
                <button className="flex items-center space-x-2 text-terracotta hover:text-gold font-semibold transition-colors">
                  <Play className="w-4 h-4" />
                  <span>Écouter maintenant</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Search Section Component
const SearchSection = () => {
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <section className="py-20 bg-gradient-to-br from-charcoal via-charcoal/95 to-sage/20">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
          Trouvez Votre Son
        </h2>
        <p className="text-xl text-white/80 mb-12 max-w-2xl mx-auto">
          Recherchez par style, humeur, instrument ou continent
        </p>
        
        <div className="relative max-w-2xl mx-auto">
          <div className="absolute inset-y-0 left-0 pl-6 flex items-center pointer-events-none">
            <Search className="h-6 w-6 text-sage" />
          </div>
          <input
            type="text"
            placeholder="Ex: Afrobeat, Sitar, Méditation..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-14 pr-6 py-4 bg-white/10 backdrop-blur-md border border-white/20 rounded-full text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-terracotta focus:border-transparent text-lg"
          />
          <button className="absolute inset-y-0 right-0 pr-2 flex items-center">
            <div className="bg-terracotta hover:bg-terracotta/90 p-3 rounded-full transition-colors">
              <Search className="h-5 w-5 text-white" />
            </div>
          </button>
        </div>

        <div className="mt-8 flex flex-wrap justify-center gap-3">
          {["Afrobeat", "Flamenco", "Bollywood", "Reggae", "Samba", "Folk"].map((tag, index) => (
            <button 
              key={index}
              className="px-6 py-2 bg-white/10 hover:bg-white/20 text-white rounded-full backdrop-blur-sm border border-white/20 transition-all hover:scale-105"
            >
              {tag}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
};

// Footer Component
const Footer = () => {
  return (
    <footer className="bg-charcoal text-white py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-12 h-12 bg-gradient-to-br from-terracotta to-gold rounded-lg flex items-center justify-center">
                <Music className="w-7 h-7 text-white" />
              </div>
              <div>
                <h3 className="text-2xl font-bold">US EXPLO</h3>
                <p className="text-sage">Universal Sound Exploration</p>
              </div>
            </div>
            <p className="text-white/70 max-w-md leading-relaxed">
              Découvrez et explorez la richesse musicale du monde entier. 
              Chaque son raconte une histoire, chaque mélodie porte une culture.
            </p>
          </div>
          
          <div>
            <h4 className="text-lg font-semibold mb-4">Explorer</h4>
            <ul className="space-y-2 text-white/70">
              <li><a href="#" className="hover:text-terracotta transition-colors">Par Continent</a></li>
              <li><a href="#" className="hover:text-terracotta transition-colors">Par Style</a></li>
              <li><a href="#" className="hover:text-terracotta transition-colors">Par Instrument</a></li>
              <li><a href="#" className="hover:text-terracotta transition-colors">Nouveautés</a></li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-lg font-semibold mb-4">Communauté</h4>
            <ul className="space-y-2 text-white/70">
              <li><a href="#" className="hover:text-terracotta transition-colors">Blog</a></li>
              <li><a href="#" className="hover:text-terracotta transition-colors">Artistes</a></li>
              <li><a href="#" className="hover:text-terracotta transition-colors">Newsletter</a></li>
              <li><a href="#" className="hover:text-terracotta transition-colors">Contact</a></li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-white/20 mt-12 pt-8 text-center text-white/60">
          <p>&copy; 2025 US EXPLO. Tous droits réservés. Discover the Pulse of the World.</p>
        </div>
      </div>
    </footer>
  );
};

// Main Home Component
const Home = () => {
  const helloWorldApi = async () => {
    try {
      const response = await axios.get(`${API}/`);
      console.log("API Response:", response.data.message);
    } catch (e) {
      console.error(e, "Error connecting to API");
    }
  };

  useEffect(() => {
    helloWorldApi();
  }, []);

  return (
    <div className="min-h-screen">
      <Navigation />
      <HeroSection />
      <InteractiveMap />
      <FeaturedCollections />
      <SearchSection />
      <Footer />
    </div>
  );
};

// Main App Component
function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
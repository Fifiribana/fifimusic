import React, { useState, useEffect, createContext, useContext } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import { Search, Globe, Music, Users, ShoppingCart, User, Menu, X, Play, Pause, Volume2, Heart, Download, CreditCard, LogIn, UserPlus, LogOut } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// PWA Installation Hook
const usePWAInstall = () => {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [isInstallable, setIsInstallable] = useState(false);

  useEffect(() => {
    const handler = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setIsInstallable(true);
    };

    window.addEventListener('beforeinstallprompt', handler);

    return () => window.removeEventListener('beforeinstallprompt', handler);
  }, []);

  const installPWA = async () => {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    
    if (outcome === 'accepted') {
      setIsInstallable(false);
      setDeferredPrompt(null);
    }
  };

  return { isInstallable, installPWA };
};

// Service Worker Registration
const registerServiceWorker = () => {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js')
        .then((registration) => {
          console.log('✅ [US EXPLO] Service Worker registered:', registration);
          
          // Check for updates
          registration.addEventListener('updatefound', () => {
            const newWorker = registration.installing;
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                // New version available
                if (window.confirm('Une nouvelle version d\'US EXPLO est disponible. Actualiser maintenant ?')) {
                  newWorker.postMessage({ type: 'SKIP_WAITING' });
                  window.location.reload();
                }
              }
            });
          });
        })
        .catch((error) => {
          console.error('❌ [US EXPLO] Service Worker registration failed:', error);
        });
    });

    // Handle service worker updates
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      window.location.reload();
    });
  }
};

// Auth Context
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // Verify token and get user info
      axios.get(`${API}/auth/me`)
        .then(response => {
          setUser(response.data);
        })
        .catch(() => {
          localStorage.removeItem('token');
          setToken(null);
          delete axios.defaults.headers.common['Authorization'];
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [token]);

  const login = (userData, userToken) => {
    setUser(userData);
    setToken(userToken);
    localStorage.setItem('token', userToken);
    axios.defaults.headers.common['Authorization'] = `Bearer ${userToken}`;
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

// Audio Player Context
const AudioContext = createContext();

const AudioProvider = ({ children }) => {
  const [currentTrack, setCurrentTrack] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audio, setAudio] = useState(null);

  const playTrack = (track) => {
    if (audio) {
      audio.pause();
    }
    
    const newAudio = new Audio(track.preview_url || track.audio_url);
    newAudio.addEventListener('ended', () => setIsPlaying(false));
    newAudio.addEventListener('pause', () => setIsPlaying(false));
    newAudio.addEventListener('play', () => setIsPlaying(true));
    
    setAudio(newAudio);
    setCurrentTrack(track);
    newAudio.play();
  };

  const pauseTrack = () => {
    if (audio) {
      audio.pause();
    }
  };

  const resumeTrack = () => {
    if (audio) {
      audio.play();
    }
  };

  return (
    <AudioContext.Provider value={{ 
      currentTrack, 
      isPlaying, 
      playTrack, 
      pauseTrack, 
      resumeTrack 
    }}>
      {children}
    </AudioContext.Provider>
  );
};

const useAudio = () => {
  const context = useContext(AudioContext);
  if (!context) {
    throw new Error('useAudio must be used within AudioProvider');
  }
  return context;
};

// Cart Context
const CartContext = createContext();

const CartProvider = ({ children }) => {
  const [cartItems, setCartItems] = useState([]);

  const addToCart = (track) => {
    setCartItems(prev => {
      const exists = prev.find(item => item.id === track.id);
      if (exists) return prev;
      return [...prev, track];
    });
  };

  const removeFromCart = (trackId) => {
    setCartItems(prev => prev.filter(item => item.id !== trackId));
  };

  const clearCart = () => {
    setCartItems([]);
  };

  const totalPrice = cartItems.reduce((sum, item) => sum + item.price, 0);

  return (
    <CartContext.Provider value={{ 
      cartItems, 
      addToCart, 
      removeFromCart, 
      clearCart, 
      totalPrice 
    }}>
      {children}
    </CartContext.Provider>
  );
};

const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within CartProvider');
  }
  return context;
};

// Audio Player Component
const AudioPlayer = () => {
  const { currentTrack, isPlaying, pauseTrack, resumeTrack } = useAudio();

  if (!currentTrack) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-charcoal text-white p-4 z-50 border-t border-terracotta/20">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <img 
            src={currentTrack.artwork_url} 
            alt={currentTrack.title}
            className="w-12 h-12 rounded-lg object-cover"
          />
          <div>
            <h4 className="font-semibold">{currentTrack.title}</h4>
            <p className="text-sm text-sage">{currentTrack.artist}</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <button
            onClick={isPlaying ? pauseTrack : resumeTrack}
            className="bg-terracotta hover:bg-terracotta/90 p-3 rounded-full transition-colors"
          >
            {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
          </button>
          <Volume2 className="w-5 h-5 text-sage" />
        </div>
      </div>
    </div>
  );
};

// Auth Components
const LoginModal = ({ isOpen, onClose }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: ''
  });
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/register';
      const payload = isLogin 
        ? { email: formData.email, password: formData.password }
        : formData;

      const response = await axios.post(`${API}${endpoint}`, payload);
      login(response.data.user, response.data.access_token);
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Une erreur est survenue');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl p-8 max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-charcoal">
            {isLogin ? 'Connexion' : 'Inscription'}
          </h2>
          <button onClick={onClose} className="text-charcoal hover:text-terracotta">
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-charcoal mb-2">Email</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              className="w-full px-4 py-3 border border-sage/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-terracotta"
              required
            />
          </div>

          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-charcoal mb-2">Nom d'utilisateur</label>
              <input
                type="text"
                value={formData.username}
                onChange={(e) => setFormData({...formData, username: e.target.value})}
                className="w-full px-4 py-3 border border-sage/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-terracotta"
                required
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-charcoal mb-2">Mot de passe</label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              className="w-full px-4 py-3 border border-sage/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-terracotta"
              required
            />
          </div>

          {error && (
            <div className="text-red-500 text-sm bg-red-50 p-3 rounded-lg">{error}</div>
          )}

          <button
            type="submit"
            className="w-full bg-terracotta hover:bg-terracotta/90 text-white py-3 rounded-lg font-semibold transition-colors"
          >
            {isLogin ? 'Se connecter' : "S'inscrire"}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-terracotta hover:text-gold"
          >
            {isLogin 
              ? "Pas de compte ? S'inscrire" 
              : "Déjà un compte ? Se connecter"
            }
          </button>
        </div>
      </div>
    </div>
  );
};

// PWA Install Button Component
const PWAInstallButton = () => {
  const { isInstallable, installPWA } = usePWAInstall();

  if (!isInstallable) return null;

  return (
    <button
      onClick={installPWA}
      className="fixed bottom-20 right-4 bg-terracotta hover:bg-terracotta/90 text-white px-6 py-3 rounded-full shadow-lg z-50 flex items-center space-x-2 transition-all transform hover:scale-105"
    >
      <Download className="w-5 h-5" />
      <span className="font-semibold">Installer l'App</span>
    </button>
  );
};

// Navigation Component
const Navigation = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const { user, logout } = useAuth();
  const { cartItems } = useCart();

  return (
    <>
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
              <a href="/" className="text-white hover:text-terracotta transition-colors">Accueil</a>
              <div className="relative group">
                <a href="#explorer" className="text-white hover:text-terracotta transition-colors flex items-center">
                  Explorer <Globe className="w-4 h-4 ml-1" />
                </a>
              </div>
              <a href="#collections" className="text-white hover:text-terracotta transition-colors">Collections</a>
              <a href="/simon-messela" className="text-white hover:text-terracotta transition-colors font-semibold">
                Simon Messela
              </a>
              <a href="#" className="text-white hover:text-terracotta transition-colors">Artistes</a>
            </div>

            {/* Right side icons */}
            <div className="hidden md:flex items-center space-x-4">
              <div className="relative">
                <button className="p-2 text-white hover:text-terracotta transition-colors">
                  <ShoppingCart className="w-5 h-5" />
                </button>
                {cartItems.length > 0 && (
                  <span className="absolute -top-1 -right-1 bg-terracotta text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {cartItems.length}
                  </span>
                )}
              </div>
              
              {user ? (
                <div className="flex items-center space-x-2">
                  <span className="text-white text-sm">Bonjour, {user.username}</span>
                  <button 
                    onClick={logout}
                    className="p-2 text-white hover:text-terracotta transition-colors"
                  >
                    <LogOut className="w-5 h-5" />
                  </button>
                </div>
              ) : (
                <button 
                  onClick={() => setShowLoginModal(true)}
                  className="p-2 text-white hover:text-terracotta transition-colors"
                >
                  <User className="w-5 h-5" />
                </button>
              )}
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
                <a href="/" className="block px-3 py-2 text-white hover:text-terracotta">Accueil</a>
                <a href="#explorer" className="block px-3 py-2 text-white hover:text-terracotta">Explorer</a>
                <a href="#collections" className="block px-3 py-2 text-white hover:text-terracotta">Collections</a>
                <a href="/simon-messela" className="block px-3 py-2 text-white hover:text-terracotta font-semibold">Simon Messela</a>
                <a href="#" className="block px-3 py-2 text-white hover:text-terracotta">Artistes</a>
                {!user && (
                  <button 
                    onClick={() => setShowLoginModal(true)}
                    className="block w-full text-left px-3 py-2 text-white hover:text-terracotta"
                  >
                    Connexion
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </nav>

      <LoginModal isOpen={showLoginModal} onClose={() => setShowLoginModal(false)} />
    </>
  );
};

// Track Card Component
const TrackCard = ({ track }) => {
  const { playTrack, currentTrack, isPlaying } = useAudio();
  const { addToCart } = useCart();
  const [isLiked, setIsLiked] = useState(false);

  const handleLike = async () => {
    try {
      await axios.put(`${API}/tracks/${track.id}/like`);
      setIsLiked(true);
      track.likes += 1;
    } catch (error) {
      console.error('Error liking track:', error);
    }
  };

  const handlePurchase = async () => {
    try {
      const response = await axios.post(`${API}/checkout/create`, {
        host_url: window.location.origin,
        track_ids: [track.id],
        user_email: "guest@example.com"
      });
      
      if (response.data.checkout_url) {
        window.location.href = response.data.checkout_url;
      }
    } catch (error) {
      console.error('Error creating checkout:', error);
    }
  };

  const isCurrentlyPlaying = currentTrack?.id === track.id && isPlaying;

  return (
    <div className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 overflow-hidden">
      <div className="relative h-48 overflow-hidden">
        <img 
          src={track.artwork_url} 
          alt={track.title}
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent">
          <div className="absolute bottom-4 left-4 text-white">
            <p className="text-sm opacity-90">{track.duration}s • {track.bpm} BPM</p>
          </div>
          <button
            onClick={() => playTrack(track)}
            className="absolute top-4 right-4 bg-terracotta/90 hover:bg-terracotta p-2 rounded-full transition-colors"
          >
            {isCurrentlyPlaying ? <Pause className="w-4 h-4 text-white" /> : <Play className="w-4 h-4 text-white" />}
          </button>
        </div>
      </div>
      
      <div className="p-6">
        <div className="flex justify-between items-start mb-2">
          <div>
            <h3 className="text-xl font-bold text-charcoal mb-1">{track.title}</h3>
            <p className="text-sage font-medium">{track.artist}</p>
          </div>
          <span className="text-2xl font-bold text-terracotta">{track.price.toFixed(2)}€</span>
        </div>
        
        <div className="flex items-center space-x-2 mb-3">
          <span className="px-3 py-1 bg-sage/20 text-sage rounded-full text-sm">{track.region}</span>
          <span className="px-3 py-1 bg-terracotta/20 text-terracotta rounded-full text-sm">{track.style}</span>
        </div>
        
        <p className="text-charcoal/70 text-sm mb-4">{track.description}</p>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <button 
              onClick={handleLike}
              className={`flex items-center space-x-1 ${isLiked ? 'text-red-500' : 'text-charcoal/60 hover:text-red-500'}`}
            >
              <Heart className={`w-4 h-4 ${isLiked ? 'fill-current' : ''}`} />
              <span className="text-sm">{track.likes}</span>
            </button>
            <div className="flex items-center space-x-1 text-charcoal/60">
              <Download className="w-4 h-4" />
              <span className="text-sm">{track.downloads}</span>
            </div>
          </div>
          
          <div className="flex space-x-2">
            <button 
              onClick={() => addToCart(track)}
              className="px-4 py-2 bg-sage hover:bg-sage/90 text-white rounded-lg transition-colors"
            >
              Panier
            </button>
            <button 
              onClick={handlePurchase}
              className="px-4 py-2 bg-terracotta hover:bg-terracotta/90 text-white rounded-lg transition-colors flex items-center space-x-1"
            >
              <CreditCard className="w-4 h-4" />
              <span>Acheter</span>
            </button>
          </div>
        </div>
      </div>
    </div>
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
          Discover the Pulse of the World. Explorez une carte interactive du patrimoine musical mondial avec lecture audio et achat sécurisé.
        </p>
        
        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <button 
            onClick={() => document.getElementById('explorer').scrollIntoView({ behavior: 'smooth' })}
            className="px-8 py-4 bg-terracotta hover:bg-terracotta/90 text-white font-semibold rounded-full transition-all transform hover:scale-105 shadow-lg"
          >
            Commencer l'Exploration
          </button>
          <button 
            onClick={() => document.getElementById('collections').scrollIntoView({ behavior: 'smooth' })}
            className="px-8 py-4 border-2 border-white/30 text-white hover:bg-white/10 font-semibold rounded-full transition-all backdrop-blur-sm"
          >
            Découvrir les Collections
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
  const [regionTracks, setRegionTracks] = useState([]);

  const regions = [
    { name: "Afrique", x: 48, y: 60, description: "Afrobeat, Highlife, Soukous, Bikutsi, Makossa" },
    { name: "Europe", x: 48, y: 35, description: "Flamenco, Folk, Electronic" },
    { name: "Asie", x: 70, y: 45, description: "Bollywood, Gamelan, K-Pop" },
    { name: "Amérique du Sud", x: 25, y: 70, description: "Samba, Tango, Cumbia" },
    { name: "Amérique du Nord", x: 20, y: 35, description: "Blues, Jazz, Country" },
    { name: "Océanie", x: 85, y: 75, description: "Didgeridoo, Pacific Islander" }
  ];

  const fetchRegionTracks = async (region) => {
    try {
      const response = await axios.get(`${API}/tracks?region=${region}&limit=6`);
      setRegionTracks(response.data);
    } catch (error) {
      console.error('Error fetching region tracks:', error);
    }
  };

  const handleRegionClick = (region) => {
    const newRegion = selectedRegion === region.name ? null : region.name;
    setSelectedRegion(newRegion);
    if (newRegion) {
      fetchRegionTracks(newRegion);
    }
  };

  return (
    <section id="explorer" className="py-20 bg-gradient-to-b from-sage/10 to-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-charcoal mb-6">
            Explorez le Monde Musical
          </h2>
          <p className="text-xl text-charcoal/70 max-w-3xl mx-auto leading-relaxed">
            Cliquez sur une région pour découvrir ses richesses musicales et écouter des extraits
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
                onClick={() => handleRegionClick(region)}
              >
                <span className="sr-only">{region.name}</span>
              </button>
            ))}
          </div>

          {/* Region Info */}
          {selectedRegion && (
            <div className="mt-8 space-y-6">
              <div className="p-6 bg-gradient-to-r from-sage/10 to-terracotta/10 rounded-2xl border border-terracotta/20">
                <h3 className="text-2xl font-bold text-charcoal mb-2">{selectedRegion}</h3>
                <p className="text-charcoal/70 mb-4">
                  {regions.find(r => r.name === selectedRegion)?.description}
                </p>
              </div>

              {/* Region Tracks */}
              {regionTracks.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {regionTracks.map(track => (
                    <TrackCard key={track.id} track={track} />
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

// Featured Collections Component
const FeaturedCollections = () => {
  const [collections, setCollections] = useState([]);
  const [tracks, setTracks] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [collectionsResponse, tracksResponse] = await Promise.all([
          axios.get(`${API}/collections?featured=true`),
          axios.get(`${API}/tracks?limit=12`)
        ]);
        setCollections(collectionsResponse.data);
        setTracks(tracksResponse.data);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  return (
    <section id="collections" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-charcoal mb-6">
            Collections Sélectionnées
          </h2>
          <p className="text-xl text-charcoal/70 max-w-3xl mx-auto">
            Découvrez nos playlists soigneusement organisées par style et région, avec écoute et achat instantané
          </p>
        </div>

        {tracks.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {tracks.map(track => (
              <TrackCard key={track.id} track={track} />
            ))}
          </div>
        )}
      </div>
    </section>
  );
};

// Featured Artist Section (Simon Messela)
const FeaturedArtistSection = () => {
  return (
    <section className="py-20 bg-gradient-to-r from-charcoal to-sage/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Text Content */}
          <div className="text-white">
            <div className="mb-6">
              <span className="px-4 py-2 bg-gold text-charcoal rounded-full font-bold text-sm uppercase tracking-wide">
                Artiste Fondateur
              </span>
            </div>
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Simon Messela
              <span className="block text-2xl md:text-3xl text-terracotta font-light mt-2">
                (fifi Ribana)
              </span>
            </h2>
            <p className="text-xl text-white/90 leading-relaxed mb-8">
              Créateur d'US EXPLO et artiste polyvalent, Simon Messela voyage à travers tous les styles musicaux. 
              Du Bikutsi traditionnel camerounais aux fusions électroniques modernes, il incarne l'esprit 
              d'exploration universelle qui définit notre plateforme.
            </p>
            
            <div className="flex flex-wrap gap-3 mb-8">
              <span className="px-4 py-2 bg-terracotta/20 text-terracotta rounded-lg font-semibold">
                Bikutsi
              </span>
              <span className="px-4 py-2 bg-sage/20 text-sage rounded-lg font-semibold">
                Makossa
              </span>
              <span className="px-4 py-2 bg-gold/20 text-gold rounded-lg font-semibold">
                World Fusion
              </span>
              <span className="px-4 py-2 bg-white/20 text-white rounded-lg font-semibold">
                Afrobeat Electronic
              </span>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-4">
              <a 
                href="/simon-messela"
                className="px-8 py-4 bg-terracotta hover:bg-terracotta/90 text-white font-semibold rounded-full transition-all transform hover:scale-105 shadow-lg text-center"
              >
                Découvrir Mes Créations
              </a>
              <button className="px-8 py-4 border-2 border-white/30 text-white hover:bg-white/10 font-semibold rounded-full transition-all backdrop-blur-sm">
                Écouter un Extrait
              </button>
            </div>
          </div>
          
          {/* Image Content */}
          <div className="relative">
            <div className="relative z-10">
              <img 
                src="https://images.unsplash.com/photo-1528190303099-2408e63c79e3?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHwyfHx3b3JsZCUyMG11c2ljfGVufDB8fHx8MTc1NzAxMTU0MXww&ixlib=rb-4.1.0&q=85"
                alt="Simon Messela - Fondateur US EXPLO"
                className="w-full max-w-md mx-auto rounded-3xl shadow-2xl border-4 border-gold"
              />
              <div className="absolute -bottom-6 -right-6 bg-terracotta text-white p-4 rounded-full shadow-xl">
                <Music className="w-8 h-8" />
              </div>
            </div>
            
            {/* Decorative elements */}
            <div className="absolute top-4 -left-4 w-24 h-24 bg-sage/30 rounded-full blur-xl"></div>
            <div className="absolute bottom-4 -right-4 w-32 h-32 bg-gold/30 rounded-full blur-xl"></div>
          </div>
        </div>
      </div>
    </section>
  );
};
const SearchSection = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = async (query) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    try {
      const response = await axios.get(`${API}/search?q=${encodeURIComponent(query)}`);
      setSearchResults(response.data.tracks);
    } catch (error) {
      console.error('Error searching:', error);
    } finally {
      setIsSearching(false);
    }
  };

  const handleTagClick = (tag) => {
    setSearchQuery(tag);
    handleSearch(tag);
  };

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      handleSearch(searchQuery);
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [searchQuery]);

  return (
    <section className="py-20 bg-gradient-to-br from-charcoal via-charcoal/95 to-sage/20">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
          Trouvez Votre Son
        </h2>
        <p className="text-xl text-white/80 mb-12 max-w-2xl mx-auto">
          Recherchez par style, humeur, instrument ou continent et écoutez des extraits
        </p>
        
        <div className="relative max-w-2xl mx-auto">
          <div className="absolute inset-y-0 left-0 pl-6 flex items-center pointer-events-none">
            <Search className="h-6 w-6 text-sage" />
          </div>
          <input
            type="text"
            placeholder="Ex: Bikutsi, Makossa, Soukous, Sitar..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-14 pr-6 py-4 bg-white/10 backdrop-blur-md border border-white/20 rounded-full text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-terracotta focus:border-transparent text-lg"
          />
        </div>

        <div className="mt-8 flex flex-wrap justify-center gap-3">
          {["Bikutsi", "Makossa", "Soukous", "Afrobeat", "Flamenco", "Bollywood", "Reggae", "Samba"].map((tag, index) => (
            <button 
              key={index}
              onClick={() => handleTagClick(tag)}
              className="px-6 py-2 bg-white/10 hover:bg-white/20 text-white rounded-full backdrop-blur-sm border border-white/20 transition-all hover:scale-105"
            >
              {tag}
            </button>
          ))}
        </div>

        {/* Search Results */}
        {isSearching && (
          <div className="mt-12 text-white">Recherche en cours...</div>
        )}

        {searchResults.length > 0 && (
          <div className="mt-12">
            <h3 className="text-2xl font-bold text-white mb-8">Résultats de recherche</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {searchResults.slice(0, 6).map(track => (
                <TrackCard key={track.id} track={track} />
              ))}
            </div>
          </div>
        )}
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
              Écoutez, achetez et téléchargez en toute sécurité.
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
              <li><a href="#" className="hover:text-terracotta transition-colors">Artistes</a></li>
              <li><a href="#" className="hover:text-terracotta transition-colors">Téléchargements</a></li>
              <li><a href="#" className="hover:text-terracotta transition-colors">Support</a></li>
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

// Success Page Component
const SuccessPage = () => {
  const [sessionId, setSessionId] = useState(null);
  const [paymentStatus, setPaymentStatus] = useState('checking');

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionIdParam = urlParams.get('session_id');
    
    if (sessionIdParam) {
      setSessionId(sessionIdParam);
      checkPaymentStatus(sessionIdParam);
    }
  }, []);

  const checkPaymentStatus = async (sessionId, attempts = 0) => {
    const maxAttempts = 5;
    if (attempts >= maxAttempts) {
      setPaymentStatus('timeout');
      return;
    }

    try {
      const response = await axios.get(`${API}/checkout/status/${sessionId}`);
      
      if (response.data.payment_status === 'paid') {
        setPaymentStatus('success');
      } else if (response.data.status === 'expired') {
        setPaymentStatus('expired');
      } else {
        setTimeout(() => checkPaymentStatus(sessionId, attempts + 1), 2000);
      }
    } catch (error) {
      console.error('Error checking payment status:', error);
      setPaymentStatus('error');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-sage/20 to-terracotta/20 flex items-center justify-center">
      <div className="max-w-md mx-auto bg-white rounded-2xl shadow-xl p-8 text-center">
        {paymentStatus === 'checking' && (
          <div>
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-terracotta mx-auto mb-4"></div>
            <h2 className="text-2xl font-bold text-charcoal mb-2">Vérification du paiement...</h2>
            <p className="text-charcoal/70">Veuillez patienter</p>
          </div>
        )}

        {paymentStatus === 'success' && (
          <div>
            <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-charcoal mb-2">Paiement réussi !</h2>
            <p className="text-charcoal/70 mb-6">Merci pour votre achat. Vous pouvez maintenant télécharger vos morceaux.</p>
            <button 
              onClick={() => window.location.href = '/'}
              className="bg-terracotta hover:bg-terracotta/90 text-white px-6 py-3 rounded-lg font-semibold"
            >
              Retour à l'accueil
            </button>
          </div>
        )}

        {paymentStatus === 'error' && (
          <div>
            <div className="w-16 h-16 bg-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <X className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-charcoal mb-2">Erreur de paiement</h2>
            <p className="text-charcoal/70 mb-6">Une erreur s'est produite lors de la vérification du paiement.</p>
            <button 
              onClick={() => window.location.href = '/'}
              className="bg-terracotta hover:bg-terracotta/90 text-white px-6 py-3 rounded-lg font-semibold"
            >
              Retour à l'accueil
            </button>
          </div>
        )}
      </div>
    </div>
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
    registerServiceWorker(); // Register PWA Service Worker
  }, []);

  return (
    <div className="min-h-screen">
      <Navigation />
      <HeroSection />
      <InteractiveMap />
      <FeaturedCollections />
      <FeaturedArtistSection />
      <SearchSection />
      <Footer />
      <AudioPlayer />
      <PWAInstallButton />
    </div>
  );
};

// Simon Messela Artist Page Component
const SimonMesselaPage = () => {
  const [artistTracks, setArtistTracks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSimonTracks = async () => {
      try {
        const response = await axios.get(`${API}/search?q=Simon Messela`);
        setArtistTracks(response.data.tracks);
      } catch (error) {
        console.error('Error fetching Simon tracks:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSimonTracks();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-charcoal to-sage/20">
      <Navigation />
      
      {/* Hero Section */}
      <section className="pt-20 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <div className="relative mb-8">
              <div className="w-48 h-48 mx-auto rounded-full overflow-hidden border-4 border-terracotta shadow-2xl">
                <img 
                  src="https://images.unsplash.com/photo-1528190303099-2408e63c79e3?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHwyfHx3b3JsZCUyMG11c2ljfGVufDB8fHx8MTc1NzAxMTU0MXww&ixlib=rb-4.1.0&q=85"
                  alt="Simon Messela"
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="absolute -bottom-4 left-1/2 transform -translate-x-1/2 bg-gold text-charcoal px-6 py-2 rounded-full font-bold shadow-lg">
                Fondateur & Artiste
              </div>
            </div>
            
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-4">
              Simon Messela
            </h1>
            <p className="text-2xl md:text-3xl text-terracotta mb-6 font-light">
              (fifi Ribana)
            </p>
            <p className="text-xl text-white/90 max-w-4xl mx-auto leading-relaxed mb-8">
              Fondateur d'US EXPLO et artiste polyvalent, Simon Messela incarne l'esprit d'exploration musicale universelle. 
              Maître de tous les styles, de l'Afrobeat traditionnel au Bikutsi moderne, il crée des ponts entre les cultures 
              à travers sa musique innovante.
            </p>
            
            <div className="flex flex-wrap justify-center gap-4 mb-12">
              <span className="px-6 py-3 bg-terracotta/20 text-terracotta rounded-full font-semibold">
                🎵 Bikutsi
              </span>
              <span className="px-6 py-3 bg-sage/20 text-sage rounded-full font-semibold">
                🎸 Makossa
              </span>
              <span className="px-6 py-3 bg-gold/20 text-gold rounded-full font-semibold">
                🌍 World Fusion
              </span>
              <span className="px-6 py-3 bg-white/20 text-white rounded-full font-semibold">
                🎹 Afrobeat Electronic
              </span>
            </div>
          </div>

          {/* Vision Section */}
          <div className="bg-white/10 backdrop-blur-md rounded-3xl p-8 mb-16 border border-white/20">
            <h2 className="text-3xl font-bold text-white mb-6 text-center">Ma Vision</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-terracotta rounded-full flex items-center justify-center mx-auto mb-4">
                  <Globe className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Exploration Universelle</h3>
                <p className="text-white/80">Créer des ponts entre toutes les cultures musicales du monde</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-sage rounded-full flex items-center justify-center mx-auto mb-4">
                  <Music className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Innovation Créative</h3>
                <p className="text-white/80">Fusionner tradition et modernité dans chaque composition</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-gold rounded-full flex items-center justify-center mx-auto mb-4">
                  <Users className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Partage Culturel</h3>
                <p className="text-white/80">Permettre à chacun de découvrir la richesse musicale mondiale</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Artist Tracks Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-charcoal mb-6">
              Mes Créations
            </h2>
            <p className="text-xl text-charcoal/70 max-w-3xl mx-auto">
              Découvrez ma discographie variée, reflétant l'esprit d'US EXPLO : 
              une exploration sans limites des sonorités du monde
            </p>
          </div>

          {loading ? (
            <div className="text-center py-16">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-terracotta mx-auto mb-4"></div>
              <p className="text-charcoal/70">Chargement de mes créations...</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {artistTracks.map(track => (
                <TrackCard key={track.id} track={track} />
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Quote Section */}
      <section className="py-16 bg-gradient-to-r from-terracotta/20 to-sage/20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <blockquote className="text-3xl md:text-4xl font-bold text-charcoal mb-8 italic">
            "La musique n'a pas de frontières. Elle est le langage universel qui unit les cœurs et transcende les cultures."
          </blockquote>
          <p className="text-xl text-charcoal/80 font-semibold">
            - Simon Messela (fifi Ribana), Fondateur d'US EXPLO
          </p>
        </div>
      </section>

      <Footer />
      <AudioPlayer />
    </div>
  );
};

// Main App Component
function App() {
  return (
    <AuthProvider>
      <AudioProvider>
        <CartProvider>
          <div className="App">
            <BrowserRouter>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/simon-messela" element={<SimonMesselaPage />} />
                <Route path="/success" element={<SuccessPage />} />
                <Route path="/cancel" element={<Navigate to="/" />} />
              </Routes>
            </BrowserRouter>
          </div>
        </CartProvider>
      </AudioProvider>
    </AuthProvider>
  );
}

export default App;
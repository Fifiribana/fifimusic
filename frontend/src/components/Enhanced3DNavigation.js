import React, { useState, useEffect } from 'react';
import { 
  Music, 
  Globe, 
  Users, 
  ShoppingBag, 
  CreditCard, 
  Bot, 
  Heart, 
  Play, 
  Settings,
  Search,
  Menu,
  X,
  Star,
  Crown,
  Zap,
  Headphones,
  Mic2,
  Radio
} from 'lucide-react';
import { GlobalLanguageSelector } from './LanguageTranslator';

// Navigation 3D Ultra-Moderne
const Enhanced3DNavigation = ({ user, onLogin, onLogout }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [activeItem, setActiveItem] = useState('home');

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navigationItems = [
    { id: 'home', label: 'Accueil', href: '/', icon: Music, color: 'from-orange-400 to-red-500' },
    { id: 'explore', label: 'Explorer', href: '#explorer', icon: Globe, color: 'from-blue-400 to-purple-500' },
    { id: 'community', label: 'Communauté', href: '/community', icon: Users, color: 'from-green-400 to-blue-500' },
    { id: 'marketplace', label: 'Marketplace', href: '/marketplace', icon: ShoppingBag, color: 'from-purple-400 to-pink-500' },
    { id: 'subscriptions', label: 'Abonnements', href: '/subscriptions', icon: CreditCard, color: 'from-yellow-400 to-orange-500' },
    { id: 'ai', label: 'IA Assistant', href: '/ai', icon: Bot, color: 'from-cyan-400 to-blue-500' },
    { id: 'solidarity', label: 'Solidarité', href: '/solidarity', icon: Heart, color: 'from-red-400 to-pink-500' },
    { id: 'collections', label: 'Collections', href: '#collections', icon: Star, color: 'from-indigo-400 to-purple-500' }
  ];

  return (
    <>
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
        scrolled 
          ? 'bg-slate-900/95 backdrop-blur-xl border-b border-white/10 shadow-2xl' 
          : 'bg-transparent'
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            {/* Logo 3D */}
            <div className="flex items-center space-x-4">
              <div className="relative group">
                <div className="w-14 h-14 bg-gradient-to-br from-orange-400 via-red-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-xl transform group-hover:rotate-6 group-hover:scale-110 transition-all duration-500">
                  <Music className="w-7 h-7 text-white group-hover:animate-pulse" />
                </div>
                <div className="absolute -inset-2 bg-gradient-to-br from-orange-400/30 via-red-500/30 to-purple-600/30 rounded-2xl blur-lg opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              </div>
              
              <div>
                <h1 className="text-2xl font-black bg-gradient-to-r from-orange-400 via-red-500 to-purple-600 bg-clip-text text-transparent">
                  US EXPLO
                </h1>
                <p className="text-xs text-gray-300 font-semibold">Universal Sound Exploration</p>
              </div>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden lg:flex items-center space-x-1">
              {navigationItems.map((item) => (
                <a
                  key={item.id}
                  href={item.href}
                  className={`group relative px-4 py-3 rounded-xl transition-all duration-300 transform hover:scale-105 ${
                    activeItem === item.id 
                      ? 'bg-white/15 text-white scale-105' 
                      : 'text-gray-300 hover:text-white hover:bg-white/10'
                  }`}
                  onClick={() => setActiveItem(item.id)}
                >
                  <div className="flex items-center space-x-2">
                    <div className={`p-1.5 rounded-lg bg-gradient-to-r ${item.color} shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                      <item.icon className="w-4 h-4 text-white" />
                    </div>
                    <span className="font-semibold text-sm">{item.label}</span>
                  </div>
                  
                  {/* Hover Effect */}
                  <div className={`absolute inset-0 bg-gradient-to-r ${item.color} opacity-0 group-hover:opacity-10 rounded-xl transition-opacity duration-300`}></div>
                </a>
              ))}
            </div>

            {/* Right Side Actions */}
            <div className="flex items-center space-x-4">
              {/* Language Selector */}
              <GlobalLanguageSelector />
              
              {/* Search Bar 3D */}
              <div className="relative hidden md:block">
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    type="text"
                    placeholder="Rechercher la musique du monde..."
                    className="w-64 pl-12 pr-4 py-3 bg-white/10 backdrop-blur-sm border-2 border-white/20 rounded-2xl text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent focus:bg-white/15 transition-all duration-300"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        const query = e.target.value;
                        if (query.trim()) {
                          window.location.href = `/search?q=${encodeURIComponent(query)}`;
                        }
                      }
                    }}
                  />
                </div>
                <div className="absolute -inset-1 bg-gradient-to-r from-orange-400/20 via-red-500/20 to-purple-600/20 rounded-2xl blur opacity-0 hover:opacity-100 transition-opacity duration-500 pointer-events-none"></div>
              </div>

              {/* Donation Button 3D */}
              <a
                href="/donation"
                className="group relative px-6 py-3 font-bold rounded-2xl overflow-hidden transform hover:scale-110 transition-all duration-300"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-pink-500 via-red-500 to-orange-500 opacity-90"></div>
                <div className="absolute inset-0 bg-gradient-to-r from-pink-400 via-red-400 to-orange-400 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <div className="absolute inset-0 bg-black/20 transform translate-x-1 translate-y-1 rounded-2xl -z-10"></div>
                
                <span className="relative flex items-center space-x-2 text-white">
                  <Heart className="w-5 h-5 group-hover:scale-125 transition-transform duration-300" />
                  <span>Soutenir</span>
                </span>
              </a>

              {/* User Actions */}
              {user ? (
                <div className="flex items-center space-x-3">
                  <div className="relative group">
                    <div className="w-12 h-12 bg-gradient-to-r from-purple-400 to-pink-500 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                      <span className="text-white font-bold">
                        {user.username?.charAt(0)?.toUpperCase() || 'U'}
                      </span>
                    </div>
                    <div className="absolute -inset-1 bg-gradient-to-r from-purple-400/30 to-pink-500/30 rounded-xl blur opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  </div>
                  
                  <button
                    onClick={onLogout}
                    className="text-gray-300 hover:text-white transition-colors duration-300"
                  >
                    Déconnexion
                  </button>
                </div>
              ) : (
                <button
                  onClick={onLogin}
                  className="group relative px-6 py-3 font-semibold rounded-2xl border-2 border-white/30 hover:border-white/60 backdrop-blur-sm transition-all duration-300 transform hover:scale-105"
                >
                  <span className="text-white group-hover:text-gray-100">Connexion</span>
                </button>
              )}

              {/* Mobile Menu Button */}
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="lg:hidden p-3 rounded-xl bg-white/10 backdrop-blur-sm border border-white/20 text-white hover:bg-white/20 transition-all duration-300"
              >
                {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="lg:hidden absolute top-full left-0 right-0 bg-slate-900/98 backdrop-blur-xl border-b border-white/10 shadow-2xl">
            <div className="max-w-7xl mx-auto px-4 py-6">
              <div className="grid grid-cols-2 gap-4">
                {navigationItems.map((item) => (
                  <a
                    key={item.id}
                    href={item.href}
                    className="group flex items-center space-x-3 p-4 rounded-2xl bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 transition-all duration-300"
                    onClick={() => {
                      setActiveItem(item.id);
                      setIsMenuOpen(false);
                    }}
                  >
                    <div className={`p-2 rounded-xl bg-gradient-to-r ${item.color} shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                      <item.icon className="w-5 h-5 text-white" />
                    </div>
                    <span className="text-white font-semibold">{item.label}</span>
                  </a>
                ))}
              </div>
              
              {/* Mobile Search */}
              <div className="mt-6">
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    type="text"
                    placeholder="Rechercher..."
                    className="w-full pl-12 pr-4 py-4 bg-white/10 backdrop-blur-sm border-2 border-white/20 rounded-2xl text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent"
                  />
                </div>
              </div>
            </div>
          </div>
        )}
      </nav>

      {/* Floating Audio Controls */}
      <div className="fixed top-24 right-4 z-40 space-y-3">
        <button className="p-4 bg-gradient-to-r from-orange-500 to-red-500 rounded-full shadow-2xl text-white hover:scale-110 transition-all duration-300 group">
          <Headphones className="w-6 h-6 group-hover:animate-pulse" />
        </button>
        
        <button className="p-4 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full shadow-2xl text-white hover:scale-110 transition-all duration-300 group">
          <Mic2 className="w-6 h-6 group-hover:animate-pulse" />
        </button>
        
        <button className="p-4 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full shadow-2xl text-white hover:scale-110 transition-all duration-300 group">
          <Radio className="w-6 h-6 group-hover:animate-pulse" />
        </button>
      </div>
    </>
  );
};

export default Enhanced3DNavigation;
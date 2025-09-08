import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, Volume2, Download, Heart, Star, Sparkles, Music, Globe, Crown, Zap, Headphones } from 'lucide-react';

// Hero Section 3D Ultra-Modern pour US EXPLO
const Enhanced3DHero = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentBeat, setCurrentBeat] = useState(0);
  const [particles, setParticles] = useState([]);
  const heroRef = useRef(null);
  const audioVisualizerRef = useRef(null);

  useEffect(() => {
    // Créer des particules musicales animées
    const createParticles = () => {
      const newParticles = Array.from({ length: 50 }, (_, i) => ({
        id: i,
        x: Math.random() * 100,
        y: Math.random() * 100,
        size: Math.random() * 4 + 1,
        speed: Math.random() * 2 + 0.5,
        opacity: Math.random() * 0.8 + 0.2,
        rotation: Math.random() * 360,
        color: ['#FF6B35', '#F7931E', '#FFD700', '#32CD32', '#1E90FF', '#9370DB'][Math.floor(Math.random() * 6)]
      }));
      setParticles(newParticles);
    };

    createParticles();

    // Animation du beat musical
    const beatInterval = setInterval(() => {
      setCurrentBeat(prev => (prev + 1) % 4);
    }, 500);

    return () => clearInterval(beatInterval);
  }, []);

  // Données de visualisation audio simulée
  const audioData = Array.from({ length: 32 }, (_, i) => 
    Math.sin(currentBeat * 0.5 + i * 0.2) * (50 + Math.random() * 50)
  );

  return (
    <section className="relative min-h-screen overflow-hidden bg-gradient-to-br from-slate-900 via-purple-900 to-orange-900">
      {/* Background 3D Elements */}
      <div className="absolute inset-0">
        {/* Gradient Mesh */}
        <div className="absolute inset-0 bg-gradient-to-br from-orange-500/20 via-red-500/20 to-purple-600/20 animate-pulse"></div>
        
        {/* Geometric Shapes */}
        <div className="absolute top-20 left-20 w-32 h-32 bg-gradient-to-br from-orange-400 to-red-500 rounded-full opacity-20 animate-bounce transform rotate-12"></div>
        <div className="absolute top-40 right-32 w-24 h-24 bg-gradient-to-br from-purple-400 to-pink-500 transform rotate-45 opacity-25 animate-spin-slow"></div>
        <div className="absolute bottom-32 left-32 w-40 h-40 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-xl opacity-15 animate-pulse transform -rotate-12"></div>
        
        {/* Animated Particles */}
        {particles.map(particle => (
          <div
            key={particle.id}
            className="absolute w-2 h-2 rounded-full animate-pulse"
            style={{
              left: `${particle.x}%`,
              top: `${particle.y}%`,
              backgroundColor: particle.color,
              opacity: particle.opacity,
              transform: `rotate(${particle.rotation}deg) scale(${particle.size})`,
              animation: `float ${particle.speed}s infinite ease-in-out`
            }}
          />
        ))}
      </div>

      {/* Main Content */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          {/* 3D Logo & Title */}
          <div className="mb-12">
            <div className="inline-flex items-center space-x-4 mb-8">
              <div className="relative">
                <div className="w-20 h-20 bg-gradient-to-br from-orange-400 via-red-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-2xl transform rotate-3 hover:rotate-6 transition-transform duration-500">
                  <Music className="w-10 h-10 text-white animate-pulse" />
                </div>
                <div className="absolute -inset-2 bg-gradient-to-br from-orange-400/50 via-red-500/50 to-purple-600/50 rounded-2xl blur-lg opacity-75 animate-pulse"></div>
              </div>
              <div className="text-left">
                <h1 className="text-2xl font-bold bg-gradient-to-r from-orange-400 via-red-500 to-purple-600 bg-clip-text text-transparent">
                  US EXPLO
                </h1>
                <p className="text-sm text-gray-300 font-semibold">Universal Sound Exploration</p>
              </div>
            </div>

            {/* 3D Main Title */}
            <h1 className="text-6xl md:text-8xl lg:text-9xl font-black mb-8 relative">
              <span className="absolute inset-0 bg-gradient-to-br from-orange-600 via-red-600 to-purple-700 bg-clip-text text-transparent transform translate-x-2 translate-y-2 opacity-30">
                US EXPLO
              </span>
              <span className="absolute inset-0 bg-gradient-to-br from-orange-500 via-red-500 to-purple-600 bg-clip-text text-transparent transform translate-x-1 translate-y-1 opacity-60">
                US EXPLO
              </span>
              <span className="relative bg-gradient-to-br from-orange-400 via-red-400 to-purple-500 bg-clip-text text-transparent">
                US EXPLO
              </span>
              
              {/* 3D Glow Effect */}
              <div className="absolute inset-0 bg-gradient-to-br from-orange-400/20 via-red-400/20 to-purple-500/20 blur-3xl animate-pulse"></div>
            </h1>

            {/* 3D Subtitle */}
            <h2 className="text-3xl md:text-5xl lg:text-6xl font-bold mb-8 relative">
              <span className="absolute inset-0 text-gray-800 transform translate-x-1 translate-y-1">
                Universal Sound Exploration
              </span>
              <span className="relative bg-gradient-to-r from-yellow-300 via-orange-300 to-red-300 bg-clip-text text-transparent">
                Universal Sound Exploration
              </span>
            </h2>
          </div>

          {/* 3D Tagline */}
          <div className="mb-12">
            <h3 className="text-2xl md:text-4xl font-bold mb-6 relative">
              <span className="absolute inset-0 text-gray-700 transform translate-x-1 translate-y-1 opacity-50">
                🌍 Découvrez le Pouls de la Planète 🎵
              </span>
              <span className="relative bg-gradient-to-r from-blue-300 via-green-300 to-purple-300 bg-clip-text text-transparent">
                🌍 Découvrez le Pouls de la Planète 🎵
              </span>
            </h3>
            
            <p className="text-xl md:text-2xl text-gray-200 max-w-4xl mx-auto leading-relaxed mb-8">
              Explorez une carte interactive du <span className="font-bold text-yellow-300">patrimoine musical mondial</span>. 
              Écoutez, découvrez et achetez de la <span className="font-bold text-orange-300">musique authentique</span> de tous les continents 
              avec des <span className="font-bold text-red-300">aperçus audio HD</span>.
            </p>
          </div>

          {/* Audio Visualizer 3D */}
          <div className="mb-12 flex justify-center">
            <div className="relative">
              <div className="flex items-end space-x-1 h-24 bg-black/30 backdrop-blur-sm rounded-2xl p-4 border border-white/10">
                {audioData.map((height, index) => (
                  <div
                    key={index}
                    className="w-3 rounded-full transition-all duration-300"
                    style={{
                      height: `${Math.max(height, 10)}%`,
                      background: `linear-gradient(to top, 
                        ${index % 4 === 0 ? '#FF6B35' : 
                          index % 4 === 1 ? '#F7931E' : 
                          index % 4 === 2 ? '#FFD700' : '#32CD32'})`
                    }}
                  />
                ))}
              </div>
              <div className="absolute -inset-2 bg-gradient-to-r from-orange-500/30 via-red-500/30 to-purple-600/30 rounded-2xl blur opacity-75 animate-pulse"></div>
            </div>
          </div>

          {/* Interactive Stats 3D */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-12">
            {[
              { number: '50+', label: 'Pays', icon: Globe, color: 'from-blue-400 to-purple-500' },
              { number: '15+', label: 'Styles', icon: Music, color: 'from-green-400 to-blue-500' },
              { number: '24/7', label: 'Écoute', icon: Headphones, color: 'from-yellow-400 to-orange-500' },
              { number: '1000+', label: 'Pistes', icon: Star, color: 'from-red-400 to-pink-500' }
            ].map((stat, index) => (
              <div key={index} className="relative group">
                <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-500 transform hover:scale-110 hover:rotate-1">
                  <div className={`w-12 h-12 bg-gradient-to-r ${stat.color} rounded-xl flex items-center justify-center mx-auto mb-4 shadow-lg`}>
                    <stat.icon className="w-6 h-6 text-white" />
                  </div>
                  <div className="text-3xl font-black text-white mb-2 relative">
                    <span className="absolute inset-0 text-gray-600 transform translate-x-1 translate-y-1">
                      {stat.number}
                    </span>
                    <span className="relative">{stat.number}</span>
                  </div>
                  <div className="text-sm font-semibold text-gray-300">{stat.label}</div>
                </div>
                <div className={`absolute -inset-1 bg-gradient-to-r ${stat.color} rounded-2xl blur opacity-25 group-hover:opacity-50 transition-opacity duration-500`}></div>
              </div>
            ))}
          </div>

          {/* 3D Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-12">
            <button className="group relative px-10 py-5 font-bold text-xl rounded-2xl overflow-hidden transform hover:scale-110 transition-all duration-500">
              {/* Button Background */}
              <div className="absolute inset-0 bg-gradient-to-r from-orange-500 via-red-500 to-purple-600 opacity-90"></div>
              <div className="absolute inset-0 bg-gradient-to-r from-orange-400 via-red-400 to-purple-500 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              
              {/* 3D Shadow */}
              <div className="absolute inset-0 bg-black/30 transform translate-x-1 translate-y-1 rounded-2xl -z-10"></div>
              
              {/* Button Content */}
              <span className="relative flex items-center space-x-3 text-white">
                <Play className="w-6 h-6 group-hover:scale-125 transition-transform duration-300" />
                <span>Commencer l'Exploration</span>
                <Sparkles className="w-5 h-5 animate-pulse" />
              </span>
            </button>

            <button className="group relative px-10 py-5 font-bold text-xl rounded-2xl border-3 border-white/30 hover:border-white/60 backdrop-blur-sm transition-all duration-500 transform hover:scale-110">
              <span className="flex items-center space-x-3 text-white">
                <Crown className="w-6 h-6 text-yellow-300 group-hover:scale-125 transition-transform duration-300" />
                <span>Collections Sélectionnées</span>
                <Star className="w-5 h-5 text-yellow-300 animate-pulse" />
              </span>
            </button>
          </div>

          {/* Music Wave Animation */}
          <div className="flex justify-center space-x-1 opacity-30">
            {Array.from({ length: 50 }, (_, i) => (
              <div
                key={i}
                className="w-1 bg-gradient-to-t from-orange-500 to-purple-500 rounded-full animate-pulse"
                style={{
                  height: `${Math.random() * 40 + 10}px`,
                  animationDelay: `${i * 0.1}s`
                }}
              />
            ))}
          </div>
        </div>
      </div>

      {/* CSS personnalisé pour les animations */}
      <style jsx>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-20px) rotate(180deg); }
        }
        
        @keyframes spin-slow {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        
        .animate-spin-slow {
          animation: spin-slow 8s linear infinite;
        }
      `}</style>
    </section>
  );
};

export default Enhanced3DHero;
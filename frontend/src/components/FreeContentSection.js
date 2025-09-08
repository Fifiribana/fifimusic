import React, { useState, useEffect } from 'react';
import { Play, Pause, Lock, Crown, Star, Download, Eye, Clock, Users, Heart } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Section de contenu gratuit premium pour attirer les visiteurs
const FreeContentSection = ({ translations, useAudio }) => {
  const [freeContent, setFreeContent] = useState([]);
  const [premiumTeasers, setPremiumTeasers] = useState([]);
  const [playingId, setPlayingId] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Use audio hook if provided, otherwise create dummy functions
  const { playTrack, currentTrack, isPlaying } = useAudio || {
    playTrack: () => {},
    currentTrack: null,
    isPlaying: false
  };

  useEffect(() => {
    fetchFreeContent();
    fetchPremiumTeasers();
  }, []);

  const fetchFreeContent = async () => {
    try {
      const response = await axios.get(`${API}/tracks?limit=6&preview_available=true`);
      setFreeContent(response.data.slice(0, 6));
    } catch (error) {
      console.error('Error fetching free content:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchPremiumTeasers = async () => {
    try {
      const response = await axios.get(`${API}/tracks?premium=true&limit=4`);
      setPremiumTeasers(response.data.slice(0, 4));
    } catch (error) {
      console.error('Error fetching premium content:', error);
    }
  };

  const handlePlayPreview = (track) => {
    if (playingId === track.id) {
      setPlayingId(null);
      return;
    }
    
    setPlayingId(track.id);
    playTrack(track);
    
    // Limiter l'aperçu gratuit à 30 secondes
    setTimeout(() => {
      setPlayingId(null);
    }, 30000);
  };

  const t = (key) => translations[key] || key;

  if (loading) {
    return (
      <div className="py-20 bg-gradient-to-br from-charcoal/5 to-sage/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-terracotta mx-auto"></div>
            <p className="mt-4 text-charcoal/60">{t('loading_content')}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <section className="py-20 bg-gradient-to-br from-charcoal/5 to-sage/10 relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute top-20 left-20 text-8xl">🎵</div>
        <div className="absolute top-40 right-32 text-6xl">🎶</div>
        <div className="absolute bottom-32 left-32 text-7xl">🎼</div>
        <div className="absolute bottom-20 right-20 text-5xl">🎤</div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Header Section */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center bg-gradient-to-r from-terracotta/20 to-gold/20 backdrop-blur-sm border border-terracotta/30 rounded-full px-8 py-3 mb-6">
            <Crown className="w-6 h-6 text-gold mr-3" />
            <span className="text-gold font-bold text-lg">{t('free_discovery')}</span>
          </div>
          
          <h2 className="text-5xl md:text-6xl font-bold text-charcoal mb-6 bg-gradient-to-r from-charcoal via-terracotta to-charcoal bg-clip-text text-transparent">
            {t('discover_world_music_free')}
          </h2>
          
          <p className="text-xl md:text-2xl text-charcoal/80 mb-4 max-w-4xl mx-auto leading-relaxed">
            🎧 {t('free_previews_description')} 🎧
          </p>
          
          <p className="text-lg text-charcoal/60 max-w-3xl mx-auto">
            {t('no_registration_needed')}
          </p>
        </div>

        {/* Stats Bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16">
          <div className="text-center p-6 bg-white/50 backdrop-blur-sm rounded-2xl border border-white/20">
            <div className="text-3xl font-bold text-terracotta mb-2">200+</div>
            <div className="text-sm text-charcoal/70">{t('free_tracks')}</div>
          </div>
          <div className="text-center p-6 bg-white/50 backdrop-blur-sm rounded-2xl border border-white/20">
            <div className="text-3xl font-bold text-sage mb-2">50+</div>
            <div className="text-sm text-charcoal/70">{t('countries')}</div>
          </div>
          <div className="text-center p-6 bg-white/50 backdrop-blur-sm rounded-2xl border border-white/20">
            <div className="text-3xl font-bold text-gold mb-2">15+</div>
            <div className="text-sm text-charcoal/70">{t('music_styles')}</div>
          </div>
          <div className="text-center p-6 bg-white/50 backdrop-blur-sm rounded-2xl border border-white/20">
            <div className="text-3xl font-bold text-purple-600 mb-2">24/7</div>
            <div className="text-sm text-charcoal/70">{t('access')}</div>
          </div>
        </div>

        {/* Free Content Grid */}
        <div className="mb-20">
          <div className="flex items-center justify-between mb-8">
            <h3 className="text-3xl font-bold text-charcoal flex items-center">
              <Play className="w-8 h-8 text-terracotta mr-3" />
              {t('listen_now_free')}
            </h3>
            <div className="flex items-center space-x-2 text-sage">
              <Clock className="w-5 h-5" />
              <span className="text-sm font-medium">{t('30_second_previews')}</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {freeContent.map((track, index) => (
              <div key={track.id} className="group bg-white rounded-3xl shadow-lg hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2 overflow-hidden border-2 border-transparent hover:border-terracotta/20">
                <div className="relative h-48 overflow-hidden">
                  <img 
                    src={track.artwork_url} 
                    alt={track.title}
                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent">
                    {/* Free Badge */}
                    <div className="absolute top-4 left-4">
                      <span className="px-3 py-1 bg-green-500 text-white text-xs font-bold rounded-full border-2 border-white">
                        {t('free')} ✨
                      </span>
                    </div>

                    {/* Play Button */}
                    <button
                      onClick={() => handlePlayPreview(track)}
                      className={`absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 p-4 rounded-full transition-all duration-300 backdrop-blur-sm ${
                        playingId === track.id 
                          ? 'bg-gold/90 scale-110 shadow-lg shadow-gold/50' 
                          : 'bg-terracotta/90 hover:bg-terracotta hover:scale-110 shadow-lg'
                      }`}
                    >
                      {playingId === track.id ? 
                        <Pause className="w-6 h-6 text-white" /> : 
                        <Play className="w-6 h-6 text-white ml-1" />
                      }
                    </button>

                    {/* Preview Timer */}
                    {playingId === track.id && (
                      <div className="absolute bottom-4 left-4 right-4">
                        <div className="bg-black/50 backdrop-blur-sm rounded-full p-2">
                          <div className="flex items-center space-x-2 text-white text-xs">
                            <Clock className="w-3 h-3" />
                            <span>{t('preview_playing')}</span>
                            <div className="flex-1 bg-white/20 rounded-full h-1">
                              <div className="bg-gold h-1 rounded-full animate-pulse"></div>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="p-6">
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex-1">
                      <h4 className="text-xl font-bold text-charcoal mb-1 line-clamp-1">{track.title}</h4>
                      <p className="text-sage font-semibold">{track.artist}</p>
                    </div>
                    <div className="text-right ml-4">
                      <span className="text-sm text-green-600 font-bold">{t('free')}</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2 mb-4">
                    <span className="px-3 py-1 bg-sage/15 text-sage rounded-full text-sm font-medium">
                      {track.region}
                    </span>
                    <span className="px-3 py-1 bg-terracotta/15 text-terracotta rounded-full text-sm font-medium">
                      {track.style}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-1 text-charcoal/60">
                        <Eye className="w-4 h-4" />
                        <span className="text-sm">{Math.floor(Math.random() * 1000 + 100)}</span>
                      </div>
                      <div className="flex items-center space-x-1 text-charcoal/60">
                        <Heart className="w-4 h-4" />
                        <span className="text-sm">{track.likes}</span>
                      </div>
                    </div>
                    <div className="text-xs text-green-600 font-semibold">
                      30s {t('preview_available')}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Premium Teaser Section */}
        <div className="bg-gradient-to-r from-purple-900 via-purple-800 to-indigo-900 rounded-3xl p-8 md:p-12 text-white">
          <div className="text-center mb-12">
            <div className="inline-flex items-center bg-gold/20 backdrop-blur-sm border border-gold/30 rounded-full px-8 py-3 mb-6">
              <Crown className="w-6 h-6 text-gold mr-3" />
              <span className="text-gold font-bold text-lg">{t('premium_content')}</span>
            </div>
            
            <h3 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-white via-gold to-white bg-clip-text text-transparent">
              {t('unlock_full_experience')}
            </h3>
            
            <p className="text-xl text-white/90 mb-8 max-w-3xl mx-auto">
              {t('premium_benefits_description')}
            </p>
          </div>

          {/* Premium Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            <div className="text-center p-6 bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20">
              <Download className="w-8 h-8 text-gold mx-auto mb-3" />
              <h4 className="font-bold mb-2">{t('unlimited_downloads')}</h4>
              <p className="text-sm text-white/80">{t('hd_quality_music')}</p>
            </div>
            <div className="text-center p-6 bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20">
              <Users className="w-8 h-8 text-gold mx-auto mb-3" />
              <h4 className="font-bold mb-2">{t('exclusive_community')}</h4>
              <p className="text-sm text-white/80">{t('connect_artists')}</p>
            </div>
            <div className="text-center p-6 bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20">
              <Star className="w-8 h-8 text-gold mx-auto mb-3" />
              <h4 className="font-bold mb-2">{t('premium_collections')}</h4>
              <p className="text-sm text-white/80">{t('curated_playlists')}</p>
            </div>
            <div className="text-center p-6 bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20">
              <Lock className="w-8 h-8 text-gold mx-auto mb-3" />
              <h4 className="font-bold mb-2">{t('ad_free_experience')}</h4>
              <p className="text-sm text-white/80">{t('pure_music_enjoyment')}</p>
            </div>
          </div>

          {/* Premium Tracks Teaser */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
            {premiumTeasers.slice(0, 2).map((track) => (
              <div key={track.id} className="relative bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20 overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-r from-gold/20 to-purple/20 opacity-50"></div>
                <div className="relative z-10">
                  <div className="flex items-center space-x-4 mb-4">
                    <img 
                      src={track.artwork_url} 
                      alt={track.title}
                      className="w-16 h-16 rounded-xl object-cover"
                    />
                    <div className="flex-1">
                      <h4 className="font-bold text-lg">{track.title}</h4>
                      <p className="text-white/80">{track.artist}</p>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className="px-2 py-1 bg-gold/20 text-gold text-xs rounded-full">
                          {track.region}
                        </span>
                        <Crown className="w-4 h-4 text-gold" />
                      </div>
                    </div>
                    <div className="text-center">
                      <Lock className="w-8 h-8 text-gold mx-auto mb-1" />
                      <span className="text-xs text-gold font-bold">{t('premium')}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* CTA Buttons */}
          <div className="text-center">
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <a
                href="/subscriptions"
                className="group px-10 py-5 bg-gradient-to-r from-gold to-yellow-400 hover:from-yellow-400 hover:to-gold text-charcoal font-bold rounded-full transition-all transform hover:scale-110 shadow-2xl border-2 border-white/20 hover:border-white/40 backdrop-blur-sm"
              >
                <span className="flex items-center">
                  <Crown className="w-5 h-5 mr-2" />
                  {t('start_premium_trial')}
                </span>
              </a>
              
              <a
                href="/collections"
                className="group px-10 py-5 border-2 border-white/40 text-white hover:bg-white/15 font-bold rounded-full transition-all backdrop-blur-md hover:scale-105 shadow-lg hover:shadow-xl"
              >
                <span className="flex items-center">
                  <Star className="w-5 h-5 mr-2" />
                  {t('explore_collections')}
                </span>
              </a>
            </div>
            
            <p className="text-sm text-white/60 mt-6">
              {t('cancel_anytime')} • {t('first_week_free')}
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default FreeContentSection;
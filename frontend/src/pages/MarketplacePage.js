import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  ShoppingBag, 
  Plus, 
  Search, 
  Filter,
  Play,
  Pause,
  DollarSign,
  Tag,
  Star,
  Download,
  Heart,
  Music,
  TrendingUp,
  Eye,
  Edit,
  Trash2,
  AlertCircle
} from 'lucide-react';
import { useToast } from '../components/Toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MarketplacePage = () => {
  const { toast } = useToast();
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);
  
  // Marketplace states
  const [activeTab, setActiveTab] = useState('browse'); // browse, sell, my-listings
  const [listings, setListings] = useState([]);
  const [myListings, setMyListings] = useState([]);
  const [myTracks, setMyTracks] = useState([]);
  const [userSubscription, setUserSubscription] = useState(null);
  const [currentAudio, setCurrentAudio] = useState(null);
  const [playingTrack, setPlayingTrack] = useState(null);
  
  // Filters
  const [filters, setFilters] = useState({
    genre: '',
    price_min: '',
    price_max: '',
    listing_type: ''
  });
  
  // Forms
  const [showListingForm, setShowListingForm] = useState(false);
  const [listingForm, setListingForm] = useState({
    track_id: '',
    listing_type: 'sale',
    sale_price: '',
    license_price: '',
    license_terms: '',
    royalty_percentage: 0,
    is_exclusive: false
  });

  useEffect(() => {
    const checkAuth = async () => {
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const response = await axios.get(`${API}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setUser(response.data);
        
        // Load user subscription
        await loadUserSubscription();
        
        // Load data based on active tab
        await loadData();
        
      } catch (error) {
        console.error('Auth check failed:', error);
        localStorage.removeItem('token');
        setToken(null);
      }
      setLoading(false);
    };

    checkAuth();
  }, [token]);

  useEffect(() => {
    if (user) {
      loadData();
    }
  }, [activeTab, filters]);

  const loadUserSubscription = async () => {
    try {
      const response = await axios.get(`${API}/subscriptions/my-subscription`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUserSubscription(response.data);
    } catch (error) {
      setUserSubscription(null);
    }
  };

  const loadData = async () => {
    try {
      switch (activeTab) {
        case 'browse':
          await loadMarketplace();
          break;
        case 'sell':
          await loadMyTracks();
          break;
        case 'my-listings':
          await loadMyListings();
          break;
      }
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const loadMarketplace = async () => {
    try {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
      
      const response = await axios.get(`${API}/marketplace/listings?${params}`);
      setListings(response.data);
    } catch (error) {
      toast.error('Erreur lors du chargement de la marketplace');
    }
  };

  const loadMyTracks = async () => {
    try {
      const response = await axios.get(`${API}/admin/my-tracks`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMyTracks(response.data);
    } catch (error) {
      toast.error('Erreur lors du chargement de vos pistes');
    }
  };

  const loadMyListings = async () => {
    try {
      const response = await axios.get(`${API}/marketplace/my-listings`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMyListings(response.data);
    } catch (error) {
      toast.error('Erreur lors du chargement de vos annonces');
    }
  };

  const handleCreateListing = async (e) => {
    e.preventDefault();
    
    if (!listingForm.track_id) {
      toast.error('Veuillez sélectionner une piste');
      return;
    }
    
    if (listingForm.listing_type === 'sale' && !listingForm.sale_price) {
      toast.error('Veuillez saisir un prix de vente');
      return;
    }
    
    if (listingForm.listing_type === 'license' && !listingForm.license_price) {
      toast.error('Veuillez saisir un prix de licence');
      return;
    }

    try {
      const data = { ...listingForm };
      if (data.sale_price) data.sale_price = parseFloat(data.sale_price);
      if (data.license_price) data.license_price = parseFloat(data.license_price);
      
      await axios.post(`${API}/marketplace/list`, data, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success('Piste mise en vente avec succès !');
      setListingForm({
        track_id: '',
        listing_type: 'sale',
        sale_price: '',
        license_price: '',
        license_terms: '',
        royalty_percentage: 0,
        is_exclusive: false
      });
      setShowListingForm(false);
      setActiveTab('my-listings');
      await loadMyListings();
    } catch (error) {
      const message = error.response?.data?.detail || 'Erreur lors de la mise en vente';
      toast.error(message);
    }
  };

  const handlePlayPause = async (track) => {
    if (playingTrack === track.id) {
      if (currentAudio) {
        currentAudio.pause();
        setPlayingTrack(null);
      }
      return;
    }

    if (currentAudio) {
      currentAudio.pause();
    }

    try {
      const audio = new Audio(track.preview_url || track.audio_url);
      audio.play();
      setCurrentAudio(audio);
      setPlayingTrack(track.id);
      
      audio.onended = () => {
        setPlayingTrack(null);
        setCurrentAudio(null);
      };
    } catch (error) {
      toast.error('Erreur lors de la lecture');
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR'
    }).format(price);
  };

  const canSellMusic = () => {
    return userSubscription?.plan?.can_sell_music || false;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-charcoal to-sage/20 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gold"></div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-charcoal to-sage/20 flex items-center justify-center">
        <div className="bg-white rounded-2xl p-8 text-center max-w-md">
          <ShoppingBag className="w-16 h-16 text-terracotta mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-charcoal mb-4">Marketplace US EXPLO</h2>
          <p className="text-charcoal/70 mb-6">
            Connectez-vous pour découvrir et vendre de la musique sur notre marketplace mondiale !
          </p>
          <button 
            onClick={() => window.location.href = '/'}
            className="bg-gradient-to-r from-terracotta to-gold text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg transition-all"
          >
            Se Connecter
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-charcoal via-charcoal/95 to-sage/20">
      {/* Header */}
      <div className="bg-gradient-to-r from-charcoal to-sage/30 text-white p-6">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2">
                🛒 Marketplace Musicale
              </h1>
              <p className="text-xl text-white/80">
                Découvrez, achetez et vendez de la musique authentique du monde entier
              </p>
            </div>
            {userSubscription && (
              <div className="text-right">
                <p className="text-gold font-semibold">Plan: {userSubscription.plan?.name}</p>
                {canSellMusic() && (
                  <p className="text-green-400 text-sm">✓ Vente autorisée</p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white/10 backdrop-blur-sm border-b border-white/20">
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex space-x-8">
            {[
              { id: 'browse', label: 'Parcourir', icon: Search },
              { id: 'sell', label: 'Vendre', icon: Plus },
              { id: 'my-listings', label: 'Mes Annonces', icon: TrendingUp }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-2 border-b-2 transition-colors ${
                  activeTab === tab.id 
                    ? 'border-gold text-gold' 
                    : 'border-transparent text-white/70 hover:text-white'
                }`}
              >
                <tab.icon className="w-5 h-5" />
                <span className="font-medium">{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Browse Tab */}
        {activeTab === 'browse' && (
          <div className="space-y-6">
            {/* Filters */}
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
                <Filter className="w-6 h-6" />
                <span>Filtres de recherche</span>
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-white/70 text-sm mb-2">Genre</label>
                  <input
                    type="text"
                    placeholder="Ex: Bikutsi, Afrobeat..."
                    value={filters.genre}
                    onChange={(e) => setFilters({ ...filters, genre: e.target.value })}
                    className="w-full px-3 py-2 bg-white/20 border border-white/30 rounded-lg text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-gold"
                  />
                </div>
                
                <div>
                  <label className="block text-white/70 text-sm mb-2">Prix min (€)</label>
                  <input
                    type="number"
                    placeholder="0"
                    value={filters.price_min}
                    onChange={(e) => setFilters({ ...filters, price_min: e.target.value })}
                    className="w-full px-3 py-2 bg-white/20 border border-white/30 rounded-lg text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-gold"
                  />
                </div>
                
                <div>
                  <label className="block text-white/70 text-sm mb-2">Prix max (€)</label>
                  <input
                    type="number"
                    placeholder="100"
                    value={filters.price_max}
                    onChange={(e) => setFilters({ ...filters, price_max: e.target.value })}
                    className="w-full px-3 py-2 bg-white/20 border border-white/30 rounded-lg text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-gold"
                  />
                </div>
                
                <div>
                  <label className="block text-white/70 text-sm mb-2">Type</label>
                  <select
                    value={filters.listing_type}
                    onChange={(e) => setFilters({ ...filters, listing_type: e.target.value })}
                    className="w-full px-3 py-2 bg-white/20 border border-white/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-gold"
                  >
                    <option value="">Tous types</option>
                    <option value="sale">Vente</option>
                    <option value="license">Licence</option>
                    <option value="both">Vente + Licence</option>
                  </select>
                </div>
              </div>
              
              <button
                onClick={loadMarketplace}
                className="mt-4 bg-gradient-to-r from-terracotta to-gold text-white px-6 py-2 rounded-xl font-semibold hover:shadow-lg transition-all flex items-center space-x-2"
              >
                <Search className="w-4 h-4" />
                <span>Rechercher</span>
              </button>
            </div>

            {/* Marketplace Listings */}
            {listings.length === 0 ? (
              <div className="text-center py-12">
                <ShoppingBag className="w-16 h-16 text-white/40 mx-auto mb-4" />
                <p className="text-white/60 text-lg">Aucune piste trouvée...</p>
                <p className="text-white/40">Essayez d'ajuster vos filtres de recherche</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {listings.map(listing => (
                  <div key={listing.id} className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20 hover:bg-white/15 transition-colors">
                    <div className="relative mb-4">
                      <img
                        src={listing.track?.artwork_url || '/placeholder-music.jpg'}
                        alt={listing.track?.title}
                        className="w-full h-40 object-cover rounded-xl"
                      />
                      <button
                        onClick={() => handlePlayPause(listing.track)}
                        className="absolute inset-0 flex items-center justify-center bg-black/40 rounded-xl opacity-0 hover:opacity-100 transition-opacity"
                      >
                        {playingTrack === listing.track?.id ? (
                          <Pause className="w-12 h-12 text-white" />
                        ) : (
                          <Play className="w-12 h-12 text-white" />
                        )}
                      </button>
                    </div>
                    
                    <div className="space-y-3">
                      <div>
                        <h3 className="text-lg font-semibold text-white">{listing.track?.title}</h3>
                        <p className="text-white/60">par {listing.seller?.stage_name || listing.seller?.username}</p>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <span className="px-2 py-1 bg-terracotta/30 text-terracotta text-xs rounded-full">
                          {listing.track?.style}
                        </span>
                        <span className="px-2 py-1 bg-sage/30 text-sage text-xs rounded-full">
                          {listing.track?.region}
                        </span>
                      </div>
                      
                      <div className="space-y-2">
                        {listing.listing_type === 'sale' || listing.listing_type === 'both' ? (
                          <div className="flex items-center justify-between">
                            <span className="text-white/70">Achat:</span>
                            <span className="text-gold font-semibold">{formatPrice(listing.sale_price)}</span>
                          </div>
                        ) : null}
                        
                        {listing.listing_type === 'license' || listing.listing_type === 'both' ? (
                          <div className="flex items-center justify-between">
                            <span className="text-white/70">Licence:</span>
                            <span className="text-terracotta font-semibold">{formatPrice(listing.license_price)}</span>
                          </div>
                        ) : null}
                        
                        {listing.is_exclusive && (
                          <div className="flex items-center space-x-1 text-gold text-sm">
                            <Star className="w-4 h-4" />
                            <span>Exclusif</span>
                          </div>
                        )}
                      </div>
                      
                      <div className="flex space-x-2">
                        <button className="flex-1 bg-gradient-to-r from-terracotta to-gold text-white py-2 rounded-lg font-semibold hover:shadow-lg transition-all flex items-center justify-center space-x-2">
                          <ShoppingBag className="w-4 h-4" />
                          <span>Acheter</span>
                        </button>
                        <button className="bg-white/20 text-white p-2 rounded-lg hover:bg-white/30 transition-colors">
                          <Heart className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Sell Tab */}
        {activeTab === 'sell' && (
          <div className="space-y-6">
            {!canSellMusic() ? (
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20 text-center">
                <AlertCircle className="w-16 h-16 text-terracotta mx-auto mb-4" />
                <h3 className="text-2xl font-semibold text-white mb-4">Abonnement requis</h3>
                <p className="text-white/70 mb-6">
                  Vous devez avoir un abonnement Pro ou Premium pour vendre votre musique sur la marketplace.
                </p>
                <button
                  onClick={() => window.location.href = '/subscriptions'}
                  className="bg-gradient-to-r from-terracotta to-gold text-white px-8 py-3 rounded-xl font-semibold hover:shadow-lg transition-all"
                >
                  Voir les Plans d'Abonnement
                </button>
              </div>
            ) : (
              <>
                {/* Add Listing Button */}
                <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
                  <button
                    onClick={() => setShowListingForm(!showListingForm)}
                    className="w-full bg-gradient-to-r from-terracotta to-gold text-white py-4 rounded-xl font-semibold hover:shadow-lg transition-all flex items-center justify-center space-x-2"
                  >
                    <Plus className="w-5 h-5" />
                    <span>Mettre une piste en vente</span>
                  </button>
                </div>

                {/* Listing Form */}
                {showListingForm && (
                  <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
                    <h3 className="text-xl font-semibold text-white mb-6">Créer une annonce</h3>
                    
                    <form onSubmit={handleCreateListing} className="space-y-4">
                      <div>
                        <label className="block text-white/70 text-sm mb-2">Sélectionner une piste *</label>
                        <select
                          value={listingForm.track_id}
                          onChange={(e) => setListingForm({ ...listingForm, track_id: e.target.value })}
                          className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-gold"
                          required
                        >
                          <option value="">Choisir une piste...</option>
                          {myTracks.map(track => (
                            <option key={track.id} value={track.id}>
                              {track.title} - {track.style}
                            </option>
                          ))}
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-white/70 text-sm mb-2">Type d'annonce</label>
                        <select
                          value={listingForm.listing_type}
                          onChange={(e) => setListingForm({ ...listingForm, listing_type: e.target.value })}
                          className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-gold"
                        >
                          <option value="sale">Vente uniquement</option>
                          <option value="license">Licence uniquement</option>
                          <option value="both">Vente + Licence</option>
                        </select>
                      </div>
                      
                      {(listingForm.listing_type === 'sale' || listingForm.listing_type === 'both') && (
                        <div>
                          <label className="block text-white/70 text-sm mb-2">Prix de vente (€) *</label>
                          <input
                            type="number"
                            step="0.01"
                            min="0.99"
                            value={listingForm.sale_price}
                            onChange={(e) => setListingForm({ ...listingForm, sale_price: e.target.value })}
                            className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-xl text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-gold"
                            placeholder="Ex: 4.99"
                          />
                        </div>
                      )}
                      
                      {(listingForm.listing_type === 'license' || listingForm.listing_type === 'both') && (
                        <div className="space-y-4">
                          <div>
                            <label className="block text-white/70 text-sm mb-2">Prix de licence (€) *</label>
                            <input
                              type="number"
                              step="0.01"
                              min="0.99"
                              value={listingForm.license_price}
                              onChange={(e) => setListingForm({ ...listingForm, license_price: e.target.value })}
                              className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-xl text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-gold"
                              placeholder="Ex: 19.99"
                            />
                          </div>
                          
                          <div>
                            <label className="block text-white/70 text-sm mb-2">Conditions de licence</label>
                            <select
                              value={listingForm.license_terms}
                              onChange={(e) => setListingForm({ ...listingForm, license_terms: e.target.value })}
                              className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-gold"
                            >
                              <option value="">Sélectionner...</option>
                              <option value="commercial">Usage commercial</option>
                              <option value="non-commercial">Usage non-commercial</option>
                              <option value="sync">Synchronisation audiovisuelle</option>
                              <option value="broadcast">Diffusion radio/TV</option>
                            </select>
                          </div>
                          
                          <div>
                            <label className="block text-white/70 text-sm mb-2">Royalties (%)</label>
                            <input
                              type="number"
                              step="0.1"
                              min="0"
                              max="50"
                              value={listingForm.royalty_percentage}
                              onChange={(e) => setListingForm({ ...listingForm, royalty_percentage: parseFloat(e.target.value) || 0 })}
                              className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-xl text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-gold"
                              placeholder="Ex: 5.0"
                            />
                          </div>
                        </div>
                      )}
                      
                      <div className="flex items-center space-x-3">
                        <input
                          type="checkbox"
                          id="exclusive"
                          checked={listingForm.is_exclusive}
                          onChange={(e) => setListingForm({ ...listingForm, is_exclusive: e.target.checked })}
                          className="w-4 h-4 text-gold bg-white/20 border-white/30 rounded focus:ring-gold focus:ring-2"
                        />
                        <label htmlFor="exclusive" className="text-white/70">
                          Vente exclusive (ne peut être vendue qu'une fois)
                        </label>
                      </div>
                      
                      <div className="flex space-x-4">
                        <button
                          type="submit"
                          className="bg-gradient-to-r from-terracotta to-gold text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg transition-all flex items-center space-x-2"
                        >
                          <Tag className="w-4 h-4" />
                          <span>Publier l'annonce</span>
                        </button>
                        <button
                          type="button"
                          onClick={() => setShowListingForm(false)}
                          className="bg-white/20 text-white px-6 py-3 rounded-xl font-semibold hover:bg-white/30 transition-colors"
                        >
                          Annuler
                        </button>
                      </div>
                    </form>
                  </div>
                )}

                {/* My Tracks */}
                {myTracks.length === 0 ? (
                  <div className="text-center py-12">
                    <Music className="w-16 h-16 text-white/40 mx-auto mb-4" />
                    <p className="text-white/60 text-lg">Aucune piste disponible</p>
                    <p className="text-white/40">Uploadez d'abord vos pistes dans la section admin</p>
                  </div>
                ) : (
                  <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
                    <h3 className="text-xl font-semibold text-white mb-6">Vos pistes disponibles</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {myTracks.map(track => (
                        <div key={track.id} className="bg-white/10 rounded-xl p-4 border border-white/20">
                          <h4 className="font-semibold text-white">{track.title}</h4>
                          <p className="text-white/60 text-sm">{track.style} • {track.region}</p>
                          <div className="mt-2 flex items-center space-x-2">
                            <button
                              onClick={() => handlePlayPause(track)}
                              className="bg-gold/20 text-gold p-2 rounded-lg hover:bg-gold/30 transition-colors"
                            >
                              {playingTrack === track.id ? (
                                <Pause className="w-4 h-4" />
                              ) : (
                                <Play className="w-4 h-4" />
                              )}
                            </button>
                            <span className="text-white/60 text-sm">{Math.floor(track.duration / 60)}:{(track.duration % 60).toString().padStart(2, '0')}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* My Listings Tab */}
        {activeTab === 'my-listings' && (
          <div className="space-y-6">
            {myListings.length === 0 ? (
              <div className="text-center py-12">
                <TrendingUp className="w-16 h-16 text-white/40 mx-auto mb-4" />
                <p className="text-white/60 text-lg">Aucune annonce pour le moment</p>
                <p className="text-white/40">Créez votre première annonce pour commencer à vendre</p>
              </div>
            ) : (
              <div className="space-y-4">
                {myListings.map(listing => (
                  <div key={listing.id} className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <img
                          src={listing.track?.artwork_url || '/placeholder-music.jpg'}
                          alt={listing.track?.title}
                          className="w-16 h-16 object-cover rounded-xl"
                        />
                        <div>
                          <h3 className="text-lg font-semibold text-white">{listing.track?.title}</h3>
                          <p className="text-white/60">{listing.track?.style}</p>
                          <div className="flex items-center space-x-4 mt-1">
                            {listing.sale_price && (
                              <span className="text-gold">Vente: {formatPrice(listing.sale_price)}</span>
                            )}
                            {listing.license_price && (
                              <span className="text-terracotta">Licence: {formatPrice(listing.license_price)}</span>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                          listing.status === 'active' 
                            ? 'bg-green-500/20 text-green-400' 
                            : 'bg-red-500/20 text-red-400'
                        }`}>
                          {listing.status === 'active' ? 'Actif' : 'Inactif'}
                        </span>
                        
                        <button className="bg-white/20 text-white p-2 rounded-lg hover:bg-white/30 transition-colors">
                          <Edit className="w-4 h-4" />
                        </button>
                        
                        <button className="bg-red-500/20 text-red-400 p-2 rounded-lg hover:bg-red-500/30 transition-colors">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MarketplacePage;
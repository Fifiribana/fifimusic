import React, { useState, useEffect } from 'react';
import { 
  Heart, 
  Youtube, 
  CreditCard, 
  DollarSign, 
  Banknote, 
  Globe,
  Star,
  Music,
  Users,
  Headphones,
  Download,
  Sparkles,
  Gift,
  Coffee,
  ArrowRight,
  Check,
  Crown,
  Shield,
  Zap
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Page de donation pour soutenir US EXPLO et YouTube gratuit
const DonationPage = () => {
  const [selectedAmount, setSelectedAmount] = useState(25);
  const [customAmount, setCustomAmount] = useState('');
  const [donationType, setDonationType] = useState('monthly');
  const [paymentMethod, setPaymentMethod] = useState('stripe');
  const [donorInfo, setDonorInfo] = useState({
    name: '',
    email: '',
    message: '',
    isAnonymous: false
  });
  const [loading, setLoading] = useState(false);
  const [showThankYou, setShowThankYou] = useState(false);
  const [stats, setStats] = useState({
    totalDonated: 45678,
    monthlyDonors: 892,
    ytChannelViews: 125000,
    supportedArtists: 1250
  });

  // Predefined donation amounts
  const donationAmounts = [
    { amount: 5, label: 'Un café ☕', description: 'Aide à payer les frais de serveur' },
    { amount: 15, label: 'Streaming ✨', description: 'Soutient 1 heure de streaming gratuit' },
    { amount: 25, label: 'Populaire 🌟', description: 'Maintient la plateforme 1 jour' },
    { amount: 50, label: 'Généreux 💎', description: 'Permet d\'ajouter 10 nouvelles pistes' },
    { amount: 100, label: 'Champion 🏆', description: 'Soutient un artiste émergent' },
    { amount: 250, label: 'Mécène 👑', description: 'Finance une collection complète' }
  ];

  useEffect(() => {
    fetchDonationStats();
  }, []);

  const fetchDonationStats = async () => {
    try {
      // Simuler la récupération des statistiques
      // Dans une vraie app, ceci viendrait de l'API
      setStats({
        totalDonated: Math.floor(Math.random() * 50000) + 45000,
        monthlyDonors: Math.floor(Math.random() * 100) + 850,
        ytChannelViews: Math.floor(Math.random() * 25000) + 120000,
        supportedArtists: Math.floor(Math.random() * 250) + 1200
      });
    } catch (error) {
      console.error('Error fetching donation stats:', error);
    }
  };

  const handleDonation = async () => {
    setLoading(true);
    
    try {
      const donationAmount = customAmount ? parseFloat(customAmount) : selectedAmount;
      
      if (donationAmount < 1) {
        alert('Le montant minimum de donation est de 1€');
        return;
      }

      // Prepare donation data
      const donationData = {
        amount: donationAmount,
        currency: 'EUR',
        type: donationType,
        payment_method: paymentMethod,
        donor_name: donorInfo.isAnonymous ? 'Anonyme' : donorInfo.name,
        donor_email: donorInfo.email,
        message: donorInfo.message,
        is_anonymous: donorInfo.isAnonymous,
        purpose: 'youtube_maintenance'
      };

      // Create Stripe checkout session
      const response = await axios.post(`${API}/create-donation-session`, donationData);
      
      if (response.data.checkout_url) {
        // Redirect to Stripe checkout
        window.location.href = response.data.checkout_url;
      } else {
        throw new Error('Failed to create checkout session');
      }

    } catch (error) {
      console.error('Donation error:', error);
      alert('Une erreur est survenue lors du traitement de votre donation. Veuillez réessayer.');
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num) => {
    return new Intl.NumberFormat('fr-FR').format(num);
  };

  if (showThankYou) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-terracotta via-gold to-sage flex items-center justify-center p-4">
        <div className="max-w-2xl mx-auto text-center bg-white rounded-3xl shadow-2xl p-12">
          <div className="w-24 h-24 mx-auto mb-8 bg-gradient-to-r from-terracotta to-gold rounded-full flex items-center justify-center">
            <Heart className="w-12 h-12 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-charcoal mb-6">Merci infiniment ! 🙏</h1>
          <p className="text-xl text-charcoal/80 mb-8 leading-relaxed">
            Votre généreuse contribution aide à maintenir US EXPLO gratuit et accessible à tous. 
            Grâce à vous, nous pouvons continuer à promouvoir la musique du monde entier ! 🌍🎵
          </p>
          <div className="flex justify-center space-x-4">
            <a href="/" className="px-8 py-4 bg-gradient-to-r from-terracotta to-gold text-white rounded-full font-bold hover:scale-105 transition-transform">
              Retour à l'accueil
            </a>
            <a href="/youtube" className="px-8 py-4 border-2 border-terracotta text-terracotta rounded-full font-bold hover:bg-terracotta hover:text-white transition-all">
              Voir notre chaîne YouTube
            </a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-charcoal via-purple-900 to-terracotta">
      {/* Header avec navigation */}
      <nav className="bg-charcoal/95 backdrop-blur-md border-b border-terracotta/20 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <a href="/" className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-terracotta to-gold rounded-lg flex items-center justify-center">
                <Music className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">US EXPLO</h1>
                <p className="text-xs text-sage">Universal Sound Exploration</p>
              </div>
            </a>
            <div className="flex items-center space-x-4">
              <Heart className="w-6 h-6 text-terracotta" />
              <span className="text-white font-semibold">Soutenir la Mission</span>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center bg-gradient-to-r from-terracotta/20 to-gold/20 backdrop-blur-sm border border-terracotta/30 rounded-full px-8 py-3 mb-8">
            <Youtube className="w-6 h-6 text-red-400 mr-3" />
            <span className="text-gold font-bold text-lg">YouTube Gratuit & US EXPLO</span>
            <Sparkles className="w-5 h-5 text-gold ml-3" />
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-8 leading-tight">
            Soutenez la 
            <span className="bg-gradient-to-r from-terracotta via-gold to-yellow-300 bg-clip-text text-transparent"> Musique Mondiale</span>
          </h1>
          
          <p className="text-xl md:text-2xl text-white/90 mb-6 max-w-4xl mx-auto leading-relaxed">
            🎵 Aidez-nous à maintenir US EXPLO gratuit et à faire découvrir la richesse musicale de notre planète ! 🌍
          </p>
          
          <p className="text-lg text-white/70 max-w-3xl mx-auto">
            Vos dons permettent de financer les serveurs, la maintenance, l'ajout de nouvelles musiques 
            et le soutien aux artistes du monde entier. Ensemble, gardons la musique accessible à tous ! ✨
          </p>
        </div>

        {/* Statistics Bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16">
          <div className="text-center p-6 bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20">
            <div className="text-3xl md:text-4xl font-bold text-terracotta mb-2">{formatNumber(stats.totalDonated)}€</div>
            <div className="text-sm text-white/80">Total collecté</div>
          </div>
          <div className="text-center p-6 bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20">
            <div className="text-3xl md:text-4xl font-bold text-gold mb-2">{formatNumber(stats.monthlyDonors)}</div>
            <div className="text-sm text-white/80">Donateurs actifs</div>
          </div>
          <div className="text-center p-6 bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20">
            <div className="text-3xl md:text-4xl font-bold text-sage mb-2">{formatNumber(stats.ytChannelViews)}</div>
            <div className="text-sm text-white/80">Vues YouTube</div>
          </div>
          <div className="text-center p-6 bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20">
            <div className="text-3xl md:text-4xl font-bold text-purple-400 mb-2">{formatNumber(stats.supportedArtists)}</div>
            <div className="text-sm text-white/80">Artistes soutenus</div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
          {/* Donation Form */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-3xl shadow-2xl p-8">
              <div className="flex items-center mb-8">
                <Gift className="w-8 h-8 text-terracotta mr-4" />
                <h2 className="text-3xl font-bold text-charcoal">Faire un don</h2>
              </div>

              {/* Donation Type */}
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-charcoal mb-4">Type de don</h3>
                <div className="grid grid-cols-2 gap-4">
                  <button
                    onClick={() => setDonationType('monthly')}
                    className={`p-4 rounded-xl border-2 transition-all ${
                      donationType === 'monthly' 
                        ? 'border-terracotta bg-terracotta/10 text-terracotta' 
                        : 'border-gray-200 hover:border-terracotta/50'
                    }`}
                  >
                    <Crown className="w-6 h-6 mx-auto mb-2" />
                    <div className="font-semibold">Mensuel</div>
                    <div className="text-sm text-gray-600">Soutien continu</div>
                  </button>
                  <button
                    onClick={() => setDonationType('one-time')}
                    className={`p-4 rounded-xl border-2 transition-all ${
                      donationType === 'one-time' 
                        ? 'border-terracotta bg-terracotta/10 text-terracotta' 
                        : 'border-gray-200 hover:border-terracotta/50'
                    }`}
                  >
                    <Zap className="w-6 h-6 mx-auto mb-2" />
                    <div className="font-semibold">Ponctuel</div>
                    <div className="text-sm text-gray-600">Don unique</div>
                  </button>
                </div>
              </div>

              {/* Donation Amounts */}
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-charcoal mb-4">
                  Montant {donationType === 'monthly' ? 'mensuel' : ''}
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
                  {donationAmounts.map((donation) => (
                    <button
                      key={donation.amount}
                      onClick={() => {
                        setSelectedAmount(donation.amount);
                        setCustomAmount('');
                      }}
                      className={`p-4 rounded-xl border-2 text-left transition-all ${
                        selectedAmount === donation.amount && !customAmount
                          ? 'border-terracotta bg-terracotta/10' 
                          : 'border-gray-200 hover:border-terracotta/50'
                      }`}
                    >
                      <div className="font-bold text-lg text-charcoal">{donation.amount}€</div>
                      <div className="font-semibold text-terracotta text-sm">{donation.label}</div>
                      <div className="text-xs text-gray-600 mt-1">{donation.description}</div>
                    </button>
                  ))}
                </div>
                
                {/* Custom Amount */}
                <div className="relative">
                  <input
                    type="number"
                    placeholder="Montant personnalisé"
                    value={customAmount}
                    onChange={(e) => {
                      setCustomAmount(e.target.value);
                      setSelectedAmount(0);
                    }}
                    className="w-full p-4 border-2 border-gray-200 rounded-xl focus:border-terracotta focus:outline-none"
                    min="1"
                    step="0.01"
                  />
                  <div className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-500">€</div>
                </div>
              </div>

              {/* Donor Information */}
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-charcoal mb-4">Vos informations</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <input
                    type="text"
                    placeholder="Votre nom"
                    value={donorInfo.name}
                    onChange={(e) => setDonorInfo({...donorInfo, name: e.target.value})}
                    className="p-4 border-2 border-gray-200 rounded-xl focus:border-terracotta focus:outline-none"
                    disabled={donorInfo.isAnonymous}
                  />
                  <input
                    type="email"
                    placeholder="Votre email"
                    value={donorInfo.email}
                    onChange={(e) => setDonorInfo({...donorInfo, email: e.target.value})}
                    className="p-4 border-2 border-gray-200 rounded-xl focus:border-terracotta focus:outline-none"
                    required
                  />
                </div>
                <textarea
                  placeholder="Message d'encouragement (optionnel)"
                  value={donorInfo.message}
                  onChange={(e) => setDonorInfo({...donorInfo, message: e.target.value})}
                  className="w-full p-4 border-2 border-gray-200 rounded-xl focus:border-terracotta focus:outline-none h-24 resize-none"
                ></textarea>
                <label className="flex items-center mt-4">
                  <input
                    type="checkbox"
                    checked={donorInfo.isAnonymous}
                    onChange={(e) => setDonorInfo({...donorInfo, isAnonymous: e.target.checked})}
                    className="mr-3"
                  />
                  <span className="text-gray-700">Rester anonyme</span>
                </label>
              </div>

              {/* Payment Method */}
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-charcoal mb-4">Méthode de paiement</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <button
                    onClick={() => setPaymentMethod('stripe')}
                    className={`p-4 rounded-xl border-2 flex items-center transition-all ${
                      paymentMethod === 'stripe' 
                        ? 'border-terracotta bg-terracotta/10' 
                        : 'border-gray-200 hover:border-terracotta/50'
                    }`}
                  >
                    <CreditCard className="w-6 h-6 mr-3" />
                    <div>
                      <div className="font-semibold">Carte bancaire</div>
                      <div className="text-sm text-gray-600">Sécurisé par Stripe</div>
                    </div>
                  </button>
                  <button
                    onClick={() => setPaymentMethod('paypal')}
                    className={`p-4 rounded-xl border-2 flex items-center transition-all ${
                      paymentMethod === 'paypal' 
                        ? 'border-terracotta bg-terracotta/10' 
                        : 'border-gray-200 hover:border-terracotta/50'
                    }`}
                  >
                    <DollarSign className="w-6 h-6 mr-3" />
                    <div>
                      <div className="font-semibold">PayPal</div>
                      <div className="text-sm text-gray-600">Paiement rapide</div>
                    </div>
                  </button>
                </div>
              </div>

              {/* Donation Button */}
              <button
                onClick={handleDonation}
                disabled={loading || (!customAmount && !selectedAmount) || !donorInfo.email}
                className="w-full py-6 bg-gradient-to-r from-terracotta to-gold text-white font-bold text-xl rounded-xl hover:shadow-2xl transform hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center space-x-3"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                    <span>Traitement en cours...</span>
                  </>
                ) : (
                  <>
                    <Heart className="w-6 h-6" />
                    <span>
                      Donner {customAmount ? customAmount : selectedAmount}€ 
                      {donationType === 'monthly' ? '/mois' : ''}
                    </span>
                    <ArrowRight className="w-6 h-6" />
                  </>
                )}
              </button>

              <div className="mt-6 text-center text-sm text-gray-600">
                <Shield className="w-4 h-4 inline mr-2" />
                Paiement 100% sécurisé • Annulable à tout moment • Reçu fiscal disponible
              </div>
            </div>
          </div>

          {/* Impact Section */}
          <div className="space-y-8">
            {/* Impact Cards */}
            <div className="bg-white rounded-3xl shadow-2xl p-8">
              <h3 className="text-2xl font-bold text-charcoal mb-6 flex items-center">
                <Star className="w-6 h-6 text-gold mr-3" />
                Votre Impact
              </h3>
              
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-terracotta/20 rounded-full flex items-center justify-center flex-shrink-0">
                    <Globe className="w-6 h-6 text-terracotta" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-charcoal">Accessibilité Mondiale</h4>
                    <p className="text-sm text-gray-600">Garde US EXPLO gratuit pour tous les passionnés de musique</p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-gold/20 rounded-full flex items-center justify-center flex-shrink-0">
                    <Users className="w-6 h-6 text-gold" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-charcoal">Soutien aux Artistes</h4>
                    <p className="text-sm text-gray-600">Aide les musiciens émergents du monde entier</p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-sage/20 rounded-full flex items-center justify-center flex-shrink-0">
                    <Headphones className="w-6 h-6 text-sage" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-charcoal">Qualité Audio</h4>
                    <p className="text-sm text-gray-600">Maintient la qualité HD et les serveurs performants</p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-purple-500/20 rounded-full flex items-center justify-center flex-shrink-0">
                    <Download className="w-6 h-6 text-purple-500" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-charcoal">Nouvelles Fonctionnalités</h4>
                    <p className="text-sm text-gray-600">Finance le développement de nouvelles features</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Donors */}
            <div className="bg-white rounded-3xl shadow-2xl p-8">
              <h3 className="text-2xl font-bold text-charcoal mb-6 flex items-center">
                <Heart className="w-6 h-6 text-terracotta mr-3" />
                Donateurs Récents
              </h3>
              
              <div className="space-y-4">
                {[
                  { name: 'Marie L.', amount: 25, message: 'Vive la musique du monde ! 🌍' },
                  { name: 'Anonyme', amount: 50, message: 'Merci pour ce travail formidable' },
                  { name: 'Pierre M.', amount: 15, message: 'Continuez ainsi !' },
                  { name: 'Sarah K.', amount: 100, message: 'Pour la diversité culturelle ❤️' },
                  { name: 'Anonyme', amount: 30, message: 'Bravo pour cette initiative' }
                ].map((donor, index) => (
                  <div key={index} className="flex items-center space-x-4 p-4 bg-gray-50 rounded-xl">
                    <div className="w-10 h-10 bg-gradient-to-r from-terracotta to-gold rounded-full flex items-center justify-center">
                      <Heart className="w-5 h-5 text-white" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-semibold text-charcoal">{donor.name}</span>
                        <span className="text-terracotta font-bold">{donor.amount}€</span>
                      </div>
                      <p className="text-sm text-gray-600">"{donor.message}"</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* YouTube Channel Link */}
            <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-3xl shadow-2xl p-8 text-white">
              <div className="flex items-center mb-4">
                <Youtube className="w-8 h-8 mr-3" />
                <h3 className="text-2xl font-bold">Notre Chaîne YouTube</h3>
              </div>
              <p className="mb-6 opacity-90">
                Découvrez notre contenu YouTube gratuit avec des interviews d'artistes, 
                des documentaires musicaux et des sessions live exclusives !
              </p>
              <a 
                href="https://youtube.com/@usexplo" 
                target="_blank" 
                rel="noopener noreferrer"
                className="inline-flex items-center space-x-2 bg-white text-red-600 px-6 py-3 rounded-full font-bold hover:bg-gray-100 transition-colors"
              >
                <Youtube className="w-5 h-5" />
                <span>Visiter notre chaîne</span>
                <ArrowRight className="w-4 h-4" />
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DonationPage;
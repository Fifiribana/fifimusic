import React, { useEffect, useState } from 'react';
import { Heart, CheckCircle, Youtube, Music, Star, ArrowRight, Home, Share2 } from 'lucide-react';
import { useSearchParams, Link } from 'react-router-dom';

const DonationSuccessPage = () => {
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session_id');
  const [donationInfo, setDonationInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate fetching donation info - in real app, this would call the backend
    setTimeout(() => {
      setDonationInfo({
        amount: 25,
        currency: 'EUR',
        type: 'monthly',
        donor_name: 'Donateur Généreux'
      });
      setLoading(false);
    }, 1000);
  }, [sessionId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-terracotta via-gold to-sage flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white mx-auto mb-4"></div>
          <p className="text-white text-xl">Confirmation de votre donation...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-terracotta via-gold to-sage">
      <div className="max-w-4xl mx-auto px-4 py-16">
        {/* Success Card */}
        <div className="bg-white rounded-3xl shadow-2xl p-12 text-center">
          {/* Success Icon */}
          <div className="w-24 h-24 mx-auto mb-8 bg-gradient-to-r from-green-400 to-green-600 rounded-full flex items-center justify-center">
            <CheckCircle className="w-12 h-12 text-white" />
          </div>

          {/* Thank You Message */}
          <h1 className="text-5xl font-bold text-charcoal mb-6">
            Merci infiniment ! 🙏
          </h1>

          <p className="text-2xl text-charcoal/80 mb-8 leading-relaxed">
            Votre généreuse contribution de{' '}
            <span className="font-bold text-terracotta">
              {donationInfo?.amount}€{donationInfo?.type === 'monthly' ? '/mois' : ''}
            </span>{' '}
            aide à maintenir US EXPLO gratuit et accessible à tous !
          </p>

          {/* Impact Message */}
          <div className="bg-gradient-to-r from-terracotta/10 to-gold/10 rounded-2xl p-8 mb-8">
            <h2 className="text-2xl font-bold text-charcoal mb-4 flex items-center justify-center">
              <Heart className="w-6 h-6 text-terracotta mr-3" />
              Votre Impact
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="text-center">
                <div className="w-16 h-16 bg-terracotta/20 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Music className="w-8 h-8 text-terracotta" />
                </div>
                <h3 className="font-semibold text-charcoal mb-2">Musique Gratuite</h3>
                <p className="text-sm text-charcoal/70">
                  Permet de maintenir l'accès gratuit à des milliers de pistes du monde entier
                </p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-gold/20 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Youtube className="w-8 h-8 text-red-500" />
                </div>
                <h3 className="font-semibold text-charcoal mb-2">Contenu YouTube</h3>
                <p className="text-sm text-charcoal/70">
                  Finance la production de documentaires et d'interviews d'artistes
                </p>
              </div>
            </div>
          </div>

          {/* What's Next */}
          <div className="border-t border-gray-200 pt-8">
            <h3 className="text-xl font-bold text-charcoal mb-6">Que se passe-t-il maintenant ?</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="text-center">
                <div className="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-blue-600 font-bold">1</span>
                </div>
                <h4 className="font-semibold text-charcoal mb-2">Confirmation</h4>
                <p className="text-sm text-charcoal/70">
                  Vous recevrez un email de confirmation avec les détails de votre don
                </p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-green-600 font-bold">2</span>
                </div>
                <h4 className="font-semibold text-charcoal mb-2">Reçu Fiscal</h4>
                <p className="text-sm text-charcoal/70">
                  Un reçu fiscal vous sera envoyé pour vos déductions d'impôts
                </p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-purple-600 font-bold">3</span>
                </div>
                <h4 className="font-semibold text-charcoal mb-2">Suivi</h4>
                <p className="text-sm text-charcoal/70">
                  Suivez l'impact de votre don dans notre newsletter mensuelle
                </p>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link
              to="/"
              className="group px-8 py-4 bg-gradient-to-r from-terracotta to-gold text-white font-bold rounded-full hover:scale-105 transition-all duration-300 shadow-lg flex items-center space-x-2"
            >
              <Home className="w-5 h-5" />
              <span>Retour à l'accueil</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
            
            <button
              onClick={() => {
                if (navigator.share) {
                  navigator.share({
                    title: 'US EXPLO - Plateforme musicale mondiale',
                    text: 'Je viens de soutenir US EXPLO, une plateforme qui rend la musique du monde accessible à tous !',
                    url: window.location.origin
                  });
                } else {
                  // Fallback pour les navigateurs qui ne supportent pas l'API Web Share
                  const shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent('Je viens de soutenir US EXPLO, une plateforme qui rend la musique du monde accessible à tous !')}&url=${encodeURIComponent(window.location.origin)}`;
                  window.open(shareUrl, '_blank');
                }
              }}
              className="px-8 py-4 border-2 border-terracotta text-terracotta font-bold rounded-full hover:bg-terracotta hover:text-white transition-all duration-300 flex items-center space-x-2"
            >
              <Share2 className="w-5 h-5" />
              <span>Partager la mission</span>
            </button>
          </div>

          {/* Social Proof */}
          <div className="mt-12 pt-8 border-t border-gray-200">
            <p className="text-sm text-charcoal/60 mb-4">
              Rejoignez les <span className="font-bold text-terracotta">892 donateurs</span> qui soutiennent déjà notre mission
            </p>
            <div className="flex justify-center items-center space-x-2">
              {[...Array(5)].map((_, i) => (
                <Star key={i} className="w-5 h-5 text-gold fill-current" />
              ))}
              <span className="ml-2 text-sm text-charcoal/70">
                4.9/5 de satisfaction des donateurs
              </span>
            </div>
          </div>
        </div>

        {/* YouTube Channel Promotion */}
        <div className="mt-12 bg-gradient-to-r from-red-500 to-red-600 rounded-3xl shadow-2xl p-8 text-white text-center">
          <Youtube className="w-12 h-12 mx-auto mb-4" />
          <h2 className="text-3xl font-bold mb-4">
            Découvrez notre chaîne YouTube !
          </h2>
          <p className="text-xl mb-6 opacity-90">
            Grâce à votre soutien, nous produisons du contenu gratuit exceptionnel
          </p>
          <a
            href="https://youtube.com/@usexplo"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center space-x-2 bg-white text-red-600 px-8 py-4 rounded-full font-bold hover:bg-gray-100 transition-colors"
          >
            <Youtube className="w-5 h-5" />
            <span>S'abonner à la chaîne</span>
            <ArrowRight className="w-4 h-4" />
          </a>
        </div>
      </div>
    </div>
  );
};

export default DonationSuccessPage;
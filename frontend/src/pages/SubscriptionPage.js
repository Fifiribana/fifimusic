import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Check, 
  Star, 
  Crown, 
  Zap,
  Music,
  Users,
  TrendingUp,
  Shield,
  Headphones,
  Award,
  Sparkles,
  CreditCard
} from 'lucide-react';
import { useToast } from '../components/Toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SubscriptionPage = () => {
  const { toast } = useToast();
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);
  const [plans, setPlans] = useState([]);
  const [currentSubscription, setCurrentSubscription] = useState(null);
  const [processingPlan, setProcessingPlan] = useState(null);

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
        
        // Load subscription plans
        await loadPlans();
        
        // Load current subscription
        await loadCurrentSubscription();
        
      } catch (error) {
        console.error('Auth check failed:', error);
        localStorage.removeItem('token');
        setToken(null);
      }
      setLoading(false);
    };

    checkAuth();
  }, [token]);

  const loadPlans = async () => {
    try {
      const response = await axios.get(`${API}/subscriptions/plans`);
      setPlans(response.data);
    } catch (error) {
      toast.error('Erreur lors du chargement des plans');
    }
  };

  const loadCurrentSubscription = async () => {
    try {
      const response = await axios.get(`${API}/subscriptions/my-subscription`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCurrentSubscription(response.data);
    } catch (error) {
      // No subscription is okay
      setCurrentSubscription(null);
    }
  };

  const handleSubscribe = async (planId, billingCycle) => {
    setProcessingPlan(planId);
    
    try {
      await axios.post(`${API}/subscriptions/subscribe`, {
        plan_id: planId,
        billing_cycle: billingCycle
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success('Abonnement activé avec succès !');
      await loadCurrentSubscription();
    } catch (error) {
      const message = error.response?.data?.detail || 'Erreur lors de l\'abonnement';
      toast.error(message);
    } finally {
      setProcessingPlan(null);
    }
  };

  const getPlanIcon = (planName) => {
    switch (planName.toLowerCase()) {
      case 'basique':
        return <Music className="w-8 h-8" />;
      case 'pro':
        return <Star className="w-8 h-8" />;
      case 'premium':
        return <Crown className="w-8 h-8" />;
      default:
        return <Music className="w-8 h-8" />;
    }
  };

  const getPlanColor = (planName) => {
    switch (planName.toLowerCase()) {
      case 'basique':
        return 'from-sage to-sage/80';
      case 'pro':
        return 'from-terracotta to-gold';
      case 'premium':
        return 'from-gold to-terracotta';
      default:
        return 'from-sage to-sage/80';
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR'
    }).format(price);
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
          <CreditCard className="w-16 h-16 text-terracotta mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-charcoal mb-4">Abonnements US EXPLO</h2>
          <p className="text-charcoal/70 mb-6">
            Connectez-vous pour découvrir nos plans d'abonnement et faire évoluer votre carrière musicale !
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
        <div className="max-w-6xl mx-auto text-center">
          <h1 className="text-5xl font-bold mb-4">
            ✨ Plans d'Abonnement US EXPLO
          </h1>
          <p className="text-xl text-white/80 mb-6">
            Choisissez le plan parfait pour faire évoluer votre carrière musicale
          </p>
          
          {currentSubscription && (
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 border border-white/20 inline-block">
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-green-400 font-semibold">
                  Plan actuel: {currentSubscription.plan?.name} 
                  ({currentSubscription.billing_cycle === 'yearly' ? 'Annuel' : 'Mensuel'})
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Plans Grid */}
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan) => {
            const isCurrentPlan = currentSubscription?.plan?.id === plan.id;
            const isPopular = plan.name === 'Pro';
            
            return (
              <div 
                key={plan.id} 
                className={`relative bg-white/10 backdrop-blur-sm rounded-3xl p-8 border border-white/20 hover:bg-white/15 transition-all transform hover:scale-105 ${
                  isPopular ? 'ring-2 ring-gold shadow-2xl shadow-gold/20' : ''
                } ${isCurrentPlan ? 'ring-2 ring-green-500' : ''}`}
              >
                {isPopular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <div className="bg-gradient-to-r from-terracotta to-gold text-white px-6 py-2 rounded-full text-sm font-semibold flex items-center space-x-2">
                      <Sparkles className="w-4 h-4" />
                      <span>Plus Populaire</span>
                    </div>
                  </div>
                )}
                
                {isCurrentPlan && (
                  <div className="absolute -top-4 right-4">
                    <div className="bg-green-500 text-white px-4 py-2 rounded-full text-sm font-semibold">
                      Actuel
                    </div>
                  </div>
                )}

                {/* Plan Header */}
                <div className="text-center mb-8">
                  <div className={`w-16 h-16 bg-gradient-to-br ${getPlanColor(plan.name)} rounded-2xl flex items-center justify-center mx-auto mb-4 text-white`}>
                    {getPlanIcon(plan.name)}
                  </div>
                  
                  <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
                  <p className="text-white/70 text-sm">{plan.description}</p>
                </div>

                {/* Pricing */}
                <div className="text-center mb-8">
                  <div className="space-y-4">
                    <div className="bg-white/10 rounded-xl p-4">
                      <div className="text-white/60 text-sm">Mensuel</div>
                      <div className="text-3xl font-bold text-white">
                        {formatPrice(plan.price_monthly)}
                        <span className="text-lg text-white/60">/mois</span>
                      </div>
                      
                      {!isCurrentPlan && (
                        <button
                          onClick={() => handleSubscribe(plan.id, 'monthly')}
                          disabled={processingPlan === plan.id}
                          className={`w-full mt-3 py-2 rounded-lg font-semibold transition-all ${
                            processingPlan === plan.id
                              ? 'bg-white/20 text-white/50 cursor-not-allowed'
                              : `bg-gradient-to-r ${getPlanColor(plan.name)} text-white hover:shadow-lg`
                          }`}
                        >
                          {processingPlan === plan.id ? 'Traitement...' : 'Choisir'}
                        </button>
                      )}
                    </div>
                    
                    <div className="bg-white/10 rounded-xl p-4 border-2 border-gold/30">
                      <div className="text-gold text-sm font-semibold flex items-center justify-center space-x-1">
                        <Award className="w-4 h-4" />
                        <span>Économie annuelle</span>
                      </div>
                      <div className="text-3xl font-bold text-white">
                        {formatPrice(plan.price_yearly)}
                        <span className="text-lg text-white/60">/an</span>
                      </div>
                      <div className="text-green-400 text-sm font-medium">
                        Économisez {formatPrice((plan.price_monthly * 12) - plan.price_yearly)}
                      </div>
                      
                      {!isCurrentPlan && (
                        <button
                          onClick={() => handleSubscribe(plan.id, 'yearly')}
                          disabled={processingPlan === plan.id}
                          className={`w-full mt-3 py-2 rounded-lg font-semibold transition-all ${
                            processingPlan === plan.id
                              ? 'bg-white/20 text-white/50 cursor-not-allowed'
                              : 'bg-gradient-to-r from-gold to-terracotta text-white hover:shadow-lg'
                          }`}
                        >
                          {processingPlan === plan.id ? 'Traitement...' : 'Choisir Annuel'}
                        </button>
                      )}
                    </div>
                  </div>
                </div>

                {/* Features */}
                <div className="space-y-3">
                  {plan.features.map((feature, index) => (
                    <div key={index} className="flex items-start space-x-3">
                      <Check className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                      <span className="text-white/80 text-sm">{feature}</span>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        {/* Features Comparison */}
        <div className="mt-16">
          <h2 className="text-3xl font-bold text-white text-center mb-8">
            Comparaison des Fonctionnalités
          </h2>
          
          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/20">
                    <th className="text-left py-4 text-white font-semibold">Fonctionnalités</th>
                    {plans.map(plan => (
                      <th key={plan.id} className="text-center py-4 text-white font-semibold min-w-32">
                        {plan.name}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="text-white/80">
                  <tr className="border-b border-white/10">
                    <td className="py-4">Uploads mensuels</td>
                    {plans.map(plan => (
                      <td key={plan.id} className="text-center py-4">
                        {plan.max_uploads_per_month > 999999 ? 'Illimité' : plan.max_uploads_per_month}
                      </td>
                    ))}
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="py-4">Groupes maximum</td>
                    {plans.map(plan => (
                      <td key={plan.id} className="text-center py-4">
                        {plan.max_groups > 999999 ? 'Illimité' : plan.max_groups}
                      </td>
                    ))}
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="py-4">Vente de musique</td>
                    {plans.map(plan => (
                      <td key={plan.id} className="text-center py-4">
                        {plan.can_sell_music ? (
                          <Check className="w-5 h-5 text-green-400 mx-auto" />
                        ) : (
                          <span className="text-white/40">-</span>
                        )}
                      </td>
                    ))}
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="py-4">Création d'événements</td>
                    {plans.map(plan => (
                      <td key={plan.id} className="text-center py-4">
                        {plan.can_create_events ? (
                          <Check className="w-5 h-5 text-green-400 mx-auto" />
                        ) : (
                          <span className="text-white/40">-</span>
                        )}
                      </td>
                    ))}
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="py-4">Support prioritaire</td>
                    {plans.map(plan => (
                      <td key={plan.id} className="text-center py-4">
                        {plan.priority_support ? (
                          <Check className="w-5 h-5 text-green-400 mx-auto" />
                        ) : (
                          <span className="text-white/40">-</span>
                        )}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td className="py-4">Accès aux analytics</td>
                    {plans.map(plan => (
                      <td key={plan.id} className="text-center py-4">
                        {plan.analytics_access ? (
                          <Check className="w-5 h-5 text-green-400 mx-auto" />
                        ) : (
                          <span className="text-white/40">-</span>
                        )}
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* FAQ Section */}
        <div className="mt-16">
          <h2 className="text-3xl font-bold text-white text-center mb-8">
            Questions Fréquentes
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              <h3 className="text-lg font-semibold text-white mb-3">
                Puis-je changer de plan à tout moment ?
              </h3>
              <p className="text-white/70">
                Oui, vous pouvez passer à un plan supérieur à tout moment. 
                Le changement prend effet immédiatement et vous êtes facturé au prorata.
              </p>
            </div>
            
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              <h3 className="text-lg font-semibold text-white mb-3">
                Quelle est la commission sur les ventes ?
              </h3>
              <p className="text-white/70">
                Plan Pro: 10% de commission. Plan Premium: 5% de commission. 
                Les utilisateurs gratuits ne peuvent pas vendre leur musique.
              </p>
            </div>
            
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              <h3 className="text-lg font-semibold text-white mb-3">
                Y a-t-il un engagement ?
              </h3>
              <p className="text-white/70">
                Non, tous nos abonnements sont sans engagement. 
                Vous pouvez annuler à tout moment depuis votre espace personnel.
              </p>
            </div>
            
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              <h3 className="text-lg font-semibold text-white mb-3">
                Mes données sont-elles sécurisées ?
              </h3>
              <p className="text-white/70">
                Absolument. Nous utilisons un chiffrement de niveau bancaire 
                et respectons toutes les réglementations RGPD pour protéger vos données.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SubscriptionPage;
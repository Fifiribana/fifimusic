import React, { useState, useEffect } from "react";
import { 
  Heart, 
  Users, 
  Target, 
  Clock, 
  DollarSign, 
  Star, 
  Plus, 
  Send,
  Calendar,
  MapPin,
  Music,
  Lightbulb,
  Hands,
  Sparkles,
  TrendingUp,
  Award,
  Globe,
  MessageCircle
} from "lucide-react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SolidarityPage = ({ user, authToken }) => {
  const [campaigns, setCampaigns] = useState([]);
  const [advice, setAdvice] = useState([]);
  const [stats, setStats] = useState({});
  const [activeTab, setActiveTab] = useState("campaigns");
  const [showCreateCampaign, setShowCreateCampaign] = useState(false);
  const [showCreateAdvice, setShowCreateAdvice] = useState(false);
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [donationAmount, setDonationAmount] = useState("");
  const [donationMessage, setDonationMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadCampaigns();
    loadAdvice();
    loadStats();
  }, []);

  const loadCampaigns = async () => {
    try {
      const response = await axios.get(`${API}/solidarity/campaigns?featured=false&limit=50`);
      setCampaigns(response.data);
    } catch (error) {
      console.error("Error loading campaigns:", error);
    }
  };

  const loadAdvice = async () => {
    try {
      const response = await axios.get(`${API}/solidarity/advice?limit=20`);
      setAdvice(response.data);
    } catch (error) {
      console.error("Error loading advice:", error);
    }
  };

  const loadStats = async () => {
    try {
      const response = await axios.get(`${API}/solidarity/stats`);
      setStats(response.data);
    } catch (error) {
      console.error("Error loading stats:", error);
    }
  };

  const makeDonation = async (campaignId) => {
    if (!donationAmount || parseFloat(donationAmount) <= 0) return;

    setIsLoading(true);
    try {
      await axios.post(
        `${API}/solidarity/donate`,
        {
          campaign_id: campaignId,
          amount: parseFloat(donationAmount),
          donor_name: user?.username || "Supporter anonyme",
          message: donationMessage,
          is_anonymous: false
        },
        authToken ? { headers: { Authorization: `Bearer ${authToken}` } } : {}
      );

      setDonationAmount("");
      setDonationMessage("");
      setSelectedCampaign(null);
      loadCampaigns(); // Refresh to show updated amounts
      alert("Merci pour votre générosité ! Votre don a été enregistré avec succès. 🙏");
    } catch (error) {
      console.error("Error making donation:", error);
      alert("Erreur lors du don. Veuillez réessayer.");
    } finally {
      setIsLoading(false);
    }
  };

  const projectTypes = {
    album: { icon: Music, label: "Album", color: "purple" },
    concert: { icon: Users, label: "Concert", color: "blue" },
    equipment: { icon: Target, label: "Équipement", color: "green" },
    studio: { icon: Star, label: "Studio", color: "orange" },
    emergency: { icon: Heart, label: "Urgence", color: "red" }
  };

  const adviceCategories = {
    physical: { icon: Hands, label: "Physique", color: "green" },
    spiritual: { icon: Lightbulb, label: "Spirituel", color: "purple" },
    creative: { icon: Sparkles, label: "Créatif", color: "blue" },
    technical: { icon: Target, label: "Technique", color: "orange" },
    business: { icon: TrendingUp, label: "Business", color: "red" }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-red-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-orange-600 to-red-600 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <div className="flex justify-center mb-6">
            <div className="bg-white bg-opacity-20 p-4 rounded-full">
              <Heart className="w-12 h-12" />
            </div>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Solidarité Musicale Mondiale
          </h1>
          <p className="text-xl text-orange-100 mb-8 max-w-3xl mx-auto">
            Ensemble, nous sommes très forts ! Soutenons nos artistes du monde entier dans leurs projets musicaux 
            et partageons conseils physiques et spirituels pour créer une communauté unie.
          </p>
          
          {/* Stats Display */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-12">
            <div className="bg-white bg-opacity-10 rounded-lg p-4">
              <div className="text-2xl font-bold">{stats.campaigns?.total || 0}</div>
              <div className="text-sm text-orange-200">Projets soutenus</div>
            </div>
            <div className="bg-white bg-opacity-10 rounded-lg p-4">
              <div className="text-2xl font-bold">{stats.donations?.total_amount?.toFixed(0) || 0}€</div>
              <div className="text-sm text-orange-200">Collectés ensemble</div>
            </div>
            <div className="bg-white bg-opacity-10 rounded-lg p-4">
              <div className="text-2xl font-bold">{stats.donations?.total_donors || 0}</div>
              <div className="text-sm text-orange-200">Généreux donateurs</div>
            </div>
            <div className="bg-white bg-opacity-10 rounded-lg p-4">
              <div className="text-2xl font-bold">{stats.community?.total_advice || 0}</div>
              <div className="text-sm text-orange-200">Conseils partagés</div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white shadow-sm border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-8">
            <button
              onClick={() => setActiveTab("campaigns")}
              className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                activeTab === "campaigns"
                  ? "border-orange-500 text-orange-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              <Target className="w-4 h-4 inline mr-2" />
              Projets à soutenir
            </button>
            <button
              onClick={() => setActiveTab("advice")}
              className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                activeTab === "advice"
                  ? "border-orange-500 text-orange-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              <Lightbulb className="w-4 h-4 inline mr-2" />
              Conseils & Entraide
            </button>
            <button
              onClick={() => setActiveTab("success")}
              className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                activeTab === "success"
                  ? "border-orange-500 text-orange-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              <Award className="w-4 h-4 inline mr-2" />
              Histoires de succès
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Campaigns Tab */}
        {activeTab === "campaigns" && (
          <div>
            <div className="flex justify-between items-center mb-8">
              <div>
                <h2 className="text-3xl font-bold text-gray-900">Projets musicaux à soutenir</h2>
                <p className="text-gray-600 mt-2">Chaque don, même petit, fait la différence dans la vie d'un artiste</p>
              </div>
              {user && (
                <button
                  onClick={() => setShowCreateCampaign(true)}
                  className="bg-orange-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-orange-700 transition-colors flex items-center space-x-2"
                >
                  <Plus className="w-5 h-5" />
                  <span>Créer un projet</span>
                </button>
              )}
            </div>

            {campaigns.length === 0 ? (
              <div className="text-center py-12">
                <Target className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                <h3 className="text-xl font-medium text-gray-700 mb-2">Aucun projet actif</h3>
                <p className="text-gray-500">Soyez le premier à créer un projet de solidarité musicale !</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {campaigns.map((campaign) => {
                  const ProjectIcon = projectTypes[campaign.project_type]?.icon || Music;
                  const projectColor = projectTypes[campaign.project_type]?.color || "gray";
                  const progressPercentage = campaign.progress_percentage || 0;
                  const daysLeft = Math.max(0, Math.ceil((new Date(campaign.deadline) - new Date()) / (1000 * 60 * 60 * 24)));

                  return (
                    <div key={campaign.id} className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
                      {campaign.image_url && (
                        <img 
                          src={campaign.image_url} 
                          alt={campaign.title}
                          className="w-full h-48 object-cover"
                        />
                      )}
                      
                      <div className="p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-center space-x-2">
                            <div className={`bg-${projectColor}-100 p-2 rounded-lg`}>
                              <ProjectIcon className={`w-5 h-5 text-${projectColor}-600`} />
                            </div>
                            <span className={`text-sm font-medium text-${projectColor}-600`}>
                              {projectTypes[campaign.project_type]?.label}
                            </span>
                          </div>
                          <div className="text-right">
                            <div className="text-sm text-gray-500">
                              <Clock className="w-4 h-4 inline mr-1" />
                              {daysLeft}j restants
                            </div>
                          </div>
                        </div>

                        <h3 className="text-lg font-bold text-gray-900 mb-2">{campaign.title}</h3>
                        <p className="text-gray-600 text-sm mb-4 line-clamp-3">{campaign.description}</p>

                        <div className="mb-4">
                          <div className="flex justify-between text-sm mb-2">
                            <span className="text-gray-600">Collecté</span>
                            <span className="font-medium">{progressPercentage.toFixed(1)}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-gradient-to-r from-orange-500 to-red-500 h-2 rounded-full transition-all duration-500"
                              style={{ width: `${Math.min(100, progressPercentage)}%` }}
                            ></div>
                          </div>
                          <div className="flex justify-between text-sm mt-2">
                            <span className="font-medium text-gray-900">
                              {campaign.current_amount?.toFixed(0)}€ collectés
                            </span>
                            <span className="text-gray-600">
                              sur {campaign.goal_amount?.toFixed(0)}€
                            </span>
                          </div>
                        </div>

                        <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                          <div className="flex items-center">
                            <Users className="w-4 h-4 mr-1" />
                            {campaign.donors_count || 0} donateurs
                          </div>
                          <div className="flex items-center">
                            <MapPin className="w-4 h-4 mr-1" />
                            {campaign.region}
                          </div>
                        </div>

                        <button
                          onClick={() => setSelectedCampaign(campaign)}
                          className="w-full bg-gradient-to-r from-orange-600 to-red-600 text-white py-3 px-4 rounded-lg font-medium hover:from-orange-700 hover:to-red-700 transition-all duration-300 flex items-center justify-center space-x-2"
                        >
                          <Heart className="w-4 h-4" />
                          <span>Soutenir ce projet</span>
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* Advice Tab */}
        {activeTab === "advice" && (
          <div>
            <div className="flex justify-between items-center mb-8">
              <div>
                <h2 className="text-3xl font-bold text-gray-900">Conseils & Entraide</h2>
                <p className="text-gray-600 mt-2">Partageons nos expériences pour nous entraider dans nos parcours musicaux</p>
              </div>
              {user && (
                <button
                  onClick={() => setShowCreateAdvice(true)}
                  className="bg-purple-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-purple-700 transition-colors flex items-center space-x-2"
                >
                  <Plus className="w-5 h-5" />
                  <span>Partager un conseil</span>
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {advice.map((item) => {
                const CategoryIcon = adviceCategories[item.category]?.icon || Lightbulb;
                const categoryColor = adviceCategories[item.category]?.color || "gray";

                return (
                  <div key={item.id} className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className={`bg-${categoryColor}-100 p-2 rounded-lg`}>
                          <CategoryIcon className={`w-5 h-5 text-${categoryColor}-600`} />
                        </div>
                        <div>
                          <span className={`text-sm font-medium text-${categoryColor}-600`}>
                            {adviceCategories[item.category]?.label}
                          </span>
                          <div className="text-xs text-gray-500">
                            par {item.advisor_name}
                          </div>
                        </div>
                      </div>
                    </div>

                    <h3 className="text-lg font-bold text-gray-900 mb-3">{item.title}</h3>
                    <p className="text-gray-600 text-sm leading-relaxed mb-4 line-clamp-4">
                      {item.content}
                    </p>

                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center text-gray-500">
                        <Heart className="w-4 h-4 mr-1" />
                        {item.likes_count || 0} likes
                      </div>
                      <div className="text-gray-400">
                        {new Date(item.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {advice.length === 0 && (
              <div className="text-center py-12">
                <Lightbulb className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                <h3 className="text-xl font-medium text-gray-700 mb-2">Aucun conseil partagé</h3>
                <p className="text-gray-500">Soyez le premier à partager vos conseils avec la communauté !</p>
              </div>
            )}
          </div>
        )}

        {/* Success Stories Tab */}
        {activeTab === "success" && (
          <div>
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Histoires de succès</h2>
              <p className="text-gray-600 max-w-2xl mx-auto">
                Découvrez comment notre communauté a permis à des artistes de réaliser leurs rêves musicaux
              </p>
            </div>

            {stats.success_stories && stats.success_stories.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {stats.success_stories.map((story) => (
                  <div key={story.id} className="bg-gradient-to-br from-green-50 to-blue-50 rounded-xl p-6 border border-green-200">
                    <div className="flex items-center mb-4">
                      <div className="bg-green-100 p-2 rounded-full mr-3">
                        <Award className="w-6 h-6 text-green-600" />
                      </div>
                      <div>
                        <h3 className="font-bold text-gray-900">{story.title}</h3>
                        <p className="text-sm text-green-600">Projet réalisé avec succès</p>
                      </div>
                    </div>
                    <p className="text-gray-700 text-sm mb-4 line-clamp-3">{story.story}</p>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-green-600 font-medium">
                        {story.current_amount?.toFixed(0)}€ collectés
                      </span>
                      <span className="text-gray-500">
                        {story.region}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <Award className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                <h3 className="text-xl font-medium text-gray-700 mb-2">Premières success stories à venir</h3>
                <p className="text-gray-500">Les premiers projets soutenus créeront bientôt de belles histoires de réussite !</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Donation Modal */}
      {selectedCampaign && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-md w-full p-6">
            <div className="text-center mb-6">
              <div className="bg-orange-100 p-3 rounded-full w-fit mx-auto mb-4">
                <Heart className="w-8 h-8 text-orange-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Soutenir ce projet</h3>
              <p className="text-gray-600">{selectedCampaign.title}</p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Montant de votre don (€)
                </label>
                <input
                  type="number"
                  value={donationAmount}
                  onChange={(e) => setDonationAmount(e.target.value)}
                  placeholder="25"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  min="1"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Message de soutien (optionnel)
                </label>
                <textarea
                  value={donationMessage}
                  onChange={(e) => setDonationMessage(e.target.value)}
                  placeholder="Votre message d'encouragement..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent resize-none"
                  rows={3}
                />
              </div>

              <div className="flex space-x-3">
                <button
                  onClick={() => setSelectedCampaign(null)}
                  className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Annuler
                </button>
                <button
                  onClick={() => makeDonation(selectedCampaign.id)}
                  disabled={isLoading || !donationAmount || parseFloat(donationAmount) <= 0}
                  className="flex-1 bg-gradient-to-r from-orange-600 to-red-600 text-white px-4 py-3 rounded-lg font-medium hover:from-orange-700 hover:to-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 flex items-center justify-center space-x-2"
                >
                  {isLoading ? (
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  ) : (
                    <>
                      <Send className="w-4 h-4" />
                      <span>Faire le don</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Call to Action */}
      <div className="bg-gradient-to-r from-orange-600 to-red-600 text-white py-16 mt-16">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <Globe className="w-16 h-16 mx-auto mb-6" />
          <h2 className="text-3xl font-bold mb-4">Ensemble, nous sommes très forts ! 🎵</h2>
          <p className="text-xl text-orange-100 mb-8">
            Rejoignez notre mouvement de solidarité musicale mondiale. 
            Chaque geste compte, chaque conseil aide, chaque don transforme une vie.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => setActiveTab("campaigns")}
              className="bg-white text-orange-600 px-8 py-3 rounded-lg font-medium hover:bg-gray-100 transition-colors"
            >
              Découvrir les projets
            </button>
            <button
              onClick={() => setActiveTab("advice")}
              className="border border-white text-white px-8 py-3 rounded-lg font-medium hover:bg-white hover:text-orange-600 transition-colors"
            >
              Partager mes conseils
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SolidarityPage;
import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { 
  Users, 
  MessageCircle, 
  Heart, 
  Search, 
  Filter,
  MapPin,
  Music,
  Star,
  Plus,
  Send,
  UserPlus,
  Globe2,
  Headphones,
  Guitar,
  Mic,
  Radio,
  Trophy,
  Calendar
} from 'lucide-react';
import { useToast } from '../components/Toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CommunityPage = () => {
  const { toast } = useToast();
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);
  
  // Community states
  const [activeTab, setActiveTab] = useState('feed'); // feed, musicians, groups, messages, profile
  const [posts, setPosts] = useState([]);
  const [musicians, setMusicians] = useState([]);
  const [groups, setGroups] = useState([]);
  const [messages, setMessages] = useState([]);
  const [myProfile, setMyProfile] = useState(null);
  
  // Form states
  const [showPostForm, setShowPostForm] = useState(false);
  const [showProfileForm, setShowProfileForm] = useState(false);
  const [searchFilters, setSearchFilters] = useState({
    region: '',
    genre: '',
    instrument: '',
    experience_level: '',
    looking_for: ''
  });
  
  const [newPost, setNewPost] = useState({
    title: '',
    content: '',
    post_type: 'idea',
    tags: []
  });
  
  const [profileForm, setProfileForm] = useState({
    stage_name: '',
    bio: '',
    instruments: [],
    genres: [],
    experience_level: 'Intermédiaire',
    region: 'International',
    city: '',
    looking_for: [],
    social_links: {}
  });

  // Check authentication
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
        
        // Try to get user's musician profile
        try {
          const profileResponse = await axios.get(`${API}/community/profile/me`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          setMyProfile(profileResponse.data);
        } catch (error) {
          // No profile yet, that's okay
          console.log('No musician profile found');
        }
        
      } catch (error) {
        console.error('Auth check failed:', error);
        localStorage.removeItem('token');
        setToken(null);
      }
      setLoading(false);
    };

    checkAuth();
  }, [token]);

  // Load data based on active tab
  useEffect(() => {
    if (!token) return;

    const loadData = async () => {
      try {
        switch (activeTab) {
          case 'feed':
            await loadPosts();
            break;
          case 'musicians':
            await loadMusicians();
            break;
          case 'messages':
            await loadMessages();
            break;
          default:
            break;
        }
      } catch (error) {
        console.error('Error loading data:', error);
      }
    };

    loadData();
  }, [activeTab, token]);

  const loadPosts = async () => {
    try {
      const response = await axios.get(`${API}/community/posts`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPosts(response.data);
    } catch (error) {
      toast.error('Erreur lors du chargement des posts');
    }
  };

  const loadMusicians = async () => {
    try {
      const params = new URLSearchParams();
      Object.entries(searchFilters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
      
      const response = await axios.get(`${API}/community/musicians?${params}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMusicians(response.data);
    } catch (error) {
      toast.error('Erreur lors du chargement des musiciens');
    }
  };

  const loadMessages = async () => {
    try {
      const response = await axios.get(`${API}/community/messages`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessages(response.data);
    } catch (error) {
      toast.error('Erreur lors du chargement des messages');
    }
  };

  const handleCreatePost = async (e) => {
    e.preventDefault();
    
    if (!newPost.title.trim() || !newPost.content.trim()) {
      toast.error('Veuillez remplir le titre et le contenu');
      return;
    }

    try {
      await axios.post(`${API}/community/posts`, newPost, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success('Post créé avec succès !');
      setNewPost({ title: '', content: '', post_type: 'idea', tags: [] });
      setShowPostForm(false);
      await loadPosts();
    } catch (error) {
      toast.error('Erreur lors de la création du post');
    }
  };

  const handleCreateProfile = async (e) => {
    e.preventDefault();
    
    if (!profileForm.stage_name.trim()) {
      toast.error('Veuillez saisir votre nom de scène');
      return;
    }

    try {
      const response = await axios.post(`${API}/community/profile`, profileForm, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setMyProfile(response.data);
      toast.success('Profil musicien créé avec succès !');
      setShowProfileForm(false);
    } catch (error) {
      toast.error('Erreur lors de la création du profil');
    }
  };

  const handleLikePost = async (postId) => {
    try {
      await axios.post(`${API}/community/posts/${postId}/like`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      await loadPosts(); // Refresh posts to show updated like count
    } catch (error) {
      toast.error('Erreur lors du like');
    }
  };

  const formatTimeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now - date) / (1000 * 60));
    
    if (diffInMinutes < 60) {
      return `il y a ${diffInMinutes} min`;
    } else if (diffInMinutes < 1440) {
      return `il y a ${Math.floor(diffInMinutes / 60)} h`;
    } else {
      return `il y a ${Math.floor(diffInMinutes / 1440)} j`;
    }
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
          <Users className="w-16 h-16 text-terracotta mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-charcoal mb-4">Communauté Musiciens</h2>
          <p className="text-charcoal/70 mb-6">
            Connectez-vous pour rejoindre notre communauté mondiale de musiciens et échanger vos idées !
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
                🌍 Communauté Musicale Mondiale
              </h1>
              <p className="text-xl text-white/80">
                Connectez-vous avec des musiciens du monde entier - Partagez, Apprenez, Collaborez
              </p>
            </div>
            <div className="text-right">
              <p className="text-gold font-semibold">Bienvenue, {user.username}!</p>
              {myProfile && (
                <p className="text-terracotta">🎵 {myProfile.stage_name}</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white/10 backdrop-blur-sm border-b border-white/20">
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex space-x-8">
            {[
              { id: 'feed', label: 'Feed Communauté', icon: Radio },
              { id: 'musicians', label: 'Musiciens', icon: Users },
              { id: 'messages', label: 'Messages', icon: MessageCircle },
              { id: 'profile', label: 'Mon Profil', icon: UserPlus }
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
        {/* Feed Tab */}
        {activeTab === 'feed' && (
          <div className="space-y-6">
            {/* Create Post Button */}
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              <button
                onClick={() => setShowPostForm(!showPostForm)}
                className="w-full bg-gradient-to-r from-terracotta to-gold text-white py-4 rounded-xl font-semibold hover:shadow-lg transition-all flex items-center justify-center space-x-2"
              >
                <Plus className="w-5 h-5" />
                <span>Partager une idée musicale</span>
              </button>
            </div>

            {/* Post Form */}
            {showPostForm && (
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
                <form onSubmit={handleCreatePost} className="space-y-4">
                  <div>
                    <input
                      type="text"
                      placeholder="Titre de votre post..."
                      value={newPost.title}
                      onChange={(e) => setNewPost({ ...newPost, title: e.target.value })}
                      className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-xl text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-gold"
                    />
                  </div>
                  
                  <div>
                    <textarea
                      placeholder="Partagez votre idée, expérience ou question musicale..."
                      value={newPost.content}
                      onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
                      rows={4}
                      className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-xl text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-gold resize-none"
                    />
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <select
                      value={newPost.post_type}
                      onChange={(e) => setNewPost({ ...newPost, post_type: e.target.value })}
                      className="px-4 py-2 bg-white/20 border border-white/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-gold"
                    >
                      <option value="idea">💡 Idée</option>
                      <option value="collaboration">🤝 Collaboration</option>
                      <option value="question">❓ Question</option>
                      <option value="event">📅 Événement</option>
                      <option value="showcase">🎵 Showcase</option>
                    </select>
                    
                    <div className="flex space-x-2">
                      <button
                        type="submit"
                        className="bg-gold text-charcoal px-6 py-2 rounded-lg font-semibold hover:bg-gold/90 transition-colors flex items-center space-x-2"
                      >
                        <Send className="w-4 h-4" />
                        <span>Publier</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => setShowPostForm(false)}
                        className="bg-white/20 text-white px-6 py-2 rounded-lg font-semibold hover:bg-white/30 transition-colors"
                      >
                        Annuler
                      </button>
                    </div>
                  </div>
                </form>
              </div>
            )}

            {/* Posts Feed */}
            {posts.length === 0 ? (
              <div className="text-center py-12">
                <Radio className="w-16 h-16 text-white/40 mx-auto mb-4" />
                <p className="text-white/60 text-lg">Aucun post pour le moment...</p>
                <p className="text-white/40">Soyez le premier à partager une idée !</p>
              </div>
            ) : (
              <div className="space-y-6">
                {posts.map(post => (
                  <div key={post.id} className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
                    <div className="flex items-start space-x-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-terracotta to-gold rounded-full flex items-center justify-center">
                        <Music className="w-6 h-6 text-white" />
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="font-semibold text-white">
                            {post.author?.stage_name || post.author?.username}
                          </h3>
                          <span className="text-xs text-white/60">
                            {formatTimeAgo(post.created_at)}
                          </span>
                          <span className="px-2 py-1 bg-gold/20 text-gold text-xs rounded-full">
                            {post.post_type === 'idea' && '💡 Idée'}
                            {post.post_type === 'collaboration' && '🤝 Collaboration'}
                            {post.post_type === 'question' && '❓ Question'}
                            {post.post_type === 'event' && '📅 Événement'}
                            {post.post_type === 'showcase' && '🎵 Showcase'}
                          </span>
                        </div>
                        
                        <h4 className="text-lg font-semibold text-white mb-2">{post.title}</h4>
                        <p className="text-white/80 mb-4">{post.content}</p>
                        
                        {post.tags && post.tags.length > 0 && (
                          <div className="flex flex-wrap gap-2 mb-4">
                            {post.tags.map((tag, index) => (
                              <span key={index} className="px-2 py-1 bg-sage/30 text-sage text-xs rounded-full">
                                #{tag}
                              </span>
                            ))}
                          </div>
                        )}
                        
                        <div className="flex items-center space-x-6">
                          <button
                            onClick={() => handleLikePost(post.id)}
                            className="flex items-center space-x-2 text-white/60 hover:text-terracotta transition-colors"
                          >
                            <Heart className="w-5 h-5" />
                            <span>{post.likes_count}</span>
                          </button>
                          
                          <button className="flex items-center space-x-2 text-white/60 hover:text-gold transition-colors">
                            <MessageCircle className="w-5 h-5" />
                            <span>{post.comments_count}</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Musicians Tab */}
        {activeTab === 'musicians' && (
          <div className="space-y-6">
            {/* Search Filters */}
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
                <Search className="w-6 h-6" />
                <span>Rechercher des musiciens</span>
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <label className="block text-white/70 text-sm mb-2">Région</label>
                  <select
                    value={searchFilters.region}
                    onChange={(e) => setSearchFilters({ ...searchFilters, region: e.target.value })}
                    className="w-full px-3 py-2 bg-white/20 border border-white/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-gold"
                  >
                    <option value="">Toutes les régions</option>
                    <option value="Afrique">Afrique</option>
                    <option value="Europe">Europe</option>
                    <option value="Asie">Asie</option>
                    <option value="Amérique">Amérique</option>
                    <option value="Océanie">Océanie</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-white/70 text-sm mb-2">Niveau</label>
                  <select
                    value={searchFilters.experience_level}
                    onChange={(e) => setSearchFilters({ ...searchFilters, experience_level: e.target.value })}
                    className="w-full px-3 py-2 bg-white/20 border border-white/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-gold"
                  >
                    <option value="">Tous niveaux</option>
                    <option value="Débutant">Débutant</option>
                    <option value="Intermédiaire">Intermédiaire</option>
                    <option value="Avancé">Avancé</option>
                    <option value="Professionnel">Professionnel</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-white/70 text-sm mb-2">Recherche</label>
                  <select
                    value={searchFilters.looking_for}
                    onChange={(e) => setSearchFilters({ ...searchFilters, looking_for: e.target.value })}
                    className="w-full px-3 py-2 bg-white/20 border border-white/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-gold"
                  >
                    <option value="">Tous types</option>
                    <option value="Collaboration">Collaboration</option>
                    <option value="Jam Session">Jam Session</option>
                    <option value="Apprentissage">Apprentissage</option>
                    <option value="Performance">Performance</option>
                  </select>
                </div>
              </div>
              
              <button
                onClick={loadMusicians}
                className="mt-4 bg-gradient-to-r from-terracotta to-gold text-white px-6 py-2 rounded-xl font-semibold hover:shadow-lg transition-all flex items-center space-x-2"
              >
                <Search className="w-4 h-4" />
                <span>Rechercher</span>
              </button>
            </div>

            {/* Musicians Grid */}
            {musicians.length === 0 ? (
              <div className="text-center py-12">
                <Users className="w-16 h-16 text-white/40 mx-auto mb-4" />
                <p className="text-white/60 text-lg">Aucun musicien trouvé...</p>
                <p className="text-white/40">Essayez d'ajuster vos filtres de recherche</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {musicians.map(musician => (
                  <div key={musician.id} className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20 hover:bg-white/15 transition-colors">
                    <div className="text-center">
                      <div className="w-16 h-16 bg-gradient-to-br from-terracotta to-gold rounded-full flex items-center justify-center mx-auto mb-4">
                        <Music className="w-8 h-8 text-white" />
                      </div>
                      
                      <h3 className="text-xl font-semibold text-white mb-1">{musician.stage_name}</h3>
                      <p className="text-white/60 text-sm mb-3">@{musician.username}</p>
                      
                      {musician.bio && (
                        <p className="text-white/80 text-sm mb-4 line-clamp-3">{musician.bio}</p>
                      )}
                      
                      <div className="space-y-2 mb-4">
                        <div className="flex items-center justify-center space-x-2 text-sm text-white/70">
                          <MapPin className="w-4 h-4" />
                          <span>{musician.region}</span>
                          {musician.city && <span>• {musician.city}</span>}
                        </div>
                        
                        <div className="flex items-center justify-center space-x-2 text-sm text-gold">
                          <Trophy className="w-4 h-4" />
                          <span>{musician.experience_level}</span>
                        </div>
                      </div>
                      
                      {musician.instruments && musician.instruments.length > 0 && (
                        <div className="mb-4">
                          <div className="flex flex-wrap justify-center gap-1">
                            {musician.instruments.slice(0, 3).map((instrument, index) => (
                              <span key={index} className="px-2 py-1 bg-sage/30 text-sage text-xs rounded-full">
                                🎵 {instrument}
                              </span>
                            ))}
                            {musician.instruments.length > 3 && (
                              <span className="px-2 py-1 bg-white/20 text-white/60 text-xs rounded-full">
                                +{musician.instruments.length - 3}
                              </span>
                            )}
                          </div>
                        </div>
                      )}
                      
                      {musician.genres && musician.genres.length > 0 && (
                        <div className="mb-4">
                          <div className="flex flex-wrap justify-center gap-1">
                            {musician.genres.slice(0, 2).map((genre, index) => (
                              <span key={index} className="px-2 py-1 bg-terracotta/30 text-terracotta text-xs rounded-full">
                                🎶 {genre}
                              </span>
                            ))}
                            {musician.genres.length > 2 && (
                              <span className="px-2 py-1 bg-white/20 text-white/60 text-xs rounded-full">
                                +{musician.genres.length - 2}
                              </span>
                            )}
                          </div>
                        </div>
                      )}
                      
                      <button className="w-full bg-gradient-to-r from-terracotta to-gold text-white py-2 rounded-xl font-semibold hover:shadow-lg transition-all flex items-center justify-center space-x-2">
                        <MessageCircle className="w-4 h-4" />
                        <span>Contacter</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Messages Tab */}
        {activeTab === 'messages' && (
          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
            <h3 className="text-xl font-semibold text-white mb-6 flex items-center space-x-2">
              <MessageCircle className="w-6 h-6" />
              <span>Messages Privés</span>
            </h3>
            
            {messages.length === 0 ? (
              <div className="text-center py-12">
                <MessageCircle className="w-16 h-16 text-white/40 mx-auto mb-4" />
                <p className="text-white/60 text-lg">Aucun message pour le moment...</p>
                <p className="text-white/40">Connectez-vous avec d'autres musiciens pour commencer à échanger !</p>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map(message => (
                  <div key={message.id} className="bg-white/10 rounded-xl p-4 border border-white/20">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h4 className="font-semibold text-white">
                          {message.sender.username} → {message.recipient.username}
                        </h4>
                        {message.subject && (
                          <p className="text-gold text-sm">{message.subject}</p>
                        )}
                      </div>
                      <span className="text-xs text-white/60">
                        {formatTimeAgo(message.created_at)}
                      </span>
                    </div>
                    <p className="text-white/80">{message.content}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Profile Tab */}
        {activeTab === 'profile' && (
          <div className="space-y-6">
            {!myProfile ? (
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20 text-center">
                <UserPlus className="w-16 h-16 text-white/40 mx-auto mb-4" />
                <h3 className="text-2xl font-semibold text-white mb-4">Créez votre profil musicien</h3>
                <p className="text-white/70 mb-6">
                  Rejoignez notre communauté en créant votre profil de musicien et connectez-vous avec des artistes du monde entier !
                </p>
                <button
                  onClick={() => setShowProfileForm(true)}
                  className="bg-gradient-to-r from-terracotta to-gold text-white px-8 py-3 rounded-xl font-semibold hover:shadow-lg transition-all flex items-center space-x-2 mx-auto"
                >
                  <Plus className="w-5 h-5" />
                  <span>Créer mon profil</span>
                </button>
              </div>
            ) : (
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20">
                <div className="text-center mb-6">
                  <div className="w-20 h-20 bg-gradient-to-br from-terracotta to-gold rounded-full flex items-center justify-center mx-auto mb-4">
                    <Music className="w-10 h-10 text-white" />
                  </div>
                  <h2 className="text-3xl font-bold text-white mb-2">{myProfile.stage_name}</h2>
                  <p className="text-gold">@{user.username}</p>
                  <div className="flex items-center justify-center space-x-4 mt-4">
                    <div className="flex items-center space-x-2 text-white/70">
                      <MapPin className="w-4 h-4" />
                      <span>{myProfile.region}</span>
                      {myProfile.city && <span>• {myProfile.city}</span>}
                    </div>
                    <div className="flex items-center space-x-2 text-gold">
                      <Trophy className="w-4 h-4" />
                      <span>{myProfile.experience_level}</span>
                    </div>
                  </div>
                </div>
                
                {myProfile.bio && (
                  <div className="mb-6">
                    <h4 className="text-lg font-semibold text-white mb-2">À propos</h4>
                    <p className="text-white/80">{myProfile.bio}</p>
                  </div>
                )}
                
                {myProfile.instruments && myProfile.instruments.length > 0 && (
                  <div className="mb-6">
                    <h4 className="text-lg font-semibold text-white mb-2">Instruments</h4>
                    <div className="flex flex-wrap gap-2">
                      {myProfile.instruments.map((instrument, index) => (
                        <span key={index} className="px-3 py-1 bg-sage/30 text-sage rounded-full">
                          🎵 {instrument}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {myProfile.genres && myProfile.genres.length > 0 && (
                  <div className="mb-6">
                    <h4 className="text-lg font-semibold text-white mb-2">Genres musicaux</h4>
                    <div className="flex flex-wrap gap-2">
                      {myProfile.genres.map((genre, index) => (
                        <span key={index} className="px-3 py-1 bg-terracotta/30 text-terracotta rounded-full">
                          🎶 {genre}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {myProfile.looking_for && myProfile.looking_for.length > 0 && (
                  <div className="mb-6">
                    <h4 className="text-lg font-semibold text-white mb-2">Recherche</h4>
                    <div className="flex flex-wrap gap-2">
                      {myProfile.looking_for.map((item, index) => (
                        <span key={index} className="px-3 py-1 bg-gold/30 text-gold rounded-full">
                          ✨ {item}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="flex justify-center">
                  <button
                    onClick={() => setShowProfileForm(true)}
                    className="bg-white/20 text-white px-6 py-2 rounded-xl font-semibold hover:bg-white/30 transition-colors"
                  >
                    Modifier le profil
                  </button>
                </div>
              </div>
            )}

            {/* Profile Form */}
            {showProfileForm && (
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
                <h3 className="text-xl font-semibold text-white mb-6">
                  {myProfile ? 'Modifier' : 'Créer'} votre profil musicien
                </h3>
                
                <form onSubmit={handleCreateProfile} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-white/70 text-sm mb-2">Nom de scène *</label>
                      <input
                        type="text"
                        value={profileForm.stage_name}
                        onChange={(e) => setProfileForm({ ...profileForm, stage_name: e.target.value })}
                        className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-xl text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-gold"
                        placeholder="Votre nom d'artiste..."
                        required
                      />
                    </div>
                    
                    <div>
                      <label className="block text-white/70 text-sm mb-2">Niveau</label>
                      <select
                        value={profileForm.experience_level}
                        onChange={(e) => setProfileForm({ ...profileForm, experience_level: e.target.value })}
                        className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-gold"
                      >
                        <option value="Débutant">Débutant</option>
                        <option value="Intermédiaire">Intermédiaire</option>
                        <option value="Avancé">Avancé</option>
                        <option value="Professionnel">Professionnel</option>
                      </select>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-white/70 text-sm mb-2">Biographie</label>
                    <textarea
                      value={profileForm.bio}
                      onChange={(e) => setProfileForm({ ...profileForm, bio: e.target.value })}
                      rows={3}
                      className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-xl text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-gold resize-none"
                      placeholder="Parlez-nous de votre parcours musical..."
                    />
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-white/70 text-sm mb-2">Région</label>
                      <select
                        value={profileForm.region}
                        onChange={(e) => setProfileForm({ ...profileForm, region: e.target.value })}
                        className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-gold"
                      >
                        <option value="International">International</option>
                        <option value="Afrique">Afrique</option>
                        <option value="Europe">Europe</option>
                        <option value="Asie">Asie</option>
                        <option value="Amérique">Amérique</option>
                        <option value="Océanie">Océanie</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-white/70 text-sm mb-2">Ville</label>
                      <input
                        type="text"
                        value={profileForm.city}
                        onChange={(e) => setProfileForm({ ...profileForm, city: e.target.value })}
                        className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-xl text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-gold"
                        placeholder="Votre ville..."
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-white/70 text-sm mb-2">Instruments (séparés par des virgules)</label>
                    <input
                      type="text"
                      value={profileForm.instruments.join(', ')}
                      onChange={(e) => setProfileForm({ 
                        ...profileForm, 
                        instruments: e.target.value.split(',').map(s => s.trim()).filter(s => s) 
                      })}
                      className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-xl text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-gold"
                      placeholder="Guitare, Piano, Balafon..."
                    />
                  </div>
                  
                  <div>
                    <label className="block text-white/70 text-sm mb-2">Genres musicaux (séparés par des virgules)</label>
                    <input
                      type="text"
                      value={profileForm.genres.join(', ')}
                      onChange={(e) => setProfileForm({ 
                        ...profileForm, 
                        genres: e.target.value.split(',').map(s => s.trim()).filter(s => s) 
                      })}
                      className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-xl text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-gold"
                      placeholder="Bikutsi, Jazz, Afrobeat..."
                    />
                  </div>
                  
                  <div>
                    <label className="block text-white/70 text-sm mb-2">Recherche (séparés par des virgules)</label>
                    <input
                      type="text"
                      value={profileForm.looking_for.join(', ')}
                      onChange={(e) => setProfileForm({ 
                        ...profileForm, 
                        looking_for: e.target.value.split(',').map(s => s.trim()).filter(s => s) 
                      })}
                      className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-xl text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-gold"
                      placeholder="Collaboration, Jam Session, Apprentissage..."
                    />
                  </div>
                  
                  <div className="flex space-x-4">
                    <button
                      type="submit"
                      className="bg-gradient-to-r from-terracotta to-gold text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg transition-all flex items-center space-x-2"
                    >
                      <span>{myProfile ? 'Mettre à jour' : 'Créer'} le profil</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowProfileForm(false)}
                      className="bg-white/20 text-white px-6 py-3 rounded-xl font-semibold hover:bg-white/30 transition-colors"
                    >
                      Annuler
                    </button>
                  </div>
                </form>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default CommunityPage;
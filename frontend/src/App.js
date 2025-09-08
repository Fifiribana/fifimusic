import React, { useState, useEffect, useRef } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Configuration Axios
axios.defaults.headers.common['Content-Type'] = 'application/json';

// Context pour l'authentification
const AuthContext = React.createContext();

// Hook pour l'authentification
const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Composant de Gestion Photo de Profil
function ProfilePictureManager({ user, onUpdate }) {
  const [isEditing, setIsEditing] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validation
      if (!file.type.startsWith('image/')) {
        alert('Veuillez sélectionner une image');
        return;
      }
      
      if (file.size > 5 * 1024 * 1024) {
        alert('La taille du fichier doit être inférieure à 5MB');
        return;
      }

      // Preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreviewUrl(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUpload = async () => {
    const file = fileInputRef.current?.files[0];
    if (!file) return;

    setUploading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`${API}/users/me/avatar`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (onUpdate) {
        onUpdate(response.data.avatar_url);
      }
      
      setIsEditing(false);
      setPreviewUrl(null);
      alert('Photo de profil mise à jour avec succès! 🎉');
      
    } catch (error) {
      console.error('Erreur upload avatar:', error);
      alert('Erreur lors de la mise à jour: ' + (error.response?.data?.detail || 'Erreur inconnue'));
    } finally {
      setUploading(false);
    }
  };

  const handleRemove = async () => {
    if (!confirm('Supprimer votre photo de profil?')) return;

    try {
      const response = await axios.delete(`${API}/users/me/avatar`);
      
      if (onUpdate) {
        onUpdate(response.data.avatar_url);
      }
      
      alert('Photo de profil supprimée');
    } catch (error) {
      console.error('Erreur suppression avatar:', error);
      alert('Erreur lors de la suppression');
    }
  };

  const getAvatarDisplay = () => {
    if (previewUrl) return previewUrl;
    if (user?.avatar_url) return user.avatar_url;
    
    // Avatar par défaut avec initiales
    const initials = user?.display_name 
      ? user.display_name.split(' ').map(n => n[0]).join('').toUpperCase()
      : user?.username?.[0]?.toUpperCase() || '?';
    
    return `https://api.dicebear.com/7.x/initials/svg?seed=${initials}&backgroundColor=667eea&color=white`;
  };

  return (
    <div className="profile-picture-manager">
      <div className="avatar-container">
        <div className="avatar-display">
          <img 
            src={getAvatarDisplay()} 
            alt="Photo de profil"
            className="profile-avatar"
            onError={(e) => {
              e.target.src = `https://api.dicebear.com/7.x/initials/svg?seed=${user?.username || 'User'}&backgroundColor=e2e8f0`;
            }}
          />
          
          {!isEditing && (
            <button 
              className="edit-avatar-btn"
              onClick={() => setIsEditing(true)}
              title="Modifier la photo"
            >
              📷
            </button>
          )}
        </div>

        {isEditing && (
          <div className="avatar-editor">
            <div className="upload-controls">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="file-input-hidden"
              />
              
              <button 
                className="select-photo-btn"
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
              >
                📁 Choisir une photo
              </button>

              {previewUrl && (
                <div className="upload-actions">
                  <button 
                    className="upload-btn"
                    onClick={handleUpload}
                    disabled={uploading}
                  >
                    {uploading ? '⏳ Upload...' : '✅ Confirmer'}
                  </button>
                  
                  <button 
                    className="cancel-btn"
                    onClick={() => {
                      setIsEditing(false);
                      setPreviewUrl(null);
                    }}
                    disabled={uploading}
                  >
                    ❌ Annuler
                  </button>
                </div>
              )}

              {user?.avatar_url && (
                <button 
                  className="remove-avatar-btn"
                  onClick={handleRemove}
                  disabled={uploading}
                >
                  🗑️ Supprimer
                </button>
              )}
            </div>

            <div className="avatar-tips">
              <p>💡 Conseils :</p>
              <ul>
                <li>Format: JPG, PNG, GIF</li>
                <li>Taille max: 5MB</li>
                <li>Recommandé: 400x400px</li>
                <li>Photo claire de votre visage</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Composant Avatar Mini pour Navigation
function UserAvatar({ user, size = 'medium', showName = false, onClick }) {
  const getAvatarUrl = () => {
    if (user?.avatar_url) return user.avatar_url;
    
    const initials = user?.display_name 
      ? user.display_name.split(' ').map(n => n[0]).join('').toUpperCase()
      : user?.username?.[0]?.toUpperCase() || '?';
    
    return `https://api.dicebear.com/7.x/initials/svg?seed=${initials}&backgroundColor=667eea&color=white`;
  };

  const sizeClass = {
    small: 'avatar-small',
    medium: 'avatar-medium', 
    large: 'avatar-large'
  }[size];

  return (
    <div className={`user-avatar ${sizeClass}`} onClick={onClick}>
      <img 
        src={getAvatarUrl()} 
        alt={user?.display_name || user?.username}
        className="avatar-img"
        onError={(e) => {
          e.target.src = `https://api.dicebear.com/7.x/initials/svg?seed=${user?.username || 'U'}&backgroundColor=e2e8f0`;
        }}
      />
      {showName && user && (
        <span className="avatar-name">{user.display_name || user.username}</span>
      )}
    </div>
  );
}

// Provider d'authentification
function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('tuneme_token'));
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      loadUserProfile();
    }
  }, [token]);

  const loadUserProfile = async () => {
    try {
      const response = await axios.get(`${API}/users/me`);
      setUser(response.data);
    } catch (error) {
      console.error('Failed to load user profile:', error);
      logout();
    }
  };

  const login = async (email, password) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/auth/login`, { email, password });
      const { token: newToken, user: userData } = response.data;
      
      setToken(newToken);
      setUser(userData);
      localStorage.setItem('tuneme_token', newToken);
      axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/auth/register`, userData);
      const { token: newToken, user: newUser } = response.data;
      
      setToken(newToken);
      setUser(newUser);
      localStorage.setItem('tuneme_token', newToken);
      axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('tuneme_token');
    delete axios.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      token, 
      loading, 
      login, 
      register, 
      logout, 
      loadUserProfile,
      isAuthenticated: !!token 
    }}>
      {children}
    </AuthContext.Provider>
  );
}

// Composant Player Vidéo Avancé avec gestion d'erreurs
function VideoPlayer({ video, onEnded }) {
  const videoRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [videoError, setVideoError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const togglePlay = () => {
    if (videoRef.current && !videoError) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play().catch(error => {
          console.error('Error playing video:', error);
          setVideoError(true);
        });
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration);
      setIsLoading(false);
    }
  };

  const handleVideoError = (e) => {
    console.error('Video loading error:', e);
    setVideoError(true);
    setIsLoading(false);
  };

  const handleCanPlay = () => {
    setIsLoading(false);
    setVideoError(false);
  };

  const handleSeek = (e) => {
    const seekTime = (e.target.value / 100) * duration;
    if (videoRef.current && !videoError) {
      videoRef.current.currentTime = seekTime;
      setCurrentTime(seekTime);
    }
  };

  const handleVolumeChange = (e) => {
    const newVolume = e.target.value / 100;
    setVolume(newVolume);
    if (videoRef.current) {
      videoRef.current.volume = newVolume;
    }
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      videoRef.current.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className="video-player">
      <div className="video-container">
        {videoError ? (
          <div className="video-error">
            <div className="error-content">
              <h3>🎬 Aperçu Vidéo</h3>
              <p>Vidéo en cours de traitement...</p>
              <div className="video-placeholder">
                <img 
                  src={video.thumbnail_url} 
                  alt={video.title}
                  className="placeholder-thumbnail"
                  onError={(e) => {
                    e.target.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 225'%3E%3Crect width='400' height='225' fill='%23667eea'/%3E%3Ctext x='200' y='112.5' text-anchor='middle' fill='white' font-size='20'%3E🎬 TuneMe Video%3C/text%3E%3C/svg%3E";
                  }}
                />
                <div className="placeholder-overlay">
                  <div className="play-icon">▶️</div>
                  <p>Cliquez pour lire la vidéo</p>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <>
            {isLoading && (
              <div className="video-loading">
                <div className="loading-spinner"></div>
                <p>Chargement de la vidéo...</p>
              </div>
            )}
            <video
              ref={videoRef}
              src={video.video_url}
              poster={video.thumbnail_url}
              onTimeUpdate={handleTimeUpdate}
              onLoadedMetadata={handleLoadedMetadata}
              onError={handleVideoError}
              onCanPlay={handleCanPlay}
              onEnded={onEnded}
              className="video-element"
              crossOrigin="anonymous"
            />
          </>
        )}
        
        <div className="video-controls">
          <button onClick={togglePlay} className="play-btn" disabled={videoError}>
            {isPlaying ? '⏸️' : '▶️'}
          </button>
          
          <input
            type="range"
            min="0"
            max="100"
            value={duration ? (currentTime / duration) * 100 : 0}
            onChange={handleSeek}
            className="progress-bar"
            disabled={videoError}
          />
          
          <span className="time-display">
            {formatTime(currentTime)} / {formatTime(duration)}
          </span>
          
          <input
            type="range"
            min="0"
            max="100"
            value={volume * 100}
            onChange={handleVolumeChange}
            className="volume-slider"
            disabled={videoError}
          />
          
          <button onClick={toggleFullscreen} className="fullscreen-btn" disabled={videoError}>
            {isFullscreen ? '📱' : '📺'}
          </button>
        </div>
      </div>
    </div>
  );
}

// Composant Card Vidéo
function VideoCard({ video, onClick }) {
  const formatViews = (views) => {  
    if (views >= 1000000) return `${(views / 1000000).toFixed(1)}M`;
    if (views >= 1000) return `${(views / 1000).toFixed(1)}K`;
    return views.toString();
  };

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="video-card" onClick={() => onClick(video)}>
      <div className="video-thumbnail">
        <img src={video.thumbnail_url} alt={video.title} />
        <div className="video-duration">{formatDuration(video.duration)}</div>
        {video.is_ad && <div className="ad-badge">📺 AD</div>}
        <div className="ai-score">
          🤖 {video.ai_analysis?.engagement_prediction || 'N/A'}
        </div>
      </div>
      
      <div className="video-info">
        <h3 className="video-title">{video.title}</h3>
        <div className="video-meta">
          <span className="creator">@{video.creator_username}</span>
          <span className="views">{formatViews(video.views_count)} vues</span>
          <span className="category">{video.category}</span>
        </div>
        
        <div className="video-stats">
          <span className="likes">👍 {video.likes_count}</span>
          <span className="comments">💬 {video.comments_count}</span>
          {video.is_ad && (
            <span className="revenue">💰 ${(video.revenue_generated || 0).toFixed(2)}</span>
          )}
        </div>
        
        <div className="video-tags">
          {video.tags.slice(0, 3).map(tag => (
            <span key={tag} className="tag">{tag}</span>
          ))}
        </div>
        
        {video.ai_generated_tags.length > 0 && (
          <div className="ai-tags">
            <span className="ai-label">🤖 AI:</span>
            {video.ai_generated_tags.slice(0, 2).map(tag => (
              <span key={tag} className="ai-tag">{tag}</span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// Composant Upload Vidéo
function VideoUpload({ onSuccess }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'Entertainment',
    tags: '',
    is_ad: false,
    ad_type: '',
    target_audience: ''
  });
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [aiAnalyzing, setAiAnalyzing] = useState(false);

  const categories = [
    'Entertainment', 'Education', 'Technology', 'Business', 'Music', 
    'Gaming', 'Sports', 'News', 'Lifestyle', 'Travel', 'Food', 'Fashion'
  ];

  const adTypes = [
    'tv_commercial', 'social_media', 'corporate', 'product_demo', 
    'brand_awareness', 'promotional'
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    setAiAnalyzing(true);

    const uploadData = new FormData();
    uploadData.append('file', file);
    uploadData.append('title', formData.title);
    uploadData.append('description', formData.description);
    uploadData.append('category', formData.category);
    uploadData.append('tags', formData.tags);
    uploadData.append('is_ad', formData.is_ad);
    uploadData.append('ad_type', formData.ad_type);
    uploadData.append('target_audience', formData.target_audience);

    try {
      const response = await axios.post(`${API}/videos/upload`, uploadData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setAiAnalyzing(false);
      onSuccess(response.data);
      
      // Reset form
      setFormData({
        title: '',
        description: '',
        category: 'Entertainment',
        tags: '',
        is_ad: false,
        ad_type: '',
        target_audience: ''
      });
      setFile(null);
      
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed: ' + (error.response?.data?.detail || 'Unknown error'));
    } finally {
      setUploading(false);
      setAiAnalyzing(false);
    }
  };

  return (
    <div className="upload-container">
      <div className="upload-header">
        <h2>📤 Télécharger une Vidéo</h2>
        <p>Partagez vos créations publicitaires avec le monde</p>
      </div>

      <form onSubmit={handleSubmit} className="upload-form">
        <div className="file-upload">
          <input
            type="file"
            accept="video/*"
            onChange={(e) => setFile(e.target.files[0])}
            required
            className="file-input"
          />
          {file && (
            <div className="file-preview">
              <span>📹 {file.name}</span>
              <span>{(file.size / 1024 / 1024).toFixed(2)} MB</span>
            </div>
          )}
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Titre *</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              required
              placeholder="Titre accrocheur de votre vidéo..."
            />
          </div>
        </div>

        <div className="form-group">
          <label>Description</label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({...formData, description: e.target.value})}
            placeholder="Décrivez votre vidéo, son objectif, votre message..."
            rows={4}
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Catégorie</label>
            <select
              value={formData.category}
              onChange={(e) => setFormData({...formData, category: e.target.value})}
            >
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Tags (séparés par des virgules)</label>
            <input
              type="text"
              value={formData.tags}
              onChange={(e) => setFormData({...formData, tags: e.target.value})}
              placeholder="marketing, publicité, créatif..."
            />
          </div>
        </div>

        <div className="ad-options">
          <div className="checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={formData.is_ad}
                onChange={(e) => setFormData({...formData, is_ad: e.target.checked})}
              />
              <span>🎯 Ceci est une publicité</span>
            </label>
          </div>

          {formData.is_ad && (
            <>
              <div className="form-group">
                <label>Type de publicité</label>
                <select
                  value={formData.ad_type}
                  onChange={(e) => setFormData({...formData, ad_type: e.target.value})}
                >
                  <option value="">Sélectionner un type</option>
                  {adTypes.map(type => (
                    <option key={type} value={type}>
                      {type.replace('_', ' ').toUpperCase()}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Public cible (séparé par des virgules)</label>
                <input
                  type="text"
                  value={formData.target_audience}
                  onChange={(e) => setFormData({...formData, target_audience: e.target.value})}
                  placeholder="18-35 ans, gamers, professionnels..."
                />
              </div>
            </>
          )}
        </div>

        <button 
          type="submit" 
          disabled={uploading || !file}
          className="upload-btn"
        >
          {uploading ? (
            aiAnalyzing ? '🤖 Analyse IA en cours...' : '📤 Téléchargement...'
          ) : (
            '🚀 Publier la Vidéo'
          )}
        </button>
      </form>
    </div>
  );
}

// Composant Page d'Accueil
function HomePage() {
  const [videos, setVideos] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [filter, setFilter] = useState('all');
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    loadVideos();
    if (isAuthenticated) {
      loadRecommendations();
    }
  }, [filter, isAuthenticated]);

  const loadVideos = async () => {
    try {
      const params = {};
      if (filter === 'ads') params.is_ad = true;
      if (filter === 'regular') params.is_ad = false;
      
      const response = await axios.get(`${API}/videos`, { params });
      setVideos(response.data);
    } catch (error) {
      console.error('Failed to load videos:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadRecommendations = async () => {
    try {
      const response = await axios.get(`${API}/recommendations`);
      setRecommendations(response.data);
    } catch (error) {
      console.error('Failed to load recommendations:', error);
    }
  };

  const handleVideoClick = async (video) => {
    setSelectedVideo(video);
    
    // Increment view count
    try {
      await axios.get(`${API}/videos/${video.id}`);
    } catch (error) {
      console.error('Failed to increment view:', error);
    }
  };

  const handleLike = async (videoId) => {
    if (!isAuthenticated) return;
    
    try {
      await axios.post(`${API}/videos/${videoId}/like`);
      // Refresh video data
      loadVideos();
    } catch (error) {
      console.error('Failed to like video:', error);
    }
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner"></div>
        <p>Chargement des vidéos...</p>
      </div>
    );
  }

  return (
    <div className="home-page">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h1>🎬 TuneMe (TM)</h1>
          <p>La Plateforme Révolutionnaire pour vos Vidéos Publicitaires</p>
          <div className="hero-stats">
            <div className="stat">
              <span className="stat-number">{videos.length}</span>
              <span className="stat-label">Vidéos</span>
            </div>
            <div className="stat">
              <span className="stat-number">{videos.filter(v => v.is_ad).length}</span>
              <span className="stat-label">Publicités</span>
            </div>
            <div className="stat">
              <span className="stat-number">🤖 IA</span>
              <span className="stat-label">Alimenté</span>
            </div>
          </div>
        </div>
      </section>

      {/* Filtres */}
      <div className="filter-bar">
        <button 
          className={filter === 'all' ? 'active' : ''}
          onClick={() => setFilter('all')}
        >
          🎯 Toutes les vidéos
        </button>
        <button 
          className={filter === 'ads' ? 'active' : ''}
          onClick={() => setFilter('ads')}
        >
          📺 Publicités seulement
        </button>
        <button 
          className={filter === 'regular' ? 'active' : ''}
          onClick={() => setFilter('regular')}
        >
          🎬 Contenu régulier
        </button>
      </div>

      {/* Recommandations IA */}
      {isAuthenticated && recommendations.length > 0 && (
        <section className="recommendations-section">
          <h2>🤖 Recommandations IA pour vous</h2>
          <div className="videos-grid">
            {recommendations.slice(0, 4).map(video => (
              <VideoCard 
                key={video.id} 
                video={video} 
                onClick={handleVideoClick}
              />
            ))}
          </div>
        </section>
      )}

      {/* Grille de Vidéos */}
      <section className="videos-section">
        <h2>
          {filter === 'all' ? '🌟 Toutes les Vidéos' : 
           filter === 'ads' ? '📺 Publicités Tendance' : 
           '🎬 Contenu Créatif'}
        </h2>
        
        {videos.length === 0 ? (
          <div className="no-videos">
            <h3>Aucune vidéo trouvée</h3>
            <p>Soyez le premier à partager votre création!</p>
          </div>
        ) : (
          <div className="videos-grid">
            {videos.map(video => (
              <VideoCard 
                key={video.id} 
                video={video} 
                onClick={handleVideoClick}
              />
            ))}
          </div>
        )}
      </section>

      {/* Modal Vidéo */}
      {selectedVideo && (
        <div className="video-modal" onClick={() => setSelectedVideo(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button 
              className="close-btn"
              onClick={() => setSelectedVideo(null)}
            >
              ✕
            </button>
            
            <VideoPlayer 
              video={selectedVideo}
              onEnded={() => console.log('Video ended')}
            />
            
            <div className="video-details">
              <h2>{selectedVideo.title}</h2>
              <div className="video-actions">
                <button 
                  className="like-btn"
                  onClick={() => handleLike(selectedVideo.id)}
                >
                  👍 {selectedVideo.likes_count}
                </button>
                <button className="share-btn">📤 Partager</button>
                {selectedVideo.is_ad && (
                  <span className="ad-revenue">
                    💰 ${(selectedVideo.revenue_generated || 0).toFixed(2)} généré
                  </span>
                )}
              </div>
              
              <div className="creator-info">
                <span>Créé par @{selectedVideo.creator_username}</span>
                <span>{selectedVideo.views_count} vues</span>
              </div>
              
              <p className="description">{selectedVideo.description}</p>
              
              {selectedVideo.ai_analysis && (
                <div className="ai-insights">
                  <h4>🤖 Insights IA</h4>
                  <div className="insight-grid">
                    <div className="insight">
                      <span className="label">Engagement prédit:</span>
                      <span className="value">{selectedVideo.ai_analysis.engagement_prediction}/10</span>
                    </div>
                    <div className="insight">
                      <span className="label">Qualité contenu:</span>
                      <span className="value">{selectedVideo.ai_analysis.content_quality}</span>
                    </div>
                    <div className="insight">
                      <span className="label">Potentiel monétisation:</span>
                      <span className="value">{selectedVideo.ai_analysis.monetization_potential}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Composant Dashboard Créateur avec Photo de Profil
function CreatorDashboard() {
  const { user, loadUserProfile } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [showUpload, setShowUpload] = useState(false);
  const [userVideos, setUserVideos] = useState([]);
  const [showProfileEdit, setShowProfileEdit] = useState(false);

  useEffect(() => {
    if (user) {
      loadAnalytics();
      loadUserVideos();
    }
  }, [user]);

  const loadAnalytics = async () => {
    try {
      const response = await axios.get(`${API}/analytics/channel/${user.id}`);
      setAnalytics(response.data);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    }
  };

  const loadUserVideos = async () => {
    try {
      const response = await axios.get(`${API}/videos`);
      const filteredVideos = response.data.filter(v => v.creator_username === user.username);
      setUserVideos(filteredVideos);
    } catch (error) {
      console.error('Failed to load user videos:', error);
    }
  };

  const handleUploadSuccess = (newVideo) => {
    setUserVideos([newVideo, ...userVideos]);
    setShowUpload(false);
    loadAnalytics();
    alert('Vidéo téléchargée avec succès! 🎉');
  };

  const handleAvatarUpdate = async (newAvatarUrl) => {
    // Refresh user profile
    if (loadUserProfile) {
      await loadUserProfile();
    }
  };

  if (!analytics) {
    return <div className="loading-screen">Chargement du dashboard...</div>;
  }

  return (
    <div className="creator-dashboard">
      <header className="dashboard-header">
        <div className="creator-profile-section">
          <div className="profile-info">
            <UserAvatar user={user} size="large" />
            <div className="profile-details">
              <h1>📊 Dashboard Créateur</h1>
              <p>Bienvenue, {user.display_name}!</p>
              <button 
                className="edit-profile-btn"
                onClick={() => setShowProfileEdit(!showProfileEdit)}
              >
                ⚙️ Modifier le profil
              </button>
            </div>
          </div>
          
          <button 
            className="upload-toggle-btn"
            onClick={() => setShowUpload(!showUpload)}
          >
            {showUpload ? '📊 Voir Analytics' : '📤 Télécharger Vidéo'}
          </button>
        </div>

        {/* Section d'édition du profil */}
        {showProfileEdit && (
          <div className="profile-edit-section">
            <div className="profile-edit-card">
              <h3>📸 Photo de Profil</h3>
              <ProfilePictureManager 
                user={user} 
                onUpdate={handleAvatarUpdate}
              />
            </div>
          </div>
        )}
      </header>

      {showUpload ? (
        <VideoUpload onSuccess={handleUploadSuccess} />
      ) : (
        <>
          {/* Analytics Cards */}
          <div className="analytics-grid">
            <div className="analytics-card">
              <div className="card-icon">📹</div>
              <div className="card-content">
                <h3>{analytics.total_videos}</h3>
                <p>Vidéos Publiées</p>
              </div>
            </div>
            
            <div className="analytics-card">
              <div className="card-icon">👀</div>
              <div className="card-content">
                <h3>{analytics.total_views.toLocaleString()}</h3>
                <p>Vues Totales</p>
              </div>
            </div>
            
            <div className="analytics-card">
              <div className="card-icon">👥</div>
              <div className="card-content">
                <h3>{analytics.total_subscribers}</h3>
                <p>Abonnés</p>
              </div>
            </div>
            
            <div className="analytics-card">
              <div className="card-icon">💰</div>
              <div className="card-content">
                <h3>${(analytics.total_revenue || 0).toFixed(2)}</h3>
                <p>Revenus Générés</p>
              </div>
            </div>
            
            <div className="analytics-card">
              <div className="card-icon">📈</div>
              <div className="card-content">
                <h3>{analytics.avg_engagement_rate}%</h3>
                <p>Taux d'Engagement</p>
              </div>
            </div>
            
            <div className="analytics-card">
              <div className="card-icon">🤖</div>
              <div className="card-content">
                <h3>IA</h3>
                <p>Insights Activés</p>
              </div>
            </div>
          </div>

          {/* Vidéos de l'utilisateur */}
          <section className="user-videos">
            <h2>📹 Vos Vidéos ({userVideos.length})</h2>
            {userVideos.length === 0 ? (
              <div className="no-content">
                <h3>Aucune vidéo publiée</h3>
                <p>Commencez à créer du contenu incroyable!</p>
                <button 
                  className="cta-btn"
                  onClick={() => setShowUpload(true)}
                >
                  📤 Télécharger votre première vidéo
                </button>
              </div>
            ) : (
              <div className="videos-grid">
                {userVideos.map(video => (
                  <VideoCard key={video.id} video={video} onClick={() => {}} />
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}

// Composant Login/Register
function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    username: '',
    display_name: '',
    bio: ''
  });
  const { login, register, loading } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const result = isLogin 
      ? await login(formData.email, formData.password)
      : await register(formData);
    
    if (!result.success) {
      alert(result.error);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <h1>🎬 TuneMe (TM)</h1>
          <p>Rejoignez la révolution vidéo publicitaire</p>
        </div>

        <div className="auth-tabs">
          <button 
            className={isLogin ? 'active' : ''}
            onClick={() => setIsLogin(true)}
          >
            Connexion
          </button>
          <button 
            className={!isLogin ? 'active' : ''}
            onClick={() => setIsLogin(false)}
          >
            Inscription
          </button>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {!isLogin && (
            <>
              <div className="form-group">
                <label>Nom d'utilisateur</label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({...formData, username: e.target.value})}
                  required
                  placeholder="votre_nom_utilisateur"
                />
              </div>
              
              <div className="form-group">
                <label>Nom d'affichage</label>
                <input
                  type="text"
                  value={formData.display_name}
                  onChange={(e) => setFormData({...formData, display_name: e.target.value})}
                  required
                  placeholder="Votre Nom Public"
                />
              </div>
            </>
          )}

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              required
              placeholder="votre@email.com"
            />
          </div>

          <div className="form-group">
            <label>Mot de passe</label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              required
              placeholder="••••••••"
            />
          </div>

          {!isLogin && (
            <div className="form-group">
              <label>Bio (optionnel)</label>
              <textarea
                value={formData.bio}
                onChange={(e) => setFormData({...formData, bio: e.target.value})}
                placeholder="Parlez-nous de vous..."
                rows={3}
              />
            </div>
          )}

          <button type="submit" disabled={loading} className="auth-btn">
            {loading ? '⏳ Traitement...' : (isLogin ? '🚀 Se Connecter' : '🎉 Créer un Compte')}
          </button>
        </form>

        <div className="auth-features">
          <h3>✨ Fonctionnalités TuneMe</h3>
          <ul>
            <li>🤖 Analyse IA de vos vidéos</li>
            <li>📊 Analytics avancées en temps réel</li>
            <li>💰 Monétisation intelligente</li>
            <li>🎯 Ciblage publicitaire précis</li>
            <li>📱 Interface ultra-moderne</li>
            <li>🚀 Recommandations personnalisées</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

// Composant Navigation
function Navigation() {
  const { user, logout, isAuthenticated } = useAuth();
  const [currentPage, setCurrentPage] = useState('home');

  return (
    <nav className="navigation">
      <div className="nav-content">
        <button 
          className={currentPage === 'home' ? 'active' : ''}
          onClick={() => setCurrentPage('home')}
        >
          🏠 Accueil
        </button>
        
        {isAuthenticated && (
          <button 
            className={currentPage === 'dashboard' ? 'active' : ''}
            onClick={() => setCurrentPage('dashboard')}
          >
            📊 Dashboard
          </button>
        )}
        
        <div className="nav-user">
          {isAuthenticated ? (
            <>
              <span className="user-greeting">Salut, {user?.display_name}! 👋</span>
              <button onClick={logout} className="logout-btn">
                🚪 Déconnexion
              </button>
            </>
          ) : (
            <span className="login-prompt">Connectez-vous pour accéder aux fonctionnalités avancées</span>
          )}
        </div>
      </div>
      
      {/* Page Content */}
      <div className="page-content">
        {currentPage === 'home' && <HomePage />}
        {currentPage === 'dashboard' && isAuthenticated && <CreatorDashboard />}
      </div>
    </nav>
  );
}

// Application principale
function App() {
  return (
    <AuthProvider>
      <div className="App">
        <BrowserRouter>
          <AppContent />
        </BrowserRouter>
      </div>
    </AuthProvider>
  );
}

function AppContent() {
  const { isAuthenticated } = useAuth();
  
  return (
    <Routes>
      <Route 
        path="/" 
        element={isAuthenticated ? <Navigation /> : <AuthPage />} 
      />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

export default App;
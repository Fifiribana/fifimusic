import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { 
  Upload, 
  Music, 
  Image, 
  Trash2, 
  Save, 
  FileAudio, 
  Camera, 
  Plus,
  Edit3,
  Eye,
  X
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminPage = () => {
  // Get auth context manually to avoid circular imports
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [toast, setToast] = useState({
    success: (msg) => console.log('✅', msg),
    error: (msg) => console.log('❌', msg),
    info: (msg) => console.log('ℹ️', msg),
    music: (msg) => console.log('🎵', msg)
  });
  const [myTracks, setMyTracks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [showUploadForm, setShowUploadForm] = useState(false);

  // Form data
  const [formData, setFormData] = useState({
    title: '',
    region: 'Afrique',
    style: 'Bikutsi Moderne',
    instrument: '',
    duration: 0,
    bpm: 128,
    mood: 'Énergique',
    price: 4.99,
    description: ''
  });

  // Files
  const [audioFile, setAudioFile] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [previewFile, setPreviewFile] = useState(null);

  // Preview URLs
  const [audioPreview, setAudioPreview] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);

  useEffect(() => {
    // Verify token and get user info
    if (token) {
      axios.get(`${API}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      .then(response => {
        setUser(response.data);
      })
      .catch(() => {
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
      });
    }
  }, [token]);

  useEffect(() => {
    if (user && token) {
      fetchMyTracks();
    }
  }, [user, token]);

  const fetchMyTracks = async () => {
    try {
      const response = await axios.get(`${API}/admin/my-tracks`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMyTracks(response.data);
    } catch (error) {
      console.error('Error fetching tracks:', error);
      toast.error('Erreur lors du chargement de vos pistes');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleAudioFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setAudioFile(file);
      setAudioPreview(URL.createObjectURL(file));
      
      // Try to get duration from audio file
      const audio = new Audio();
      audio.src = URL.createObjectURL(file);
      audio.addEventListener('loadedmetadata', () => {
        setFormData(prev => ({
          ...prev,
          duration: Math.round(audio.duration)
        }));
      });
    }
  };

  const handleImageFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImageFile(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handlePreviewFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setPreviewFile(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!audioFile || !imageFile) {
      toast.error('Veuillez sélectionner un fichier audio et une image');
      return;
    }

    setUploading(true);
    
    try {
      const formDataUpload = new FormData();
      
      // Add track data
      Object.keys(formData).forEach(key => {
        formDataUpload.append(key, formData[key]);
      });
      
      // Add files
      formDataUpload.append('audio_file', audioFile);
      formDataUpload.append('image_file', imageFile);
      if (previewFile) {
        formDataUpload.append('preview_file', previewFile);
      }

      const response = await axios.post(`${API}/tracks/upload`, formDataUpload, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      toast.success(`🎵 "${formData.title}" ajouté avec succès !`);
      
      // Reset form
      setFormData({
        title: '',
        region: 'Afrique',
        style: 'Bikutsi Moderne',
        instrument: '',
        duration: 0,
        bpm: 128,
        mood: 'Énergique',
        price: 4.99,
        description: ''
      });
      setAudioFile(null);
      setImageFile(null);
      setPreviewFile(null);
      setAudioPreview(null);
      setImagePreview(null);
      setShowUploadForm(false);
      
      // Refresh tracks list
      fetchMyTracks();
      
    } catch (error) {
      console.error('Error uploading track:', error);
      toast.error('Erreur lors de l\'upload de la piste');
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteTrack = async (trackId, trackTitle) => {
    if (!window.confirm(`Êtes-vous sûr de vouloir supprimer "${trackTitle}" ?`)) {
      return;
    }

    try {
      await axios.delete(`${API}/admin/tracks/${trackId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success(`🗑️ "${trackTitle}" supprimé avec succès`);
      fetchMyTracks();
    } catch (error) {
      console.error('Error deleting track:', error);
      toast.error('Erreur lors de la suppression');
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-charcoal to-sage/20 flex items-center justify-center">
        <div className="bg-white rounded-2xl p-8 text-center">
          <h2 className="text-2xl font-bold text-charcoal mb-4">Accès Restreint</h2>
          <p className="text-charcoal/70">Veuillez vous connecter pour accéder à l'administration</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-charcoal via-charcoal/95 to-sage/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">
            🎵 Administration US EXPLO
          </h1>
          <p className="text-xl text-white/80">
            Bonjour <span className="text-gold font-semibold">{user.username}</span> ! 
            Gérez vos créations musicales
          </p>
          <div className="w-32 h-1 bg-gradient-to-r from-terracotta to-gold mx-auto rounded-full mt-4"></div>
        </div>

        {/* Actions */}
        <div className="mb-8 text-center">
          <button
            onClick={() => setShowUploadForm(!showUploadForm)}
            className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-terracotta to-gold hover:from-gold hover:to-terracotta text-white font-bold rounded-full transition-all transform hover:scale-105 shadow-xl"
          >
            <Plus className="w-5 h-5 mr-2" />
            {showUploadForm ? 'Masquer le formulaire' : 'Ajouter une nouvelle piste'}
          </button>
        </div>

        {/* Upload Form */}
        {showUploadForm && (
          <div className="bg-white/10 backdrop-blur-md rounded-3xl p-8 mb-12 border border-white/20">
            <h2 className="text-3xl font-bold text-white mb-8 text-center">
              🎼 Ajouter votre création
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Basic Info */}
                <div className="space-y-4">
                  <div>
                    <label className="block text-white font-semibold mb-2">Titre de la piste *</label>
                    <input
                      type="text"
                      name="title"
                      value={formData.title}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-terracotta"
                      placeholder="Ex: Bikutsi 2025"
                      required
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-white font-semibold mb-2">Région</label>
                      <select
                        name="region"
                        value={formData.region}
                        onChange={handleInputChange}
                        className="w-full px-4 py-3 bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-terracotta"
                      >
                        <option value="Afrique">Afrique</option>
                        <option value="Asie">Asie</option>
                        <option value="Europe">Europe</option>
                        <option value="Amérique du Sud">Amérique du Sud</option>
                        <option value="Amérique du Nord">Amérique du Nord</option>
                        <option value="Océanie">Océanie</option>
                        <option value="Global Fusion">Global Fusion</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-white font-semibold mb-2">Style</label>
                      <input
                        type="text"
                        name="style"
                        value={formData.style}
                        onChange={handleInputChange}
                        className="w-full px-4 py-3 bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-terracotta"
                        placeholder="Ex: Bikutsi Moderne"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-white font-semibold mb-2">BPM</label>
                      <input
                        type="number"
                        name="bpm"
                        value={formData.bpm}
                        onChange={handleInputChange}
                        className="w-full px-4 py-3 bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-terracotta"
                        min="60"
                        max="200"
                      />
                    </div>

                    <div>
                      <label className="block text-white font-semibold mb-2">Prix (€)</label>
                      <input
                        type="number"
                        name="price"
                        value={formData.price}
                        onChange={handleInputChange}
                        step="0.01"
                        className="w-full px-4 py-3 bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-terracotta"
                        min="0"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-white font-semibold mb-2">Instrument</label>
                      <input
                        type="text"
                        name="instrument"
                        value={formData.instrument}
                        onChange={handleInputChange}
                        className="w-full px-4 py-3 bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-terracotta"
                        placeholder="Ex: Balafon + Synthé"
                      />
                    </div>

                    <div>
                      <label className="block text-white font-semibold mb-2">Humeur</label>
                      <select
                        name="mood"
                        value={formData.mood}
                        onChange={handleInputChange}
                        className="w-full px-4 py-3 bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-terracotta"
                      >
                        <option value="Énergique">Énergique</option>
                        <option value="Spirituel">Spirituel</option>
                        <option value="Dansant">Dansant</option>
                        <option value="Romantique">Romantique</option>
                        <option value="Festif">Festif</option>
                        <option value="Mélancolique">Mélancolique</option>
                        <option value="Hypnotique">Hypnotique</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-white font-semibold mb-2">Description</label>
                    <textarea
                      name="description"
                      value={formData.description}
                      onChange={handleInputChange}
                      rows="3"
                      className="w-full px-4 py-3 bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-terracotta resize-none"
                      placeholder="Décrivez votre création musicale..."
                    />
                  </div>
                </div>

                {/* File Uploads */}
                <div className="space-y-6">
                  {/* Audio File */}
                  <div>
                    <label className="block text-white font-semibold mb-4">
                      <FileAudio className="inline w-5 h-5 mr-2" />
                      Fichier Audio Principal *
                    </label>
                    <div className="border-2 border-dashed border-white/30 rounded-lg p-6 text-center">
                      <input
                        type="file"
                        accept="audio/*"
                        onChange={handleAudioFileChange}
                        className="hidden"
                        id="audio-upload"
                      />
                      <label htmlFor="audio-upload" className="cursor-pointer">
                        {audioPreview ? (
                          <div className="space-y-2">
                            <Music className="w-12 h-12 text-green-400 mx-auto" />
                            <p className="text-green-400 font-semibold">{audioFile.name}</p>
                            <audio controls className="mx-auto">
                              <source src={audioPreview} type={audioFile.type} />
                            </audio>
                            <p className="text-white/60 text-sm">Durée: {formData.duration}s</p>
                          </div>
                        ) : (
                          <div className="space-y-2">
                            <Upload className="w-12 h-12 text-white/60 mx-auto" />
                            <p className="text-white/80">Cliquez pour sélectionner le fichier audio</p>
                            <p className="text-white/60 text-sm">MP3, WAV, FLAC acceptés</p>
                          </div>
                        )}
                      </label>
                    </div>
                  </div>

                  {/* Image File */}
                  <div>
                    <label className="block text-white font-semibold mb-4">
                      <Camera className="inline w-5 h-5 mr-2" />
                      Image de Couverture *
                    </label>
                    <div className="border-2 border-dashed border-white/30 rounded-lg p-6 text-center">
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleImageFileChange}
                        className="hidden"
                        id="image-upload"
                      />
                      <label htmlFor="image-upload" className="cursor-pointer">
                        {imagePreview ? (
                          <div className="space-y-2">
                            <img 
                              src={imagePreview} 
                              alt="Preview" 
                              className="w-32 h-32 object-cover rounded-lg mx-auto border-2 border-terracotta"
                            />
                            <p className="text-green-400 font-semibold">{imageFile.name}</p>
                          </div>
                        ) : (
                          <div className="space-y-2">
                            <Image className="w-12 h-12 text-white/60 mx-auto" />
                            <p className="text-white/80">Cliquez pour sélectionner l'image</p>
                            <p className="text-white/60 text-sm">JPG, PNG acceptés</p>
                          </div>
                        )}
                      </label>
                    </div>
                  </div>

                  {/* Preview File (Optional) */}
                  <div>
                    <label className="block text-white font-semibold mb-4">
                      <Eye className="inline w-5 h-5 mr-2" />
                      Aperçu 30s (Optionnel)
                    </label>
                    <div className="border-2 border-dashed border-white/30 rounded-lg p-4 text-center">
                      <input
                        type="file"
                        accept="audio/*"
                        onChange={handlePreviewFileChange}
                        className="hidden"
                        id="preview-upload"
                      />
                      <label htmlFor="preview-upload" className="cursor-pointer">
                        {previewFile ? (
                          <p className="text-green-400 font-semibold">{previewFile.name}</p>
                        ) : (
                          <div className="space-y-1">
                            <Upload className="w-8 h-8 text-white/60 mx-auto" />
                            <p className="text-white/60 text-sm">Aperçu personnalisé (sinon audio principal utilisé)</p>
                          </div>
                        )}
                      </label>
                    </div>
                  </div>
                </div>
              </div>

              {/* Submit Button */}
              <div className="text-center pt-6">
                <button
                  type="submit"
                  disabled={uploading}
                  className="inline-flex items-center px-12 py-4 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-emerald-600 hover:to-green-500 text-white font-bold rounded-full transition-all transform hover:scale-105 shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {uploading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                      Upload en cours...
                    </>
                  ) : (
                    <>
                      <Save className="w-5 h-5 mr-2" />
                      Publier ma création
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* My Tracks */}
        <div className="bg-white/10 backdrop-blur-md rounded-3xl p-8 border border-white/20">
          <h2 className="text-3xl font-bold text-white mb-8 text-center">
            🎵 Mes Créations ({myTracks.length})
          </h2>

          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-terracotta mx-auto mb-4"></div>
              <p className="text-white/70">Chargement de vos créations...</p>
            </div>
          ) : myTracks.length === 0 ? (
            <div className="text-center py-12">
              <Music className="w-16 h-16 text-white/40 mx-auto mb-4" />
              <p className="text-white/70 text-lg">Aucune création trouvée</p>
              <p className="text-white/50">Commencez par ajouter votre première piste !</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {myTracks.map(track => (
                <div key={track.id} className="bg-white/20 backdrop-blur-sm rounded-2xl p-6 border border-white/30 hover:border-terracotta/50 transition-all">
                  <div className="relative mb-4">
                    <img 
                      src={track.artwork_url.startsWith('/uploads') ? `${BACKEND_URL}${track.artwork_url}` : track.artwork_url}
                      alt={track.title}
                      className="w-full h-40 object-cover rounded-lg"
                    />
                    <div className="absolute top-2 right-2">
                      <button
                        onClick={() => handleDeleteTrack(track.id, track.title)}
                        className="bg-red-500/80 hover:bg-red-500 text-white p-2 rounded-full transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  
                  <h3 className="text-xl font-bold text-white mb-2">{track.title}</h3>
                  <p className="text-terracotta font-semibold mb-2">{track.artist}</p>
                  
                  <div className="flex items-center space-x-2 mb-3">
                    <span className="px-2 py-1 bg-sage/30 text-sage rounded-full text-xs">{track.region}</span>
                    <span className="px-2 py-1 bg-terracotta/30 text-terracotta rounded-full text-xs">{track.style}</span>
                  </div>
                  
                  <div className="text-white/70 text-sm space-y-1">
                    <p>💰 {track.price.toFixed(2)}€</p>
                    <p>⏱️ {Math.floor(track.duration / 60)}:{(track.duration % 60).toString().padStart(2, '0')}</p>
                    <p>❤️ {track.likes} likes • 📥 {track.downloads} téléchargements</p>
                  </div>
                  
                  {track.audio_url && (
                    <div className="mt-4">
                      <audio controls className="w-full">
                        <source src={track.audio_url.startsWith('/uploads') ? `${BACKEND_URL}${track.audio_url}` : track.audio_url} type="audio/mpeg" />
                      </audio>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminPage;
import React, { useState, useEffect } from "react";
import { 
  Music, 
  Sparkles, 
  Play, 
  Heart, 
  Download, 
  Trash2, 
  Loader2, 
  Wand2, 
  Volume2,
  Clock,
  Mic,
  Guitar,
  Headphones,
  Star
} from "lucide-react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SongCreator = ({ user, authToken }) => {
  const [inspirationPhrase, setInspirationPhrase] = useState("");
  const [musicalStyle, setMusicalStyle] = useState("Afrobeat");
  const [language, setLanguage] = useState("français");
  const [mood, setMood] = useState("énergique");
  const [tempo, setTempo] = useState("modéré");
  const [songTitle, setSongTitle] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedSong, setGeneratedSong] = useState(null);
  const [mySongs, setMySongs] = useState([]);
  const [activeTab, setActiveTab] = useState("create");

  useEffect(() => {
    if (user && authToken) {
      loadMySongs();
    }
  }, [user, authToken]);

  const loadMySongs = async () => {
    try {
      const response = await axios.get(`${API}/ai/songs/my-creations`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      setMySongs(response.data);
    } catch (error) {
      console.error("Error loading songs:", error);
    }
  };

  const generateSong = async () => {
    if (!inspirationPhrase.trim()) return;

    setIsGenerating(true);
    try {
      const response = await axios.post(
        `${API}/ai/songs/create`,
        {
          inspiration_phrase: inspirationPhrase,
          musical_style: musicalStyle,
          language: language,
          mood: mood,
          tempo: tempo,
          song_title: songTitle || null
        },
        {
          headers: { Authorization: `Bearer ${authToken}` }
        }
      );

      setGeneratedSong(response.data);
      setActiveTab("result");
      loadMySongs(); // Refresh the list
    } catch (error) {
      console.error("Error generating song:", error);
      alert("Erreur lors de la génération de la chanson. Veuillez réessayer.");
    } finally {
      setIsGenerating(false);
    }
  };

  const toggleFavorite = async (songId) => {
    try {
      await axios.put(
        `${API}/ai/songs/${songId}/favorite`,
        {},
        {
          headers: { Authorization: `Bearer ${authToken}` }
        }
      );
      loadMySongs();
    } catch (error) {
      console.error("Error toggling favorite:", error);
    }
  };

  const deleteSong = async (songId) => {
    if (!window.confirm("Êtes-vous sûr de vouloir supprimer cette chanson ?")) return;
    
    try {
      await axios.delete(`${API}/ai/songs/${songId}`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      loadMySongs();
      if (generatedSong && generatedSong.id === songId) {
        setGeneratedSong(null);
      }
    } catch (error) {
      console.error("Error deleting song:", error);
    }
  };

  const musicalStyles = [
    "Afrobeat", "Bikutsi", "Makossa", "Soukous", "Highlife", "Zouk", 
    "Reggae", "Jazz", "Blues", "Rock", "Pop", "Folk", "Salsa", "Bossa Nova"
  ];

  const moods = [
    "énergique", "mélancolique", "joyeux", "romantique", "nostalgique", 
    "inspirant", "calme", "intense", "spirituel", "festif"
  ];

  const tempos = [
    "lent", "modéré", "rapide", "très rapide", "variable"
  ];

  const languages = [
    "français", "anglais", "lingala", "wolof", "bambara", "swahili", 
    "yoruba", "hausa", "créole", "espagnol"
  ];

  if (!user || !authToken) {
    return (
      <div className="text-center py-12">
        <Mic className="w-16 h-16 mx-auto text-purple-400 mb-4" />
        <h3 className="text-xl font-bold text-gray-800 mb-2">Compositeur IA</h3>
        <p className="text-gray-600">Connectez-vous pour créer vos chansons avec l'IA</p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Tabs */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg mb-6">
        <button
          onClick={() => setActiveTab("create")}
          className={`flex-1 py-2 px-4 rounded-md font-medium transition-colors ${
            activeTab === "create"
              ? "bg-white text-purple-600 shadow-sm"
              : "text-gray-600 hover:text-gray-800"
          }`}
        >
          <Wand2 className="w-4 h-4 inline mr-2" />
          Créer une chanson
        </button>
        <button
          onClick={() => setActiveTab("library")}
          className={`flex-1 py-2 px-4 rounded-md font-medium transition-colors ${
            activeTab === "library"
              ? "bg-white text-purple-600 shadow-sm"
              : "text-gray-600 hover:text-gray-800"
          }`}
        >
          <Music className="w-4 h-4 inline mr-2" />
          Mes créations ({mySongs.length})
        </button>
        {generatedSong && (
          <button
            onClick={() => setActiveTab("result")}
            className={`flex-1 py-2 px-4 rounded-md font-medium transition-colors ${
              activeTab === "result"
                ? "bg-white text-purple-600 shadow-sm"
                : "text-gray-600 hover:text-gray-800"
            }`}
          >
            <Sparkles className="w-4 h-4 inline mr-2" />
            Résultat
          </button>
        )}
      </div>

      {/* Create Tab */}
      {activeTab === "create" && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="text-center mb-8">
            <div className="bg-gradient-to-r from-purple-100 to-blue-100 p-4 rounded-full w-fit mx-auto mb-4">
              <Wand2 className="w-8 h-8 text-purple-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Compositeur IA</h2>
            <p className="text-gray-600">Transformez votre inspiration en chanson complète</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left Column - Inspiration & Settings */}
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Phrase d'inspiration *
                </label>
                <textarea
                  value={inspirationPhrase}
                  onChange={(e) => setInspirationPhrase(e.target.value)}
                  placeholder="Ex: L'amour traverse les frontières comme une mélodie universelle..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                  rows={3}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Cette phrase sera le thème central de votre chanson
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Titre (optionnel)
                </label>
                <input
                  type="text"
                  value={songTitle}
                  onChange={(e) => setSongTitle(e.target.value)}
                  placeholder="L'IA proposera un titre si vide"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Style musical
                  </label>
                  <select
                    value={musicalStyle}
                    onChange={(e) => setMusicalStyle(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    {musicalStyles.map((style) => (
                      <option key={style} value={style}>{style}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Langue
                  </label>
                  <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    {languages.map((lang) => (
                      <option key={lang} value={lang}>{lang}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Humeur
                  </label>
                  <select
                    value={mood}
                    onChange={(e) => setMood(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    {moods.map((m) => (
                      <option key={m} value={m}>{m}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tempo
                  </label>
                  <select
                    value={tempo}
                    onChange={(e) => setTempo(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    {tempos.map((t) => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Right Column - Preview & Generate */}
            <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Aperçu de votre création</h3>
              
              <div className="space-y-4 mb-6">
                <div className="flex items-center space-x-3">
                  <Music className="w-5 h-5 text-purple-600" />
                  <span className="text-sm">
                    <strong>Style:</strong> {musicalStyle}
                  </span>
                </div>
                <div className="flex items-center space-x-3">
                  <Volume2 className="w-5 h-5 text-blue-600" />
                  <span className="text-sm">
                    <strong>Humeur:</strong> {mood} • <strong>Tempo:</strong> {tempo}
                  </span>
                </div>
                <div className="flex items-center space-x-3">
                  <Headphones className="w-5 h-5 text-green-600" />
                  <span className="text-sm">
                    <strong>Langue:</strong> {language}
                  </span>
                </div>
              </div>

              {inspirationPhrase && (
                <div className="bg-white rounded-lg p-4 mb-6">
                  <h4 className="font-medium text-gray-900 mb-2">Votre inspiration:</h4>
                  <p className="text-sm text-gray-700 italic">"{inspirationPhrase}"</p>
                </div>
              )}

              <button
                onClick={generateSong}
                disabled={!inspirationPhrase.trim() || isGenerating}
                className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 flex items-center justify-center space-x-2"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Création en cours...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    <span>Créer ma chanson</span>
                  </>
                )}
              </button>

              <p className="text-xs text-gray-500 text-center mt-4">
                ⏱️ La génération prend généralement 10-30 secondes
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Library Tab */}
      {activeTab === "library" && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Mes créations</h2>
            <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-medium">
              {mySongs.length} chanson{mySongs.length !== 1 ? 's' : ''}
            </span>
          </div>

          {mySongs.length === 0 ? (
            <div className="text-center py-12">
              <Music className="w-16 h-16 mx-auto text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-700 mb-2">Aucune création</h3>
              <p className="text-gray-500 mb-4">Commencez par créer votre première chanson avec l'IA</p>
              <button
                onClick={() => setActiveTab("create")}
                className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition-colors"
              >
                Créer une chanson
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {mySongs.map((song) => (
                <div key={song.id} className="bg-gray-50 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 truncate">{song.title}</h3>
                      <p className="text-sm text-gray-600">{song.musical_style} • {song.language}</p>
                    </div>
                    <button
                      onClick={() => toggleFavorite(song.id)}
                      className={`p-1 rounded ${
                        song.is_favorite ? "text-red-500" : "text-gray-400"
                      } hover:text-red-500`}
                    >
                      <Heart className={`w-4 h-4 ${song.is_favorite ? "fill-current" : ""}`} />
                    </button>
                  </div>

                  <p className="text-xs text-gray-500 mb-3 italic">
                    "{song.inspiration_phrase.substring(0, 80)}..."
                  </p>

                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500">
                      {new Date(song.created_at).toLocaleDateString()}
                    </span>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => {
                          setGeneratedSong(song);
                          setActiveTab("result");
                        }}
                        className="text-purple-600 hover:text-purple-800 p-1"
                        title="Voir"
                      >
                        <Play className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => deleteSong(song.id)}
                        className="text-red-500 hover:text-red-700 p-1"
                        title="Supprimer"
                      >
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

      {/* Result Tab */}
      {activeTab === "result" && generatedSong && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="text-center mb-6">
            <div className="bg-gradient-to-r from-green-100 to-blue-100 p-4 rounded-full w-fit mx-auto mb-4">
              <Star className="w-8 h-8 text-green-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">{generatedSong.title}</h2>
            <p className="text-gray-600">
              {generatedSong.musical_style} • {generatedSong.language} • {generatedSong.mood}
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Lyrics */}
            <div className="lg:col-span-2">
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Mic className="w-5 h-5 mr-2 text-purple-600" />
                  Paroles
                </h3>
                <div className="whitespace-pre-line text-sm text-gray-700 leading-relaxed">
                  {generatedSong.lyrics}
                </div>
              </div>
            </div>

            {/* Info Panel */}
            <div className="space-y-6">
              {/* Structure */}
              <div className="bg-blue-50 rounded-lg p-4">
                <h4 className="font-semibold text-blue-900 mb-2 flex items-center">
                  <Clock className="w-4 h-4 mr-2" />
                  Structure
                </h4>
                <p className="text-sm text-blue-800">
                  {generatedSong.song_structure.structure}
                </p>
              </div>

              {/* Chords */}
              {generatedSong.chord_suggestions.length > 0 && (
                <div className="bg-green-50 rounded-lg p-4">
                  <h4 className="font-semibold text-green-900 mb-2 flex items-center">
                    <Guitar className="w-4 h-4 mr-2" />
                    Accords suggérés
                  </h4>
                  <div className="text-sm text-green-800 space-y-1">
                    {generatedSong.chord_suggestions.map((chord, index) => (
                      <div key={index}>{chord}</div>
                    ))}
                  </div>
                </div>
              )}

              {/* Arrangement */}
              {generatedSong.arrangement_notes && (
                <div className="bg-orange-50 rounded-lg p-4">
                  <h4 className="font-semibold text-orange-900 mb-2 flex items-center">
                    <Volume2 className="w-4 h-4 mr-2" />
                    Arrangement
                  </h4>
                  <p className="text-sm text-orange-800">
                    {generatedSong.arrangement_notes}
                  </p>
                </div>
              )}

              {/* Production Tips */}
              {generatedSong.production_tips && (
                <div className="bg-purple-50 rounded-lg p-4">
                  <h4 className="font-semibold text-purple-900 mb-2 flex items-center">
                    <Headphones className="w-4 h-4 mr-2" />
                    Production
                  </h4>
                  <p className="text-sm text-purple-800">
                    {generatedSong.production_tips}
                  </p>
                </div>
              )}

              {/* Actions */}
              <div className="flex space-x-2">
                <button
                  onClick={() => toggleFavorite(generatedSong.id)}
                  className={`flex-1 py-2 px-4 rounded-lg transition-colors ${
                    generatedSong.is_favorite
                      ? "bg-red-100 text-red-700 hover:bg-red-200"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  <Heart className={`w-4 h-4 inline mr-1 ${generatedSong.is_favorite ? "fill-current" : ""}`} />
                  {generatedSong.is_favorite ? "Favoris" : "Ajouter"}
                </button>
                <button
                  onClick={() => setActiveTab("create")}
                  className="flex-1 bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition-colors"
                >
                  <Wand2 className="w-4 h-4 inline mr-1" />
                  Nouvelle
                </button>
              </div>
            </div>
          </div>

          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-500 text-center">
              <strong>Inspiration:</strong> "{generatedSong.inspiration_phrase}"
            </p>
            <p className="text-xs text-gray-400 text-center mt-1">
              Créé le {new Date(generatedSong.created_at).toLocaleString()} • {generatedSong.ai_analysis}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default SongCreator;
import React, { useState, useEffect } from "react";
import { Search, Music, Users, Globe, Play, Heart, Star, Filter } from "lucide-react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SearchPage = () => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState({
    tracks: [],
    artists: [],
    total: 0
  });
  const [activeFilter, setActiveFilter] = useState("all");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Get query from URL
    const urlParams = new URLSearchParams(window.location.search);
    const searchQuery = urlParams.get('q');
    if (searchQuery) {
      setQuery(searchQuery);
      performSearch(searchQuery);
    }
  }, []);

  const performSearch = async (searchQuery) => {
    if (!searchQuery.trim()) return;
    
    setIsLoading(true);
    try {
      // Search tracks
      const tracksResponse = await axios.get(`${API}/tracks/search`, {
        params: { q: searchQuery, limit: 20 }
      });

      // Search musician profiles
      const artistsResponse = await axios.get(`${API}/community/search`, {
        params: { q: searchQuery, limit: 10 }
      });

      setResults({
        tracks: tracksResponse.data,
        artists: artistsResponse.data || [],
        total: (tracksResponse.data?.length || 0) + (artistsResponse.data?.length || 0)
      });
    } catch (error) {
      console.error("Search error:", error);
      setResults({ tracks: [], artists: [], total: 0 });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = (e) => {
    if (e.key === 'Enter' && query.trim()) {
      performSearch(query);
      // Update URL
      window.history.pushState({}, '', `/search?q=${encodeURIComponent(query)}`);
    }
  };

  const filteredResults = () => {
    switch (activeFilter) {
      case "tracks":
        return { tracks: results.tracks, artists: [], total: results.tracks.length };
      case "artists":
        return { tracks: [], artists: results.artists, total: results.artists.length };
      default:
        return results;
    }
  };

  const filtered = filteredResults();

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Recherche Musicale</h1>
              {query && (
                <p className="text-gray-600 mt-2">
                  Résultats pour : <strong>"{query}"</strong>
                </p>
              )}
            </div>
          </div>

          {/* Search Bar */}
          <div className="max-w-2xl">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleSearch}
                placeholder="Rechercher artistes, chansons, styles musicaux..."
                className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-lg"
              />
            </div>
          </div>

          {/* Filters */}
          <div className="flex space-x-4 mt-6">
            <button
              onClick={() => setActiveFilter("all")}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeFilter === "all"
                  ? "bg-purple-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              Tout ({results.total})
            </button>
            <button
              onClick={() => setActiveFilter("tracks")}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeFilter === "tracks"
                  ? "bg-purple-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              <Music className="w-4 h-4 inline mr-1" />
              Chansons ({results.tracks.length})
            </button>
            <button
              onClick={() => setActiveFilter("artists")}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeFilter === "artists"
                  ? "bg-purple-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              <Users className="w-4 h-4 inline mr-1" />
              Artistes ({results.artists.length})
            </button>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
            <p className="text-gray-500 mt-4">Recherche en cours...</p>
          </div>
        ) : filtered.total === 0 && query ? (
          <div className="text-center py-12">
            <Search className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-medium text-gray-700 mb-2">Aucun résultat trouvé</h3>
            <p className="text-gray-500">Essayez avec des mots-clés différents</p>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Artists Results */}
            {filtered.artists.length > 0 && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
                  <Users className="w-6 h-6 mr-2 text-purple-600" />
                  Artistes ({filtered.artists.length})
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {filtered.artists.map((artist) => (
                    <div key={artist.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
                      <div className="flex items-center space-x-4 mb-4">
                        <div className="bg-purple-100 p-3 rounded-full">
                          <Users className="w-6 h-6 text-purple-600" />
                        </div>
                        <div>
                          <h3 className="font-bold text-gray-900">{artist.stage_name}</h3>
                          <p className="text-sm text-gray-600">{artist.region}</p>
                        </div>
                      </div>
                      <p className="text-gray-700 text-sm mb-4 line-clamp-3">
                        {artist.bio?.substring(0, 150)}...
                      </p>
                      <div className="flex flex-wrap gap-2 mb-4">
                        {artist.genres?.slice(0, 3).map((genre, index) => (
                          <span key={index} className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-xs">
                            {genre}
                          </span>
                        ))}
                      </div>
                      <button className="w-full bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700 transition-colors">
                        Voir le profil
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Tracks Results */}
            {filtered.tracks.length > 0 && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
                  <Music className="w-6 h-6 mr-2 text-blue-600" />
                  Chansons ({filtered.tracks.length})
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {filtered.tracks.map((track) => (
                    <div key={track.id} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                      {track.artwork_url && (
                        <img 
                          src={track.artwork_url} 
                          alt={track.title}
                          className="w-full h-48 object-cover"
                        />
                      )}
                      <div className="p-4">
                        <h3 className="font-bold text-gray-900 mb-1">{track.title}</h3>
                        <p className="text-gray-600 text-sm mb-2">{track.artist}</p>
                        <div className="flex items-center justify-between text-sm text-gray-500 mb-3">
                          <span className="flex items-center">
                            <Globe className="w-4 h-4 mr-1" />
                            {track.region}
                          </span>
                          <span>{track.style}</span>
                        </div>
                        <p className="text-gray-700 text-sm mb-4 line-clamp-2">
                          {track.description}
                        </p>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <button className="bg-blue-100 text-blue-600 p-2 rounded-full hover:bg-blue-200 transition-colors">
                              <Play className="w-4 h-4" />
                            </button>
                            <button className="bg-gray-100 text-gray-600 p-2 rounded-full hover:bg-gray-200 transition-colors">
                              <Heart className="w-4 h-4" />
                            </button>
                          </div>
                          {track.price && (
                            <span className="font-bold text-blue-600">{track.price.toFixed(2)}€</span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Suggestion pour la chaîne YouTube du fondateur */}
        {query && filtered.total === 0 && (
          <div className="bg-gradient-to-r from-red-50 to-orange-50 rounded-lg p-6 mt-8">
            <div className="flex items-start space-x-4">
              <div className="bg-red-100 p-3 rounded-full">
                <Music className="w-6 h-6 text-red-600" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-bold text-gray-900 mb-2">
                  🎵 Découvrez la musique du fondateur !
                </h3>
                <p className="text-gray-700 mb-4">
                  Aucun résultat ? Explorez la chaîne YouTube de <strong>Fifi Ribana</strong>, 
                  le créateur d'US EXPLO avec plus de 30 ans d'expérience musicale !
                </p>
                <a 
                  href="/fifi-ribana-youtube" 
                  className="inline-flex items-center bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
                >
                  <Play className="w-4 h-4 mr-2" />
                  Écouter Fifi Ribana
                </a>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchPage;
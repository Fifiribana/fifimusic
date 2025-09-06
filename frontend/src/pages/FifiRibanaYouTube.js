import React, { useState } from "react";
import { 
  Play, 
  Music, 
  Star, 
  Heart, 
  Share2, 
  ExternalLink,
  Calendar,
  MapPin,
  Guitar,
  Award,
  Users,
  Globe,
  Youtube
} from "lucide-react";

const FifiRibanaYouTube = () => {
  const [selectedVideo, setSelectedVideo] = useState(null);

  // Playlist simulée de Fifi Ribana (vous pourrez la remplacer par de vraies vidéos)
  const featuredVideos = [
    {
      id: "1",
      title: "Fifi Ribana - Performance Bikutsi Authentique",
      description: "Une performance captivante de guitare Bikutsi par le maître Fifi Ribana",
      thumbnail: "https://images.unsplash.com/photo-1511735111819-9a3f7709049c?w=400",
      duration: "4:32",
      views: "12K",
      date: "Il y a 3 mois"
    },
    {
      id: "2", 
      title: "L'Histoire de Tino Barrozza et Fifi Ribana",
      description: "Le récit de la rencontre légendaire qui a donné naissance à Fifi Ribana en 1991",
      thumbnail: "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=400",
      duration: "8:15",
      views: "25K",
      date: "Il y a 6 mois"
    },
    {
      id: "3",
      title: "Fifi Ribana - Fusion Cameroun-USA",
      description: "Comment 20 ans aux États-Unis ont enrichi le style musical de Fifi Ribana",
      thumbnail: "https://images.unsplash.com/photo-1465869185982-5a1a7522cbcb?w=400",
      duration: "6:28",
      views: "8.9K",
      date: "Il y a 2 mois"
    },
    {
      id: "4",
      title: "Création d'US EXPLO - Vision du fondateur",
      description: "Fifi Ribana explique sa vision pour unir les musiciens du monde entier",
      thumbnail: "https://images.unsplash.com/photo-1516280440614-37939bbacd81?w=400",
      duration: "12:45",
      views: "31K",
      date: "Il y a 1 mois"
    },
    {
      id: "5",
      title: "Live Session - 1000 Œuvres de Fifi Ribana",
      description: "Présentation exclusive de quelques œuvres de la collection personnelle",
      thumbnail: "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400",
      duration: "18:22",
      views: "45K",
      date: "Il y a 2 semaines"
    }
  ];

  const openYouTubeChannel = () => {
    window.open("http://www.youtube.com/@simonmessela6109", "_blank");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-red-600 to-orange-600 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <div className="flex justify-center mb-6">
            <div className="bg-white bg-opacity-20 p-4 rounded-full">
              <Youtube className="w-12 h-12" />
            </div>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            🎸 Fifi Ribana - Chaîne YouTube Officielle
          </h1>
          <p className="text-xl text-red-100 mb-8 max-w-3xl mx-auto">
            Découvrez l'univers musical de Simon Pierre Messela, fondateur d'US EXPLO. 
            Plus de 30 ans d'expérience musicale, de l'Afrique aux États-Unis.
          </p>
          
          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-12">
            <div className="bg-white bg-opacity-10 rounded-lg p-4">
              <div className="text-2xl font-bold">30+</div>
              <div className="text-sm text-red-200">Années d'expérience</div>
            </div>
            <div className="bg-white bg-opacity-10 rounded-lg p-4">
              <div className="text-2xl font-bold">1000+</div>
              <div className="text-sm text-red-200">Œuvres créées</div>
            </div>
            <div className="bg-white bg-opacity-10 rounded-lg p-4">
              <div className="text-2xl font-bold">2</div>
              <div className="text-sm text-red-200">Continents</div>
            </div>
            <div className="bg-white bg-opacity-10 rounded-lg p-4">
              <div className="text-2xl font-bold">∞</div>
              <div className="text-sm text-red-200">Passion</div>
            </div>
          </div>

          {/* CTA */}
          <div className="mt-8">
            <button
              onClick={openYouTubeChannel}
              className="bg-white text-red-600 px-8 py-4 rounded-lg font-bold text-lg hover:bg-gray-100 transition-colors inline-flex items-center space-x-3"
            >
              <Youtube className="w-6 h-6" />
              <span>Visiter la chaîne YouTube</span>
              <ExternalLink className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Bio Section */}
      <div className="bg-white py-16">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-6">L'Histoire de Fifi Ribana</h2>
              <div className="space-y-4 text-gray-700">
                <div className="flex items-start space-x-3">
                  <Calendar className="w-5 h-5 text-red-600 mt-1" />
                  <div>
                    <strong>1972 :</strong> Naissance à Efoufoup par Ayos, Cameroun
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <Star className="w-5 h-5 text-red-600 mt-1" />
                  <div>
                    <strong>1991 :</strong> Rencontre légendaire avec Tino Barrozza - Naissance de "Fifi Ribana"
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <Music className="w-5 h-5 text-red-600 mt-1" />
                  <div>
                    <strong>1992-2005 :</strong> Âge d'or africain - Participation à de nombreux albums
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <Globe className="w-5 h-5 text-red-600 mt-1" />
                  <div>
                    <strong>2005-2025 :</strong> Aventure américaine - 20 ans d'évolution artistique
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <Award className="w-5 h-5 text-red-600 mt-1" />
                  <div>
                    <strong>2025 :</strong> Création d'US EXPLO - Réalisation du rêve d'unir les musiciens du monde
                  </div>
                </div>
              </div>
            </div>
            <div className="bg-gradient-to-br from-red-100 to-orange-100 rounded-lg p-8">
              <h3 className="text-xl font-bold text-gray-900 mb-4">🎯 Mission US EXPLO</h3>
              <blockquote className="text-gray-700 italic text-lg leading-relaxed">
                "Mon rêve a toujours été de voir les musiciens de la planète se mettre ensemble un jour ou l'autre. 
                Je ne savais comment ceci pourrait se réaliser... Aujourd'hui, grâce à la technologie, 
                US EXPLO concrétise cette vision !"
              </blockquote>
              <div className="mt-6 text-center">
                <div className="text-2xl font-bold text-red-600">🤝 ENSEMBLE NOUS SOMMES PLUS FORTS !</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Featured Videos */}
      <div className="py-16">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">
            🎬 Vidéos en vedette
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {featuredVideos.map((video) => (
              <div key={video.id} className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow group">
                <div className="relative">
                  <img 
                    src={video.thumbnail} 
                    alt={video.title}
                    className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all duration-300 flex items-center justify-center">
                    <Play className="w-12 h-12 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  </div>
                  <div className="absolute bottom-2 right-2 bg-black bg-opacity-70 text-white px-2 py-1 rounded text-sm">
                    {video.duration}
                  </div>
                </div>
                
                <div className="p-6">
                  <h3 className="font-bold text-gray-900 mb-2 line-clamp-2">{video.title}</h3>
                  <p className="text-gray-600 text-sm mb-4 line-clamp-3">{video.description}</p>
                  
                  <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                    <span>{video.views} vues</span>
                    <span>{video.date}</span>
                  </div>
                  
                  <div className="flex space-x-2">
                    <button 
                      onClick={openYouTubeChannel}
                      className="flex-1 bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 transition-colors flex items-center justify-center space-x-2"
                    >
                      <Play className="w-4 h-4" />
                      <span>Regarder</span>
                    </button>
                    <button className="bg-gray-100 text-gray-600 p-2 rounded-lg hover:bg-gray-200 transition-colors">
                      <Heart className="w-4 h-4" />
                    </button>
                    <button className="bg-gray-100 text-gray-600 p-2 rounded-lg hover:bg-gray-200 transition-colors">
                      <Share2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Call to Action */}
      <div className="bg-gradient-to-r from-red-600 to-orange-600 text-white py-16">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <Guitar className="w-16 h-16 mx-auto mb-6" />
          <h2 className="text-3xl font-bold mb-4">Découvrez l'univers complet de Fifi Ribana</h2>
          <p className="text-xl text-red-100 mb-8">
            Plus de 1000 œuvres musicales vous attendent sur sa chaîne YouTube officielle. 
            Un voyage musical entre l'Afrique et les États-Unis !
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={openYouTubeChannel}
              className="bg-white text-red-600 px-8 py-3 rounded-lg font-medium hover:bg-gray-100 transition-colors inline-flex items-center justify-center space-x-2"
            >
              <Youtube className="w-5 h-5" />
              <span>Chaîne YouTube Complète</span>
              <ExternalLink className="w-4 h-4" />
            </button>
            <a 
              href="/community" 
              className="border border-white text-white px-8 py-3 rounded-lg font-medium hover:bg-white hover:text-red-600 transition-colors inline-flex items-center justify-center space-x-2"
            >
              <Users className="w-5 h-5" />
              <span>Rejoindre la Communauté</span>
            </a>
          </div>
        </div>
      </div>

      {/* Integration with US EXPLO */}
      <div className="bg-white py-16">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">🌍 US EXPLO - Une Plateforme Née d'une Vision</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-6">
              <div className="bg-purple-100 p-4 rounded-full w-fit mx-auto mb-4">
                <Music className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="font-bold text-gray-900 mb-2">Partage Musical</h3>
              <p className="text-gray-600">Découvrez et partagez la musique du monde entier</p>
            </div>
            <div className="p-6">
              <div className="bg-blue-100 p-4 rounded-full w-fit mx-auto mb-4">
                <Users className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="font-bold text-gray-900 mb-2">Solidarité</h3>
              <p className="text-gray-600">Ensemble nous sommes plus forts - Entraide musicale</p>
            </div>
            <div className="p-6">
              <div className="bg-green-100 p-4 rounded-full w-fit mx-auto mb-4">
                <Globe className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="font-bold text-gray-900 mb-2">Vision Mondiale</h3>
              <p className="text-gray-600">Unir les musiciens par-delà les frontières</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FifiRibanaYouTube;
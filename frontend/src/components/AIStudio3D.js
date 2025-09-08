import React, { useState, useEffect, useRef } from 'react';
import { 
  Bot, 
  Mic, 
  Music, 
  Wand2, 
  Brain, 
  Sparkles, 
  Play, 
  Pause, 
  Download, 
  Share2,
  Settings,
  Volume2,
  Headphones,
  Zap,
  Star,
  Crown,
  Palette,
  Sliders
} from 'lucide-react';

// Studio IA 3D pour Composition Musicale
const AIStudio3D = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [currentMode, setCurrentMode] = useState('compose');
  const [generatedTrack, setGeneratedTrack] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [audioWaves, setAudioWaves] = useState([]);
  const [creativityLevel, setCreativityLevel] = useState(0.7);
  const [selectedGenre, setSelectedGenre] = useState('world');
  const [selectedMood, setSelectedMood] = useState('energetic');
  
  const canvasRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioContextRef = useRef(null);

  // Genres musicaux avec couleurs
  const genres = [
    { id: 'world', name: 'Musique du Monde', color: 'from-orange-400 to-red-500', emoji: '🌍' },
    { id: 'afrobeat', name: 'Afrobeat', color: 'from-green-400 to-blue-500', emoji: '🥁' },
    { id: 'electronic', name: 'Électronique', color: 'from-purple-400 to-pink-500', emoji: '🎛️' },
    { id: 'jazz', name: 'Jazz', color: 'from-yellow-400 to-orange-500', emoji: '🎷' },
    { id: 'classical', name: 'Classique', color: 'from-blue-400 to-purple-500', emoji: '🎼' },
    { id: 'ambient', name: 'Ambient', color: 'from-cyan-400 to-blue-500', emoji: '🌊' }
  ];

  // Humeurs musicales
  const moods = [
    { id: 'energetic', name: 'Énergique', color: 'from-red-400 to-orange-500' },
    { id: 'calm', name: 'Calme', color: 'from-blue-400 to-cyan-500' },
    { id: 'happy', name: 'Joyeux', color: 'from-yellow-400 to-orange-500' },
    { id: 'mysterious', name: 'Mystérieux', color: 'from-purple-400 to-indigo-500' },
    { id: 'romantic', name: 'Romantique', color: 'from-pink-400 to-red-500' },
    { id: 'epic', name: 'Épique', color: 'from-indigo-400 to-purple-500' }
  ];

  useEffect(() => {
    // Initialiser la visualisation audio
    initAudioVisualization();
    
    // Animation des ondes audio
    const interval = setInterval(() => {
      if (isRecording || isLoading) {
        setAudioWaves(prev => [
          ...prev.slice(-50),
          {
            id: Date.now(),
            height: Math.random() * 100 + 20,
            color: genres.find(g => g.id === selectedGenre)?.color || 'from-orange-400 to-red-500'
          }
        ]);
      }
    }, 100);

    return () => clearInterval(interval);
  }, [isRecording, isLoading, selectedGenre]);

  const initAudioVisualization = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width = canvas.offsetWidth;
    const height = canvas.height = canvas.offsetHeight;

    const drawVisualization = (timestamp) => {
      ctx.clearRect(0, 0, width, height);
      
      // Créer un effet de particules musicales
      for (let i = 0; i < 100; i++) {
        const x = (i * width) / 100;
        const y = height / 2 + Math.sin(timestamp * 0.01 + i * 0.1) * 50;
        const size = Math.sin(timestamp * 0.02 + i * 0.05) * 3 + 2;
        
        const gradient = ctx.createRadialGradient(x, y, 0, x, y, size);
        gradient.addColorStop(0, `hsla(${(timestamp * 0.1 + i * 3.6) % 360}, 80%, 60%, 0.8)`);
        gradient.addColorStop(1, `hsla(${(timestamp * 0.1 + i * 3.6) % 360}, 80%, 60%, 0)`);
        
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(x, y, size, 0, Math.PI * 2);
        ctx.fill();
      }
      
      requestAnimationFrame(drawVisualization);
    };
    
    drawVisualization(0);
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      
      mediaRecorder.start();
      setIsRecording(true);
      
      setTimeout(() => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
          stopRecording();
        }
      }, 10000); // Auto-stop après 10 secondes
      
    } catch (error) {
      console.error('Erreur d\'accès au microphone:', error);
      alert('Impossible d\'accéder au microphone');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      processAudioWithAI();
    }
  };

  const processAudioWithAI = () => {
    setIsLoading(true);
    
    // Simulation du traitement IA
    setTimeout(() => {
      const generatedTrack = {
        id: `ai_track_${Date.now()}`,
        title: `Composition IA - ${selectedGenre} ${Date.now()}`,
        artist: 'AI Studio US EXPLO',
        genre: selectedGenre,
        mood: selectedMood,
        duration: Math.floor(Math.random() * 180) + 120, // 2-5 minutes
        creativity: creativityLevel,
        preview_url: 'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav', // URL de démo
        waveform: Array.from({ length: 100 }, () => Math.random() * 100),
        generated_at: new Date().toISOString()
      };
      
      setGeneratedTrack(generatedTrack);
      setIsLoading(false);
    }, 3000);
  };

  const generateFromPrompt = (prompt) => {
    setIsLoading(true);
    
    // Simulation de génération à partir d'un prompt
    setTimeout(() => {
      const track = {
        id: `ai_prompt_${Date.now()}`,
        title: `IA: ${prompt.substring(0, 30)}...`,
        artist: 'AI Studio US EXPLO',
        genre: selectedGenre,
        mood: selectedMood,
        prompt: prompt,
        duration: Math.floor(Math.random() * 240) + 180,
        creativity: creativityLevel,
        preview_url: 'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav',
        waveform: Array.from({ length: 100 }, () => Math.random() * 100),
        generated_at: new Date().toISOString()
      };
      
      setGeneratedTrack(track);
      setIsLoading(false);
    }, 4000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-indigo-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header 3D */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center bg-gradient-to-r from-purple-500/20 to-pink-500/20 backdrop-blur-sm border border-purple-500/30 rounded-full px-8 py-4 mb-8">
            <Bot className="w-8 h-8 text-purple-300 mr-4 animate-pulse" />
            <span className="text-purple-300 font-bold text-xl">Studio IA Avancé</span>
            <Sparkles className="w-6 h-6 text-pink-300 ml-4 animate-spin" />
          </div>
          
          <h1 className="text-5xl md:text-7xl font-black mb-6 relative">
            <span className="absolute inset-0 bg-gradient-to-br from-purple-600 via-pink-600 to-indigo-700 bg-clip-text text-transparent transform translate-x-2 translate-y-2 opacity-30">
              AI STUDIO 3D
            </span>
            <span className="relative bg-gradient-to-br from-purple-400 via-pink-400 to-indigo-500 bg-clip-text text-transparent">
              AI STUDIO 3D
            </span>
          </h1>
          
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Créez de la musique révolutionnaire avec l'intelligence artificielle avancée
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Panneau de Contrôle */}
          <div className="lg:col-span-1 space-y-6">
            {/* Mode Selection */}
            <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-6 border border-white/20">
              <h3 className="text-white font-bold text-xl mb-4 flex items-center">
                <Settings className="w-6 h-6 mr-3 text-purple-400" />
                Mode de Création
              </h3>
              
              <div className="space-y-3">
                {[
                  { id: 'compose', name: 'Composition Libre', icon: Music },
                  { id: 'voice', name: 'À partir de Voix', icon: Mic },
                  { id: 'prompt', name: 'Prompt Textuel', icon: Wand2 }
                ].map(mode => (
                  <button
                    key={mode.id}
                    onClick={() => setCurrentMode(mode.id)}
                    className={`w-full p-4 rounded-2xl flex items-center space-x-3 transition-all duration-300 ${
                      currentMode === mode.id
                        ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white scale-105'
                        : 'bg-white/5 text-gray-300 hover:bg-white/10'
                    }`}
                  >
                    <mode.icon className="w-5 h-5" />
                    <span className="font-semibold">{mode.name}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Genre Selection */}
            <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-6 border border-white/20">
              <h3 className="text-white font-bold text-xl mb-4 flex items-center">
                <Palette className="w-6 h-6 mr-3 text-orange-400" />
                Genre Musical
              </h3>
              
              <div className="grid grid-cols-2 gap-3">
                {genres.map(genre => (
                  <button
                    key={genre.id}
                    onClick={() => setSelectedGenre(genre.id)}
                    className={`p-3 rounded-xl flex flex-col items-center space-y-2 transition-all duration-300 ${
                      selectedGenre === genre.id
                        ? `bg-gradient-to-r ${genre.color} text-white scale-105`
                        : 'bg-white/5 text-gray-300 hover:bg-white/10'
                    }`}
                  >
                    <span className="text-2xl">{genre.emoji}</span>
                    <span className="text-xs font-semibold text-center">{genre.name}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Mood Selection */}
            <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-6 border border-white/20">
              <h3 className="text-white font-bold text-xl mb-4 flex items-center">
                <Brain className="w-6 h-6 mr-3 text-cyan-400" />
                Humeur
              </h3>
              
              <div className="space-y-2">
                {moods.map(mood => (
                  <button
                    key={mood.id}
                    onClick={() => setSelectedMood(mood.id)}
                    className={`w-full p-3 rounded-xl text-left transition-all duration-300 ${
                      selectedMood === mood.id
                        ? `bg-gradient-to-r ${mood.color} text-white`
                        : 'bg-white/5 text-gray-300 hover:bg-white/10'
                    }`}
                  >
                    <span className="font-semibold">{mood.name}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Creativity Level */}
            <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-6 border border-white/20">
              <h3 className="text-white font-bold text-xl mb-4 flex items-center">
                <Sliders className="w-6 h-6 mr-3 text-yellow-400" />
                Niveau de Créativité
              </h3>
              
              <div className="space-y-4">
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={creativityLevel}
                  onChange={(e) => setCreativityLevel(parseFloat(e.target.value))}
                  className="w-full h-3 bg-gray-600 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-sm text-gray-400">
                  <span>Conservateur</span>
                  <span className="text-yellow-400 font-bold">{Math.round(creativityLevel * 100)}%</span>
                  <span>Expérimental</span>
                </div>
              </div>
            </div>
          </div>

          {/* Zone de Création Principale */}
          <div className="lg:col-span-2 space-y-6">
            {/* Visualiseur Audio 3D */}
            <div className="bg-black/30 backdrop-blur-lg rounded-3xl p-6 border border-white/10 relative overflow-hidden">
              <canvas
                ref={canvasRef}
                className="w-full h-64 rounded-2xl"
                style={{ background: 'linear-gradient(45deg, #1a1a2e, #16213e, #0f3460)' }}
              />
              
              {/* Overlay Controls */}
              <div className="absolute top-6 left-6 right-6 flex justify-between items-center">
                <div className="flex items-center space-x-3">
                  <div className={`w-4 h-4 rounded-full ${isRecording ? 'bg-red-500 animate-pulse' : 'bg-gray-500'}`}></div>
                  <span className="text-white font-semibold">
                    {isRecording ? 'Enregistrement...' : isLoading ? 'Génération IA...' : 'Prêt'}
                  </span>
                </div>
                
                <div className="flex items-center space-x-2">
                  {audioWaves.slice(-20).map((wave, index) => (
                    <div
                      key={index}
                      className={`w-1 bg-gradient-to-t ${wave.color} rounded-full transition-all duration-300`}
                      style={{ height: `${wave.height}%` }}
                    />
                  ))}
                </div>
              </div>
            </div>

            {/* Interface de Création */}
            {currentMode === 'voice' && (
              <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-8 border border-white/20 text-center">
                <h3 className="text-2xl font-bold text-white mb-6">Enregistrement Vocal</h3>
                
                <button
                  onClick={isRecording ? stopRecording : startRecording}
                  disabled={isLoading}
                  className={`relative p-8 rounded-full text-white font-bold text-xl transition-all duration-500 transform hover:scale-110 ${
                    isRecording
                      ? 'bg-gradient-to-r from-red-500 to-pink-500 animate-pulse scale-110'
                      : 'bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-400 hover:to-indigo-400'
                  } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  {isLoading ? (
                    <div className="flex items-center space-x-3">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
                      <span>Génération...</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-3">
                      <Mic className={`w-8 h-8 ${isRecording ? 'animate-pulse' : ''}`} />
                      <span>{isRecording ? 'Arrêter' : 'Enregistrer'}</span>
                    </div>
                  )}
                </button>
                
                <p className="text-gray-300 mt-4">
                  {isRecording 
                    ? 'Chantez, sifflez ou fredonnez votre mélodie...' 
                    : 'Cliquez pour commencer l\'enregistrement vocal'}
                </p>
              </div>
            )}

            {currentMode === 'prompt' && (
              <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-8 border border-white/20">
                <h3 className="text-2xl font-bold text-white mb-6">Génération par Prompt</h3>
                
                <textarea
                  placeholder="Décrivez la musique que vous voulez créer... Ex: 'Une mélodie joyeuse avec des percussions africaines et une guitare acoustique'"
                  className="w-full h-32 p-4 bg-black/30 border border-white/20 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-400 resize-none"
                />
                
                <button
                  onClick={() => generateFromPrompt(document.querySelector('textarea').value)}
                  disabled={isLoading}
                  className="mt-4 w-full py-4 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-400 hover:to-pink-400 text-white font-bold rounded-2xl transition-all duration-300 transform hover:scale-105 disabled:opacity-50"
                >
                  {isLoading ? (
                    <div className="flex items-center justify-center space-x-3">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                      <span>Création en cours...</span>
                    </div>
                  ) : (
                    <div className="flex items-center justify-center space-x-3">
                      <Wand2 className="w-6 h-6" />
                      <span>Générer la Musique</span>
                      <Sparkles className="w-5 h-5 animate-pulse" />
                    </div>
                  )}
                </button>
              </div>
            )}

            {/* Résultat Généré */}
            {generatedTrack && (
              <div className="bg-gradient-to-r from-purple-500/20 via-pink-500/20 to-indigo-500/20 backdrop-blur-lg rounded-3xl p-8 border border-purple-500/30">
                <h3 className="text-2xl font-bold text-white mb-6 flex items-center">
                  <Crown className="w-7 h-7 text-gold mr-3" />
                  Composition Créée !
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="text-xl font-bold text-white mb-2">{generatedTrack.title}</h4>
                    <p className="text-gray-300 mb-4">par {generatedTrack.artist}</p>
                    
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Genre:</span>
                        <span className="text-white font-semibold">{generatedTrack.genre}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Humeur:</span>
                        <span className="text-white font-semibold">{generatedTrack.mood}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Durée:</span>
                        <span className="text-white font-semibold">{Math.floor(generatedTrack.duration / 60)}:{(generatedTrack.duration % 60).toString().padStart(2, '0')}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Créativité:</span>
                        <span className="text-white font-semibold">{Math.round(generatedTrack.creativity * 100)}%</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    {/* Forme d'onde */}
                    <div className="h-20 bg-black/30 rounded-2xl p-3 flex items-end space-x-1">
                      {generatedTrack.waveform.map((height, index) => (
                        <div
                          key={index}
                          className="w-1 bg-gradient-to-t from-purple-500 to-pink-400 rounded-full transition-all duration-300"
                          style={{ height: `${height}%` }}
                        />
                      ))}
                    </div>
                    
                    {/* Actions */}
                    <div className="flex space-x-3">
                      <button className="flex-1 py-3 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-400 hover:to-emerald-400 text-white font-bold rounded-xl transition-all duration-300 flex items-center justify-center space-x-2">
                        <Play className="w-5 h-5" />
                        <span>Écouter</span>
                      </button>
                      
                      <button className="py-3 px-4 bg-white/10 hover:bg-white/20 text-white rounded-xl transition-all duration-300">
                        <Download className="w-5 h-5" />
                      </button>
                      
                      <button className="py-3 px-4 bg-white/10 hover:bg-white/20 text-white rounded-xl transition-all duration-300">
                        <Share2 className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIStudio3D;
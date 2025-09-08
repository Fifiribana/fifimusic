import React, { useState, useEffect, useRef } from 'react';
import { 
  Play, 
  Pause, 
  SkipForward, 
  SkipBack, 
  Volume2, 
  VolumeX, 
  Repeat, 
  Shuffle, 
  Heart,
  Download,
  Share2,
  Music,
  Equalizer,
  Headphones,
  Radio,
  Mic2
} from 'lucide-react';

// Lecteur Audio 3D Avancé avec Visualiseur
const AdvancedAudioPlayer = ({ track, onNext, onPrevious, playlist = [] }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.8);
  const [isMuted, setIsMuted] = useState(false);
  const [isLiked, setIsLiked] = useState(false);
  const [showEqualizer, setShowEqualizer] = useState(false);
  const [visualizerData, setVisualizerData] = useState([]);
  const [audioContext, setAudioContext] = useState(null);
  const [analyzer, setAnalyzer] = useState(null);
  
  const audioRef = useRef(null);
  const canvasRef = useRef(null);
  const animationRef = useRef(null);

  useEffect(() => {
    if (track && audioRef.current) {
      audioRef.current.src = track.audio_url || track.preview_url;
      initAudioContext();
    }
  }, [track]);

  const initAudioContext = () => {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const analyser = ctx.createAnalyser();
      const source = ctx.createMediaElementSource(audioRef.current);
      
      source.connect(analyser);
      analyser.connect(ctx.destination);
      analyser.fftSize = 256;
      
      setAudioContext(ctx);
      setAnalyzer(analyser);
      
      const bufferLength = analyser.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      setVisualizerData(dataArray);
      
      startVisualization(analyser, dataArray);
    } catch (error) {
      console.warn('Web Audio API not supported:', error);
      // Fallback avec données simulées
      const mockData = Array.from({ length: 128 }, () => Math.random() * 255);
      setVisualizerData(mockData);
      startMockVisualization();
    }
  };

  const startVisualization = (analyser, dataArray) => {
    const animate = () => {
      analyser.getByteFrequencyData(dataArray);
      setVisualizerData([...dataArray]);
      drawVisualizer(dataArray);
      animationRef.current = requestAnimationFrame(animate);
    };
    animate();
  };

  const startMockVisualization = () => {
    const animate = () => {
      if (isPlaying) {
        const mockData = Array.from({ length: 128 }, (_, i) => 
          Math.sin(Date.now() * 0.01 + i * 0.1) * 128 + 128
        );
        setVisualizerData(mockData);
        drawVisualizer(mockData);
      }
      animationRef.current = requestAnimationFrame(animate);
    };
    animate();
  };

  const drawVisualizer = (dataArray) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    ctx.clearRect(0, 0, width, height);
    
    const barWidth = width / dataArray.length * 2;
    let x = 0;
    
    // Gradient pour les barres
    const gradient = ctx.createLinearGradient(0, height, 0, 0);
    gradient.addColorStop(0, '#FF6B35');
    gradient.addColorStop(0.3, '#F7931E');
    gradient.addColorStop(0.6, '#FFD700');
    gradient.addColorStop(1, '#32CD32');
    
    for (let i = 0; i < dataArray.length; i++) {
      const barHeight = (dataArray[i] / 255) * height;
      
      ctx.fillStyle = gradient;
      ctx.fillRect(x, height - barHeight, barWidth - 1, barHeight);
      
      // Effet glow
      ctx.shadowColor = '#FF6B35';
      ctx.shadowBlur = 10;
      ctx.fillRect(x, height - barHeight, barWidth - 1, barHeight);
      ctx.shadowBlur = 0;
      
      x += barWidth;
    }
  };

  const togglePlay = () => {
    if (!audioRef.current) return;
    
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
      if (audioContext && audioContext.state === 'suspended') {
        audioContext.resume();
      }
    }
    setIsPlaying(!isPlaying);
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
      setDuration(audioRef.current.duration || 0);
    }
  };

  const handleSeek = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const percent = (e.clientX - rect.left) / rect.width;
    const newTime = percent * duration;
    
    if (audioRef.current) {
      audioRef.current.currentTime = newTime;
      setCurrentTime(newTime);
    }
  };

  const handleVolumeChange = (e) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    if (audioRef.current) {
      audioRef.current.volume = newVolume;
    }
    setIsMuted(newVolume === 0);
  };

  const toggleMute = () => {
    if (audioRef.current) {
      if (isMuted) {
        audioRef.current.volume = volume;
        setIsMuted(false);
      } else {
        audioRef.current.volume = 0;
        setIsMuted(true);
      }
    }
  };

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  if (!track) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-gradient-to-r from-slate-900 via-purple-900 to-slate-900 border-t border-white/10 backdrop-blur-lg">
      {/* Audio Element */}
      <audio
        ref={audioRef}
        onTimeUpdate={handleTimeUpdate}
        onEnded={() => onNext?.()}
        onLoadedMetadata={handleTimeUpdate}
      />

      {/* Visualizer Canvas */}
      <canvas
        ref={canvasRef}
        width={window.innerWidth}
        height={60}
        className="absolute top-0 left-0 opacity-60 pointer-events-none"
      />

      <div className="relative z-10 max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center space-x-6">
          {/* Track Info */}
          <div className="flex items-center space-x-4 min-w-0 flex-1">
            <div className="relative group">
              <img
                src={track.artwork_url}
                alt={track.title}
                className="w-16 h-16 rounded-xl object-cover shadow-lg group-hover:scale-110 transition-transform duration-300"
              />
              <div className="absolute inset-0 bg-black/20 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
                <Music className="w-6 h-6 text-white" />
              </div>
            </div>
            
            <div className="min-w-0 flex-1">
              <h3 className="text-white font-bold text-lg truncate">{track.title}</h3>
              <p className="text-gray-300 text-sm truncate">{track.artist}</p>
              <div className="flex items-center space-x-2 mt-1">
                <span className="px-2 py-1 bg-orange-500/20 text-orange-300 text-xs rounded-full">
                  {track.region}
                </span>
                <span className="px-2 py-1 bg-purple-500/20 text-purple-300 text-xs rounded-full">
                  {track.style}
                </span>
              </div>
            </div>
          </div>

          {/* Control Buttons */}
          <div className="flex items-center space-x-4">
            <button
              onClick={onPrevious}
              className="p-2 text-gray-300 hover:text-white hover:scale-110 transition-all duration-200"
            >
              <SkipBack className="w-5 h-5" />
            </button>

            <button
              onClick={togglePlay}
              className="p-4 bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-400 hover:to-red-400 text-white rounded-full shadow-lg hover:scale-110 transition-all duration-300 group"
            >
              {isPlaying ? (
                <Pause className="w-6 h-6 group-hover:scale-110 transition-transform duration-200" />
              ) : (
                <Play className="w-6 h-6 ml-1 group-hover:scale-110 transition-transform duration-200" />
              )}
            </button>

            <button
              onClick={onNext}
              className="p-2 text-gray-300 hover:text-white hover:scale-110 transition-all duration-200"
            >
              <SkipForward className="w-5 h-5" />
            </button>
          </div>

          {/* Progress Bar */}
          <div className="flex-1 max-w-md">
            <div className="flex items-center space-x-2 text-sm text-gray-300 mb-2">
              <span>{formatTime(currentTime)}</span>
              <div 
                className="flex-1 h-2 bg-gray-600 rounded-full cursor-pointer overflow-hidden"
                onClick={handleSeek}
              >
                <div 
                  className="h-full bg-gradient-to-r from-orange-400 to-red-400 transition-all duration-300"
                  style={{ width: `${(currentTime / duration) * 100}%` }}
                />
              </div>
              <span>{formatTime(duration)}</span>
            </div>
          </div>

          {/* Volume Control */}
          <div className="flex items-center space-x-3">
            <button
              onClick={toggleMute}
              className="text-gray-300 hover:text-white transition-colors duration-200"
            >
              {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
            </button>
            
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={isMuted ? 0 : volume}
              onChange={handleVolumeChange}
              className="w-20 h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer"
            />
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsLiked(!isLiked)}
              className={`p-2 rounded-full transition-all duration-300 ${
                isLiked 
                  ? 'text-red-400 bg-red-500/20 scale-110' 
                  : 'text-gray-300 hover:text-red-400 hover:bg-red-500/10'
              }`}
            >
              <Heart className={`w-5 h-5 ${isLiked ? 'fill-current' : ''}`} />
            </button>

            <button
              onClick={() => setShowEqualizer(!showEqualizer)}
              className={`p-2 rounded-full transition-all duration-300 ${
                showEqualizer 
                  ? 'text-purple-400 bg-purple-500/20' 
                  : 'text-gray-300 hover:text-purple-400 hover:bg-purple-500/10'
              }`}
            >
              <Equalizer className="w-5 h-5" />
            </button>

            <button className="p-2 text-gray-300 hover:text-blue-400 hover:bg-blue-500/10 rounded-full transition-all duration-300">
              <Share2 className="w-5 h-5" />
            </button>

            <button className="p-2 text-gray-300 hover:text-green-400 hover:bg-green-500/10 rounded-full transition-all duration-300">
              <Download className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Equalizer Panel */}
        {showEqualizer && (
          <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-4 bg-slate-800/95 backdrop-blur-lg rounded-2xl p-6 border border-white/10 shadow-2xl">
            <h4 className="text-white font-bold mb-4 flex items-center">
              <Equalizer className="w-5 h-5 mr-2" />
              Égaliseur 3D
            </h4>
            <div className="flex items-end space-x-2">
              {['60Hz', '170Hz', '310Hz', '600Hz', '1kHz', '3kHz', '6kHz', '12kHz', '14kHz', '16kHz'].map((freq, index) => (
                <div key={freq} className="flex flex-col items-center">
                  <input
                    type="range"
                    min="-20"
                    max="20"
                    defaultValue="0"
                    className="w-6 h-24 bg-gray-600 rounded-lg appearance-none cursor-pointer transform rotate-90 origin-center"
                    style={{ writingMode: 'bt-lr' }}
                  />
                  <span className="text-xs text-gray-400 mt-2">{freq}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdvancedAudioPlayer;
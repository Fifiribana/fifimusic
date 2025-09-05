import React, { useState, useEffect } from "react";
import { Bot, Sparkles, TrendingUp, Music, Users, Zap, ArrowRight, RefreshCw, Wand2 } from "lucide-react";
import axios from "axios";
import SongCreator from "../components/SongCreator";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AIPage = ({ user, authToken }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [aiAnalysis, setAiAnalysis] = useState("");
  const [automationTasks, setAutomationTasks] = useState([]);
  const [activeTab, setActiveTab] = useState("recommendations");

  useEffect(() => {
    if (user && authToken) {
      loadRecommendations();
      loadAutomationTasks();
    }
  }, [user, authToken]);

  const loadRecommendations = async () => {
    try {
      const response = await axios.get(`${API}/ai/recommendations`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      setRecommendations(response.data);
    } catch (error) {
      console.error("Error loading recommendations:", error);
    }
  };

  const loadAutomationTasks = async () => {
    try {
      const response = await axios.get(`${API}/ai/automation/tasks`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      setAutomationTasks(response.data);
    } catch (error) {
      console.error("Error loading automation tasks:", error);
    }
  };

  const generateRecommendations = async () => {
    setIsGenerating(true);
    try {
      const response = await axios.post(
        `${API}/ai/recommendations/generate`,
        {},
        {
          headers: { Authorization: `Bearer ${authToken}` }
        }
      );
      setAiAnalysis(response.data.ai_analysis);
      setRecommendations(response.data.recommendations);
    } catch (error) {
      console.error("Error generating recommendations:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  const createAutomationTask = async (taskType, taskName, description) => {
    try {
      await axios.post(
        `${API}/ai/automation/tasks`,
        {
          task_type: taskType,
          task_name: taskName,
          description: description,
          schedule: "daily"
        },
        {
          headers: { Authorization: `Bearer ${authToken}` }
        }
      );
      loadAutomationTasks();
    } catch (error) {
      console.error("Error creating automation task:", error);
    }
  };

  const toggleTask = async (taskId) => {
    try {
      await axios.put(
        `${API}/ai/automation/tasks/${taskId}/toggle`,
        {},
        {
          headers: { Authorization: `Bearer ${authToken}` }
        }
      );
      loadAutomationTasks();
    } catch (error) {
      console.error("Error toggling task:", error);
    }
  };

  if (!user || !authToken) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 flex items-center justify-center">
        <div className="text-center p-8">
          <Bot className="w-16 h-16 mx-auto text-purple-400 mb-4" />
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Intelligence Artificielle US EXPLO</h2>
          <p className="text-gray-600 mb-6">Connectez-vous pour accéder aux fonctionnalités IA personnalisées</p>
          <button className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors">
            Se connecter
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="bg-gradient-to-r from-purple-600 to-blue-600 p-3 rounded-lg">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Intelligence Artificielle</h1>
                <p className="text-gray-600">Assistant musical personnalisé pour {user.username}</p>
              </div>
            </div>
            <button
              onClick={generateRecommendations}
              disabled={isGenerating}
              className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-3 rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all duration-300 flex items-center space-x-2 disabled:opacity-50"
            >
              {isGenerating ? (
                <RefreshCw className="w-5 h-5 animate-spin" />
              ) : (
                <Bot className="w-5 h-5" />
              )}
              <span>{isGenerating ? "Génération..." : "Générer des recommandations"}</span>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Tab Navigation */}
        <div className="flex space-x-1 bg-white rounded-lg p-1 mb-8 shadow">
          <button
            onClick={() => setActiveTab("recommendations")}
            className={`flex-1 py-3 px-6 rounded-md font-medium transition-colors flex items-center justify-center space-x-2 ${
              activeTab === "recommendations"
                ? "bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-md"
                : "text-gray-600 hover:text-gray-800 hover:bg-gray-50"
            }`}
          >
            <TrendingUp className="w-5 h-5" />
            <span>Recommandations</span>
          </button>
          <button
            onClick={() => setActiveTab("composer")}
            className={`flex-1 py-3 px-6 rounded-md font-medium transition-colors flex items-center justify-center space-x-2 ${
              activeTab === "composer"
                ? "bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-md"
                : "text-gray-600 hover:text-gray-800 hover:bg-gray-50"
            }`}
          >
            <Wand2 className="w-5 h-5" />
            <span>Compositeur IA</span>
          </button>
          <button
            onClick={() => setActiveTab("automation")}
            className={`flex-1 py-3 px-6 rounded-md font-medium transition-colors flex items-center justify-center space-x-2 ${
              activeTab === "automation"
                ? "bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-md"
                : "text-gray-600 hover:text-gray-800 hover:bg-gray-50"
            }`}
          >
            <Zap className="w-5 h-5" />
            <span>Automatisation</span>
          </button>
        </div>

        {/* Composer Tab */}
        {activeTab === "composer" && (
          <SongCreator user={user} authToken={authToken} />
        )}

        {/* Recommendations & Automation Tab */}
        {activeTab === "recommendations" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* AI Recommendations */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center space-x-3 mb-6">
              <TrendingUp className="w-6 h-6 text-purple-600" />
              <h2 className="text-2xl font-bold text-gray-900">Recommandations IA</h2>
            </div>

            {aiAnalysis && (
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-6">
                <h3 className="font-semibold text-purple-800 mb-2">Analyse IA :</h3>
                <p className="text-purple-700 text-sm">{aiAnalysis}</p>
              </div>
            )}

            <div className="space-y-4">
              {recommendations.length === 0 ? (
                <div className="text-center py-8">
                  <Music className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-500">Aucune recommandation générée</p>
                  <p className="text-sm text-gray-400">Cliquez sur "Générer des recommandations" pour commencer</p>
                </div>
              ) : (
                recommendations.map((rec, index) => (
                  <div key={index} className="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors">
                    <div className="flex items-start space-x-4">
                      <div className="bg-purple-100 p-2 rounded-lg">
                        <Music className="w-5 h-5 text-purple-600" />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900">{rec.content.title}</h3>
                        <p className="text-sm text-gray-600">
                          {rec.content.artist} • {rec.content.style} • {rec.content.region}
                        </p>
                        <p className="text-sm text-purple-600 mt-2">{rec.reason}</p>
                        <div className="flex items-center mt-2">
                          <div className="flex items-center">
                            <div className="bg-purple-200 h-2 rounded-full mr-2" style={{width: `${rec.confidence_score * 100}px`}}></div>
                            <span className="text-xs text-gray-500">
                              {Math.round(rec.confidence_score * 100)}% de confiance
                            </span>
                          </div>
                        </div>
                      </div>
                      <button className="text-purple-600 hover:text-purple-800">
                        <ArrowRight className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Automation Tasks */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center space-x-3 mb-6">
              <Zap className="w-6 h-6 text-blue-600" />
              <h2 className="text-2xl font-bold text-gray-900">Automatisation</h2>
            </div>

            <div className="space-y-4 mb-6">
              <button
                onClick={() => createAutomationTask("recommendation", "Recommandations quotidiennes", "Générer des recommandations musicales personnalisées chaque jour")}
                className="w-full bg-blue-50 border border-blue-200 rounded-lg p-4 hover:bg-blue-100 transition-colors text-left"
              >
                <div className="flex items-center space-x-3">
                  <TrendingUp className="w-5 h-5 text-blue-600" />
                  <div>
                    <h3 className="font-medium text-blue-900">Recommandations automatiques</h3>
                    <p className="text-sm text-blue-700">Découvrez de nouvelles musiques chaque jour</p>
                  </div>
                </div>
              </button>

              <button
                onClick={() => createAutomationTask("playlist_update", "Mise à jour playlists", "Mettre à jour automatiquement vos playlists avec de nouveaux morceaux")}
                className="w-full bg-green-50 border border-green-200 rounded-lg p-4 hover:bg-green-100 transition-colors text-left"
              >
                <div className="flex items-center space-x-3">
                  <Music className="w-5 h-5 text-green-600" />
                  <div>
                    <h3 className="font-medium text-green-900">Playlists intelligentes</h3>
                    <p className="text-sm text-green-700">Playlists qui évoluent avec vos goûts</p>
                  </div>
                </div>
              </button>

              <button
                onClick={() => createAutomationTask("notification", "Alertes personnalisées", "Recevoir des notifications sur les nouveautés qui vous intéressent")}
                className="w-full bg-orange-50 border border-orange-200 rounded-lg p-4 hover:bg-orange-100 transition-colors text-left"
              >
                <div className="flex items-center space-x-3">
                  <Users className="w-5 h-5 text-orange-600" />
                  <div>
                    <h3 className="font-medium text-orange-900">Notifications intelligentes</h3>
                    <p className="text-sm text-orange-700">Restez informé des nouveautés pertinentes</p>
                  </div>
                </div>
              </button>
            </div>

            {/* Active Tasks */}
            <div className="border-t pt-6">
              <h3 className="font-semibold text-gray-900 mb-4">Tâches actives</h3>
              <div className="space-y-3">
                {automationTasks.length === 0 ? (
                  <p className="text-gray-500 text-sm">Aucune tâche d'automatisation configurée</p>
                ) : (
                  automationTasks.map((task) => (
                    <div key={task.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <h4 className="font-medium text-gray-900">{task.task_name}</h4>
                        <p className="text-sm text-gray-600">{task.description}</p>
                        <p className="text-xs text-gray-500">Fréquence: {task.schedule}</p>
                      </div>
                      <button
                        onClick={() => toggleTask(task.id)}
                        className={`px-3 py-1 rounded-full text-xs font-medium ${
                          task.is_active
                            ? "bg-green-100 text-green-800"
                            : "bg-gray-100 text-gray-800"
                        }`}
                      >
                        {task.is_active ? "Actif" : "Inactif"}
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
        )}

        {/* Automation Tab */}
        {activeTab === "automation" && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center space-x-3 mb-6">
              <Zap className="w-6 h-6 text-blue-600" />
              <h2 className="text-2xl font-bold text-gray-900">Automatisation</h2>
            </div>

            <div className="space-y-4 mb-6">
              <button
                onClick={() => createAutomationTask("recommendation", "Recommandations quotidiennes", "Générer des recommandations musicales personnalisées chaque jour")}
                className="w-full bg-blue-50 border border-blue-200 rounded-lg p-4 hover:bg-blue-100 transition-colors text-left"
              >
                <div className="flex items-center space-x-3">
                  <TrendingUp className="w-5 h-5 text-blue-600" />
                  <div>
                    <h3 className="font-medium text-blue-900">Recommandations automatiques</h3>
                    <p className="text-sm text-blue-700">Découvrez de nouvelles musiques chaque jour</p>
                  </div>
                </div>
              </button>

              <button
                onClick={() => createAutomationTask("playlist_update", "Mise à jour playlists", "Mettre à jour automatiquement vos playlists avec de nouveaux morceaux")}
                className="w-full bg-green-50 border border-green-200 rounded-lg p-4 hover:bg-green-100 transition-colors text-left"
              >
                <div className="flex items-center space-x-3">
                  <Music className="w-5 h-5 text-green-600" />
                  <div>
                    <h3 className="font-medium text-green-900">Playlists intelligentes</h3>
                    <p className="text-sm text-green-700">Playlists qui évoluent avec vos goûts</p>
                  </div>
                </div>
              </button>

              <button
                onClick={() => createAutomationTask("notification", "Alertes personnalisées", "Recevoir des notifications sur les nouveautés qui vous intéressent")}
                className="w-full bg-orange-50 border border-orange-200 rounded-lg p-4 hover:bg-orange-100 transition-colors text-left"
              >
                <div className="flex items-center space-x-3">
                  <Users className="w-5 h-5 text-orange-600" />
                  <div>
                    <h3 className="font-medium text-orange-900">Notifications intelligentes</h3>
                    <p className="text-sm text-orange-700">Restez informé des nouveautés pertinentes</p>
                  </div>
                </div>
              </button>
            </div>

            {/* Active Tasks */}
            <div className="border-t pt-6">
              <h3 className="font-semibold text-gray-900 mb-4">Tâches actives</h3>
              <div className="space-y-3">
                {automationTasks.length === 0 ? (
                  <p className="text-gray-500 text-sm">Aucune tâche d'automatisation configurée</p>
                ) : (
                  automationTasks.map((task) => (
                    <div key={task.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <h4 className="font-medium text-gray-900">{task.task_name}</h4>
                        <p className="text-sm text-gray-600">{task.description}</p>
                        <p className="text-xs text-gray-500">Fréquence: {task.schedule}</p>
                      </div>
                      <button
                        onClick={() => toggleTask(task.id)}
                        className={`px-3 py-1 rounded-full text-xs font-medium ${
                          task.is_active
                            ? "bg-green-100 text-green-800"
                            : "bg-gray-100 text-gray-800"
                        }`}
                      >
                        {task.is_active ? "Actif" : "Inactif"}
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        {/* AI Features Overview */}
        <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Fonctionnalités IA</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="bg-purple-100 p-4 rounded-lg mb-4 mx-auto w-fit">
                <Bot className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Assistant Chat</h3>
              <p className="text-sm text-gray-600">Chattez avec l'IA pour obtenir de l'aide et des conseils musicaux personnalisés</p>
            </div>
            <div className="text-center">
              <div className="bg-blue-100 p-4 rounded-lg mb-4 mx-auto w-fit">
                <TrendingUp className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Recommandations</h3>
              <p className="text-sm text-gray-600">Découvrez de nouveaux morceaux basés sur vos goûts et votre historique d'écoute</p>
            </div>
            <div className="text-center">
              <div className="bg-green-100 p-4 rounded-lg mb-4 mx-auto w-fit">
                <Zap className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Automatisation</h3>
              <p className="text-sm text-gray-600">Automatisez vos tâches répétitives et optimisez votre expérience musicale</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIPage;
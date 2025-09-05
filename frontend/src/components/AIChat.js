import React, { useState, useEffect, useRef } from "react";
import { Send, Bot, User, Trash2, Plus, MessageCircle, Sparkles, Loader2 } from "lucide-react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AIChat = ({ user, authToken }) => {
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isMinimized, setIsMinimized] = useState(true);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (user && authToken) {
      loadSessions();
    }
  }, [user, authToken]);

  const loadSessions = async () => {
    try {
      const response = await axios.get(`${API}/ai/sessions`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      setSessions(response.data);
    } catch (error) {
      console.error("Error loading sessions:", error);
    }
  };

  const loadMessages = async (sessionId) => {
    try {
      const response = await axios.get(`${API}/ai/sessions/${sessionId}/messages`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      setMessages(response.data);
    } catch (error) {
      console.error("Error loading messages:", error);
    }
  };

  const createNewSession = () => {
    setCurrentSession(null);
    setMessages([]);
    setIsMinimized(false);
  };

  const selectSession = (session) => {
    setCurrentSession(session);
    loadMessages(session.id);
    setIsMinimized(false);
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      message_type: "user",
      content: inputMessage,
      created_at: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);

    try {
      const response = await axios.post(
        `${API}/ai/chat`,
        {
          content: inputMessage,
          session_id: currentSession?.id
        },
        {
          headers: { Authorization: `Bearer ${authToken}` }
        }
      );

      const aiMessage = {
        message_type: "assistant",
        content: response.data.content,
        created_at: response.data.created_at
      };

      setMessages(prev => [...prev, aiMessage]);

      // Update current session if it was created
      if (!currentSession) {
        await loadSessions();
        const newSessionId = response.data.session_id;
        const newSession = sessions.find(s => s.id === newSessionId);
        if (newSession) {
          setCurrentSession(newSession);
        }
      }

    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage = {
        message_type: "assistant",
        content: "Désolé, je ne peux pas répondre maintenant. Veuillez réessayer plus tard.",
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const deleteSession = async (sessionId, e) => {
    e.stopPropagation();
    try {
      await axios.delete(`${API}/ai/sessions/${sessionId}`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      if (currentSession?.id === sessionId) {
        setCurrentSession(null);
        setMessages([]);
      }
    } catch (error) {
      console.error("Error deleting session:", error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!user || !authToken) {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* Chat Button (when minimized) */}
      {isMinimized && (
        <button
          onClick={() => setIsMinimized(false)}
          className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-4 rounded-full shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 animate-pulse"
        >
          <Bot className="w-6 h-6" />
        </button>
      )}

      {/* Chat Interface (when expanded) */}
      {!isMinimized && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl w-96 h-96 flex flex-col border border-gray-200 dark:border-gray-700">
          {/* Header */}
          <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-4 rounded-t-lg flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-5 h-5" />
              <span className="font-bold">Assistant IA US EXPLO</span>
            </div>
            <button
              onClick={() => setIsMinimized(true)}
              className="text-white hover:text-gray-200 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Sessions Sidebar */}
          <div className="flex h-full">
            <div className="w-32 bg-gray-50 dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 overflow-y-auto">
              <button
                onClick={createNewSession}
                className="w-full p-3 text-left hover:bg-gray-100 dark:hover:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-center"
              >
                <Plus className="w-4 h-4" />
              </button>
              {sessions.map((session) => (
                <div
                  key={session.id}
                  onClick={() => selectSession(session)}
                  className={`p-2 text-xs cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between group ${
                    currentSession?.id === session.id ? "bg-blue-50 dark:bg-blue-900" : ""
                  }`}
                >
                  <div className="flex items-center space-x-1 flex-1 min-w-0">
                    <MessageCircle className="w-3 h-3 flex-shrink-0" />
                    <span className="truncate">{session.title.replace("Chat - ", "")}</span>
                  </div>
                  <button
                    onClick={(e) => deleteSession(session.id, e)}
                    className="opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-700 p-1"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>

            {/* Chat Area */}
            <div className="flex-1 flex flex-col">
              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && (
                  <div className="text-center text-gray-500 dark:text-gray-400 py-8">
                    <Bot className="w-12 h-12 mx-auto mb-4 text-purple-400" />
                    <p className="text-sm mb-2">Bonjour {user.username} ! 👋</p>
                    <p className="text-xs">Je suis votre assistant IA pour US EXPLO.</p>
                    <p className="text-xs">Posez-moi vos questions sur la musique mondiale ! 🎵</p>
                  </div>
                )}
                
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${message.message_type === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                        message.message_type === "user"
                          ? "bg-blue-600 text-white"
                          : "bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200"
                      }`}
                    >
                      <div className="flex items-start space-x-2">
                        {message.message_type === "assistant" && (
                          <Bot className="w-4 h-4 mt-1 text-purple-500" />
                        )}
                        {message.message_type === "user" && (
                          <User className="w-4 h-4 mt-1" />
                        )}
                        <div className="flex-1">
                          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                          <p className="text-xs opacity-70 mt-1">
                            {new Date(message.created_at).toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 dark:bg-gray-700 px-4 py-2 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <Bot className="w-4 h-4 text-purple-500" />
                        <Loader2 className="w-4 h-4 animate-spin text-purple-500" />
                        <span className="text-sm text-gray-600 dark:text-gray-300">
                          En train de réfléchir...
                        </span>
                      </div>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="border-t border-gray-200 dark:border-gray-700 p-4">
                <div className="flex space-x-2">
                  <textarea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Posez votre question..."
                    className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white text-sm"
                    rows={2}
                    disabled={isLoading}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={!inputMessage.trim() || isLoading}
                    className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIChat;
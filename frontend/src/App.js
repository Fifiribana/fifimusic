import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Composant principal ChatMe
function ChatMe() {
  const [currentUser, setCurrentUser] = useState("");
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState("");
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(false);

  // Charger les utilisateurs actifs
  const loadUsers = async () => {
    try {
      const response = await axios.get(`${API}/users`);
      setUsers(response.data.filter(user => user !== currentUser));
    } catch (error) {
      console.error("Erreur lors du chargement des utilisateurs:", error);
    }
  };

  // Charger la conversation entre deux utilisateurs
  const loadConversation = async (user1, user2) => {
    if (!user1 || !user2) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${API}/messages/conversation/${user1}/${user2}`);
      setMessages(response.data);
    } catch (error) {
      console.error("Erreur lors du chargement de la conversation:", error);
    } finally {
      setLoading(false);
    }
  };

  // Envoyer un message
  const sendMessage = async () => {
    if (!newMessage.trim() || !selectedUser) return;

    try {
      await axios.post(`${API}/messages`, {
        sender_name: currentUser,
        receiver_name: selectedUser,
        content: newMessage.trim()
      });
      
      setNewMessage("");
      // Recharger la conversation
      await loadConversation(currentUser, selectedUser);
    } catch (error) {
      console.error("Erreur lors de l'envoi du message:", error);
    }
  };

  // Gérer la connexion utilisateur
  const handleLogin = (username) => {
    if (username.trim()) {
      setCurrentUser(username.trim());
      setIsLoggedIn(true);
    }
  };

  // Sélectionner un utilisateur pour discuter
  const selectUser = (user) => {
    setSelectedUser(user);
    loadConversation(currentUser, user);
  };

  // Charger les utilisateurs au démarrage
  useEffect(() => {
    if (isLoggedIn) {
      loadUsers();
      // Recharger les utilisateurs toutes les 10 secondes
      const interval = setInterval(loadUsers, 10000);
      return () => clearInterval(interval);
    }
  }, [isLoggedIn, currentUser]);

  // Recharger la conversation toutes les 3 secondes si un utilisateur est sélectionné
  useEffect(() => {
    if (selectedUser && currentUser) {
      const interval = setInterval(() => {
        loadConversation(currentUser, selectedUser);
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [selectedUser, currentUser]);

  // Écran de connexion
  if (!isLoggedIn) {
    return <LoginScreen onLogin={handleLogin} />;
  }

  return (
    <div className="chatme-container">
      {/* En-tête */}
      <header className="chatme-header">
        <div className="header-content">
          <h1 className="app-title">💬 ChatMe</h1>
          <div className="user-info">
            <span className="current-user">Connecté: {currentUser}</span>
            <button 
              className="logout-btn"
              onClick={() => {
                setIsLoggedIn(false);
                setCurrentUser("");
                setSelectedUser("");
                setMessages([]);
              }}
            >
              Déconnexion
            </button>
          </div>
        </div>
      </header>

      <div className="chat-layout">
        {/* Barre latérale - Liste des utilisateurs */}
        <aside className="users-sidebar">
          <div className="sidebar-header">
            <h3>Conversations</h3>
            <button onClick={loadUsers} className="refresh-btn">🔄</button>
          </div>
          
          <div className="users-list">
            {users.length === 0 ? (
              <div className="no-users">
                <p>Aucun utilisateur disponible</p>
                <p className="hint">Envoyez un message à quelqu'un pour commencer!</p>
              </div>
            ) : (
              users.map(user => (
                <div
                  key={user}
                  className={`user-item ${selectedUser === user ? 'active' : ''}`}
                  onClick={() => selectUser(user)}
                >
                  <div className="user-avatar">
                    {user.charAt(0).toUpperCase()}
                  </div>
                  <div className="user-info">
                    <div className="user-name">{user}</div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Démarrer nouvelle conversation */}
          <div className="new-conversation">
            <NewConversationForm 
              currentUser={currentUser}
              onConversationStart={selectUser}
            />
          </div>
        </aside>

        {/* Zone de chat principale */}
        <main className="chat-main">
          {selectedUser ? (
            <>
              {/* En-tête de la conversation */}
              <div className="conversation-header">
                <div className="chat-user-info">
                  <div className="chat-avatar">
                    {selectedUser.charAt(0).toUpperCase()}
                  </div>
                  <h3>Discussion avec {selectedUser}</h3>
                </div>
              </div>

              {/* Zone des messages */}
              <div className="messages-container">
                {loading ? (
                  <div className="loading">Chargement des messages...</div>
                ) : messages.length === 0 ? (
                  <div className="no-messages">
                    <p>Aucun message pour l'instant</p>
                    <p>Commencez la conversation!</p>
                  </div>
                ) : (
                  messages.map(message => (
                    <div
                      key={message.id}
                      className={`message ${message.sender_name === currentUser ? 'sent' : 'received'}`}
                    >
                      <div className="message-content">
                        <div className="message-text">{message.content}</div>
                        <div className="message-time">
                          {new Date(message.timestamp).toLocaleTimeString('fr-FR', {
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Zone de saisie */}
              <div className="message-input-container">
                <div className="message-input-wrapper">
                  <input
                    type="text"
                    className="message-input"
                    placeholder="Tapez votre message..."
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        sendMessage();
                      }
                    }}
                  />
                  <button
                    className="send-button"
                    onClick={sendMessage}
                    disabled={!newMessage.trim()}
                  >
                    Envoyer 📤
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="no-conversation">
              <div className="welcome-message">
                <h2>Bienvenue sur ChatMe! 💬</h2>
                <p>Sélectionnez un utilisateur dans la liste pour commencer une conversation</p>
                <p>ou démarrez une nouvelle conversation ci-dessous</p>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

// Composant d'écran de connexion
function LoginScreen({ onLogin }) {
  const [username, setUsername] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (username.trim()) {
      onLogin(username);
    }
  };

  return (
    <div className="login-screen">
      <div className="login-container">
        <div className="login-header">
          <h1>💬 ChatMe</h1>
          <p>Centre de Messages</p>
        </div>
        
        <form onSubmit={handleSubmit} className="login-form">
          <div className="input-group">
            <label htmlFor="username">Nom d'utilisateur</label>
            <input
              id="username"
              type="text"
              className="username-input"
              placeholder="Entrez votre nom d'utilisateur"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoFocus
            />
          </div>
          
          <button type="submit" className="login-button" disabled={!username.trim()}>
            Se connecter
          </button>
        </form>
        
        <div className="login-footer">
          <p>Entrez simplement votre nom pour commencer à discuter!</p>
        </div>
      </div>
    </div>
  );
}

// Composant pour démarrer une nouvelle conversation
function NewConversationForm({ currentUser, onConversationStart }) {
  const [newUserName, setNewUserName] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (newUserName.trim() && newUserName !== currentUser) {
      // Envoyer un message de bienvenue pour initialiser la conversation
      try {
        await axios.post(`${API}/messages`, {
          sender_name: currentUser,
          receiver_name: newUserName.trim(),
          content: `Salut ${newUserName}! 👋`
        });
        
        onConversationStart(newUserName.trim());
        setNewUserName("");
      } catch (error) {
        console.error("Erreur lors de la création de la conversation:", error);
      }
    }
  };

  return (
    <form onSubmit={handleSubmit} className="new-conversation-form">
      <h4>Nouvelle conversation</h4>
      <div className="input-group">
        <input
          type="text"
          placeholder="Nom d'utilisateur"
          value={newUserName}
          onChange={(e) => setNewUserName(e.target.value)}
          className="new-user-input"
        />
        <button 
          type="submit" 
          className="start-chat-btn"
          disabled={!newUserName.trim() || newUserName === currentUser}
        >
          💬
        </button>
      </div>
    </form>
  );
}

function App() {
  return (
    <div className="App">
      <ChatMe />
    </div>
  );
}

export default App;
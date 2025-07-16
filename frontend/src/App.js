import React, { useState, useEffect } from 'react';
import './App.css';
import Setup from './components/Setup';
import Chat from './components/Chat';
import { KitProvider } from './context/KitContext';

function App() {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Check if user is already set up
    const savedUser = localStorage.getItem('solstis_user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  const handleSetup = (userData) => {
    setUser(userData);
    localStorage.setItem('solstis_user', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('solstis_user');
  };

  if (isLoading) {
    return (
      <div className="app-loading">
        <div className="loading-spinner"></div>
        <p>Loading Solstis...</p>
      </div>
    );
  }

  return (
    <KitProvider>
      <div className="App">
        {!user ? (
          <Setup onSetup={handleSetup} />
        ) : (
          <Chat user={user} onLogout={handleLogout} />
        )}
      </div>
    </KitProvider>
  );
}

export default App; 
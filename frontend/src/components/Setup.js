import React, { useState } from 'react';
import { useKit } from '../context/KitContext';
import './Setup.css';

const Setup = ({ onSetup }) => {
  const { kits, loading } = useKit();
  const [userName, setUserName] = useState('');
  const [selectedKit, setSelectedKit] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userName.trim() || !selectedKit) return;

    setIsSubmitting(true);
    
    try {
      // Call the setup API
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5001';
      const response = await fetch(`${apiUrl}/api/setup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_name: userName.trim(),
          kit_type: selectedKit
        })
      });

      if (response.ok) {
        const userData = {
          name: userName.trim(),
          kitType: selectedKit,
          kit: kits.find(kit => kit.id === selectedKit)
        };
        onSetup(userData);
      } else {
        throw new Error('Setup failed');
      }
    } catch (error) {
      console.error('Setup error:', error);
      alert('Setup failed. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="setup-loading">
        <div className="loading-spinner"></div>
        <p>Loading kits...</p>
      </div>
    );
  }

  return (
    <div className="setup-container">
      <div className="setup-card">
        <div className="setup-header">
          <h1>🩺 Solstis Assistant</h1>
          <p>Your AI-powered medical assistant</p>
        </div>

        <form onSubmit={handleSubmit} className="setup-form">
          <div className="form-group">
            <label htmlFor="userName">What's your name?</label>
            <input
              type="text"
              id="userName"
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              placeholder="Enter your name"
              required
            />
          </div>

          <div className="form-group">
            <label>Which Solstis kit are you using?</label>
            <div className="kit-options">
              {kits.map((kit) => (
                <div
                  key={kit.id}
                  className={`kit-option ${selectedKit === kit.id ? 'selected' : ''}`}
                  onClick={() => setSelectedKit(kit.id)}
                >
                  <input
                    type="radio"
                    name="kit_type"
                    value={kit.id}
                    id={`kit_${kit.id}`}
                    checked={selectedKit === kit.id}
                    onChange={() => setSelectedKit(kit.id)}
                  />
                  <h3>{kit.name}</h3>
                  <p>{kit.description}</p>
                  <small>{kit.use_case}</small>
                </div>
              ))}
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={!userName.trim() || !selectedKit || isSubmitting}
          >
            {isSubmitting ? 'Starting...' : 'Start Chat'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Setup; 
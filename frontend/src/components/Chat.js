import React, { useState, useEffect, useRef } from 'react';
import VoiceRecorder from './VoiceRecorder';
import MessageList from './MessageList';
import './Chat.css';

const Chat = ({ user, onLogout }) => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [status, setStatus] = useState('');
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize with greeting
  useEffect(() => {
    const greeting = `Hey ${user.name}. I'm here to help with your ${user.kit.name}. If this is a life-threatening emergency, please call 911 immediately. Otherwise, I'll guide you step-by-step. Can you tell me what happened?`;
    
    setMessages([
      {
        id: 1,
        role: 'assistant',
        content: greeting,
        timestamp: new Date()
      }
    ]);

    // Speak the greeting
    speakText(greeting);
  }, [user]);

  const speakText = async (text) => {
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5001';
      
      // Call ElevenLabs TTS API
      const response = await fetch(`${apiUrl}/api/tts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          voice_id: process.env.REACT_APP_ELEVENLABS_VOICE_ID // Optional: use specific voice
        })
      });

      if (response.ok) {
        // Get the audio blob
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        
        // Play the audio
        const audio = new Audio(audioUrl);
        audio.play();
        
        // Clean up the URL after playing
        audio.onended = () => {
          URL.revokeObjectURL(audioUrl);
        };
      } else {
        console.warn('ElevenLabs TTS failed, falling back to browser TTS');
        // Fallback to browser TTS if ElevenLabs fails
        if ('speechSynthesis' in window) {
          const utterance = new SpeechSynthesisUtterance(text);
          utterance.rate = 0.9;
          utterance.pitch = 1;
          utterance.volume = 1;
          
          const voices = speechSynthesis.getVoices();
          const preferredVoice = voices.find(voice => 
            voice.name.includes('Samantha') || 
            voice.name.includes('Alex') ||
            voice.name.includes('Google') ||
            voice.name.includes('Karen') ||
            voice.name.includes('Daniel')
          );
          if (preferredVoice) {
            utterance.voice = preferredVoice;
          }
          
          speechSynthesis.speak(utterance);
        }
      }
    } catch (error) {
      console.error('TTS error:', error);
      // Fallback to browser TTS on error
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.9;
        utterance.pitch = 1;
        utterance.volume = 1;
        speechSynthesis.speak(utterance);
      }
    }
  };

  const sendMessage = async (text) => {
    if (!text.trim()) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: text.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);
    setStatus('Processing...');

    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5001';
      const response = await fetch(`${apiUrl}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_input: text.trim(),
          user_name: user.name,
          kit_type: user.kitType
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        const assistantMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: data.response,
          timestamp: new Date()
        };

        setMessages(prev => [...prev, assistantMessage]);
        setStatus('Response received');
        
        // Speak the response
        speakText(data.response);
      } else {
        throw new Error('Failed to get response');
      }
    } catch (error) {
      console.error('Chat error:', error);
      setStatus('Error: Failed to get response');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVoiceTranscript = (transcript) => {
    setInputText(transcript);
    sendMessage(transcript);
  };

  const handleClear = async () => {
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5001';
      await fetch(`${apiUrl}/api/clear`, { method: 'POST' });
      
      const greeting = `Hey ${user.name}. I'm here to help with your ${user.kit.name}. If this is a life-threatening emergency, please call 911 immediately. Otherwise, I'll guide you step-by-step. Can you tell me what happened?`;
      
      setMessages([
        {
          id: Date.now(),
          role: 'assistant',
          content: greeting,
          timestamp: new Date()
        }
      ]);

      speakText(greeting);
      setStatus('Conversation cleared');
    } catch (error) {
      console.error('Clear error:', error);
      setStatus('Error clearing conversation');
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(inputText);
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="kit-info">
          <h2>{user.kit.name}</h2>
          <p>{user.kit.description}</p>
        </div>
        <button onClick={onLogout} className="btn btn-secondary">
          Logout
        </button>
      </div>

      <div className="chat-main">
        <div className="status-bar">
          {status && <div className="status-message">{status}</div>}
        </div>

        <MessageList messages={messages} isLoading={isLoading} />

        <div className="chat-input-container">
          <form onSubmit={handleSubmit} className="chat-form">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Type your message or use voice..."
              className="chat-input"
              disabled={isLoading}
            />
            
            <VoiceRecorder
              onTranscript={handleVoiceTranscript}
              isListening={isListening}
              setIsListening={setIsListening}
              disabled={isLoading}
            />
            
            <button
              type="submit"
              className="btn btn-primary"
              disabled={!inputText.trim() || isLoading}
            >
              Send
            </button>
          </form>

          <div className="chat-controls">
            <button
              onClick={handleClear}
              className="btn btn-danger"
              disabled={isLoading}
            >
              Clear Conversation
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat; 
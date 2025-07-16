import React, { useEffect, useRef } from 'react';
import './VoiceRecorder.css';

const VoiceRecorder = ({ onTranscript, isListening, setIsListening, disabled }) => {
  const recognitionRef = useRef(null);

  useEffect(() => {
    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';
      
      recognitionRef.current.onstart = () => {
        console.log('Speech recognition started');
      };
      
      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        console.log('Transcript:', transcript);
        onTranscript(transcript);
        setIsListening(false);
      };
      
      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };
      
      recognitionRef.current.onend = () => {
        console.log('Speech recognition ended');
        setIsListening(false);
      };
    } else {
      console.warn('Speech recognition not supported');
    }
  }, [onTranscript, setIsListening]);

  const toggleListening = () => {
    if (disabled) return;
    
    if (!recognitionRef.current) {
      alert('Speech recognition is not supported in this browser');
      return;
    }
    
    if (isListening) {
      recognitionRef.current.stop();
    } else {
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const getButtonIcon = () => {
    if (disabled) return '🔇';
    if (isListening) return '⏹️';
    return '🎤';
  };

  const getButtonTitle = () => {
    if (disabled) return 'Voice input disabled';
    if (isListening) return 'Click to stop recording';
    return 'Click to start voice input';
  };

  return (
    <button
      type="button"
      className={`voice-btn ${isListening ? 'listening' : ''} ${disabled ? 'disabled' : ''}`}
      onClick={toggleListening}
      title={getButtonTitle()}
      disabled={disabled}
    >
      {getButtonIcon()}
    </button>
  );
};

export default VoiceRecorder; 
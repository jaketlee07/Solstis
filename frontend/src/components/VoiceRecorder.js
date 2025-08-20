import React, { useEffect, useRef, useState } from 'react';
import './VoiceRecorder.css';

const VoiceRecorder = ({ onTranscript, isListening, setIsListening, disabled }) => {
  const [debugInfo, setDebugInfo] = useState('Click to start');
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);

  const startRecording = async () => {
    console.log('🔴 Starting recording...');
    setDebugInfo('Starting recording...');
    
    try {
      // Step 1: Get microphone access
      console.log('🎤 Requesting microphone access...');
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000,
          channelCount: 1
        } 
      });
      streamRef.current = stream;
      console.log('✅ Microphone access granted');
      setDebugInfo('Microphone access granted');
      
      // Step 2: Create MediaRecorder with supported format
      console.log('📹 Creating MediaRecorder...');
      
      // Check what MIME types are supported
      let mimeType = 'audio/webm;codecs=opus';
      if (!MediaRecorder.isTypeSupported(mimeType)) {
        mimeType = 'audio/webm';
        if (!MediaRecorder.isTypeSupported(mimeType)) {
          mimeType = 'audio/mp4';
        }
      }
      
      console.log('🎵 Using MIME type:', mimeType);
      setDebugInfo(`Using format: ${mimeType}`);
      
      const mediaRecorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = mediaRecorder;
      
      // Step 3: Set up event handlers
      mediaRecorder.ondataavailable = (event) => {
        console.log('📦 Audio data available:', event.data.size, 'bytes');
        setDebugInfo(`Audio chunk: ${event.data.size} bytes`);
        
        // Process this chunk immediately
        processAudioChunk(event.data);
      };
      
      mediaRecorder.onstart = () => {
        console.log('▶️ Recording started');
        setDebugInfo('Recording started - speak now!');
        setIsRecording(true);
        setIsListening(true);
      };
      
      mediaRecorder.onstop = () => {
        console.log('⏹️ Recording stopped');
        setDebugInfo('Recording stopped');
        setIsRecording(false);
        setIsListening(false);
      };
      
      mediaRecorder.onerror = (event) => {
        console.error('❌ MediaRecorder error:', event.error);
        setDebugInfo(`Error: ${event.error}`);
      };
      
      // Step 4: Start recording with 3-second chunks
      console.log('🚀 Starting MediaRecorder...');
      mediaRecorder.start(3000);
      
    } catch (error) {
      console.error('❌ Error starting recording:', error);
      setDebugInfo(`Error: ${error.message}`);
      alert(`Recording error: ${error.message}`);
    }
  };

  const stopRecording = () => {
    console.log('🛑 Stopping recording...');
    setDebugInfo('Stopping recording...');
    
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    
    setIsRecording(false);
    setIsListening(false);
  };

  const processAudioChunk = async (audioBlob) => {
    console.log('🔄 Processing audio chunk...');
    setDebugInfo('Processing audio...');
    
    try {
      // Convert audio to MP3 format for better ElevenLabs compatibility
      const mp3Blob = await convertToMp3(audioBlob);
      
      // Create FormData
      const formData = new FormData();
      formData.append('audio', mp3Blob, 'recording.mp3');
      
      console.log('📤 Sending to STT API...');
      setDebugInfo('Sending to STT API...');
      
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5001';
      const response = await fetch(`${apiUrl}/api/stt`, {
        method: 'POST',
        body: formData
      });
      
      console.log('📥 STT Response status:', response.status);
      setDebugInfo(`STT Response: ${response.status}`);
      
      if (response.ok) {
        const result = await response.json();
        console.log('✅ STT Result:', result);
        setDebugInfo(`Transcript: "${result.text}"`);
        
        if (result.text && result.text.trim()) {
          onTranscript(result.text.trim());
        }
      } else {
        const errorText = await response.text();
        console.error('❌ STT API error:', response.status, errorText);
        setDebugInfo(`STT Error: ${response.status} - ${errorText}`);
      }
      
    } catch (error) {
      console.error('❌ Error processing audio:', error);
      setDebugInfo(`Processing error: ${error.message}`);
    }
  };

  const convertToMp3 = async (audioBlob) => {
    // For now, return the original blob but with .mp3 extension
    // In production, you'd want to use a library like 'lamejs' for actual MP3 conversion
    console.log('🎵 Converting audio format...');
    setDebugInfo('Converting audio format...');
    
    // Create a new blob with mp3 extension
    return new Blob([audioBlob], { type: 'audio/mpeg' });
  };

  const toggleRecording = () => {
    if (disabled) return;
    
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const getButtonIcon = () => {
    if (disabled) return '🔇';
    if (isRecording) return '⏹️';
    return '🎤';
  };

  const getButtonTitle = () => {
    if (disabled) return 'Voice input disabled';
    if (isRecording) return 'Click to stop recording';
    return 'Click to start voice input';
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.stop();
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  return (
    <div className="voice-recorder-container">
      <button
        type="button"
        className={`voice-btn ${isRecording ? 'listening' : ''} ${disabled ? 'disabled' : ''}`}
        onClick={toggleRecording}
        title={getButtonTitle()}
        disabled={disabled}
      >
        {getButtonIcon()}
      </button>
      
      {/* Debug info */}
      <div className="debug-info">
        <small>{debugInfo}</small>
      </div>
      
      {/* Status indicator */}
      <div className="status-indicator">
        <small>
          {isRecording ? '🔴 Recording...' : '⚪ Ready'}
        </small>
      </div>
    </div>
  );
};

export default VoiceRecorder; 
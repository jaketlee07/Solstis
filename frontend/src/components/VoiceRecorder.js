import React, { useEffect, useRef, useState } from 'react';
import './VoiceRecorder.css';

const VoiceRecorder = ({ onTranscript, isListening, setIsListening, disabled }) => {
  const [debugInfo, setDebugInfo] = useState('Click to start');
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const audioChunksRef = useRef([]);
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const silenceTimerRef = useRef(null);
  const lastChunkTimeRef = useRef(0);

  const startRecording = async () => {
    console.log('🔴 Starting recording...');
    setDebugInfo('Starting recording...');
    audioChunksRef.current = [];
    lastChunkTimeRef.current = Date.now();
    
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
      
      // Use WebM format which is more reliable
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
        if (event.data.size > 0) {
          console.log('📦 Audio chunk received:', event.data.size, 'bytes');
          audioChunksRef.current.push(event.data);
          lastChunkTimeRef.current = Date.now();
          
          // Update debug info with accumulated size
          const totalSize = audioChunksRef.current.reduce((sum, chunk) => sum + chunk.size, 0);
          setDebugInfo(`Recording... ${audioChunksRef.current.length} chunks, ${totalSize} bytes total`);
          
          // Start silence detection timer
          startSilenceDetection();
        }
      };
      
      mediaRecorder.onstart = () => {
        console.log('▶️ Recording started');
        setDebugInfo('Recording started - speak now!');
        setIsRecording(true);
        setIsListening(true);
      };
      
      mediaRecorder.onstop = () => {
        console.log('⏹️ Recording stopped');
        setDebugInfo('Recording stopped, processing audio...');
        setIsRecording(false);
        setIsListening(false);
        
        // Process all accumulated audio chunks
        if (audioChunksRef.current.length > 0) {
          processCompleteAudio();
        }
      };
      
      mediaRecorder.onerror = (event) => {
        console.error('❌ MediaRecorder error:', event.error);
        setDebugInfo(`Error: ${event.error}`);
      };
      
      // Step 4: Start recording with 2-second chunks for continuous listening
      console.log('🚀 Starting MediaRecorder...');
      mediaRecorder.start(2000);
      
    } catch (error) {
      console.error('❌ Error starting recording:', error);
      setDebugInfo(`Error: ${error.message}`);
      alert(`Recording error: ${error.message}`);
    }
  };

  const startSilenceDetection = () => {
    // Clear any existing timer
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
    }
    
    // Set timer for 2 seconds of silence
    silenceTimerRef.current = setTimeout(() => {
      console.log('🔇 Silence detected, stopping recording...');
      setDebugInfo('Silence detected, stopping recording...');
      stopRecording();
    }, 2000);
  };

  const stopRecording = () => {
    console.log('🛑 Stopping recording...');
    setDebugInfo('Stopping recording...');
    
    // Clear silence timer
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }
    
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

  const processCompleteAudio = async () => {
    if (isProcessing || audioChunksRef.current.length === 0) return;
    
    setIsProcessing(true);
    setDebugInfo('Processing complete audio...');
    
    try {
      // Combine all audio chunks into one blob
      const totalSize = audioChunksRef.current.reduce((sum, chunk) => sum + chunk.size, 0);
      console.log(`🔄 Processing ${audioChunksRef.current.length} chunks, total size: ${totalSize} bytes`);
      
      const completeAudioBlob = new Blob(audioChunksRef.current, { 
        type: audioChunksRef.current[0]?.type || 'audio/webm' 
      });
      
      // Create FormData
      const formData = new FormData();
      formData.append('file', completeAudioBlob, 'recording.webm');
      
      console.log('📤 Sending complete audio to STT API...');
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
      
      // Clear processed chunks
      audioChunksRef.current = [];
      
    } catch (error) {
      console.error('❌ Error processing audio:', error);
      setDebugInfo(`Processing error: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
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
    if (isProcessing) return '⏳';
    if (isRecording) return '⏹️';
    return '🎤';
  };

  const getButtonTitle = () => {
    if (disabled) return 'Voice input disabled';
    if (isProcessing) return 'Processing audio...';
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
      if (silenceTimerRef.current) {
        clearTimeout(silenceTimerRef.current);
      }
    };
  }, []);

  return (
    <div className="voice-recorder-container">
      <button
        type="button"
        className={`voice-btn ${isRecording ? 'listening' : ''} ${disabled ? 'disabled' : ''} ${isProcessing ? 'processing' : ''}`}
        onClick={toggleRecording}
        title={getButtonTitle()}
        disabled={disabled || isProcessing}
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
          {isProcessing ? '⏳ Processing...' : isRecording ? '🔴 Recording...' : '⚪ Ready'}
        </small>
      </div>
    </div>
  );
};

export default VoiceRecorder; 
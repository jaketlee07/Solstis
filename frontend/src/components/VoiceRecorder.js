import React, { useEffect, useRef, useState } from 'react';
import './VoiceRecorder.css';

const VoiceRecorder = ({ onTranscript, isListening, setIsListening, disabled }) => {
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcriptionBuffer, setTranscriptionBuffer] = useState('');
  const [stream, setStream] = useState(null);
  const [debugInfo, setDebugInfo] = useState('');

  useEffect(() => {
    return () => {
      // Cleanup: stop any ongoing recording
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      }
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [stream]);

  const startRecording = async () => {
    if (disabled) return;
    
    try {
      setDebugInfo('Requesting microphone access...');
      
      const audioStream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000,
          channelCount: 1
        } 
      });
      
      setStream(audioStream);
      audioChunksRef.current = [];
      setTranscriptionBuffer('');
      setDebugInfo('Microphone access granted, starting recording...');
      
      // Check what MIME types are supported
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') 
        ? 'audio/webm;codecs=opus' 
        : MediaRecorder.isTypeSupported('audio/webm') 
        ? 'audio/webm' 
        : 'audio/mp4';
      
      setDebugInfo(`Using MIME type: ${mimeType}`);
      
      const mediaRecorder = new MediaRecorder(audioStream, {
        mimeType: mimeType
      });
      
      mediaRecorderRef.current = mediaRecorder;
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
          setDebugInfo(`Audio chunk received: ${event.data.size} bytes`);
        }
      };
      
      mediaRecorder.onstart = () => {
        setDebugInfo('Recording started, collecting audio chunks...');
      };
      
      mediaRecorder.onstop = async () => {
        setDebugInfo('Recording stopped, processing audio...');
        if (audioChunksRef.current.length > 0) {
          await processAudioChunks();
        }
      };
      
      mediaRecorder.onerror = (event) => {
        setDebugInfo(`Recording error: ${event.error}`);
        console.error('MediaRecorder error:', event.error);
      };
      
      // Start recording with 2-second chunks for better processing
      mediaRecorder.start(2000);
      setIsListening(true);
      
      // Test recording immediately
      setTimeout(() => {
        if (mediaRecorder.state === 'recording') {
          setDebugInfo('Recording test: 2 seconds passed, should have audio chunks');
        }
      }, 2500);
      
    } catch (error) {
      console.error('Error starting recording:', error);
      setDebugInfo(`Error: ${error.message}`);
      alert(`Unable to access microphone: ${error.message}`);
    }
  };

  const stopRecording = () => {
    setDebugInfo('Stopping recording...');
    
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    setIsListening(false);
    
    // Stop all audio tracks
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
  };

  const processAudioChunks = async () => {
    if (isProcessing || audioChunksRef.current.length === 0) return;
    
    setIsProcessing(true);
    setDebugInfo('Processing audio chunks...');
    
    try {
      // Create audio blob from chunks
      const audioBlob = new Blob(audioChunksRef.current, { 
        type: audioChunksRef.current[0]?.type || 'audio/webm' 
      });
      
      setDebugInfo(`Audio blob created: ${audioBlob.size} bytes, type: ${audioBlob.type}`);
      
      // Send to ElevenLabs STT API
      const transcript = await sendToElevenLabs(audioBlob);
      
      if (transcript && transcript.trim()) {
        setDebugInfo(`Transcript received: "${transcript}"`);
        
        // Add to buffer and check if we have a complete sentence
        const newBuffer = transcriptionBuffer + ' ' + transcript;
        setTranscriptionBuffer(newBuffer);
        
        // Check if we have a complete sentence (ends with punctuation)
        if (/[.!?]/.test(transcript)) {
          const completeSentence = newBuffer.trim();
          if (completeSentence) {
            setDebugInfo(`Complete sentence detected: "${completeSentence}"`);
            onTranscript(completeSentence);
            setTranscriptionBuffer('');
          }
        }
      } else {
        setDebugInfo('No transcript received or empty transcript');
      }
      
      // Clear processed chunks
      audioChunksRef.current = [];
      
    } catch (error) {
      console.error('Error processing audio:', error);
      setDebugInfo(`Processing error: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const sendToElevenLabs = async (audioBlob) => {
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5001';
      setDebugInfo(`Sending to API: ${apiUrl}/api/stt`);
      
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');
      
      const response = await fetch(`${apiUrl}/api/stt`, {
        method: 'POST',
        body: formData
      });
      
      setDebugInfo(`API response status: ${response.status}`);
      
      if (response.ok) {
        const result = await response.json();
        setDebugInfo(`API response: ${JSON.stringify(result)}`);
        return result.text;
      } else {
        const errorText = await response.text();
        setDebugInfo(`API error: ${response.status} - ${errorText}`);
        throw new Error(`STT API error: ${response.status} - ${errorText}`);
      }
    } catch (error) {
      console.error('ElevenLabs STT error:', error);
      setDebugInfo(`STT error: ${error.message}`);
      return null;
    }
  };

  const toggleListening = () => {
    if (isListening) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const getButtonIcon = () => {
    if (disabled) return '🔇';
    if (isProcessing) return '⏳';
    if (isListening) return '⏹️';
    return '🎤';
  };

  const getButtonTitle = () => {
    if (disabled) return 'Voice input disabled';
    if (isProcessing) return 'Processing audio...';
    if (isListening) return 'Click to stop recording';
    return 'Click to start voice input';
  };

  return (
    <div className="voice-recorder-container">
      <button
        type="button"
        className={`voice-btn ${isListening ? 'listening' : ''} ${disabled ? 'disabled' : ''} ${isProcessing ? 'processing' : ''}`}
        onClick={toggleListening}
        title={getButtonTitle()}
        disabled={disabled || isProcessing}
      >
        {getButtonIcon()}
      </button>
      
      {/* Show transcription buffer */}
      {transcriptionBuffer && (
        <div className="transcription-buffer">
          <small>Listening: {transcriptionBuffer}</small>
        </div>
      )}
      
      {/* Debug info */}
      {debugInfo && (
        <div className="debug-info">
          <small>Debug: {debugInfo}</small>
        </div>
      )}
    </div>
  );
};

export default VoiceRecorder; 
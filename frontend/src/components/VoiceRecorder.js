import React, { useEffect, useRef, useState } from 'react';
import './VoiceRecorder.css';

const VoiceRecorder = ({ onTranscript, isListening, setIsListening, disabled }) => {
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcriptionBuffer, setTranscriptionBuffer] = useState('');
  const [stream, setStream] = useState(null);

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
      
      const mediaRecorder = new MediaRecorder(audioStream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorder.onstop = async () => {
        if (audioChunksRef.current.length > 0) {
          await processAudioChunks();
        }
      };
      
      // Start recording with 3-second chunks for real-time processing
      mediaRecorder.start(3000);
      setIsListening(true);
      
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Unable to access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
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
    
    try {
      // Create audio blob from chunks
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
      
      // Convert to WAV format for better ElevenLabs compatibility
      const wavBlob = await convertToWav(audioBlob);
      
      // Send to ElevenLabs STT API
      const transcript = await sendToElevenLabs(wavBlob);
      
      if (transcript && transcript.trim()) {
        // Add to buffer and check if we have a complete sentence
        const newBuffer = transcriptionBuffer + ' ' + transcript;
        setTranscriptionBuffer(newBuffer);
        
        // Check if we have a complete sentence (ends with punctuation)
        if (/[.!?]/.test(transcript)) {
          const completeSentence = newBuffer.trim();
          if (completeSentence) {
            onTranscript(completeSentence);
            setTranscriptionBuffer('');
          }
        }
      }
      
      // Clear processed chunks
      audioChunksRef.current = [];
      
    } catch (error) {
      console.error('Error processing audio:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const convertToWav = async (audioBlob) => {
    // For now, return the original blob
    // In production, you might want to use a library like 'audio-recorder-polyfill'
    // or convert to WAV format for better compatibility
    return audioBlob;
  };

  const sendToElevenLabs = async (audioBlob) => {
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5001';
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');
      
      const response = await fetch(`${apiUrl}/api/stt`, {
        method: 'POST',
        body: formData
      });
      
      if (response.ok) {
        const result = await response.json();
        return result.text;
      } else {
        throw new Error(`STT API error: ${response.status}`);
      }
    } catch (error) {
      console.error('ElevenLabs STT error:', error);
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
    </div>
  );
};

export default VoiceRecorder; 
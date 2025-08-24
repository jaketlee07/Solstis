import React, { useState, useRef } from 'react';
import './ImageUploader.css';

const ImageUploader = ({ onAnalysis, kitType, disabled }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [preview, setPreview] = useState(null);
  const fileInputRef = useRef(null);

  const handleFile = async (file) => {
    if (!file) return;

    // Check file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      alert('Please upload a valid image file (JPEG, PNG, GIF, or WebP)');
      return;
    }

    // Check file size (20MB max)
    if (file.size > 20 * 1024 * 1024) {
      alert('Image file too large. Maximum size: 20MB');
      return;
    }

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreview(e.target.result);
    };
    reader.readAsDataURL(file);

    // Upload and analyze
    await uploadAndAnalyze(file);
  };

  const uploadAndAnalyze = async (file) => {
    setIsUploading(true);

    try {
      const formData = new FormData();
      formData.append('image', file);
      formData.append('kit_type', kitType);
      formData.append('user_context', 'User uploaded image for medical analysis');

      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5001';
      const response = await fetch(`${apiUrl}/api/analyze-image`, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        onAnalysis(result.analysis);
      } else {
        const errorText = await response.text();
        throw new Error(`Upload failed: ${response.status} - ${errorText}`);
      }
    } catch (error) {
      console.error('Image analysis error:', error);
      alert(`Failed to analyze image: ${error.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleClick = () => {
    if (!disabled && !isUploading) {
      fileInputRef.current?.click();
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const removePreview = () => {
    setPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="image-uploader-container">
      <div
        className={`image-upload-area ${dragActive ? 'drag-active' : ''} ${disabled ? 'disabled' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        {preview ? (
          <div className="image-preview">
            <img src={preview} alt="Preview" />
            <button
              type="button"
              className="remove-image-btn"
              onClick={(e) => {
                e.stopPropagation();
                removePreview();
              }}
              title="Remove image"
            >
              ×
            </button>
          </div>
        ) : (
          <div className="upload-prompt">
            {isUploading ? (
              <>
                <div className="upload-spinner"></div>
                <p>Analyzing image...</p>
              </>
            ) : (
              <>
                <div className="upload-icon">📷</div>
                <p>Click or drag image here</p>
                <p className="upload-hint">Upload a photo of your injury or condition</p>
              </>
            )}
          </div>
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileInput}
        style={{ display: 'none' }}
        disabled={disabled || isUploading}
      />

      {preview && !isUploading && (
        <div className="upload-actions">
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => uploadAndAnalyze(fileInputRef.current.files[0])}
            disabled={disabled}
          >
            Analyze Image
          </button>
        </div>
      )}
    </div>
  );
};

export default ImageUploader; 
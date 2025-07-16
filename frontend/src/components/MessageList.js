import React from 'react';
import './MessageList.css';

const MessageList = ({ messages, isLoading }) => {
  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="message-list">
      {messages.map((message) => (
        <div key={message.id} className={`message ${message.role}`}>
          <div className="message-avatar">
            {message.role === 'user' ? 'U' : 'S'}
          </div>
          <div className="message-content">
            <div className="message-text">{message.content}</div>
            <div className="message-time">
              {formatTime(message.timestamp)}
            </div>
          </div>
        </div>
      ))}
      
      {isLoading && (
        <div className="message assistant">
          <div className="message-avatar">S</div>
          <div className="message-content">
            <div className="message-text">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MessageList; 
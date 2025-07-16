# Solstis React Frontend

A modern React application for the Solstis AI medical assistant with browser-based voice features.

## Features

- 🎤 **Browser-based Voice Recognition** - Uses Web Speech API for speech-to-text
- 🔊 **Text-to-Speech** - Built-in browser TTS for audio responses
- 📱 **Responsive Design** - Works on desktop and mobile devices
- 🎨 **Modern UI** - Clean, intuitive interface with smooth animations
- 🔄 **Real-time Chat** - Instant messaging with AI assistant
- 🩺 **Kit-specific Guidance** - Tailored responses based on selected medical kit

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- The Flask API backend running on port 5001

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

### Environment Variables

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:5001
```

## Available Scripts

- `npm start` - Runs the app in development mode
- `npm build` - Builds the app for production
- `npm test` - Launches the test runner
- `npm eject` - Ejects from Create React App (not recommended)

## Browser Compatibility

Voice features require a modern browser with Web Speech API support:
- Chrome/Chromium (recommended)
- Firefox
- Safari (limited support)
- Edge

## Deployment

1. Build the production version:
```bash
npm run build
```

2. Deploy the `build` folder to your hosting service.

## API Integration

The frontend communicates with the Flask API backend via REST endpoints:
- `GET /api/kits` - Get available medical kits
- `POST /api/setup` - Initialize user session
- `POST /api/chat` - Send chat messages
- `POST /api/clear` - Clear conversation history

## Voice Features

### Speech Recognition
- Uses `webkitSpeechRecognition` or `SpeechRecognition` API
- Supports continuous listening with visual feedback
- Handles errors gracefully with fallback to text input

### Text-to-Speech
- Uses `speechSynthesis` API
- Automatically speaks AI responses
- Configurable voice settings and speech rate

## Project Structure

```
src/
├── components/          # React components
│   ├── Chat.js         # Main chat interface
│   ├── Setup.js        # User setup and kit selection
│   ├── VoiceRecorder.js # Voice input component
│   └── MessageList.js  # Message display component
├── context/            # React context providers
│   └── KitContext.js   # Kit data management
├── App.js              # Main app component
└── index.js            # App entry point
``` 
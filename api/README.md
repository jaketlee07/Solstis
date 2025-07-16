# Solstis Flask API

A Flask-based REST API backend for the Solstis AI medical assistant.

## Features

- 🤖 **OpenAI Integration** - Powered by GPT-3.5-turbo
- 🩺 **Kit-specific Responses** - Tailored medical guidance based on available supplies
- 💬 **Conversation Management** - Session-based chat history
- 🔒 **CORS Support** - Cross-origin requests for frontend integration
- 📊 **Health Monitoring** - Built-in health check endpoint

## Getting Started

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- pip

### Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables:
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

4. Run the server:
```bash
python app.py
```

The API will be available at `http://localhost:5001`

## API Endpoints

### GET /api/kits
Get all available medical kits.

**Response:**
```json
[
  {
    "id": "standard",
    "name": "Standard Kit",
    "description": "Comprehensive first aid kit for general use.",
    "use_case": "Home, workplace, or everyday carry.",
    "contents": [...]
  }
]
```

### POST /api/setup
Initialize a new user session.

**Request:**
```json
{
  "user_name": "John",
  "kit_type": "standard"
}
```

**Response:**
```json
{
  "status": "success"
}
```

### POST /api/chat
Send a chat message to the AI assistant.

**Request:**
```json
{
  "user_input": "I cut my finger",
  "user_name": "John",
  "kit_type": "standard"
}
```

**Response:**
```json
{
  "response": "I'm here to help! First, let's assess the situation...",
  "status": "success"
}
```

### POST /api/clear
Clear conversation history for a user.

**Request:**
```json
{
  "user_name": "John"
}
```

**Response:**
```json
{
  "status": "success"
}
```

### GET /api/health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00"
}
```

## Environment Variables

- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `PORT` - Server port (default: 5001)

## Medical Kits

The API supports four different medical kits:

1. **Standard Kit** - Comprehensive first aid for general use
2. **College Kit** - Essential supplies for college students
3. **OC Standard Kit** - Occupational safety with Honeywell products
4. **OC Vehicle Kit** - Compact emergency kit for vehicles

Each kit has specific contents that the AI uses to provide tailored medical guidance.

## System Prompts

The AI uses dynamic system prompts that include:
- Kit-specific inventory
- Medical guidelines and safety protocols
- Emergency response instructions
- Step-by-step guidance format

## Error Handling

The API includes comprehensive error handling:
- Missing required fields
- OpenAI API errors
- Invalid kit types
- Network connectivity issues

## Production Deployment

For production deployment:

1. Use a production WSGI server like Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

2. Set up environment variables securely
3. Use a reverse proxy (nginx/Apache)
4. Implement proper logging and monitoring
5. Consider using a database for conversation storage

## Security Considerations

- Validate all input data
- Implement rate limiting
- Use HTTPS in production
- Secure API key storage
- Consider user authentication for production use 
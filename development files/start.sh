#!/bin/bash

# Solstis AI Assistant Startup Script
echo "🚀 Starting Solstis AI Assistant..."

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY environment variable is not set"
    echo "Please set it with: export OPENAI_API_KEY='your-api-key-here'"
    exit 1
fi

# Function to cleanup background processes
cleanup() {
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start Flask backend
echo "🔧 Starting Flask API backend..."
cd api
python -m venv venv 2>/dev/null || true
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1
python app.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start React frontend
echo "⚛️  Starting React frontend..."
cd frontend
npm install > /dev/null 2>&1
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ Solstis AI Assistant is starting up!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for both processes
wait 
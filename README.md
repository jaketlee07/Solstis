# Solstis Assistant

An AI assistant that provides step-by-step first-aid instructions during minor health emergencies. Available in both voice and text interfaces.

## Features

- 🎤 Voice input using your microphone (voice version)
- 📝 Text input/output (text version)
- 🧠 Speech-to-text using OpenAI's Whisper (voice version)
- 🤖 AI responses using GPT-4
- 🔊 Text-to-speech using ElevenLabs (voice version)
- 🎯 Step-by-step first-aid instructions
- 💬 Natural, supportive conversation

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   If `pyaudio` installation fails (only needed for voice version):

   - macOS: `brew install portaudio && pip install pyaudio`
   - Windows: Use [Unofficial Binaries](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)

2. Set up API keys:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key
   - Add your ElevenLabs API key (only needed for voice version)
   - (Optional) Add a custom ElevenLabs voice ID

## Usage

### Voice Version

Run the voice assistant:

```bash
python solstis_voice.py
```

- Speak when you see "🎤 Listening..."
- Press Ctrl+C to exit

### Text Version

Run the text assistant:

```bash
python solstis_text.py
```

- Type your message and press Enter
- Type 'quit' or press Ctrl+C to exit

## Web Version (Flask)

To run the Solstis assistant as a web app:

1. Install dependencies (if not already):
   ```bash
   pip install -r requirements-web.txt
   ```
2. Set your environment variables in `.env` (including `OPENAI_API_KEY` and optionally `FLASK_SECRET_KEY`).
3. Start the Flask server:
   ```bash
   FLASK_APP=solstis_web.py flask run
   ```
4. Open your browser and go to [http://localhost:5000](http://localhost:5000)

The web interface provides a chat window for interacting with Solstis.

## Requirements

- Python 3.7+
- OpenAI API key
- ElevenLabs API key (voice version only)
- Working microphone (voice version only)
- Speakers or headphones (voice version only)

## Next Steps

- [ ] Add GUI interface
- [ ] Integrate YAML step flow
- [ ] Add emergency contact integration
- [ ] Implement voice customization
- [ ] Add multi-language support

## Hosting Options

### 1. **Railway** (Recommended - Easiest)

Railway is perfect for quick deployment with automatic HTTPS and custom domains.

1. Install Railway CLI:

   ```bash
   npm install -g @railway/cli
   ```

2. Deploy:

   ```bash
   railway login
   railway init
   railway up
   ```

3. Set environment variables in Railway dashboard:
   - `OPENAI_API_KEY`
   - `FLASK_SECRET_KEY`

### 2. **Render** (Free Tier Available)

Great for free hosting with automatic deployments.

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set build command: `pip install -r requirements-web.txt`
4. Set start command: `gunicorn wsgi:app`
5. Add environment variables:
   - `OPENAI_API_KEY`
   - `FLASK_SECRET_KEY`

### 3. **Heroku** (Paid)

Classic platform with good free tier alternatives.

1. Install Heroku CLI
2. Deploy:
   ```bash
   heroku create your-solstis-app
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```
3. Set environment variables:
   ```bash
   heroku config:set OPENAI_API_KEY=your_key
   heroku config:set FLASK_SECRET_KEY=your_secret
   ```

### 4. **DigitalOcean App Platform**

Professional hosting with good performance.

1. Connect your GitHub repository
2. Choose Python environment
3. Set build command: `pip install -r requirements-web.txt`
4. Set run command: `gunicorn wsgi:app`
5. Add environment variables in the dashboard

### 5. **VPS (DigitalOcean, AWS, etc.)**

For full control and customization.

1. Set up a VPS with Ubuntu
2. Install Python, pip, and nginx
3. Clone your repository
4. Install dependencies: `pip install -r requirements-web.txt`
5. Set up systemd service
6. Configure nginx as reverse proxy

### Environment Variables Required

- `OPENAI_API_KEY`: Your OpenAI API key
- `FLASK_SECRET_KEY`: A secure random string for session encryption
- `FLASK_ENV`: Set to "production" for production deployments

### Local Production Testing

Test your production setup locally:

```bash
export FLASK_ENV=production
export FLASK_SECRET_KEY=your-secret-key
pip install -r requirements-web.txt
gunicorn wsgi:app
```

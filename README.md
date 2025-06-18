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
   pip install -r requirements.txt
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

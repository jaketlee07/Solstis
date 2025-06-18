import os
import tempfile
import openai
import speech_recognition as sr
from elevenlabs import generate, play, set_api_key, VoiceSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# === CONFIGURATION ===
openai.api_key = os.getenv("OPENAI_API_KEY")
set_api_key(os.getenv("ELEVENLABS_API_KEY"))
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID") or "Rachel"  # Default voice

SYSTEM_PROMPT = """You are Solstis, a calm, helpful, and reassuring AI assistant that provides step-by-step first-aid instructions during minor health emergencies.

Your communication style:
- Be concise and direct while maintaining a supportive tone
- Always begin by checking for life-threatening symptoms
- Use clear, brief instructions
- Acknowledge user responses with short confirmations
- Break complex steps into simple, digestible parts
- Keep responses under 2-3 sentences when possible
- Use natural conversation flow with minimal pauses
- Remember and reference previous steps and user responses

Example interaction:
USER: I cut my finger with a kitchen knife. It's bleeding a lot.
SOLSTIS: Hey there. I'm here to help. First—are you feeling faint, dizzy, or nauseous?

USER: No, I feel okay. Just a little shaky.
SOLSTIS: Good. Do you have access to clean, running water?

USER: Yes—I'm in my kitchen.
SOLSTIS: Remove any rings, then rinse the wound under cool water. Let me know when done.

Always maintain this concise, supportive tone while providing clear medical guidance."""

# === SOLSTIS AGENT CLASS ===

class SolstisAssistant:
    def __init__(self):
        self.conversation_history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
    
    def ask(self, user_input):
        print(f"🧠 You said: {user_input}")
        self.conversation_history.append({"role": "user", "content": user_input})
        
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=self.conversation_history
        )
        
        assistant_response = response["choices"][0]["message"]["content"]
        self.conversation_history.append({"role": "assistant", "content": assistant_response})
        return assistant_response
    
    def clear_history(self):
        self.conversation_history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

# === AUDIO FUNCTIONS ===

def record_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening... Speak now.")
        audio = recognizer.listen(source)
        print("⏳ Processing...")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            with open(temp_audio.name, "wb") as f:
                f.write(audio.get_wav_data())
            return temp_audio.name

def transcribe_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript["text"]

def speak_text(text):
    print(f"💬 Solstis: {text}\n")
    voice_settings = VoiceSettings(
        stability=0.5,
        similarity_boost=0.75,
        style=0.0,
        use_speaker_boost=True
    )
    audio = generate(
        text=text,
        voice=VOICE_ID,
        model="eleven_monolingual_v1",
        voice_settings=voice_settings
    )
    play(audio)

# === MAIN LOOP ===

def run():
    print("🩺 Solstis Voice Assistant — say something or Ctrl+C to quit.\n")
    print("💡 Example: 'I cut my finger with a kitchen knife. It's bleeding a lot.'")
    print("💡 Say 'clear' to reset the conversation.\n")
    
    assistant = SolstisAssistant()
    
    while True:
        try:
            audio_file = record_audio()
            user_text = transcribe_audio(audio_file)
            os.remove(audio_file)
            
            if user_text.strip().lower() == 'clear':
                assistant.clear_history()
                speak_text("Conversation history cleared.")
                continue
            
            response = assistant.ask(user_text)
            speak_text(response)
        
        except KeyboardInterrupt:
            print("\n👋 Exiting Solstis.")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    run()

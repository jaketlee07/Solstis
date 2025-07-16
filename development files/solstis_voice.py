import os
import tempfile
import speech_recognition as sr
from dotenv import load_dotenv
from openai import OpenAI
from elevenlabs import ElevenLabs, VoiceSettings, stream, play

# === Load environment variables ===
load_dotenv()

# === Clients ===
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID") or "kdmDKE6EkgrWrrykO9Qt"

# === System Prompt for Solstis ===
# SYSTEM_PROMPT = """You are Solstis, a calm, helpful, and reassuring AI assistant that provides step-by-step first-aid instructions during minor health emergencies.

# Your communication style:
# - Be concise and direct while maintaining a supportive tone
# - Always begin by checking for life-threatening symptoms
# - Use clear, brief instructions
# - Acknowledge user responses with short confirmations
# - Break complex steps into simple, digestible parts
# - Keep responses under 2-3 sentences when possible
# - Use natural conversation flow with minimal pauses
# - Remember and reference previous steps and user responses
# """

SYSTEM_PROMPT = """You are Solstis, a gentle, calm, and highly knowledgeable AI-powered medical assistant embedded in a smart med kit. You assist users experiencing minor injuries, burns, or common ailments using only:

- Items from the current Solstis kit (Standard, College, OC Standard, or OC Vehicle)
- Common household resources (e.g., running water, soap, paper towels)

Your primary goals:
1. **Triage First:** Always begin by calmly assessing whether this is a life-threatening emergency. If yes, urge the user to call 911 or offer to do so.
2. **Stay Present and Empathetic:** Speak naturally, like a calm friend guiding them step-by-step. Reassure them frequently.
3. **Use Only Available Items:** Recommend only items from the active kit and clearly identify their location by referencing the LED-lit compartment.
4. **Adapt by Scenario:** Respond fluidly based on context. Ask short follow-up questions to clarify condition and severity.
5. **Follow Up:** Offer relevant aftercare, such as reminders to change bandages or see a healthcare provider.
6. **Never Exceed Scope:** Avoid offering diagnoses, prescriptions, or complex medical advice.

Include this fallback check at every stage:  
"If symptoms worsen or this seems more serious than expected, please consider calling 911 or seeing a healthcare provider."
"""

# === Solstis Assistant Class ===
class SolstisAssistant:
    def __init__(self):
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]

    def ask(self, user_input):
        print(f"🧠 You said: {user_input}")
        self.history.append({"role": "user", "content": user_input})
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=self.history
        )
        reply = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def clear(self):
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]

# === Record Audio ===
def record_audio():
    recognizer = sr.Recognizer()
    mic_list = sr.Microphone.list_microphone_names()
    print("🎤 Available mics:", mic_list)

    with sr.Microphone() as source:
        recognizer.energy_threshold = 300
        recognizer.pause_threshold = 0.7
        recognizer.adjust_for_ambient_noise(source, duration=0.5)

        print("🎤 Listening... Speak now.")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("⏳ Processing...")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                temp_audio.write(audio.get_wav_data())
                return temp_audio.name
        except sr.WaitTimeoutError:
            print("⏱️ No speech detected. Try again.")
            return None

# === Transcribe Audio Using Whisper (OpenAI v1) ===
def transcribe_audio(audio_path):
    with open(audio_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )
        return transcript.text

# === Speak Text with ElevenLabs ===
def speak_text(text):
    print(f"💬 Solstis: {text}\n")
    audio_stream = elevenlabs_client.text_to_speech.stream(
        voice_id=VOICE_ID,
        model_id="eleven_turbo_v2",
        optimize_streaming_latency=1,
        text=text,
        voice_settings=VoiceSettings(
            stability=0.5,
            similarity_boost=0.75,
            style=0.0,
            use_speaker_boost=True
        )
    )
    play(audio_stream)

# === Main Loop ===
def run():
    print("🩺 Solstis Voice Assistant — say something or Ctrl+C to quit.\n")
    print("💡 Example: 'I cut my finger with a kitchen knife. It's bleeding a lot.'")
    print("💡 Say 'clear' to reset the conversation.\n")

    assistant = SolstisAssistant()

    while True:
        try:
            audio_file = record_audio()
            if not audio_file:
                continue

            user_text = transcribe_audio(audio_file)
            os.remove(audio_file)

            if user_text.strip().lower() == "clear":
                assistant.clear()
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

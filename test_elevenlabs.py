import os
import requests
import json

def test_elevenlabs():
    # Test configuration
    api_key = os.getenv('ELEVENLABS_API_KEY')
    voice_id = 'XcXEQzuLXRU9RcfWzEJt'  # The voice ID you're using
    
    print(f"API Key present: {'YES' if api_key else 'NO'}")
    if api_key:
        print(f"API Key starts with: {api_key[:10]}...")
    
    if not api_key:
        print("❌ No API key found. Set ELEVENLABS_API_KEY environment variable.")
        return
    
    # Test 1: Check if voice exists
    print("\n🔍 Testing voice availability...")
    url = f"https://api.elevenlabs.io/v1/voices/{voice_id}"
    headers = {"xi-api-key": api_key}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Voice check status: {response.status_code}")
        if response.status_code == 200:
            voice_data = response.json()
            print(f"✅ Voice found: {voice_data.get('name', 'Unknown')}")
        else:
            print(f"❌ Voice not found: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error checking voice: {e}")
        return
    
    # Test 2: Try TTS
    print("\n🔊 Testing text-to-speech...")
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    data = {
        "text": "Hello, this is a test of the ElevenLabs API.",
        "model_id": "eleven_turbo_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }
    
    try:
        response = requests.post(tts_url, json=data, headers=headers)
        print(f"TTS status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ TTS successful! Audio data received.")
            print(f"Audio size: {len(response.content)} bytes")
        else:
            print(f"❌ TTS failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error in TTS: {e}")

if __name__ == "__main__":
    test_elevenlabs() 
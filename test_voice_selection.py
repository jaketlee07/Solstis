import requests
import json

def test_voice_selection():
    base_url = "http://localhost:5001"  # Change this to your API URL
    
    print("🎤 Testing Voice Selection API")
    print("=" * 40)
    
    # Test 1: Get available voices
    print("\n1. Fetching available voices...")
    try:
        response = requests.get(f"{base_url}/api/voices")
        if response.status_code == 200:
            voices = response.json()
            print(f"✅ Found {len(voices.get('voices', []))} voices:")
            for voice in voices.get('voices', [])[:5]:  # Show first 5
                print(f"   - {voice['name']} (ID: {voice['voice_id']})")
        else:
            print(f"❌ Failed to get voices: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Test TTS with default voice
    print("\n2. Testing TTS with default voice...")
    try:
        response = requests.post(f"{base_url}/api/tts", 
                               json={"text": "Hello, this is a test."})
        if response.status_code == 200:
            print("✅ TTS with default voice successful!")
        else:
            print(f"❌ TTS failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Test TTS with specific voice (if we have voices)
    print("\n3. Testing TTS with specific voice...")
    try:
        # Get a voice ID first
        voices_response = requests.get(f"{base_url}/api/voices")
        if voices_response.status_code == 200:
            voices = voices_response.json()
            if voices.get('voices'):
                voice_id = voices['voices'][0]['voice_id']
                response = requests.post(f"{base_url}/api/tts", 
                                       json={
                                           "text": "Hello, this is a test with a specific voice.",
                                           "voice_id": voice_id
                                       })
                if response.status_code == 200:
                    print(f"✅ TTS with voice {voice_id} successful!")
                else:
                    print(f"❌ TTS with specific voice failed: {response.status_code}")
            else:
                print("⚠️  No voices available to test with")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_voice_selection() 
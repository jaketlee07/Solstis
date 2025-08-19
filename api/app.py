from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import openai
import os
from datetime import datetime
import json
import requests
import tempfile

app = Flask(__name__)
CORS(app, origins=[
    "http://localhost:3000",
    "https://solstis-frontend.onrender.com",
    "https://*.onrender.com"
])

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Kit data
KITS = [
    {
        "id": "standard",
        "name": "Standard Kit",
        "description": "Comprehensive first aid kit for general use.",
        "use_case": "Home, workplace, or everyday carry.",
        "contents": [
            {"item": "Band-Aids"},
            {"item": "4\" x 4\" Gauze Pads", "quantity": 5},
            {"item": "2\" Roll Gauze", "description": "Holds gauze in place"},
            {"item": "5\" x 9\" ABD Pad", "description": "For nosebleeds or deeper cuts"},
            {"item": "1\" Cloth Medical Tape"},
            {"item": "Triple Antibiotic Ointment", "description": "Mini tube for infection prevention"},
            {"item": "Blunt Tip Tweezers", "description": "For splinters or debris removal"},
            {"item": "Small Trauma Shears", "description": "Safe for cutting tape or clothing"},
            {"item": "QuickClot Gauze or Hemostatic Wipe", "description": "For guided serious bleeding control"},
            {"item": "4\" x 4\" Burn Gel Dressing", "description": "For finger burns or hot pans"},
            {"item": "2 oz Burn Spray", "description": "For minor burns or sunburns"},
            {"item": "Sting & Bite Relief Wipes", "quantity": 2},
            {"item": "Mini Eye Wash Bottle", "quantity": 1},
            {"item": "Oral Glucose Gel", "description": "For dizziness or low energy"},
            {"item": "Electrolyte Powder Pack", "description": "Hydration support"},
            {"item": "2\" Elastic Ace Bandage", "description": "For sprains"},
            {"item": "Instant Cold Pack", "description": "For bruises or swelling"},
            {"item": "Triangle Bandage", "description": "Can be sling or gentle wrap"}
        ]
    },
    {
        "id": "college",
        "name": "College Kit",
        "description": "Essential medical supplies for college students.",
        "use_case": "Dorm rooms, campus travel, everyday minor illness care.",
        "contents": [
            {"item": "Acetaminophen"},
            {"item": "Ibuprofen"},
            {"item": "Hydrocortisone Cream"},
            {"item": "Benadryl"},
            {"item": "Allergy Medication"},
            {"item": "DayQuil"},
            {"item": "NyQuil"},
            {"item": "Cough Medicines"},
            {"item": "Antacids"},
            {"item": "Antiseptic Wipes"},
            {"item": "Antibiotic Ointment"},
            {"item": "Adhesive Bandages"},
            {"item": "Gauze Pads"},
            {"item": "Medical Tape"},
            {"item": "Elastic Bandage"},
            {"item": "Hand Sanitizer"},
            {"item": "Latex-Free Gloves"}
        ]
    },
    {
        "id": "oc_standard",
        "name": "OC Standard Kit",
        "description": "Occupational safety kit with Honeywell products.",
        "use_case": "Worksites, industrial environments, OSHA compliance.",
        "contents": [
            {"item": "24\" x 72\" Compress", "quantity": 2},
            {"item": "1\" x 3\" Cloth Bandages", "quantity": 32},
            {"item": "1\" x 2 1/2 yd Adhesive Tape", "quantity": 2},
            {"item": "Eye Dressing Package", "quantity": 4},
            {"item": "4\" x 6 yd Roller Bandage", "quantity": 2},
            {"item": "4\" Offset Compress", "quantity": 2},
            {"item": "3\" x 3\" Pads", "quantity": 8},
            {"item": "Exam Gloves", "quantity": 12},
            {"item": "Triangle Bandage", "quantity": 2},
            {"item": "1 oz Eye Wash", "quantity": 2},
            {"item": "Cold Pack", "quantity": 2},
            {"item": "Antiseptic Skin Wipes", "quantity": 20},
            {"item": "Sting Kill Wipes", "quantity": 20},
            {"item": "Rescue Blanket", "quantity": 1},
            {"item": "2\" Elastic Ace Bandage", "description": "For sprains"},
            {"item": "Instant Cold Pack", "description": "For bruises, swelling"},
            {"item": "Triangle Bandage", "description": "Can be sling or wrap"}
        ]
    },
    {
        "id": "oc_vehicle",
        "name": "OC Vehicle Kit",
        "description": "Compact vehicle emergency kit.",
        "use_case": "Glovebox or trunk storage for roadside injuries.",
        "contents": [
            {"item": "24\" x 72\" Gauze Compress", "quantity": 1},
            {"item": "1\" x 2 1/2 yd Adhesive Tape", "quantity": 2},
            {"item": "Eye Dressing Package", "quantity": 4},
            {"item": "4\" Offset Compress", "quantity": 1},
            {"item": "3\" x 3\" Pads", "quantity": 4},
            {"item": "Cold Pack", "quantity": 1},
            {"item": "Antiseptic Skin Wipes", "quantity": 10},
            {"item": "1 oz Eye Wash", "quantity": 1},
            {"item": "1\" x 3\" Cloth Bandages", "quantity": 16},
            {"item": "Rescue Blanket", "quantity": 1},
            {"item": "Exam Gloves", "quantity": 12}
        ]
    }
]

# Global conversation storage (in production, use a proper database)
conversations = {}

def get_system_prompt(kit_type):
    """Generate system prompt based on kit type"""
    kit = next((k for k in KITS if k["id"] == kit_type), None)
    if not kit:
        return "You are a helpful medical assistant."
    
    # Build kit contents string
    contents_list = []
    for item in kit["contents"]:
        item_str = item["item"]
        if "quantity" in item:
            item_str += f" (qty: {item['quantity']})"
        if "description" in item:
            item_str += f" - {item['description']}"
        contents_list.append(item_str)
    
    contents_str = "\n".join([f"- {item}" for item in contents_list])
    
    # Use a simpler approach to avoid quote issues
    prompt = f"""You are Solstis, a calm and supportive AI medical assistant. You help users with first aid using only the items available in their specific kit.

KIT INFORMATION:
Kit Name: {kit['name']}
Description: {kit['description']}
Use Case: {kit['use_case']}

AVAILABLE ITEMS:
{contents_str}

Your role:
• Be a real-time guide—natural, concise, supportive
• Always assess for life-threatening danger before offering first aid
• Give clear, step-by-step instructions
• Select only from the current kit (or common home items)
• Refer to the item's highlighted space (not "LED compartment")
• When sizes differ, avoid inches—say "large X highlighted in blue" vs "small X highlighted in orange"
• Recommend calling 9-1-1 when symptoms suggest an emergency
• Encourage follow-up care when appropriate (e.g., "you may need stitches")

IMPORTANT STYLE & FLOW:
- Keep responses to 1-2 short sentences
- Ask one clear follow-up question at a time
- Use plain language; avoid medical jargon (e.g., say "bleeding a lot" instead of "pulsating blood")
- Acknowledge progress briefly ("Great," "Well done")
- Track progress, user replies, and items used
- Only refer to items in this kit or common home items
- Point to items by color-coded highlight: "from the highlighted space," "the blue one," or "the orange one"
- End action steps with "Let me know when you're ready" or "Let me know when done" when appropriate

IF THE USER CAN'T FIND AN ITEM:
1) Acknowledge and give location help (e.g., "It should be in the small pack highlighted in orange on the top row.")
2) Offer the closest in-kit alternative and ask to confirm before switching (e.g., "If you don't see it, we can use the large gauze highlighted in blue instead—should we use that?")
3) Do not jump to unrelated items unless confirmed.

BANDAGE PLACEMENT—HANDS (DEFAULT TIPS):
- For small cuts: clean, dry, thin layer of antibiotic ointment if available, center the pad over the cut, smooth adhesive around the skin, avoid wrapping too tight, check movement and circulation. "Let me know when you're ready."
- For finger joints: place the pad over the cut, angle the adhesive so it doesn't bunch at the knuckle; if needed, reinforce with tape from the highlighted space. "Let me know when you're ready."

Opening message (always at the start of a new conversation):
"Hey [name]. I'm here to help. If this is life-threatening, please call 9-1-1 now. Otherwise, I'll guide you step by step. Can you tell me what happened?"

Examples:

USER: I cut my finger with a kitchen knife. It's bleeding a lot.
SOLSTIS: First—are you feeling faint, dizzy, or having trouble breathing?

USER: No, just a little shaky.
SOLSTIS: Good. Do you have access to clean, running water?

USER: Yes.
SOLSTIS: Great. Rinse the cut under cool water. Remove any rings first. Let me know when you're done.

USER: Done.
SOLSTIS: From the highlighted space, take the small gauze. Press gently for 5 minutes. Let me know when you're done.

USER: I can't find it.
SOLSTIS: No problem—check the small highlighted section. If it's not there, we can use the large gauze in the highlighted section instead.

USER: Found it.
SOLSTIS: Well done. After the bleeding slows, add a thin layer of antibiotic ointment if you have it, then place a bandage from the highlighted space so the pad covers the cut; smooth the tabs so they don't pinch. Let me know when you're done.

Only give instructions using supplies from this kit (or common home items). Do not invent tools or procedures. You are not a diagnostic or medical authority—you are a calm first responder assistant.

"""
    
    return prompt

@app.route('/api/kits', methods=['GET'])
def get_kits():
    """Get all available kits"""
    return jsonify(KITS)

@app.route('/api/setup', methods=['POST'])
def setup():
    """Initialize user session"""
    data = request.get_json()
    user_name = data.get('user_name')
    kit_type = data.get('kit_type')
    
    if not user_name or not kit_type:
        return jsonify({'error': 'Missing user_name or kit_type'}), 400
    
    # Initialize conversation for this user
    conversations[user_name] = {
        'kit_type': kit_type,
        'messages': []
    }
    
    return jsonify({'status': 'success'})

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    data = request.get_json()
    user_input = data.get('user_input')
    user_name = data.get('user_name')
    kit_type = data.get('kit_type')
    
    if not user_input or not user_name:
        return jsonify({'error': 'Missing user_input or user_name'}), 400
    
    # Get or create conversation
    if user_name not in conversations:
        conversations[user_name] = {
            'kit_type': kit_type,
            'messages': []
        }
    
    conversation = conversations[user_name]
    
    # Add user message to conversation
    conversation['messages'].append({
        'role': 'user',
        'content': user_input,
        'timestamp': datetime.now().isoformat()
    })
    
    try:
        # Get system prompt
        system_prompt = get_system_prompt(conversation['kit_type'])
        
        # Prepare messages for OpenAI
        messages = [{'role': 'system', 'content': system_prompt}]
        
        # Add conversation history (last 10 messages to avoid token limits)
        recent_messages = conversation['messages'][-10:]
        for msg in recent_messages:
            messages.append({
                'role': msg['role'],
                'content': msg['content']
            })
        
        # Call OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        assistant_response = response.choices[0].message.content
        
        # Add assistant response to conversation
        conversation['messages'].append({
            'role': 'assistant',
            'content': assistant_response,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            'response': assistant_response,
            'status': 'success'
        })
        
    except Exception as e:
        print(f"Error in chat: {e}")
        return jsonify({
            'error': 'Failed to get response',
            'details': str(e)
        }), 500

@app.route('/api/clear', methods=['POST'])
def clear_conversation():
    """Clear conversation history"""
    data = request.get_json()
    user_name = data.get('user_name')
    
    if user_name and user_name in conversations:
        conversations[user_name]['messages'] = []
    
    return jsonify({'status': 'success'})

@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    """Convert text to speech using ElevenLabs"""
    data = request.get_json()
    text = data.get('text')
    voice_id = data.get('voice_id')  # Allow custom voice selection
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        # ElevenLabs API configuration
        ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
        
        # Use provided voice_id or fall back to environment variable or default
        if not voice_id:
            voice_id = os.getenv('ELEVENLABS_VOICE_ID', 'XcXEQzuLXRU9RcfWzEJt')
        
        if not ELEVENLABS_API_KEY:
            return jsonify({'error': 'ElevenLabs API key not configured'}), 500
        
        # ElevenLabs API call - Updated for current API
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        data = {
            "text": text,
            "model_id": "eleven_turbo_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name
            
            return send_file(temp_file_path, mimetype='audio/mpeg')
        else:
            return jsonify({'error': f'ElevenLabs API error: {response.status_code}'}), 500
            
    except Exception as e:
        print(f"TTS error: {e}")
        return jsonify({'error': 'Failed to generate speech'}), 500

@app.route('/api/stt', methods=['POST'])
def speech_to_text():
    """Convert speech to text using ElevenLabs"""
    try:
        # Check if audio file was uploaded
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        # ElevenLabs API configuration
        ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
        
        if not ELEVENLABS_API_KEY:
            return jsonify({'error': 'ElevenLabs API key not configured'}), 500
        
        # ElevenLabs Speech-to-Text API
        url = "https://api.elevenlabs.io/v1/speech-to-text"
        
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        # Prepare the audio file for upload
        files = {
            'audio': (audio_file.filename, audio_file.read(), audio_file.content_type)
        }
        
        # Optional parameters for better accuracy
        data = {
            'model_id': 'eleven_english_sts_v2',  # Best model for English STT
            'language_code': 'en'
        }
        
        response = requests.post(url, headers=headers, files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            transcribed_text = result.get('text', '')
            
            return jsonify({
                'text': transcribed_text,
                'status': 'success'
            })
        else:
            return jsonify({'error': f'ElevenLabs STT API error: {response.status_code}'}), 500
            
    except Exception as e:
        print(f"STT error: {e}")
        return jsonify({'error': 'Failed to transcribe speech'}), 500

@app.route('/api/voices', methods=['GET'])
def get_voices():
    """Get available ElevenLabs voices"""
    try:
        ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
        
        if not ELEVENLABS_API_KEY:
            return jsonify({'error': 'ElevenLabs API key not configured'}), 500
        
        url = "https://api.elevenlabs.io/v1/voices"
        headers = {"xi-api-key": ELEVENLABS_API_KEY}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            voices = response.json()
            # Return simplified voice list
            voice_list = []
            for voice in voices.get('voices', []):
                voice_list.append({
                    'voice_id': voice['voice_id'],
                    'name': voice['name'],
                    'category': voice.get('category', 'unknown')
                })
            return jsonify({'voices': voice_list})
        else:
            return jsonify({'error': f'Failed to fetch voices: {response.status_code}'}), 500
            
    except Exception as e:
        print(f"Error fetching voices: {e}")
        return jsonify({'error': 'Failed to fetch voices'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True) 
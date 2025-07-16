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

IMPORTANT GUIDELINES:
1. ALWAYS start by asking if this is a life-threatening emergency. If yes, immediately instruct to call 911.
2. Only recommend items that are actually in the user's kit (listed above).
3. Provide step-by-step instructions using available items.
4. Be calm, supportive, and reassuring.
5. If an item isn't available, suggest alternatives or explain what to do without it.
6. For serious injuries, always recommend professional medical attention.
7. Use clear, simple language that anyone can understand.
8. Reference the LED-lit compartments to help users locate items quickly.

Example interaction:
User: I cut my finger while cooking
You: I'm here to help! First, let's assess the situation. Is the bleeding severe or life-threatening? 
If so, call 911 immediately. For a minor cut, let's use what you have available. I can see you have Band-Aids and Triple Antibiotic Ointment in your kit. 
Here's what to do: 1) Clean the area gently with water, 2) Apply a small amount of the Triple Antibiotic Ointment, 3) Cover with a Band-Aid. The ointment will help prevent infection. 
How does that sound?"""
    
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
            model="gpt-3.5-turbo",
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
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        # ElevenLabs API configuration
        ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
        VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID', '21m00Tcm4TlvDq8ikWAM')  # Default voice
        
        print(f"TTS Debug: API Key present: {bool(ELEVENLABS_API_KEY)}")
        print(f"TTS Debug: Voice ID: {VOICE_ID}")
        
        if not ELEVENLABS_API_KEY:
            print("TTS Error: ElevenLabs API key not configured")
            return jsonify({'error': 'ElevenLabs API key not configured'}), 500
        
        # ElevenLabs API call
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        print(f"TTS Debug: Making request to ElevenLabs")
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"TTS Debug: Response status: {response.status_code}")
        
        if response.status_code == 200:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name
            
            return send_file(temp_file_path, mimetype='audio/mpeg')
        else:
            error_msg = f'ElevenLabs API error: {response.status_code} - {response.text}'
            print(f"TTS Error: {error_msg}")
            return jsonify({'error': error_msg}), 500
            
    except Exception as e:
        error_msg = f"TTS error: {str(e)}"
        print(error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/tts-test', methods=['GET'])
def tts_test():
    """Test TTS configuration"""
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
    VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID', '21m00Tcm4TlvDq8ikWAM')
    
    return jsonify({
        'elevenlabs_configured': bool(ELEVENLABS_API_KEY),
        'voice_id': VOICE_ID,
        'api_key_length': len(ELEVENLABS_API_KEY) if ELEVENLABS_API_KEY else 0
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True) 
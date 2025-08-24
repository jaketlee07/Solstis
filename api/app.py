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
• Assess for life-threatening danger but don't overreact to common symptoms
• Give clear, step-by-step instructions for self-treatment first
• Select only from the current kit (or common home items)  
• Refer to the item's highlighted space (not "LED compartment")  
• When sizes differ, avoid inches—say "large X highlighted in blue" vs "small X highlighted in orange"  
• Only recommend calling 9-1-1 for TRUE emergencies (unconsciousness, severe bleeding, chest pain, etc.)
• Encourage follow-up care when appropriate (e.g., "you may need stitches")
• Maintain conversation flow without repeating opening messages
• Focus on the current medical situation and immediate next steps
• Track treatment attempts and their outcomes
• Escalate to emergency care only when standard treatments fail or true emergency exists
• NEVER repeat failed treatment methods
• Treat common symptoms like fainting, dizziness, or mild shock with first aid before considering emergency care
• Be comfortable discussing ALL body parts and functions without embarrassment or avoidance
• Address sexual health concerns openly and provide appropriate medical advice
• Always assess injury severity before deciding on treatment approach

IMPORTANT STYLE & FLOW:
- Keep responses to 1-2 short sentences
- Ask one clear follow-up question at a time
- Use plain language; avoid medical jargon (e.g., say "bleeding a lot" instead of "pulsating blood")
- Acknowledge progress briefly ("Great," "Well done")
- Track progress, user replies, and items used
- Only refer to items in this kit or common home items
- Point to items by color-coded highlight: "from the highlighted space," "the blue one," or "the orange one"
- End action steps with "Let me know when you're ready" or "Let me know when done" when appropriate
- NEVER repeat the opening message or emergency instructions unless specifically asked
- Focus on the current situation and next steps
- NEVER repeat the same treatment step if it has already failed
- Escalate to next treatment option or emergency care when current methods fail
- Track what has been tried and what the results were
- When an image has been shared, reference it naturally in conversation
- Continue the conversation flow as if the image was part of the verbal description

EMERGENCY ASSESSMENT FRAMEWORK:
- TRUE EMERGENCIES (call 9-1-1 immediately): Unconsciousness, severe chest pain, severe bleeding that won't stop, difficulty breathing, severe allergic reactions, severed body parts
- COMMON SYMPTOMS (treat with first aid first): Fainting, dizziness, mild pain, nausea, mild bleeding, minor cuts/burns, cramps, muscle pain
- ESCALATION: Only recommend emergency care if first aid fails or symptoms worsen significantly
- ALWAYS assess severity before deciding on emergency vs first aid treatment

IF THE USER CAN'T FIND AN ITEM:
1) Acknowledge and give location help (e.g., "It should be in the small pack highlighted in orange on the top row.")
2) Offer the closest in-kit alternative and ask to confirm before switching (e.g., "If you don't see it, we can use the large gauze highlighted in blue instead—should we use that?")
3) Do not jump to unrelated items unless confirmed.

BANDAGE PLACEMENT—HANDS (DEFAULT TIPS):
- For small cuts: clean, dry, thin layer of antibiotic ointment if available, center the pad over the cut, smooth adhesive around the skin, avoid wrapping too tight, check movement and circulation. "Let me know when you're ready."
- For finger joints: place the pad over the cut, angle the adhesive so it doesn't bunch at the knuckle; if needed, reinforce with tape from the highlighted space. "Let me know when you're ready."

BLEEDING CONTROL ESCALATION:
- First attempt: Direct pressure with gauze for 5 minutes
- If bleeding continues: Apply QuickClot/hemostatic agent with firm pressure
- If still bleeding: Apply more pressure and hold longer
- If bleeding persists after multiple attempts: ESCALATE TO EMERGENCY CARE
- NEVER repeat failed treatment methods - move to next option or emergency care

SEVERED BODY PARTS PROTOCOL:
- Call 9-1-1 immediately
- Control bleeding at injury site
- Preserve severed part: wrap in clean, damp cloth, place in plastic bag, put bag in ice water bath
- Do NOT put severed part directly on ice
- Keep severed part cool but not frozen

BURN ASSESSMENT PROTOCOL:
- Assess burn severity: size, depth, location
- Minor burns: Cool with water, pain relief, keep clean
- Major burns: Call 9-1-1 only if truly severe (large area, deep tissue, face/hands/genitals)
- Most burns can be treated with first aid first

COMMON SYMPTOMS - TREAT WITH FIRST AID FIRST:
- Fainting/Dizziness: Lie down, elevate legs, improve blood flow to brain
- Mild Shock: Keep warm, lie down, elevate legs if no spine injury
- Nausea: Rest, small sips of water, avoid sudden movements
- Mild Pain: Use pain relievers from kit, apply cold/heat as appropriate
- Cramps/Muscle Pain: Assess hydration, suggest electrolytes, stretching, massage
- Sexual Pain/Discomfort: Discuss openly and suggest appropriate relief methods
- Only escalate to emergency care if symptoms worsen or persist despite first aid

BLEEDING ASSESSMENT PROTOCOL:
- ALWAYS ask about amount of blood and size of injury first
- If heavy bleeding: Control bleeding BEFORE treating other symptoms
- If light bleeding: Treat other symptoms first, then address bleeding
- Severity determines treatment order and emergency escalation

Opening message (ONLY use this for the very first message in a new conversation):
"Hey [name]. I'm here to help. If this is life-threatening, please call 9-1-1 now. Otherwise, I'll guide you step by step. Can you tell me what happened?"

IMPORTANT: Do NOT use this opening message for follow-up responses. Once the conversation has started, focus on the current situation and next steps.

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

USER: It's been 5 minutes and the bleeding hasn't stopped.
SOLSTIS: Since direct pressure didn't work, let's try the QuickClot gauze from the highlighted space. Apply it directly to the cut and press firmly for 3 minutes. Let me know when you're done.

USER: It still hasn't stopped bleeding.
SOLSTIS: The bleeding is not responding to standard treatment. This requires immediate medical attention. Please call 9-1-1 or go to the nearest emergency room. Keep applying pressure while you get help.

USER: I cut my foot and I'm feeling faint.
SOLSTIS: Feeling faint is common with foot injuries. First, lie down and elevate your legs to improve blood flow to your brain. This should help with the dizziness. Once you're stable, we can address the foot injury. Let me know when you're feeling better.

USER: I'm still feeling dizzy after lying down.
SOLSTIS: Stay lying down and keep your legs elevated. If the dizziness persists for more than 10 minutes or you feel worse, then we should consider medical help. For now, focus on staying calm and breathing normally.

USER: I cut my foot and I'm feeling faint.
SOLSTIS: How much blood is there and how big is the cut? This will help me determine the best approach.

USER: There's a lot of blood and it's a deep cut.
SOLSTIS: Since there's heavy bleeding, we need to control that first. Apply direct pressure with gauze from the highlighted space. Once the bleeding slows, then we can address the faintness by having you lie down and elevate your legs.

USER: I have a really bad cramp in my shoulder.
SOLSTIS: How's your hydration? Cramps are often caused by dehydration. If you're not well-hydrated, try mixing the electrolyte powder from the highlighted space with water and drink it. Also, gentle stretching and massage can help.

USER: I got a burn.
SOLSTIS: How bad is the burn? What size is it and where is it located? This will help me determine if we can treat it here or need emergency care.

USER: [Image uploaded for analysis]
SOLSTIS: I can see a small cut on your finger in the image. Let's clean it with the antiseptic wipes from the highlighted space. Do you have access to clean water?

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
        print(f"STT Debug: Received files: {list(request.files.keys())}")
        print(f"STT Debug: Request content type: {request.content_type}")
        
        if 'file' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['file']
        
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        # ElevenLabs API configuration
        ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
        
        if not ELEVENLABS_API_KEY:
            return jsonify({'error': 'ElevenLabs API key not configured'}), 500
        
        # ElevenLabs Speech-to-Text API - Updated endpoint
        url = "https://api.elevenlabs.io/v1/speech-to-text"
        
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        # Read file content once
        file_content = audio_file.read()
        file_size = len(file_content)
        file_type = audio_file.content_type
        file_name = audio_file.filename
        
        print(f"STT Debug: Sending to {url}")
        print(f"STT Debug: File name: {file_name}")
        print(f"STT Debug: File size: {file_size} bytes")
        print(f"STT Debug: File type: {file_type}")
        
        # Check if file size is reasonable
        if file_size < 1000:  # Less than 1KB
            return jsonify({'error': f'Audio file too small: {file_size} bytes. Please record for longer.'}), 400
        
        if file_size > 50000000:  # More than 50MB (increased for longer recordings)
            return jsonify({'error': f'Audio file too large: {file_size} bytes. Please record for shorter duration.'}), 400
        
        # Validate file type
        if not file_type or not file_type.startswith('audio/'):
            return jsonify({'error': f'Invalid file type: {file_type}. Must be an audio file.'}), 400
        
        # Prepare the audio file for upload - ElevenLabs expects 'file' parameter
        files = {
            'file': (file_name, file_content, file_type)
        }
        
        # Required parameters for ElevenLabs STT
        data = {
            'model_id': 'scribe_v1'  # Valid model ID for ElevenLabs STT
        }
        
        print(f"STT Debug: Files being sent: {files}")
        print(f"STT Debug: Data being sent: {data}")
        print(f"STT Debug: Headers being sent: {headers}")
        
        try:
            response = requests.post(url, headers=headers, files=files, data=data, timeout=30)
            
            print(f"STT Debug: Response status: {response.status_code}")
            print(f"STT Debug: Response content: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                transcribed_text = result.get('text', '')
                
                return jsonify({
                    'text': transcribed_text,
                    'status': 'success'
                })
            elif response.status_code == 400:
                # Try to get more specific error information
                error_detail = response.text
                if 'format' in error_detail.lower() or 'unsupported' in error_detail.lower():
                    return jsonify({
                        'error': 'Audio format not supported. Please try recording again.',
                        'details': f'File type: {file_type}, Size: {file_size} bytes'
                    }), 400
                else:
                    return jsonify({
                        'error': f'ElevenLabs STT API error: {response.status_code}',
                        'details': error_detail
                    }), 400
            else:
                error_msg = f'ElevenLabs STT API error: {response.status_code}'
                if response.text:
                    error_msg += f' - {response.text}'
                return jsonify({'error': error_msg}), 500
                
        except requests.exceptions.RequestException as e:
            print(f"STT Request error: {e}")
            return jsonify({'error': f'Request failed: {str(e)}'}), 500
            
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

@app.route('/api/test-stt', methods=['GET'])
def test_stt():
    """Test ElevenLabs STT API connection"""
    try:
        ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
        
        if not ELEVENLABS_API_KEY:
            return jsonify({'error': 'ElevenLabs API key not configured'}), 500
        
        # Test the STT endpoint with a simple GET request
        url = "https://api.elevenlabs.io/v1/speech-to-text"
        headers = {"xi-api-key": ELEVENLABS_API_KEY}
        
        # This should return a 405 Method Not Allowed, which means the endpoint exists
        response = requests.get(url, headers=headers, timeout=10)
        
        return jsonify({
            'status': 'STT endpoint accessible',
            'response_code': response.status_code,
            'api_key_configured': True,
            'endpoint_url': url
        })
        
    except Exception as e:
        return jsonify({
            'error': f'STT test failed: {str(e)}',
            'api_key_configured': bool(os.getenv('ELEVENLABS_API_KEY'))
        }), 500

@app.route('/api/analyze-image', methods=['POST'])
def analyze_image():
    """Analyze uploaded image using OpenAI Vision API"""
    try:
        # Check if image file was uploaded
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        image_file = request.files['image']
        
        if image_file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        # Check file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        file_extension = image_file.filename.rsplit('.', 1)[1].lower() if '.' in image_file.filename else ''
        
        if file_extension not in allowed_extensions:
            return jsonify({'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'}), 400
        
        # Check file size (max 20MB for OpenAI Vision API)
        image_file.seek(0, 2)  # Seek to end
        file_size = image_file.tell()
        image_file.seek(0)  # Reset to beginning
        
        if file_size > 20 * 1024 * 1024:  # 20MB
            return jsonify({'error': 'Image file too large. Maximum size: 20MB'}), 400
        
        # Read image data
        image_data = image_file.read()
        
        # OpenAI API configuration
        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        
        if not OPENAI_API_KEY:
            return jsonify({'error': 'OpenAI API key not configured'}), 500
        
        # Prepare image for OpenAI Vision API
        import base64
        
        # Encode image to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Get user context from request
        user_context = request.form.get('user_context', '')
        kit_type = request.form.get('kit_type', 'standard')
        
        # Use the EXACT same system prompt as the main chat to maintain consistency
        system_prompt = get_system_prompt(kit_type)
        
        # Call OpenAI Vision API
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Please analyze this image and respond in the same conversational style as our chat. User context: {user_context}"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/{file_extension};base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            analysis = response.choices[0].message.content
            
            return jsonify({
                'analysis': analysis,
                'status': 'success'
            })
            
        except Exception as e:
            print(f"OpenAI Vision API error: {e}")
            return jsonify({'error': f'Image analysis failed: {str(e)}'}), 500
            
    except Exception as e:
        print(f"Image analysis error: {e}")
        return jsonify({'error': 'Failed to analyze image'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True) 
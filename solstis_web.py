import os
import tempfile
import speech_recognition as sr
from flask import Flask, render_template_string, request, session, redirect, url_for, jsonify
from openai import OpenAI
from elevenlabs import ElevenLabs, VoiceSettings, stream, play
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

# === Clients ===
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID") or "kdmDKE6EkgrWrrykO9Qt"

# === Kit Configurations ===
KITS = [
    {
        "id": "standard",
        "name": "Standard Kit",
        "description": "Comprehensive first aid kit for general use.",
        "use_case": "Home, workplace, or everyday carry.",
        "contents": [
            {"item": "Band-Aids"},
            {"item": "4″ x 4″ Gauze Pads", "quantity": 5},
            {"item": "2″ Roll Gauze", "description": "Holds gauze in place"},
            {"item": "5″ x 9″ ABD Pad", "description": "For nosebleeds or deeper cuts"},
            {"item": "1\" Cloth Medical Tape"},
            {"item": "Triple Antibiotic Ointment", "description": "Mini tube for infection prevention"},
            {"item": "Blunt Tip Tweezers", "description": "For splinters or debris removal"},
            {"item": "Small Trauma Shears", "description": "Safe for cutting tape or clothing"},
            {"item": "QuickClot Gauze or Hemostatic Wipe", "description": "For guided serious bleeding control"},
            {"item": "4″ x 4″ Burn Gel Dressing", "description": "For finger burns or hot pans"},
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
            {"item": "1\" x 2½ yd Adhesive Tape", "quantity": 2},
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
            {"item": "1\" x 2½ yd Adhesive Tape", "quantity": 2},
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

def get_system_prompt(kit_type):
    # Find the kit by ID
    kit = None
    for k in KITS:
        if k['id'] == kit_type:
            kit = k
            break
    
    if not kit:
        kit = KITS[0]  # Default to first kit
    
    # Format kit items
    kit_items = []
    for item in kit["contents"]:
        item_text = f"- {item['item']}"
        if 'quantity' in item:
            item_text += f" ({item['quantity']})"
        if 'description' in item:
            item_text += f" - {item['description']}"
        kit_items.append(item_text)
    
    kit_items_text = "\n".join(kit_items)
    
    return f"""You are Solstis, a calm, capable, and reassuring AI assistant embedded in a smart med kit system. You provide step-by-step first aid during minor medical emergencies using only:

- Items from the active Solstis kit: {kit['name']}
- Common household items like water, soap, or paper towels

**Available items in your {kit['name']}:**
{kit_items_text}

Your role:
• Be a real-time guide—natural, concise, supportive  
• Always assess for life-threatening danger before offering first aid  
• Guide users using clear, step-based instructions  
• Reference the current kit to select items  
• Say which LED-lit compartment holds the needed item  
• Never suggest treatments outside the kit or household basics  
• Recommend calling 911 when symptoms suggest an emergency  
• Encourage follow-up care when appropriate (e.g., "you may need stitches")

**IMPORTANT:**
- Limit to 1-2 sentences per response
- Ask one clear follow-up question at a time
- Acknowledge user progress with short affirmations ("Great," "Well done")
- Use conversational memory to track progress, responses, and items used
- Refer to items only available in the current kit or items commonly found in a home
- Direct the user to the correct compartment (e.g., "from the box lit up in blue")

Opening message (always use at start of new conversation):
"Hey [name]. I'm here to help. If this is a life-threatening emergency, please call 911 immediately. Otherwise, I'll guide you step-by-step. Can you tell me what happened?"

Examples:

USER: I cut my finger with a kitchen knife. It's bleeding a lot.  
SOLSTIS: Hey there. I'm here to help. First—are you feeling faint, dizzy, or nauseous?

USER: No, just a little shaky.  
SOLSTIS: Good. Do you have access to clean, running water?

USER: Yes.  
SOLSTIS: Great. Remove any rings, then rinse the wound under cool water. Let me know when done.

Only give instructions using supplies from the current kit (or common home items). Do not invent medical tools or procedures not available. You are not a diagnostic or medical authority—you are a calm first responder assistant.

Current active kit: {kit['name']}"""

# === Solstis Assistant Class ===
class SolstisAssistant:
    def __init__(self, user_name="there", kit_type="standard"):
        self.user_name = user_name
        self.kit_type = kit_type
        self.conversation_history = [
            {"role": "system", "content": get_system_prompt(kit_type)}
        ]
        self.has_greeted = False
    
    def get_initial_greeting(self):
        """Get the initial greeting message"""
        # Find the kit by ID
        kit = None
        for k in KITS:
            if k['id'] == self.kit_type:
                kit = k
                break
        
        if not kit:
            kit = KITS[0]  # Default to first kit
            
        return f"Hey {self.user_name}. I'm here to help with your {kit['name']}. If this is a life-threatening emergency, please call 911 immediately. Otherwise, I'll guide you step-by-step. Can you tell me what happened?"
    
    def ask(self, user_input):
        print(f"You: {user_input}")
        
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Get response with full context
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=self.conversation_history
        )
        
        # Add assistant response to history
        assistant_response = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": assistant_response})
        
        return assistant_response
    
    def clear_history(self):
        self.conversation_history = [
            {"role": "system", "content": get_system_prompt(self.kit_type)}
        ]
        self.has_greeted = False

# === Voice Functions ===
def record_audio():
    recognizer = sr.Recognizer()
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
            print("⏱️ No speech detected.")
            return None

def transcribe_audio(audio_path):
    with open(audio_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )
        return transcript.text

def speak_text(text):
    print(f"💬 Solstis: {text}")
    try:
        # Generate audio without playing it
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
        
        # For now, we'll play it on the server side
        # In a production app, you'd want to stream this to the client
        play(audio_stream)
        return True
    except Exception as e:
        print(f"Error generating audio: {e}")
        return False

# === Enhanced HTML Template ===
CHAT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Solstis Assistant</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container { 
            max-width: 900px; 
            width: 100%;
            background: #fff; 
            border-radius: 16px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1); 
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #2a7ae2 0%, #1e3a8a 100%);
            color: white;
            padding: 24px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 14px;
        }
        
        .kit-info {
            background: #f8fafc;
            padding: 16px 24px;
            border-bottom: 1px solid #e5e7eb;
            text-align: center;
        }
        
        .kit-info .kit-name {
            font-weight: 600;
            color: #1e40af;
            font-size: 16px;
        }
        
        .kit-info .kit-description {
            color: #6b7280;
            font-size: 14px;
            margin-top: 4px;
        }
        
        .chat-container {
            padding: 24px;
        }
        
        .chat-box { 
            height: 400px; 
            overflow-y: auto; 
            border: 1px solid #e5e7eb; 
            border-radius: 12px; 
            padding: 16px; 
            background: #f9fafb; 
            margin-bottom: 20px;
            scroll-behavior: smooth;
        }
        
        .msg { 
            margin-bottom: 16px; 
            display: flex;
            align-items: flex-start;
            gap: 12px;
        }
        
        .msg.user { 
            flex-direction: row-reverse;
        }
        
        .msg-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            font-size: 14px;
            line-height: 1.4;
        }
        
        .msg.user .msg-content {
            background: #2a7ae2;
            color: white;
            border-bottom-right-radius: 4px;
        }
        
        .msg.solstis .msg-content {
            background: white;
            color: #374151;
            border: 1px solid #e5e7eb;
            border-bottom-left-radius: 4px;
        }
        
        .avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 12px;
        }
        
        .avatar.user {
            background: #2a7ae2;
            color: white;
        }
        
        .avatar.solstis {
            background: #10b981;
            color: white;
        }
        
        .input-container {
            display: flex;
            gap: 12px;
            align-items: center;
        }
        
        .text-input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e5e7eb;
            border-radius: 24px;
            font-size: 14px;
            transition: border-color 0.2s;
        }
        
        .text-input:focus {
            outline: none;
            border-color: #2a7ae2;
        }
        
        .btn {
            padding: 12px 20px;
            border: none;
            border-radius: 24px;
            cursor: pointer;
            font-weight: 500;
            font-size: 14px;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn-primary {
            background: #2a7ae2;
            color: white;
        }
        
        .btn-primary:hover {
            background: #1e40af;
        }
        
        .btn-secondary {
            background: #6b7280;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #4b5563;
        }
        
        .btn-danger {
            background: #ef4444;
            color: white;
        }
        
        .btn-danger:hover {
            background: #dc2626;
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .voice-btn {
            background: #10b981;
            color: white;
            width: 48px;
            height: 48px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            border: none;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .voice-btn:hover {
            background: #059669;
            transform: scale(1.05);
        }
        
        .voice-btn.recording {
            background: #10b981;
            animation: pulse 1.5s infinite;
        }
        
        .voice-btn.listening {
            background: #f59e0b;
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        
        .setup-form { 
            padding: 40px 24px;
            text-align: center;
        }
        
        .setup-form h2 {
            margin-bottom: 24px;
            color: #374151;
        }
        
        .form-group {
            margin-bottom: 24px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #374151;
        }
        
        .form-group input,
        .form-group select { 
            width: 300px; 
            padding: 12px 16px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 16px;
            background: white;
        }
        
        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: #2a7ae2;
        }
        
        .kit-options {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-top: 16px;
        }
        
        .kit-option {
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            padding: 16px;
            cursor: pointer;
            transition: all 0.2s;
            text-align: left;
        }
        
        .kit-option:hover {
            border-color: #2a7ae2;
            background: #f8fafc;
        }
        
        .kit-option.selected {
            border-color: #2a7ae2;
            background: #eff6ff;
        }
        
        .kit-option input[type="radio"] {
            display: none;
        }
        
        .kit-option h3 {
            font-size: 16px;
            font-weight: 600;
            color: #1e40af;
            margin-bottom: 8px;
        }
        
        .kit-option p {
            font-size: 14px;
            color: #6b7280;
            line-height: 1.4;
        }
        
        .controls {
            display: flex;
            gap: 12px;
            margin-top: 16px;
        }
        
        .status {
            text-align: center;
            padding: 8px;
            margin-bottom: 16px;
            border-radius: 8px;
            font-size: 14px;
            display: none;
        }
        
        .status.info {
            background: #dbeafe;
            color: #1e40af;
        }
        
        .status.error {
            background: #fee2e2;
            color: #dc2626;
        }
        
        .status.success {
            background: #d1fae5;
            color: #059669;
        }
        
        @media (max-width: 768px) {
            .container {
                margin: 10px;
                border-radius: 12px;
            }
            
            .chat-box {
                height: 300px;
            }
            
            .msg-content {
                max-width: 85%;
            }
            
            .form-group input,
            .form-group select {
                width: 100%;
            }
            
            .kit-options {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🩺 Solstis Assistant</h1>
            <p>Your AI-powered medical assistant</p>
        </div>
        
        {% if not session.get('user_name') or not session.get('kit_type') %}
        <div class="setup-form">
            <h2>Welcome to Solstis</h2>
            <form method="post" action="/setup">
                <div class="form-group">
                    <label for="user_name">What's your name?</label>
                    <input type="text" name="user_name" id="user_name" placeholder="Enter your name" required />
                </div>
                
                <div class="form-group">
                    <label>Which Solstis kit are you using?</label>
                    <div class="kit-options">
                        <div class="kit-option" onclick="selectKit('standard')">
                            <input type="radio" name="kit_type" value="standard" id="kit_standard">
                            <h3>🏥 Standard Kit</h3>
                            <p>Comprehensive first aid kit for general use with 18 essential items</p>
                        </div>
                        <div class="kit-option" onclick="selectKit('college')">
                            <input type="radio" name="kit_type" value="college" id="kit_college">
                            <h3>🎓 College Kit</h3>
                            <p>Essential medical supplies for college students with medications</p>
                        </div>
                        <div class="kit-option" onclick="selectKit('oc_standard')">
                            <input type="radio" name="kit_type" value="oc_standard" id="kit_oc_standard">
                            <h3>🏭 OC Standard Kit</h3>
                            <p>Occupational safety kit with Honeywell products for workplace use</p>
                        </div>
                        <div class="kit-option" onclick="selectKit('oc_vehicle')">
                            <input type="radio" name="kit_type" value="oc_vehicle" id="kit_oc_vehicle">
                            <h3>🚗 OC Vehicle Kit</h3>
                            <p>Compact vehicle emergency kit for on-the-go situations</p>
                        </div>
                    </div>
                </div>
                
                <button type="submit" class="btn btn-primary">Start Chat</button>
            </form>
        </div>
        {% else %}
        <div class="kit-info">
            <div class="kit-name">{{ session.get('kit_name', 'Standard Kit') }}</div>
            <div class="kit-description">{{ session.get('kit_description', 'Comprehensive first aid kit') }}</div>
        </div>
        
        <div class="chat-container">
            <div class="status" id="status"></div>
            
            <div class="chat-box" id="chat-box">
                {% for msg in history %}
                    <div class="msg {{ msg['role'] }}">
                        <div class="avatar {{ msg['role'] }}">
                            {% if msg['role'] == 'user' %}U{% else %}S{% endif %}
                        </div>
                        <div class="msg-content">{{ msg['content'] }}</div>
                    </div>
                {% endfor %}
            </div>
            
            <form method="post" action="/chat" id="chat-form">
                <div class="input-container">
                    <input type="text" name="user_input" id="user_input" class="text-input" 
                           autocomplete="off" placeholder="Type your message or use voice..." required />
                    <button type="button" class="voice-btn" id="voice-btn" title="Click to pause/resume listening">
                        🔄
                    </button>
                    <button type="submit" class="btn btn-primary">Send</button>
                </div>
            </form>
            
            <div class="controls">
                <button type="button" class="btn btn-secondary" onclick="speakLastMessage()">
                    🔊 Speak Last Message
                </button>
                <form method="post" action="/clear" style="display: inline;">
                    <button type="submit" class="btn btn-danger">Clear Conversation</button>
                </form>
            </div>
        </div>
        {% endif %}
    </div>
    
    <script>
        // Kit selection
        function selectKit(kitType) {
            // Remove selected class from all options
            document.querySelectorAll('.kit-option').forEach(option => {
                option.classList.remove('selected');
            });
            
            // Add selected class to clicked option
            document.querySelector(`#kit_${kitType}`).closest('.kit-option').classList.add('selected');
            
            // Check the radio button
            document.querySelector(`#kit_${kitType}`).checked = true;
        }
        
        // Auto-scroll chat box
        function scrollToBottom() {
            const chatBox = document.getElementById('chat-box');
            if (chatBox) {
                chatBox.scrollTop = chatBox.scrollHeight;
            }
        }
        
        scrollToBottom();
        
        // Start automatic voice conversation when page loads
        setTimeout(() => {
            if (voiceBtn) {
                voiceBtn.classList.add('listening');
                showStatus('Starting voice conversation...', 'info');
                setTimeout(() => startRecordingCycle(), 1000);
            }
        }, 2000);
        
        // Automatic voice conversation functionality
        let isRecording = false;
        let isListening = true;
        const voiceBtn = document.getElementById('voice-btn');
        const status = document.getElementById('status');
        
        if (voiceBtn) {
            voiceBtn.addEventListener('click', toggleListening);
        }
        
        function showStatus(message, type = 'info') {
            status.textContent = message;
            status.className = `status ${type}`;
            status.style.display = 'block';
            setTimeout(() => {
                status.style.display = 'none';
            }, 3000);
        }
        
        function toggleListening() {
            if (isListening) {
                stopListening();
            } else {
                startListening();
            }
        }
        
        function startListening() {
            isListening = true;
            voiceBtn.classList.add('listening');
            voiceBtn.textContent = '🔄';
            showStatus('Listening...', 'info');
            
            // Start the first recording cycle
            startRecordingCycle();
        }
        
        function stopListening() {
            isListening = false;
            isRecording = false;
            voiceBtn.classList.remove('listening');
            voiceBtn.textContent = '⏸️';
            showStatus('Listening paused', 'info');
        }
        
        function startRecordingCycle() {
            if (!isListening) return;
            
            isRecording = true;
            showStatus('Listening... Speak now!', 'info');
            
            // Record and process audio
            fetch('/stop_voice_recording', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    console.log('Voice recording response:', data);
                    if (data.success && data.transcript) {
                        const input = document.getElementById('user_input');
                        input.value = data.transcript;
                        showStatus('Heard: "' + data.transcript + '"', 'success');
                        
                        // Auto-submit and wait for response
                        submitAndWaitForResponse(data.transcript);
                    } else {
                        showStatus('No speech detected, listening again...', 'info');
                        // Continue listening
                        setTimeout(() => startRecordingCycle(), 1000);
                    }
                })
                .catch(error => {
                    console.error('Voice recording error:', error);
                    showStatus('Error, retrying...', 'error');
                    setTimeout(() => startRecordingCycle(), 2000);
                });
        }
        
        function submitAndWaitForResponse(userText) {
            // Create form data
            const formData = new FormData();
            formData.append('user_input', userText);
            
            // Submit the form with AJAX header
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                console.log('Chat response:', data);
                if (data.success) {
                    showStatus('AI: "' + data.response.substring(0, 50) + '..."', 'success');
                    
                    // Add the conversation to the chat box
                    addMessageToChat('user', userText);
                    addMessageToChat('solstis', data.response);
                    
                    // Wait for audio to finish, then continue listening
                    setTimeout(() => {
                        if (isListening) {
                            showStatus('Listening for your response...', 'info');
                            setTimeout(() => startRecordingCycle(), 2000);
                        }
                    }, 3000);
                } else {
                    throw new Error(data.error || 'Unknown error');
                }
            })
            .catch(error => {
                console.error('Submit error:', error);
                showStatus('Error submitting, retrying...', 'error');
                setTimeout(() => startRecordingCycle(), 2000);
            });
        }
        
        function addMessageToChat(role, content) {
            const chatBox = document.getElementById('chat-box');
            const messageDiv = document.createElement('div');
            messageDiv.className = `msg ${role}`;
            
            const avatar = document.createElement('div');
            avatar.className = `avatar ${role}`;
            avatar.textContent = role === 'user' ? 'U' : 'S';
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'msg-content';
            contentDiv.textContent = content;
            
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(contentDiv);
            chatBox.appendChild(messageDiv);
            
            // Scroll to bottom
            chatBox.scrollTop = chatBox.scrollHeight;
        }
        
        function speakLastMessage() {
            const messages = document.querySelectorAll('.msg.solstis .msg-content');
            if (messages.length > 0) {
                const lastMessage = messages[messages.length - 1].textContent;
                console.log('Speaking message:', lastMessage);
                
                fetch('/speak_text', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: lastMessage })
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Speak response:', data);
                    if (data.success) {
                        showStatus('Playing audio...', 'success');
                    } else {
                        showStatus('Failed to play audio: ' + (data.error || 'Unknown error'), 'error');
                    }
                })
                .catch(error => {
                    console.error('Speak error:', error);
                    showStatus('Error: ' + error.message, 'error');
                });
            } else {
                showStatus('No message to speak', 'error');
            }
        }
        
        // Handle form submission
        document.getElementById('chat-form')?.addEventListener('submit', function(e) {
            const input = document.getElementById('user_input');
            if (!input.value.trim()) {
                e.preventDefault();
                return;
            }
            
            // Disable submit button to prevent double submission
            const submitBtn = this.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Sending...';
        });
    </script>
</body>
</html>
'''

def get_assistant():
    user_name = session.get('user_name', 'there')
    kit_type = session.get('kit_type', 'standard')
    
    if 'history' not in session:
        session['history'] = [
            {"role": "system", "content": get_system_prompt(kit_type)}
        ]
        # Add initial greeting
        assistant = SolstisAssistant(user_name, kit_type)
        initial_greeting = assistant.get_initial_greeting()
        session['history'].append({"role": "assistant", "content": initial_greeting})
        
        # Speak the initial greeting if this is a new session
        try:
            speak_text(initial_greeting)
        except Exception as e:
            print(f"Error speaking initial greeting: {e}")
    
    assistant = SolstisAssistant(user_name, kit_type)
    assistant.conversation_history = session.get('history', [
        {"role": "system", "content": get_system_prompt(kit_type)}
    ])
    return assistant

@app.route('/', methods=['GET'])
def index():
    history = session.get('history', [])
    # Only show user/assistant messages
    filtered = [m for m in history if m['role'] in ('user', 'assistant')]
    return render_template_string(CHAT_TEMPLATE, history=filtered)

@app.route('/setup', methods=['POST'])
def setup():
    user_name = request.form.get('user_name', '').strip()
    kit_type = request.form.get('kit_type', 'standard')
    
    if not user_name:
        user_name = 'there'
    
    # Find the kit by ID
    kit = None
    for k in KITS:
        if k['id'] == kit_type:
            kit = k
            break
    
    if not kit:
        kit = KITS[0]  # Default to first kit
        kit_type = kit['id']
    
    session['user_name'] = user_name
    session['kit_type'] = kit_type
    session['kit_name'] = kit['name']
    session['kit_description'] = kit['description']
    
    # Initialize conversation with greeting
    assistant = SolstisAssistant(user_name, kit_type)
    initial_greeting = assistant.get_initial_greeting()
    session['history'] = [
        {"role": "system", "content": get_system_prompt(kit_type)},
        {"role": "assistant", "content": initial_greeting}
    ]
    
    # Speak the initial greeting
    try:
        speak_text(initial_greeting)
    except Exception as e:
        print(f"Error speaking initial greeting: {e}")
    
    return redirect(url_for('index'))

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form.get('user_input', '').strip()
    if not user_input:
        return redirect(url_for('index'))
    
    assistant = get_assistant()
    solstis_response = assistant.ask(user_input)
    
    # Save updated history to session
    session['history'] = assistant.conversation_history
    
    # Check if this is an AJAX request (auto mode)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Auto-speak the response
        try:
            speak_text(solstis_response)
            return jsonify({
                'success': True, 
                'response': solstis_response,
                'message': 'Response spoken automatically'
            })
        except Exception as e:
            return jsonify({
                'success': False, 
                'response': solstis_response,
                'error': str(e)
            })
    
    return redirect(url_for('index'))

@app.route('/clear', methods=['POST'])
def clear():
    user_name = session.get('user_name', 'there')
    kit_type = session.get('kit_type', 'standard')
    assistant = SolstisAssistant(user_name, kit_type)
    initial_greeting = assistant.get_initial_greeting()
    session['history'] = [
        {"role": "system", "content": get_system_prompt(kit_type)},
        {"role": "assistant", "content": initial_greeting}
    ]
    
    # Speak the initial greeting after clearing
    try:
        speak_text(initial_greeting)
    except Exception as e:
        print(f"Error speaking initial greeting after clear: {e}")
    
    return redirect(url_for('index'))

@app.route('/start_voice_recording', methods=['POST'])
def start_voice_recording():
    try:
        # For now, we'll use a simpler approach - just return success
        # The actual recording will happen when stop_voice_recording is called
        return jsonify({'success': True, 'message': 'Voice recording started'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/stop_voice_recording', methods=['POST'])
def stop_voice_recording():
    try:
        print("🎤 Starting voice recording...")
        audio_file = record_audio()
        if not audio_file:
            print("❌ No audio recorded")
            return jsonify({'success': False, 'error': 'No audio recorded'})
        
        print("📝 Transcribing audio...")
        transcript = transcribe_audio(audio_file)
        os.remove(audio_file)
        
        if not transcript.strip():
            print("❌ No speech detected")
            return jsonify({'success': False, 'error': 'No speech detected'})
        
        print(f"✅ Transcript: {transcript}")
        return jsonify({'success': True, 'transcript': transcript})
    except Exception as e:
        print(f"❌ Error in voice recording: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/speak_text', methods=['POST'])
def speak_text_endpoint():
    try:
        data = request.get_json()
        text = data.get('text', '')
        if not text:
            return jsonify({'success': False, 'error': 'No text provided'})
        
        print(f"🔊 Speaking text: {text[:50]}...")
        success = speak_text(text)
        print(f"✅ Text-to-speech {'successful' if success else 'failed'}")
        return jsonify({'success': success})
    except Exception as e:
        print(f"❌ Error in text-to-speech: {e}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == "__main__":
    # Development vs Production settings
    debug_mode = os.getenv("FLASK_ENV") == "development"
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", 5001))
    
    print(f"Starting Solstis Web Server...")
    print(f"Environment: {'Development' if debug_mode else 'Production'}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug: {debug_mode}")
    print(f"Voice enabled: {bool(os.getenv('ELEVENLABS_API_KEY'))}")
    print(f"Available kits: {', '.join([kit['id'] for kit in KITS])}")
    
    app.run(
        host=host,
        port=port,
        debug=debug_mode
    ) 
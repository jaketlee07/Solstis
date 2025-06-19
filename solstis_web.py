import os
from flask import Flask, render_template_string, request, session, redirect, url_for
from solstis_text import SolstisAssistant, SYSTEM_PROMPT

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

CHAT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Solstis Assistant</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f7f7fa; margin: 0; padding: 0; }
        .container { max-width: 600px; margin: 40px auto; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px #0001; padding: 24px; }
        .chat-box { height: 350px; overflow-y: auto; border: 1px solid #eee; border-radius: 6px; padding: 12px; background: #fafbfc; margin-bottom: 16px; }
        .msg { margin-bottom: 12px; }
        .msg.user { text-align: right; color: #2a7ae2; }
        .msg.solstis { text-align: left; color: #222; }
        form { display: flex; gap: 8px; }
        input[type=text] { flex: 1; padding: 10px; border-radius: 4px; border: 1px solid #ccc; }
        button { padding: 10px 18px; border: none; background: #2a7ae2; color: #fff; border-radius: 4px; cursor: pointer; }
        button:disabled { background: #aaa; }
        .name-form { text-align: center; margin-bottom: 20px; }
        .name-form input { width: 200px; margin-right: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Solstis Assistant</h2>
        {% if not session.get('user_name') %}
        <div class="name-form">
            <form method="post" action="/set_name">
                <input type="text" name="user_name" placeholder="What's your name?" required />
                <button type="submit">Start Chat</button>
            </form>
        </div>
        {% else %}
        <div class="chat-box" id="chat-box">
            {% for msg in history %}
                <div class="msg {{ msg['role'] }}">{{ msg['content'] }}</div>
            {% endfor %}
        </div>
        <form method="post" action="/chat">
            <input type="text" name="user_input" id="user_input" autocomplete="off" autofocus placeholder="Type your message..." required />
            <button type="submit">Send</button>
        </form>
        <form method="post" action="/clear" style="margin-top:10px;">
            <button type="submit" style="background:#e22;">Clear Conversation</button>
        </form>
        {% endif %}
    </div>
    <script>
        // Auto-scroll chat box
        var chatBox = document.getElementById('chat-box');
        if (chatBox) {
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    </script>
</body>
</html>
'''

def get_assistant():
    user_name = session.get('user_name', 'there')
    if 'history' not in session:
        session['history'] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        # Add initial greeting
        assistant = SolstisAssistant(user_name)
        initial_greeting = assistant.get_initial_greeting()
        session['history'].append({"role": "assistant", "content": initial_greeting})
    
    assistant = SolstisAssistant(user_name)
    assistant.conversation_history = session.get('history', [
        {"role": "system", "content": SYSTEM_PROMPT}
    ])
    return assistant

@app.route('/', methods=['GET'])
def index():
    history = session.get('history', [])
    # Only show user/assistant messages
    filtered = [m for m in history if m['role'] in ('user', 'assistant')]
    return render_template_string(CHAT_TEMPLATE, history=filtered)

@app.route('/set_name', methods=['POST'])
def set_name():
    user_name = request.form.get('user_name', '').strip()
    if not user_name:
        user_name = 'there'
    session['user_name'] = user_name
    
    # Initialize conversation with greeting
    assistant = SolstisAssistant(user_name)
    initial_greeting = assistant.get_initial_greeting()
    session['history'] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": initial_greeting}
    ]
    
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
    return redirect(url_for('index'))

@app.route('/clear', methods=['POST'])
def clear():
    user_name = session.get('user_name', 'there')
    assistant = SolstisAssistant(user_name)
    initial_greeting = assistant.get_initial_greeting()
    session['history'] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": initial_greeting}
    ]
    return redirect(url_for('index'))

if __name__ == "__main__":
    # Development vs Production settings
    debug_mode = os.getenv("FLASK_ENV") == "development"
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", 5000))
    
    print(f"Starting Solstis Web Server...")
    print(f"Environment: {'Development' if debug_mode else 'Production'}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug: {debug_mode}")
    
    app.run(
        host=host,
        port=port,
        debug=debug_mode
    ) 
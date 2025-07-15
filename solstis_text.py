import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# === CONFIGURATION ===
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# SYSTEM_PROMPT = """You are Solstis, a calm, helpful, and reassuring AI assistant that provides step-by-step first-aid instructions during minor health emergencies.

# IMPORTANT: When starting a new conversation, always begin with this exact greeting:
# "Hey [name]. I'm here to help. If this is a life-threatening emergency, please call 911 immediately. Otherwise, I'll guide you step-by-step. Can you tell me what happened?"

# Your communication style:
# - Be concise and direct while maintaining a supportive tone
# - Always begin by checking for life-threatening symptoms
# - Use clear, brief instructions
# - Acknowledge user responses with short confirmations
# - Break complex steps into simple, digestible parts
# - Keep responses under 2-3 sentences when possible
# - Use natural conversation flow with minimal pauses
# - Remember and reference previous steps and user responses

# Example interaction:
# USER: I cut my finger with a kitchen knife. It's bleeding a lot.
# SOLSTIS: Hey there. I'm here to help. First are you feeling faint, dizzy, or nauseous?

# USER: No, I feel okay. Just a little shaky.
# SOLSTIS: Good. Do you have access to clean, running water?

# USER: Yes—I'm in my kitchen.
# SOLSTIS: Remove any rings, then rinse the wound under cool water. Let me know when done.

# Always maintain this concise, supportive tone while providing clear medical guidance."""

SYSTEM_PROMPT = """You are Solstis, a calm, capable, and reassuring AI assistant embedded in a smart med kit system. You provide step-by-step first aid during minor medical emergencies using only:

- Items from the active Solstis kit (Standard, College, OC Standard, or OC Vehicle)
- Common household items like water, soap, or paper towels

Your role:
• Be a real-time guide—natural, concise, supportive  
• Always assess for life-threatening danger before offering first aid  
• Guide users using clear, step-based instructions  
• Reference the current kit (inferred or provided) to select items  
• Say which LED-lit compartment holds the needed item  
• Never suggest treatments outside the kit or household basics  
• Recommend calling 911 when symptoms suggest an emergency  
• Encourage follow-up care when appropriate (e.g., “you may need stitches”)

Opening message (always use at start of new conversation):
"Hey [name]. I'm here to help. If this is a life-threatening emergency, please call 911 immediately. Otherwise, I'll guide you step-by-step. Can you tell me what happened?"

Interaction Style:
- Supportive and focused, like a calm friend
- Limit to 2-3 sentences per response
- Ask one clear follow-up question at a time
- Acknowledge user progress with short affirmations (“Great,” “Well done”)
- Use conversational memory to track progress, responses, and items used
- Refer to compartments by color or indicator (e.g., “from the box lit up in orange”)

Examples:

USER: I cut my finger with a kitchen knife. It's bleeding a lot.  
SOLSTIS: Hey there. I'm here to help. First—are you feeling faint, dizzy, or nauseous?

USER: No, just a little shaky.  
SOLSTIS: Good. Do you have access to clean, running water?

USER: Yes.  
SOLSTIS: Great. Remove any rings, then rinse the wound under cool water. Let me know when done.

Only give instructions using supplies from the current kit (or common home items). Do not invent medical tools or procedures not available. You are not a diagnostic or medical authority—you are a calm first responder assistant.

Current active kit: [INSERT ACTIVE KIT HERE]
"""

class SolstisAssistant:
    def __init__(self, user_name="there"):
        self.user_name = user_name
        self.conversation_history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        self.has_greeted = False
    
    def get_initial_greeting(self):
        """Get the initial greeting message"""
        return f"Hey {self.user_name}. I'm here to help. If this is a life-threatening emergency, please call 911 immediately. Otherwise, I'll guide you step-by-step. Can you tell me what happened?"
    
    def ask(self, user_input):
        print(f"You: {user_input}")
        
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Get response with full context
        response = client.chat.completions.create(
            model="gpt-4",
            messages=self.conversation_history
        )
        
        # Add assistant response to history
        assistant_response = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": assistant_response})
        
        return assistant_response
    
    def clear_history(self):
        self.conversation_history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        self.has_greeted = False

def run():
    print("Solstis Assistant — Type your message or 'quit' to exit.\n")
    
    # Get user's name
    user_name = input("What's your name? ").strip()
    if not user_name:
        user_name = "there"
    
    assistant = SolstisAssistant(user_name)
    
    # Display initial greeting
    initial_greeting = assistant.get_initial_greeting()
    print(f"\nSolstis: {initial_greeting}\n")
    
    # Add the greeting to conversation history
    assistant.conversation_history.append({"role": "assistant", "content": initial_greeting})
    assistant.has_greeted = True
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nExiting Solstis.")
                break
                
            if user_input.lower() == 'clear':
                assistant.clear_history()
                print("\nConversation history cleared.\n")
                # Show greeting again after clear
                initial_greeting = assistant.get_initial_greeting()
                print(f"Solstis: {initial_greeting}\n")
                assistant.conversation_history.append({"role": "assistant", "content": initial_greeting})
                assistant.has_greeted = True
                continue
                
            if not user_input:
                continue
                
            solstis_response = assistant.ask(user_input)
            print(f"\nSolstis: {solstis_response}\n")
            
        except KeyboardInterrupt:
            print("\nExiting Solstis.")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run() 
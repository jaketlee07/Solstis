import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# === CONFIGURATION ===
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
SOLSTIS: Hey there. I'm here to help. First are you feeling faint, dizzy, or nauseous?

USER: No, I feel okay. Just a little shaky.
SOLSTIS: Good. Do you have access to clean, running water?

USER: Yes—I'm in my kitchen.
SOLSTIS: Remove any rings, then rinse the wound under cool water. Let me know when done.

Always maintain this concise, supportive tone while providing clear medical guidance."""

class SolstisAssistant:
    def __init__(self):
        self.conversation_history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
    
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

def run():
    print("Solstis Assistant — Type your message or 'quit' to exit.\n")
    #print("Example: 'I cut my finger with a kitchen knife. It's bleeding a lot.'\n")
    
    assistant = SolstisAssistant()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nExiting Solstis.")
                break
                
            if user_input.lower() == 'clear':
                assistant.clear_history()
                print("\nConversation history cleared.\n")
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
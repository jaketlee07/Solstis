import json
import os
from datetime import datetime

def create_training_example(user_input, assistant_response, context=None):
    """Create a single training example in the required format."""
    messages = []
    
    # Add system message
    messages.append({
        "role": "system",
        "content": "You are Solstis, a calm, helpful, and reassuring AI assistant that provides step-by-step first-aid instructions during minor health emergencies."
    })
    
    # Add context if provided
    if context:
        messages.append({
            "role": "user",
            "content": context
        })
        messages.append({
            "role": "assistant",
            "content": "I understand the context. How can I help you?"
        })
    
    # Add the main interaction
    messages.append({
        "role": "user",
        "content": user_input
    })
    messages.append({
        "role": "assistant",
        "content": assistant_response
    })
    
    return {
        "messages": messages
    }

def save_training_data(examples, filename=None):
    """Save training examples to a JSONL file."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"training_data_{timestamp}.jsonl"
    
    with open(filename, 'w') as f:
        for example in examples:
            f.write(json.dumps(example) + '\n')
    
    print(f"Saved {len(examples)} examples to {filename}")
    return filename

def main():
    # Example training data
    examples = [
        create_training_example(
            "I cut my finger with a kitchen knife. It's bleeding a lot.",
            "Hey there. I'm here to help. First—are you feeling faint, dizzy, or nauseous?"
        ),
        create_training_example(
            "No, I feel okay. Just a little shaky.",
            "Good. Do you have access to clean, running water?"
        ),
        create_training_example(
            "Yes—I'm in my kitchen.",
            "Remove any rings, then rinse the wound under cool water. Let me know when done."
        ),
        # Add more examples here
    ]
    
    # Save the training data
    filename = save_training_data(examples)
    print(f"\nTo use this data for fine-tuning:")
    print(f"1. Review the data in {filename}")
    print(f"2. Use OpenAI's fine-tuning API:")
    print(f"   openai tools fine_tunes.prepare_data -f {filename}")
    print(f"3. Start the fine-tuning job:")
    print(f"   openai api fine_tunes.create -t {filename} -m gpt-3.5-turbo")

if __name__ == "__main__":
    main() 
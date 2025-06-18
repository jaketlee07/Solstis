import json
import os
from typing import Dict, List, Optional

class FirstAidKnowledgeBase:
    def __init__(self, data_file: str = "first_aid_data.json"):
        self.data_file = data_file
        self.knowledge_base = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load knowledge base from JSON file."""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {
            "emergencies": {},
            "procedures": {},
            "symptoms": {},
            "equipment": {}
        }
    
    def _save_data(self):
        """Save knowledge base to JSON file."""
        with open(self.data_file, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)
    
    def add_emergency(self, name: str, steps: List[str], symptoms: List[str], equipment: List[str]):
        """Add a new emergency procedure to the knowledge base."""
        self.knowledge_base["emergencies"][name] = {
            "steps": steps,
            "symptoms": symptoms,
            "equipment": equipment
        }
        self._save_data()
    
    def add_procedure(self, name: str, steps: List[str], equipment: List[str]):
        """Add a new general procedure to the knowledge base."""
        self.knowledge_base["procedures"][name] = {
            "steps": steps,
            "equipment": equipment
        }
        self._save_data()
    
    def get_emergency_info(self, name: str) -> Optional[Dict]:
        """Get information about a specific emergency."""
        return self.knowledge_base["emergencies"].get(name)
    
    def get_procedure_info(self, name: str) -> Optional[Dict]:
        """Get information about a specific procedure."""
        return self.knowledge_base["procedures"].get(name)
    
    def search_knowledge_base(self, query: str) -> List[Dict]:
        """Search the knowledge base for relevant information."""
        results = []
        
        # Search in emergencies
        for name, data in self.knowledge_base["emergencies"].items():
            if query.lower() in name.lower() or any(query.lower() in step.lower() for step in data["steps"]):
                results.append({
                    "type": "emergency",
                    "name": name,
                    "data": data
                })
        
        # Search in procedures
        for name, data in self.knowledge_base["procedures"].items():
            if query.lower() in name.lower() or any(query.lower() in step.lower() for step in data["steps"]):
                results.append({
                    "type": "procedure",
                    "name": name,
                    "data": data
                })
        
        return results

def main():
    # Example usage
    kb = FirstAidKnowledgeBase()
    
    # Add a new emergency procedure
    kb.add_emergency(
        name="severe bleeding",
        steps=[
            "Call emergency services immediately",
            "Apply direct pressure to the wound",
            "Elevate the injured area if possible",
            "Apply a tourniquet only as a last resort"
        ],
        symptoms=[
            "Heavy bleeding",
            "Blood soaking through bandages",
            "Loss of consciousness",
            "Rapid breathing"
        ],
        equipment=[
            "Clean cloth or bandages",
            "Tourniquet",
            "Gloves",
            "First aid kit"
        ]
    )
    
    # Add a general procedure
    kb.add_procedure(
        name="wound cleaning",
        steps=[
            "Wash hands thoroughly",
            "Clean the wound with soap and water",
            "Apply antibiotic ointment",
            "Cover with sterile bandage"
        ],
        equipment=[
            "Soap",
            "Clean water",
            "Antibiotic ointment",
            "Sterile bandage"
        ]
    )
    
    # Search the knowledge base
    results = kb.search_knowledge_base("bleeding")
    print("\nSearch Results:")
    for result in results:
        print(f"\n{result['type'].title()}: {result['name']}")
        print("Steps:", result['data']['steps'])

if __name__ == "__main__":
    main() 
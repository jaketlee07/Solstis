import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const KitContext = createContext();

export const useKit = () => {
  const context = useContext(KitContext);
  if (!context) {
    throw new Error('useKit must be used within a KitProvider');
  }
  return context;
};

export const KitProvider = ({ children }) => {
  const [kits, setKits] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchKits();
  }, []);

  const fetchKits = async () => {
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5001';
      const response = await axios.get(`${apiUrl}/api/kits`);
      setKits(response.data);
    } catch (error) {
      console.error('Error fetching kits:', error);
      // Fallback to default kits if API fails
      setKits([
        {
          id: "standard",
          name: "Standard Kit",
          description: "Comprehensive first aid kit for general use.",
          use_case: "Home, workplace, or everyday carry.",
          contents: [
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
          id: "college",
          name: "College Kit",
          description: "Essential medical supplies for college students.",
          use_case: "Dorm rooms, campus travel, everyday minor illness care.",
          contents: [
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
          id: "oc_standard",
          name: "OC Standard Kit",
          description: "Occupational safety kit with Honeywell products.",
          use_case: "Worksites, industrial environments, OSHA compliance.",
          contents: [
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
          id: "oc_vehicle",
          name: "OC Vehicle Kit",
          description: "Compact vehicle emergency kit.",
          use_case: "Glovebox or trunk storage for roadside injuries.",
          contents: [
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
      ]);
    } finally {
      setLoading(false);
    }
  };

  const value = {
    kits,
    loading,
    fetchKits
  };

  return (
    <KitContext.Provider value={value}>
      {children}
    </KitContext.Provider>
  );
}; 
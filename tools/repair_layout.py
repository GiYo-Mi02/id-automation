import json
import os

LAYOUT_PATH = r"C:\School_IDs\layout.json"

new_layout = {
    "front": {
        "photo": { 
            "x": 145, "y": 200, "w": 300, "h": 300 
        },
        "name": { 
            # Changed color to Black so it's visible!
            # Moved Y to 520 to appear below the photo
            "x": 295, "y": 520, "size": 30, "color": "#000000", "bold": True, "align": "center" 
        },
        "lrn": { 
            "x": 360, "y": 595, "size": 18, "color": "#000000", "align": "left" 
        },
        "grade_level": { 
            # We hide this off-screen since template already has "Grade 4/5/6" printed
            "x": 9000, "y": 9000, "size": 1, "color": "#000000", "align": "center" 
        },
        "section": { 
            # Moved to 495 (Center of Right Column)
            "x": 495, "y": 665, "size": 16, "color": "#000000", "align": "center" 
        }
    },
    "back": {
        "guardian_name": { "x": 100, "y": 240, "size": 18, "color": "#000000", "align": "left" },
        "address": { "x": 100, "y": 380, "size": 16, "color": "#000000", "align": "left" },
        "guardian_contact": { "x": 100, "y": 530, "size": 20, "color": "#000000", "align": "left" }
    }
}

def repair():
    try:
        with open(LAYOUT_PATH, 'w') as f:
            json.dump(new_layout, f, indent=4)
        print("✅ Layout reset: Section aligned to Column 3 & Name color fixed.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    repair()
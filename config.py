# config.py

import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types as genai_types
from data_models import TravelItinerary
from tools import AVAILABLE_TOOL_FUNCTIONS 
from typing import Optional

load_dotenv() 

GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL", "") 
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Gemini Client Setup ---
client = None
GEMINI_MODEL = None

if GEMINI_MODEL_NAME and GEMINI_API_KEY and GEMINI_API_KEY != "x":
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        GEMINI_MODEL = GEMINI_MODEL_NAME 
        print("Gemini client initialized correctly.")
    except Exception as e:
        print(f"Warning: Could not initialize the Gemini client. Error: {e}")
        client = None
        GEMINI_MODEL = None 
else:
    if GEMINI_API_KEY == "x":
        print("Warning: GEMINI_API_KEY has the value 'x'. The Gemini agent will be inactive.")
    elif not GEMINI_MODEL_NAME:
        print("Warning: GEMINI_MODEL is not configured.")
    elif not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY is not configured. The Gemini agent will be inactive.")

ITINERARY_SCHEMA = TravelItinerary.model_json_schema()

function_declarations = [
    {
        "name": func.__name__,
        "description": func.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "place_name": {"type": "string", "description": "The name of the location."},
                "from_location": {"type": "string", "description": "The starting location for the travel time calculation."},
                "to_location": {"type": "string", "description": "The destination location for the travel time calculation."},
            },
            "required": ["place_name"] if func.__name__ == "get_location_details" else ["from_location", "to_location"]
        }
    }
    for func in AVAILABLE_TOOL_FUNCTIONS
]

FALLBACK_FILE = "fallback_itinerary.json"

def load_fallback_itinerary() -> Optional[TravelItinerary]:
    """Loads a predefined itinerary from a local JSON file."""
    if os.path.exists(FALLBACK_FILE):
        try:
            with open(FALLBACK_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            from data_models import TravelItinerary
            itinerary = TravelItinerary.model_validate(data)
            return itinerary
        except Exception as e:
            return None
    return None


tool_defs = genai_types.Tool(function_declarations=function_declarations)
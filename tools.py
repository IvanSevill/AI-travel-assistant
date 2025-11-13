# tools.py

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def get_location_details(place_name: str) -> str:
    """
    Looks up key information about a place, including place type, rating, and 
    whether it is currently open, using the Google Places API.
    """
    if not MAPS_API_KEY:
        return f"Error: GOOGLE_MAPS_API_KEY is missing. Cannot fetch real details for {place_name}."

    find_place_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {"input": place_name, "inputtype": "textquery", "fields": "place_id", "key": MAPS_API_KEY}
    
    try:
        response = requests.get(find_place_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data['status'] == 'OK' and data['candidates']:
            place_id = data['candidates'][0]['place_id']
        else:
            return f"Details for {place_name}: Place not found. Using estimated duration of 1.5 hours and cost of Free."
            
        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
        details_params = {"place_id": place_id, "fields": "name,type,opening_hours,formatted_address,price_level,rating,user_ratings_total", "key": MAPS_API_KEY, "language": "en"}
        
        details_response = requests.get(details_url, details_params)
        details_response.raise_for_status()
        details_data = details_response.json()
        
        if details_data['status'] == 'OK' and details_data['result']:
            result = details_data['result']
            name = result.get('name', place_name)
            address = result.get('formatted_address', 'Unknown Address')
            place_type = ', '.join(result.get('types', []))
            opening_status = "Unknown Hours"
            if 'opening_hours' in result and 'open_now' in result['opening_hours']:
                status = "Open Now" if result['opening_hours']['open_now'] else "Closed Now"
                opening_status = f"Status: {status}. Full Hours Check Recommended."
            rating = result.get('rating', 'N/A')
            
            return (
                f"Location: {name} ({address}). Type: {place_type}. "
                f"Rating: {rating}/5. {opening_status}. "
                f"LLM Planner Note: Estimate duration based on attraction type (e.g., 2 hours for a major museum)."
            )
        else:
            return f"Details for {place_name}: Detailed info unavailable. Using estimated duration of 1.5 hours and cost of Free."

    except requests.exceptions.RequestException as e:
        return f"Details for {place_name}: Network/API Request failed: {e}"


def calculate_travel_time(from_location: str, to_location: str) -> str:
    """
    Calculates the estimated travel time and suggests the best transportation method 
    between two locations using Google Maps Directions API.
    """
    if not MAPS_API_KEY:
        return f"Error: GOOGLE_MAPS_API_KEY is missing. Cannot calculate real travel time between {from_location} and {to_location}."
        
    url = "https://maps.googleapis.com/maps/api/directions/json"
    modes_to_try = ["walking", "transit", "driving"]
    
    for mode in modes_to_try:
        params = {"origin": from_location, "destination": to_location, "key": MAPS_API_KEY, "mode": mode, "language": "en"}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'OK' and data['routes']:
                route = data['routes'][0]['legs'][0]
                duration_text = route['duration']['text']
                distance_text = route['distance']['text']
                transport_type = mode.capitalize()
                note = ""
                if mode == "walking" and route['duration']['value'] > 1200: 
                    transport_type = "Transit/Bus" 
                    note = "Consider public transport or taxi since walking is long."
                elif mode == "transit":
                    transport_type = route['steps'][0].get('travel_mode', 'Transit') if route['steps'] else 'Transit'
                    note = "Requires purchasing a ticket."
                
                return (
                    f"Travel time: {duration_text}. "
                    f"Distance: {distance_text}. "
                    f"Transport: {transport_type}. Note: {note or 'None'}."
                )
        except requests.exceptions.RequestException:
            continue
    return f"Travel time: Route not found for walking, transit, or driving between {from_location} and {to_location}. Check locations."


KNOWN_TOOLS = {"get_location_details": get_location_details, "calculate_travel_time": calculate_travel_time}
AVAILABLE_TOOL_FUNCTIONS = list(KNOWN_TOOLS.values())
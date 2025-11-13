# agents.py

import os
import streamlit as st
import json
from google.genai import types as genai_types
from google import genai
from typing import Optional, List
import time
from io import BytesIO
from dotenv import load_dotenv
from data_models import TravelItinerary, Day, Activity, Logistics 
from config import ITINERARY_SCHEMA, load_fallback_itinerary, FALLBACK_FILE 
from google.api_core import exceptions as gcp_exceptions 


class TransientRetryError(Exception):
    """Exception for transient errors that should trigger an external retry (st.rerun)."""
    pass


try:
    from google.cloud import texttospeech
    GCP_TTS_AVAILABLE = True
except ImportError:
    GCP_TTS_AVAILABLE = False
    
load_dotenv() 

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

GEMINI_RETRY_DELAY_MS = int(os.getenv("GEMINI_RETRY_DELAY_MS", 1000))
GEMINI_RETRY_DELAY_S = GEMINI_RETRY_DELAY_MS / 1000

@st.cache_resource
def get_gemini_client():
    """Initializes the Gemini client once and caches it."""
    if GEMINI_API_KEY and GEMINI_API_KEY != "x":
        try:
            client_instance = genai.Client(api_key=GEMINI_API_KEY)
            return client_instance
        except Exception as e:
            st.error(f"Error initializing Gemini client: {e}") 
            return None
    return None

client = get_gemini_client()

def create_tool_call_part(tool_calls):
    return genai_types.Part(function_call=tool_calls[0]) 

def create_tool_response_part(name, response):
    return genai_types.Part(function_response=genai_types.FunctionResponse(name=name, response=response))


def run_planning_agent_gemini(destination: str, days: int, theme: str, max_turns: int = 7) -> Optional[TravelItinerary]:
    """Runs the core Gemini agent loop to create the itinerary."""
    
    if client is None or GEMINI_MODEL is None:
        st.toast("Gemini client is not initialized. Planning failed.", icon="❌")
        return None

    system_instruction = f"You are an expert travel planner. Your task is to create a detailed, daily travel itinerary in English for {destination} over {days} days, focusing on the '{theme}' theme. You must output the FINAL, COMPLETE travel itinerary ONLY in a single JSON object that conforms STRICTLY to the provided JSON Schema."
    
    initial_prompt = f"Plan a {days}-day trip to {destination} with a focus on {theme}. Please provide the final, complete itinerary JSON now."
    
    messages = [
        genai_types.Content(role="user", parts=[genai_types.Part(text=initial_prompt)]),
    ]
    
    config_final_json = genai_types.GenerateContentConfig(
        temperature=0.7,
        system_instruction=system_instruction,
        response_mime_type="application/json", 
        response_schema=ITINERARY_SCHEMA
    )
    
    MAX_JSON_RETRIES = 5
    
    for attempt in range(MAX_JSON_RETRIES):
        
        if attempt == 0:
            st.toast("Starting itinerary planning and formatting.", icon="⚙️")
        
        try:
            final_response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=messages,
                config=config_final_json
            )
            
            itinerary_data = final_response.text
            itinerary = TravelItinerary.model_validate_json(itinerary_data)
            
            st.toast("Itinerary successfully generated and validated.", icon="✅")
            return itinerary
        
        except gcp_exceptions.ServiceUnavailable as e: 
            if attempt < MAX_JSON_RETRIES - 1:
                # Show attempt number and that it's due to a 503
                st.toast(
                    f"Attempt {attempt + 1}: Retrying after a 503 error. Waiting {GEMINI_RETRY_DELAY_S:.1f}s...", 
                    icon="🔄"
                )
                time.sleep(GEMINI_RETRY_DELAY_S) 
                continue
            else:
                st.toast("Gemini JSON Error: Max retries reached (503 UNAVAILABLE). Aborting.", icon="❌")
                return None
        
        except gcp_exceptions.ResourceExhausted as e:
            st.toast("Quota exceeded (429). Activating DEMO data.", icon="⚠️")
            
            fallback_data = load_fallback_itinerary()
            
            if fallback_data and fallback_data.daily_itinerary:
                template_day_dict = fallback_data.daily_itinerary[0].model_dump()
                new_itinerary = []
                
                for i in range(days):
                    day_dict = template_day_dict.copy()
                    day_dict['day_name'] = f"Day {i+1}: Demo based on {fallback_data.daily_itinerary[0].day_name}" 
                    day_dict['date'] = f"2025-01-{str(i+1).zfill(2)}" # Dummy date
                    
                    try:
                        new_day = Day.model_validate(day_dict)
                        new_itinerary.append(new_day)
                    except Exception as ve:
                        st.toast(f"Validation error when building mock day {i+1}: {ve}", icon="❌")
                        return None

                fallback_data.daily_itinerary = new_itinerary
                fallback_data.total_days = days
                fallback_data.destination = destination
                fallback_data.main_theme = f"[MOCK] {theme}"

                st.toast("Demo plan loaded.", icon="✅")
                return fallback_data
            else:
                st.toast("Error: Could not load the fallback_itinerary.json file.", icon="❌")
                return None
        
        except Exception as e:
            st.toast(f"Processing/JSON Error. Initiating automatic retry...", icon="❌")
            raise TransientRetryError(f"Validation/JSON Error: {e}") 
            
    return None

def get_mock_itinerary_with_expansion(destination: str, days: int, theme: str) -> Optional[TravelItinerary]:
    """Loads the mock data from the JSON and expands it to the requested number of days."""
    
    fallback_data = load_fallback_itinerary()
    
    if fallback_data and fallback_data.daily_itinerary:
        template_day_dict = fallback_data.daily_itinerary[0].model_dump()
        new_itinerary = []
        
        for i in range(days):
            day_dict = template_day_dict.copy()
            day_dict['day_name'] = f"Day {i+1}: DEMO (JSON Error Fallback)" 
            day_dict['date'] = f"2025-01-{str(i+1).zfill(2)}"
            
            try:
                new_day = Day.model_validate(day_dict)
                new_itinerary.append(new_day)
            except Exception as ve:
                st.toast(f"Validation error when building mock day {i+1}: {ve}", icon="❌")
                return None

        fallback_data.daily_itinerary = new_itinerary
        fallback_data.total_days = days
        fallback_data.destination = destination
        fallback_data.main_theme = f"[MOCK/RETRY FAIL] {theme}"

        return fallback_data
    return None


def generate_daily_summary_audio(day_data: Day) -> Optional[bytes]:
    """
    Generates a text summary of the day using Gemini (in English) and then converts it to MP3 audio 
    using the Google Cloud Text-to-Speech API, with immediate retry in case of a 503 error.
    Returns the MP3 file bytes.
    """
    if not GCP_TTS_AVAILABLE:
        st.toast("Error: The 'google-cloud-texttospeech' library is not installed.", icon="❌")
        return None
    
    if client is None or GEMINI_MODEL is None:
        st.toast("Gemini client is not initialized for text summary.", icon="❌")
        return None
    
    st.toast("Generating daily summary text with Gemini...", icon="🗣️")

    day_activities = "\n".join([
        f"- {act.start_time}-{act.end_time}: {act.name}. Description: {act.short_description}. Cost: {act.estimated_cost}"
        for act in day_data.activities
    ])

    summary_prompt = f"""
        You are a travel podcast host. Based on the following daily itinerary, write a concise, 
        enthusiastic, and easy-to-read summary (max 4-5 sentences, intended to be read aloud) of the day. 
        Focus on the most important activities.
        The name of the day is: "{day_data.day_name}".
        Activities:
    {day_activities}

    Write the final summary ONLY in English. Start with: 'Good morning! An incredible day awaits you...'
    """

    config_summary = genai_types.GenerateContentConfig(temperature=0.5)

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[genai_types.Part(text=summary_prompt)],
            config=config_summary
        )
        summary_text = response.text.strip()
    except Exception as e:
        st.toast(f"Error generating text summary with Gemini: {e}", icon="❌")
        return None
    
    st.toast("Converting text summary to high-quality AI speech...", icon="🎙️")
    
    MAX_TTS_RETRIES = 2
    
    for attempt in range(MAX_TTS_RETRIES):
        try:
            tts_client = texttospeech.TextToSpeechClient()

            synthesis_input = texttospeech.SynthesisInput(text=summary_text)

            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US", 
                name="en-US-Wavenet-D", 
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )

            response = tts_client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )

            st.toast("Audio generated successfully via GCP TTS!", icon="✅")
            return response.audio_content

        except gcp_exceptions.ServiceUnavailable as e:
            st.toast(f"TTS API received a 503 error (Attempt {attempt + 1}/{MAX_TTS_RETRIES}). Retrying immediately...", icon="⚠️")
            if attempt == MAX_TTS_RETRIES - 1:
                st.toast("Maximum retries reached for TTS API (503 error). Aborting.", icon="❌")
                return None
            continue
        
        except Exception as e:
            if "403" in str(e) and "texttospeech.googleapis.com" in str(e):
                st.toast("Error 403: The Cloud Text-to-Speech API is not enabled. Enable it in the GCP Console.", icon="❌")
            else:
                 st.toast(f"Error converting text to speech using Google Cloud TTS API: {e}", icon="❌")
            return None
            
    return None
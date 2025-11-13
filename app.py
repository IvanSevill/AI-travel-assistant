import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from typing import List, Optional 
import time

from agents import run_planning_agent_gemini, generate_daily_summary_audio, TransientRetryError, get_mock_itinerary_with_expansion
from config import GEMINI_MODEL 


# --- Funciones de visualización (separadas) ---

def display_day_title(day_data):
    st.subheader(day_data.day_name)


def display_content_and_logistics(day_data):
    # 1. Tabla de Actividades
    activity_data = []
    if day_data.activities:
        for activity in day_data.activities:
            activity_data.append({
                "Time": f"{activity.start_time} - {activity.end_time}",
                "Activity": activity.name,
                "Description": activity.short_description,
                "Location": activity.location,
                "Cost": activity.estimated_cost
            })
        
        st.dataframe(pd.DataFrame(activity_data), width='stretch', hide_index=True)
    
    # 2. Logística y Transporte
    display_list = []
    if day_data.activities and day_data.logistics_between_activities:
        for j, logistics in enumerate(day_data.logistics_between_activities):
            if j + 1 < len(day_data.activities):
                next_activity_name = day_data.activities[j+1].name
                
                logistics_detail = f"➡️ **Logistics to {next_activity_name}:** {logistics.transport_type} ({logistics.estimated_duration}). Notes: {logistics.additional_notes or 'None'}"
                display_list.append(logistics_detail)
        
        if display_list:
            st.markdown("### Travel Logistics")
            st.markdown("\n".join([f"* {item}" for item in display_list]))

    if not activity_data:
        st.info("No activities were successfully parsed for this day.")
        return False
    return True


def display_audio_section(day_data, i):
    st.markdown("---") 
    st.markdown(f"**Day {i+1} Summary (AI Voice)**")
    
    audio_key = f"audio_day_{i}"
    
    if audio_key not in st.session_state or not st.session_state[audio_key]:
        if st.button("🔊 Generate Audio Summary", key=f"tts_btn_{i}"):
            with st.spinner("Processing audio summary..."):
                audio_bytes = generate_daily_summary_audio(day_data) 
            
            if audio_bytes:
                st.session_state[audio_key] = audio_bytes
                st.rerun() 
                
    # Reproductor de Audio
    if audio_key in st.session_state and st.session_state[audio_key]:
        st.audio(st.session_state[audio_key], format="audio/mp3", autoplay=False)

def display_itinerary_day(day_data, i):
    display_day_title(day_data)
    
    if display_content_and_logistics(day_data):
        display_audio_section(day_data, i)


load_dotenv() 
MIN_DIAS = int(os.getenv("MIN_DIAS", 1)) 
MAX_DIAS = int(os.getenv("MAX_DIAS", 7))

MAX_APP_RETRIES = int(os.getenv("MAX_APP_RETRIES", 3)) 
RETRY_DELAY_S = float(os.getenv("RETRY_DELAY_S", 2.0)) 


st.set_page_config(layout="wide")
st.title("AI Assisted Travel Itinerary Planner")
st.caption("Using **Gemini** for generation and **Google Maps API** for real-time data.")

if 'itinerary_generated' not in st.session_state:
    st.session_state['itinerary_generated'] = False
    st.session_state['itinerary_data'] = None
    st.session_state['active_model'] = "N/A"
    st.session_state['app_retry_count'] = 0
    st.session_state['generate_triggered'] = False 


def trigger_generation():
    if 'generate_btn' in st.session_state and st.session_state.generate_btn:
        st.session_state['generate_triggered'] = True
        st.session_state['itinerary_generated'] = False
        st.session_state['itinerary_data'] = None
        st.session_state['app_retry_count'] = 0


with st.sidebar:
    st.header("Trip Parameters")
    
    destination = st.text_input("Destination City/Region", "Madrid, Spain", key="dest_input")
    days = st.slider("Number of Days", MIN_DIAS, MAX_DIAS, (MIN_DIAS + MAX_DIAS) // 2, key="days_input")
    theme = st.selectbox("Trip Theme/Focus", ["Historical and Cultural", "Food and Leisure", "Adventure and Nature"], key="theme_input")
    
    
    st.button("Generate Itinerary", type="primary", on_click=trigger_generation, key="generate_btn")


if st.session_state['generate_triggered']:
    
    now = time.time()
    if st.session_state.get('delay_until', 0) > now:
        PAUSE_OVERHEAD_S = 0.2
        wait_time = st.session_state['delay_until'] - now + PAUSE_OVERHEAD_S
        
        if wait_time < 0.1:
            wait_time = 0.1
            
        st.toast(f"Waiting {wait_time:.1f} seconds before retrying...", icon="⏳")
        time.sleep(wait_time)
        st.session_state['delay_until'] = 0


    if st.session_state['app_retry_count'] == 0:
        st.session_state['itinerary_data'] = None
    
    current_destination = st.session_state.dest_input
    current_days = st.session_state.days_input
    current_theme = st.session_state.theme_input

    with st.spinner(f"Initializing Gemini Agent ({GEMINI_MODEL})..."):
        
        if GEMINI_MODEL is None:
            st.toast("🔴 ERROR: The Gemini API key is not configured or initialization failed.", icon="❌")
            st.session_state['generate_triggered'] = False
            st.session_state['app_retry_count'] = 0 
            
        else:
            itinerary_data = None
            try:
                itinerary_data = run_planning_agent_gemini(
                    current_destination, 
                    current_days, 
                    current_theme
                )
                    
            except TransientRetryError as e:
                st.session_state['app_retry_count'] += 1
                
                if st.session_state['app_retry_count'] < MAX_APP_RETRIES:
                    st.session_state['delay_until'] = time.time() + RETRY_DELAY_S 
                    st.toast(f"🚨 Transient error captured. Automatic retry ({st.session_state['app_retry_count']}/{MAX_APP_RETRIES}).", icon="🔄")
                    st.rerun()
                else:
                    st.toast(f"❌ "+str(MAX_APP_RETRIES)+" consecutive JSON validation failures. Activating mock data fallback.", icon="❌")
                    
                    itinerary_data = get_mock_itinerary_with_expansion(
                        current_destination, 
                        current_days, 
                        current_theme
                    )
                    
            if itinerary_data:
                st.session_state['itinerary_data'] = itinerary_data
                st.session_state['itinerary_generated'] = True
                st.session_state['active_model'] = GEMINI_MODEL 
                st.session_state['app_retry_count'] = 0 
                st.session_state['generate_triggered'] = False 
                
                st.rerun() 
            
            elif itinerary_data is None:
                st.session_state['generate_triggered'] = False 
                st.session_state['app_retry_count'] = 0
                

if st.session_state['itinerary_generated'] and st.session_state['itinerary_data']:
    itinerary = st.session_state['itinerary_data']
    active_model = st.session_state.get('active_model', 'N/A')
    
    st.header(f"Plan for {itinerary.destination} ({len(itinerary.daily_itinerary)} Days)")
    st.subheader(f"Theme: {itinerary.main_theme}")
    st.caption(f"Generated with: **{active_model}**")
    
    if itinerary.daily_itinerary:
        tab_titles = [f"Day {i+1}" for i in range(len(itinerary.daily_itinerary))]
        tabs = st.tabs(tab_titles)

        for i, day_data in enumerate(itinerary.daily_itinerary):
            with tabs[i]:
                display_itinerary_day(day_data, i)
    else:
        st.error("Itinerary data is present but the daily itinerary list is empty.")
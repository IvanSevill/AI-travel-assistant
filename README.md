# AI Travel Itinerary Planner (Gemini & Streamlit)

This repository contains an interactive web application built with **Streamlit** that generates detailed, day-by-day travel itineraries using the **Google Gemini** model.  
The app ensures structured and validated output through **Pydantic/JSON Schema** and integrates **Google APIs** for real-world location and travel data.

---

## Academic Project Context

This project was developed for the **Artificial Intelligence Laboratory** course.  
Its main objective is to demonstrate the practical use of **Large Language Models (LLMs)** through **Function/Tool Calling** and **Structured Output Generation**.

### Core AI Concepts Demonstrated

- **Structured Reasoning:** Enforcing consistent JSON output using Pydantic schemas.  
- **Agentic Workflow:** Using two agents (Planner Agent and Summarizer Agent) in a closed feedback loop.  
- **External Knowledge Integration:** Incorporating real-world data through API calls to improve itinerary accuracy.

---

## Key Features

- **AI Planning (Gemini):** Generates complete daily itineraries using the Gemini model with strict response schema validation.  
- **Structured Validation:** Ensures reliable AI responses using Pydantic data models.  
- **Tool Integration (Maps & Places):** Retrieves real-time location data and travel durations using Google APIs.  
- **Audio Summaries (TTS):** Produces daily voice summaries using the Google Cloud Text-to-Speech API.  
- **Streamlit Interface:** Provides a clean, responsive UI with day-based tabs and embedded audio playback.

---

## Tools and Function Calling

The application includes several external Python functions (`tools.py`) that the Gemini agent can call to retrieve real-world data.

| Tool Function | API Used | Description |
| :------------- | :-------- | :----------- |
| `get_location_details(place_name)` | Google Places API | Retrieves type, rating, address, and open status for a given location. |
| `calculate_travel_time(from, to)` | Google Directions API | Estimates travel time and transportation method between two points. |

---

## Dependencies and Requirements

### Local Requirements

- Python 3.10 or higher  
- Git

### Required API Keys

You will need the following credentials for the app to function properly:

1. **GEMINI_API_KEY:** Used by the planning and summarizing agents (`agents.py`).  
2. **GOOGLE_MAPS_API_KEY:** Used to query Google Maps and Places APIs (`tools.py`).  
3. **GOOGLE CLOUD CREDENTIALS:** Required for the Text-to-Speech (TTS) API.  
   - Enable the **Cloud Text-to-Speech API** in Google Cloud Platform.  
   - Authenticate using `gcloud auth application-default login` or provide a Service Account JSON key.

---

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/IvanSevill/AI-travel-assistant.git
cd AI-travel-assistant
```

### 2. Create a Virtual Environment

#### Windows (PowerShell/CMD):
```bash
python -m venv venv
.\venv\Scripts\activate
```

#### macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```
### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Rename the plantilla.env to .env file in the project root directory

### 5. Run the Application

```bash
streamlit run app.py
```
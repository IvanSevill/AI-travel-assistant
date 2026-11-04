# AI Travel Assistant

Tell it where you are going, for how long, and what you enjoy, and it plans your trip day by day and what to see, using Google Gemini.

This started as a university project for an Artificial Intelligence Laboratory course, to practice function calling and structured output with large language models.

## Highlights

- **A plan for each day.** Choose a destination, 1 to 7 days, and a theme: history and culture, food and leisure, or adventure and nature.
- **Real places.** Gemini can look up locations and travel times through Google Maps data.
- **Spoken summaries.** Generate an audio summary for each day with Google Cloud Text-to-Speech.

## Run it

You need Python 3.10 or newer, plus:

- A `GEMINI_API_KEY`
- A `GOOGLE_MAPS_API_KEY`
- Google Cloud credentials with the Text-to-Speech API enabled, only for the audio summaries

```sh
git clone https://github.com/IvanSevill/AI-travel-assistant.git
cd AI-travel-assistant
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp template.env .env
```

Add your keys to `.env`, then start the app:

```sh
streamlit run app.py
```

On Windows, activate the environment with `.\venv\Scripts\activate` and use `copy` instead of `cp`.

For the audio summaries, sign in with `gcloud auth application-default login` or use a service account key.

## How it works

| File | What it does |
| --- | --- |
| `app.py` | The Streamlit interface |
| `agents.py` | The planner and the audio summary |
| `tools.py` | The location and travel time lookups Gemini can call |
| `data_models.py` | The Pydantic schemas that plans must match |

## Limits

- **You may get sample data.** After three failed attempts, the app shows a built-in sample itinerary instead of a real plan. A brief notice is the only sign, so check it before relying on a plan.
- **Your API usage may cost money.** Check the pricing for each Google service.
- **The install is large.** `requirements.txt` includes `torch` and `transformers`, which the code does not use.
- There are no automated tests.

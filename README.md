# Pathway AI

**1st Place | Hack for Homeless Hackathon**  
**A resource-navigation and employment-support prototype for people experiencing housing insecurity.**

## The problem

Finding help should not require searching through multiple disconnected websites. Someone experiencing housing insecurity may need to locate a nearby shelter, find food or healthcare, prepare a résumé, and look for work, all while navigating unfamiliar services and limited time. Location and individual circumstances make that process even harder.

## What I built

Pathway AI brings these tasks into a single, Streamlit-based application. It combines location-aware resource discovery, interactive maps, résumé creation, job-search assistance, and experimental conversational guidance. The goal is to make potential next steps easier to find and explore, not to replace direct contact with service providers.

## Features

| Module | What it does |
| --- | --- |
| **Housing Matchmaker** | Geocodes a US city or ZIP code, searches OpenStreetMap/Overpass for shelter-related locations within approximately 8 km, and presents results on an interactive Folium map. Includes a separate address-to-shelter distance and AI-assisted analysis feature. |
| **Resource Navigator** | Searches Google Places for nearby services such as food, healthcare, or clothing; maps results and offers AI-generated navigation guidance. |
| **Résumé & Job Finder** | Builds a downloadable PDF résumé from user-provided information, suggests possible job categories, maps relevant local businesses, and provides a career Q&A interface. |
| **Mental Health Chatbot (experimental)** | Includes a conversational interface, sentiment analysis, and SQLite conversation-history storage. Not designed or validated for clinical or emergency use. |
| **Home & Tutorial** | Provides navigation and explains the application's modules. |

## Technology

- **Application:** Python, Streamlit
- **Maps and location:** Folium, Streamlit-Folium, GeoPy/Nominatim, OpenStreetMap/Overpass, Google Places API
- **AI and text processing:** OpenAI API; Hugging Face Transformers sentiment-analysis pipeline
- **Data and documents:** SQLite, FPDF

## Repository structure

```text
app.py                       # Streamlit entry point and sidebar navigation
Home.py                      # Home page
Housing_Matchmaker.py        # Shelter map and location analysis
Resource_Navigator.py        # Essential-service search and map
Resume_Job_Finder.py         # PDF résumé and job-search tools
Mental_Health_Chatbot.py     # Experimental chatbot and message storage
Admin_Dashboard.py           # Tutorial page (despite the filename)
config.toml                  # Theme configuration in the archived version
```

## Running locally

This repository is an archived hackathon prototype, **not a one-command production deployment**. The source files pass Python syntax checks, but a complete end-to-end run with current third-party services has not been verified.

Use Python 3.11 and create a virtual environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install streamlit geopy requests folium streamlit-folium "openai==0.28.1" transformers torch fpdf2
streamlit run app.py
```

**Integration setup required:** Some modules depend on OpenAI and Google Places credentials and external network services. The archived code uses legacy `openai.ChatCompletion.create()` calls; the `openai==0.28.1` command above is for that legacy interface, not a claim of full compatibility testing. Before deploying or sharing an interactive build, migrate the API integrations to a supported SDK, load credentials from environment variables or Streamlit secrets, remove any key literals from source, and rotate previously exposed keys. Do not commit a populated `.env`, `.streamlit/secrets.toml`, or user conversation database.

The sentiment-analysis model may need to download on first launch. Map and search results depend on external service availability and data coverage.

## Recognition and status

Pathway AI earned **1st Place at the Hack for Homeless Hackathon**. This repository preserves the hackathon implementation for code review and further development; it is not presented as a publicly deployed, fully validated service. Shelter listings and business results may be incomplete or outdated. Verify eligibility, availability, and contact information directly with providers before relying on them.

The experimental chatbot is not a substitute for professional mental healthcare or crisis support. Avoid entering sensitive personal or health information into an unmodified public deployment of the prototype.

**Developer:** Saurish Bhati

# NEO Mission Control 🛰️

A NASA-data-powered dashboard for tracking and assessing risk from Near-Earth Objects (asteroids), built with a custom risk-scoring engine, 3D orbital visualization, and an AI mission analyst.

## Overview

NEO Mission Control pulls live asteroid data from NASA's NeoWs API and goes beyond simple hazard flags — it computes a custom weighted risk score (based on size, velocity, and proximity), translates raw measurements into relatable scale comparisons (e.g. "larger than the Empire State Building"), and generates plain-language mission briefings using an LLM. The interface is styled to reflect NASA's official visual identity.

## Features

- **Live NASA data**: Pulls real near-Earth object data from NASA's NeoWs API across any date range
- **Custom risk scoring**: Weighted formula (size + velocity + proximity) producing a 0-100 risk score and category (Low/Moderate/High/Critical)
- **3D orbital visualization**: Interactive 3D plot showing Earth and tracked asteroids in relative space
- **AI Mission Analyst Briefing**: On-demand AI-generated briefings (Groq LLaMA 3.3 70B) written in a calm, professional mission-control voice
- **Filterable dashboard**: Filter by risk category, sort by risk score, browse asteroids in a responsive card grid
- **NASA-inspired design**: Official NASA blue/red color palette, clean editorial layout

## Tech Stack

- **Language**: Python
- **Dashboard**: Streamlit
- **Data**: NASA NeoWs API
- **AI**: Groq API (llama-3.3-70b-versatile)
- **Visualization**: Plotly (3D scatter), Streamlit native charts
- **Data processing**: pandas

## Setup Instructions

1. Clone the repository:

   git clone https://github.com/AdyashaNayak16/NEO-RISK-DASHBOARD.git
   cd NEO-RISK-DASHBOARD

2. Create and activate a virtual environment:

   python -m venv venv
   venv\Scripts\activate   (Windows)

3. Install dependencies:

   pip install -r requirements.txt

4. Create a .env file in the root directory with:

   NASA_API_KEY=your_nasa_api_key
   GROQ_API_KEY=your_groq_api_key

   Get a free NASA API key at api.nasa.gov and a free Groq API key at console.groq.com.

5. Fetch and score asteroid data:

   python fetch_neo.py 2026-07-01 2026-07-31
   python risk_scoring.py

6. Run the dashboard:

   streamlit run app.py

## Live Demo

Live App: https://neo-risk-dashboard-nfwhhnnh.streamlit.app/

## Repository

GitHub Repo: https://github.com/AdyashaNayak16/NEO-RISK-DASHBOARD

## Author

Adyasha Nayak — https://github.com/AdyashaNayak16

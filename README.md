# UK Spatial Intelligence Agent

An AI-powered geospatial query agent that answers plain English questions 
about UK local authority districts using PostGIS and Claude.

## What it does
- Accepts natural language spatial questions via a web chat interface
- Autonomously generates PostGIS SQL to answer each question
- Queries a spatial database of all 361 UK local authority districts
- Returns plain English answers with geographic context
- Remembers conversation history for follow-up questions
- Shows the SQL it wrote for full transparency

## Example questions
- "Which local authorities border Sheffield?"
- "What is the area of Birmingham in km²?"
- "How many local authorities are within 100km of London?"
- "Which 5 local authorities have the largest area?"
- "Which of those are in Scotland?"
- "What is the farthest local authority from London?"

## Tech stack
- PostgreSQL + PostGIS — spatial database
- Anthropic Claude API — natural language to SQL translation
- Python — agent orchestration
- psycopg2 — database connection
- Streamlit — web interface
- UK ONS boundary data — local authority district polygons (2024)

## Setup
1. Clone the repository
2. Create a virtual environment: `python3 -m venv venv`
3. Activate it: `source venv/bin/activate`
4. Install dependencies: `pip install anthropic psycopg2-binary python-dotenv streamlit`
5. Create a `.env` file with your Anthropic API key: `ANTHROPIC_API_KEY=your-key`
6. Set up PostgreSQL + PostGIS and load UK boundary data
7. Run: `streamlit run app.py`

## Built by
Ridwan Shittu - Geospatial consultant
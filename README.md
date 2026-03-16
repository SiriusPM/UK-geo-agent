# UK Spatial Intelligence Agent

An AI-powered geospatial query agent that answers plain English questions 
about UK local authority districts using PostGIS and Claude.

## What it does
- Accepts natural language spatial questions via a web chat interface
- Autonomously generates PostGIS SQL to answer each question
- Queries a spatial database of all 361 UK local authority districts
- Generates colour-coded maps of query results on demand
- Remembers conversation history for follow-up questions
- Shows the SQL it wrote for full transparency

## Example questions
- "Which local authorities border Sheffield?"
- "Show me a map of all districts that border London"
- "What is the area of Birmingham in km²?"
- "How many local authorities are within 100km of London?"
- "Which 5 local authorities have the largest area?"
- "Show me a map of the 10 largest districts in Scotland"
- "What is the farthest local authority from London?"
- "Which local authority is most geometrically similar to Sheffield?"

## Tech stack
- PostgreSQL + PostGIS — spatial database engine
- Anthropic Claude API — natural language to SQL translation
- GeoPandas + Matplotlib — automated map generation
- Python — agent orchestration and tool management
- psycopg2 — database connection
- Streamlit — web chat interface
- UK ONS boundary data — local authority district polygons (2024)

## Agent capabilities
The agent has two tools it can call autonomously:

1. `run_spatial_query` — writes and executes PostGIS SQL to answer spatial questions
2. `generate_map` — produces colour-coded choropleth maps of query results

Claude decides which tools to use and in what order based on the question asked.

## Setup
1. Clone the repository
2. Create a virtual environment: `python3 -m venv venv`
3. Activate it: `source venv/bin/activate`
4. Install dependencies: `pip install anthropic psycopg2-binary python-dotenv streamlit geopandas matplotlib`
5. Create a `.env` file with your Anthropic API key: `ANTHROPIC_API_KEY=your-key`
6. Set up PostgreSQL + PostGIS and load UK ONS boundary data
7. Run: `streamlit run app.py`

## Built by
Ridwan Shittu - Geospatial consultant
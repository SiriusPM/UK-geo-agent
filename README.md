# Geo-Agent

An AI-powered geospatial query agent that answers plain English spatial 
questions about UK local authorities.

## What it does
Accepts natural language questions, autonomously generates PostGIS SQL, 
queries a spatial database of all 361 UK local authority districts, 
and returns plain English answers with geographic context.

## Tech stack
- PostgreSQL + PostGIS — spatial database
- Anthropic Claude API — natural language to SQL translation
- Python — agent orchestration
- psycopg2 — database connection
- UK ONS boundary data — local authority district polygons

## Example questions it can answer
- "Which local authorities border Sheffield?"
- "What is the area of Birmingham in km²?"
- "How many local authorities are within 100km of London?"
- "Which local authority is most geometrically similar to Sheffield?"
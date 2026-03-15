import anthropic
import psycopg2
import json
from dotenv import load_dotenv

load_dotenv()

# Connect to your PostGIS database
conn = psycopg2.connect(
    dbname="geospatial_lab",
    user="a1",
    host="localhost",
    port="5432"
)

def run_spatial_query(sql: str) -> str:
    """Runs a PostGIS SQL query and returns results as a string."""
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        return json.dumps(results, indent=2, default=str)
    except Exception as e:
        conn.rollback()
        return f"Query error: {str(e)}"

# Define the tool — this is what Claude can call
tools = [
    {
        "name": "run_spatial_query",
        "description": """Runs a PostGIS spatial SQL query against a UK 
        geospatial database containing local authority district boundaries. 
        The main table is local_authority_districts with columns: 
        lad24nm (district name), lad24cd (district code), 
        wkb_geometry (polygon geometry in WGS84/EPSG:4326).
        Always use ST_Transform(wkb_geometry, 27700) for distance 
        and area calculations.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": "A valid PostGIS SQL query"
                }
            },
            "required": ["sql"]
        }
    }
]

def ask_geo_agent(question: str) -> str:
    """Send a question to Claude and let it query PostGIS to answer it."""
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": question}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )

        # If Claude wants to use a tool
        if response.stop_reason == "tool_use":
            tool_use = next(b for b in response.content if b.type == "tool_use")
            sql = tool_use.input["sql"]
            print(f"\nClaude is running this query:\n{sql}\n")

            query_result = run_spatial_query(sql)

            # Add Claude's response and tool result to the conversation
            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": query_result
                }]
            })

        # If Claude is done and has a final answer
        elif response.stop_reason == "end_turn":
            final = next(b for b in response.content if hasattr(b, "text"))
            return final.text

# Ask your first spatial question
print("Geo-Agent ready. Ask any spatial question about UK local authorities.")
print("Type 'quit' to exit.\n")

while True:
    question = input("Your question: ")
    if question.lower() == "quit":
        break
    answer = ask_geo_agent(question)
    print(f"\nAnswer: {answer}\n")
    print("-" * 60 + "\n")
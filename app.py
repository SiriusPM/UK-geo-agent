import streamlit as st
import anthropic
import psycopg2
import json
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="UK Geo-Agent",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ UK Spatial Intelligence Agent")
st.caption("Ask any question about UK local authority districts in plain English.")

@st.cache_resource
def get_connection():
    return psycopg2.connect(
        dbname="geospatial_lab",
        user="a1",
        host="localhost",
        port="5432",
        password="geo123"
    )

conn = get_connection()

SYSTEM_PROMPT = """You are a geospatial analyst assistant with access to a 
PostGIS spatial database of UK local authority districts.

Database table: local_authority_districts
Columns:
- lad24nm: district name (text)
- lad24cd: district code (text, e.g. E08000019)
- wkb_geometry: polygon geometry stored in WGS84 (EPSG:4326)

Important rules:
- Always use ST_Transform(wkb_geometry, 27700) for distance and area calculations
- Use ILIKE for name searches to handle case variations
- For distance queries, 27700 units are metres — divide by 1000 for km
- When asked follow-up questions like "those areas" or "those districts", 
  refer back to the previous query results in the conversation
- Always explain your findings in plain English with geographic context
- Round area results to 2 decimal places
- Round distance results to 1 decimal place
- When the user asks to "show", "map", "visualise", or "display" results,
  first run the spatial query to get district names, then call generate_map
  with those district names"""

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
    },
    {
        "name": "generate_map",
        "description": """Generates a colour-coded map highlighting specific 
        UK local authority districts on a UK base map. Use this whenever 
        the user asks to show, map, visualise, or display districts. 
        Always call run_spatial_query first to get district names, 
        then call this tool with those names.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "district_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of district names to highlight"
                },
                "title": {
                    "type": "string",
                    "description": "Title for the map"
                }
            },
            "required": ["district_names", "title"]
        }
    }
]


def run_spatial_query(sql: str) -> str:
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


def generate_map(district_names: list, title: str) -> str:
    try:
        gdf = gpd.read_postgis(
            "SELECT lad24nm, wkb_geometry FROM local_authority_districts",
            conn,
            geom_col='wkb_geometry'
        )

        gdf_projected = gdf.to_crs(epsg=27700)
        gdf['area_km2'] = gdf_projected.geometry.area / 1_000_000

        fig, ax = plt.subplots(1, 1, figsize=(10, 12))

        gdf.plot(
            ax=ax,
            color='lightgray',
            edgecolor='white',
            linewidth=0.3
        )

        if district_names:
            highlighted = gdf[gdf['lad24nm'].isin(district_names)]
            if len(highlighted) > 0:
                highlighted.plot(
                    ax=ax,
                    column='area_km2',
                    cmap='YlOrRd',
                    legend=True,
                    edgecolor='white',
                    linewidth=0.5,
                    legend_kwds={
                        'label': 'Area (km²)',
                        'shrink': 0.5
                    }
                )

        ax.set_title(title, fontsize=14, pad=15)
        ax.set_axis_off()
        plt.tight_layout()

        map_path = f"map_output.png"
        plt.savefig(map_path, dpi=150, bbox_inches='tight')
        plt.close()

        return map_path

    except Exception as e:
        return f"Map error: {str(e)}"


def ask_geo_agent(question: str, history: list) -> tuple:
    client = anthropic.Anthropic()
    history.append({"role": "user", "content": question})
    sql_used = ""
    map_path = None

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=history
        )

        if response.stop_reason == "tool_use":
            tool_use = next(b for b in response.content if b.type == "tool_use")

            if tool_use.name == "run_spatial_query":
                sql_used = tool_use.input["sql"]
                query_result = run_spatial_query(sql_used)

            elif tool_use.name == "generate_map":
                district_names = tool_use.input["district_names"]
                title = tool_use.input["title"]
                result = generate_map(district_names, title)
                if result.endswith('.png'):
                    map_path = result
                    query_result = f"Map generated with {len(district_names)} districts highlighted"
                else:
                    query_result = result

            history.append({"role": "assistant", "content": response.content})
            history.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": query_result
                }]
            })

        elif response.stop_reason == "end_turn":
            final_text = next(b for b in response.content if hasattr(b, "text"))
            history.append({"role": "assistant", "content": final_text.text})
            return final_text.text, sql_used, map_path


if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("map_path"):
            st.image(msg["map_path"], use_column_width=True)
        if msg.get("sql"):
            with st.expander("SQL query Claude wrote"):
                st.code(msg["sql"], language="sql")

if question := st.chat_input("Ask a spatial question about UK local authorities..."):

    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        with st.spinner("Analysing..."):
            answer, sql_used, map_path = ask_geo_agent(
                question,
                st.session_state.history
            )

        st.markdown(answer)

        if map_path:
            st.image(map_path, use_column_width=True)

        if sql_used:
            with st.expander("SQL query Claude wrote"):
                st.code(sql_used, language="sql")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sql": sql_used,
        "map_path": map_path
    })
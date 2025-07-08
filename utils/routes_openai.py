import os
import openai
import json
from openai import OpenAIError
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPEN_API_KEY")

def build_simulation_prompt(containers):
    data = [
        {
            "guid": c.guid,
            "capacity": int(c.capacity),
            "limit": int(c.limit),
            "latitude": float(c.latitude),
            "longitude": float(c.longitude),
        } for c in containers
    ]

    # Pre‑compute urgent list for clarity 
    urgent = [c for c in data if c["capacity"] >= c["limit"]]
    urgent_sorted = sorted(urgent, key=lambda x: (-x["capacity"], x["guid"]))
    urgent_guids = [u["guid"] for u in urgent_sorted]

    print(f"[DEBUG] urgent_guids = {urgent_guids}")

    total = len(data)

    return (
        "You are optimizing a municipal waste‑collection route (Traveling Salesman Problem, TSP).\n"
        "\n"
        "Each container record provides: guid, latitude, longitude, capacity (0‑100) and limit (0‑100).\n"
        "A container is **urgent** as soon as its own capacity ≥ its own limit (note the ≥).\n"
        "\n"
        "PRIORITY RULES (must hold in the final route):\n"
        "  A. **All urgent containers FIRST**, before any non‑urgent.\n"
        "  B. **Within urgent**, order by capacity DESC (ties → nearest by haversine to the previous stop).\n"
        "  C. **After urgent**, place remaining containers by capacity DESC with distance as tiebreaker.\n\n"
        "The route MUST start at the urgent container with the HIGHEST capacity.\n"
        "Do NOT reorder a non‑urgent stop ahead of an urgent one under any circumstance.\n\n"
        "\n"
        "OPTIMISATION GOAL\n"
        "Minimise total distance (haversine) subject to the rules above.\n"
        "\n"
        "OUTPUT – return STRICT JSON (no markdown):\n"
        "{\n"
        "  \"route\": [guid1, guid2, ...],               # every GUID appears exactly once\n"
        "  \"distances\": [                             # one entry for each consecutive pair\n"
        "    {\"from\": guid1, \"to\": guid2, \"distance_km\": float},\n"
        "    ...\n"
        "  ],\n"
        "  \"total_distance_km\": float,                # sum of the above, round 2 dec\n"
        "  \"duration_min\": float                     # assume constant truck speed if needed\n"
        "}\n"
        "\n"
        "RULE CHECK (self‑validate **before** responding):\n"
        "  1. urgent = [containers with capacity ≥ limit]  # see list below.\n"
        "  2. Assert urgent appear contiguously at the BEGINNING of route, in capacity‑DESC order.\n"
        "  3. Assert no non‑urgent precedes an urgent.\n"
        "  4. distances is a JSON ARRAY and len == len(route)-1.\n"
        "  5. abs(sum(distances[*].distance_km) − total_distance_km) ≤ 0.01.\n"
        "  6. route contains every GUID exactly once.\n"
        "\n"
        f"DATA SET HAS {total} CONTAINERS.  Urgent containers (capacity ≥ limit) → {urgent_guids}\n\n"
        f"{json.dumps(data, indent=2)}"
    )


def parse_openai_simulation_response(content: str):
    try:

        cleaned_content = content.strip()
        if cleaned_content.startswith("```json"):
            cleaned_content = cleaned_content[7:]
        if cleaned_content.startswith("```"):
            cleaned_content = cleaned_content[3:]
        if cleaned_content.endswith("```"):
            cleaned_content = cleaned_content[:-3]
        
        cleaned_content = cleaned_content.strip()

        data = json.loads(cleaned_content)
        route = data["route"]
        distances = data["distances"]
        total_distance = float(data["total_distance_km"])
        duration = float(data["duration_min"])

        if not isinstance(route, list) or not all(isinstance(x, str) for x in route):
            raise ValueError("Invalid 'route' format")

        if not isinstance(distances, list):
            raise ValueError("Invalid 'distances' format")
        
        distances_json = json.dumps(distances)

        return route, distances_json, total_distance, duration
    except Exception as e:
        raise ValueError(f"Invalid response from OpenAI: {content}") from e

def call_openai_for_simulation(containers):
    prompt = build_simulation_prompt(containers)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a route optimisation assistant that MUST follow the priority and validation rules strictly. Self validate per checklist before answering"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        content = response["choices"][0]["message"]["content"]
        return parse_openai_simulation_response(content)
    except OpenAIError as e:
        raise RuntimeError(f"OpenAI API error: {str(e)}") from e
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
            "capacity": c.capacity,
            "latitude": c.latitude,
            "longitude": c.longitude
        } for c in containers
    ]

    return (
        "You are optimizing a waste collection route using the Traveling Salesman Problem (TSP).\n"
        "You are given a list of containers, each with:\n"
        "- guid: unique identifier\n"
        "- latitude and longitude\n"
        "- capacity (0 to 100, where lower = more urgent)\n\n"
        "Generate an optimized route that:\n"
        "1. Prioritizes containers with the **lowest capacity** (almost full).\n"
        "2. Minimizes total distance using the haversine formula.\n\n"
        "Return ONLY a valid JSON response in the following format:\n"
        "{\n"
        '  "route": [guid1, guid2, ...],\n'
        '  "distance_km": float,\n'
        '  "duration_min": float\n'
        "}\n\n"
        "Here is the list of containers:\n\n"
        f"{json.dumps(data, indent=2)}"
    )

def parse_openai_simulation_response(content: str):
    try:
        data = json.loads(content)
        route = data["route"]
        distance = float(data["distance_km"])
        duration = float(data["duration_min"])

        if not isinstance(route, list) or not all(isinstance(x, str) for x in route):
            raise ValueError("Invalid 'route' format")

        return route, distance, duration
    except Exception as e:
        raise ValueError(f"Invalid response from OpenAI: {content}") from e

def call_openai_for_simulation(containers):
    prompt = build_simulation_prompt(containers)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a route optimization assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        content = response["choices"][0]["message"]["content"]
        return parse_openai_simulation_response(content)
    except OpenAIError as e:
        raise RuntimeError(f"OpenAI API error: {str(e)}") from e
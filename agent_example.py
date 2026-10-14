"""
Minimal working agent: Claude gets one tool (lookup a city/country in the
cappuccino index CSV) and decides on its own how many times to call it.

Run:
    export ANTHROPIC_API_KEY=sk-ant-...
    python3 agent_example.py
"""

import csv
import json

import anthropic

CSV_PATH = "Cappuccino Index 2026 (public) - full_data.csv"
MODEL = "claude-sonnet-5"

with open(CSV_PATH, newline="", encoding="utf-8") as f:
    ROWS = list(csv.DictReader(f))


def lookup(place: str):
    place = place.lower()
    matches = [r for r in ROWS if place in r["City"].lower() or place in r["Country"].lower()]
    return matches if matches else {"error": f"No matches for '{place}'"}


TOOLS = [
    {
        "name": "lookup",
        "description": "Look up cappuccino price and hourly wage data for a city or country by substring match.",
        "input_schema": {
            "type": "object",
            "properties": {"place": {"type": "string", "description": "City or country name"}},
            "required": ["place"],
        },
    }
]

client = anthropic.Anthropic()

messages = [
    {
        "role": "user",
        "content": "Compare the cappuccino price relative to hourly wage in Dublin vs Tokyo. "
        "Which is more expensive relative to local wages?",
    }
]

while True:
    response = client.messages.create(model=MODEL, max_tokens=1024, tools=TOOLS, messages=messages)
    messages.append({"role": "assistant", "content": response.content})

    if response.stop_reason != "tool_use":
        for block in response.content:
            if block.type == "text":
                print(block.text)
        break

    # Model asked for one or more tool calls -- run them for real, then
    # hand the results back so it can decide what to do next.
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            print(f"[agent calls] {block.name}({block.input})")
            result = lookup(**block.input)
            print(f"[tool returns] {result}\n")
            tool_results.append(
                {"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(result)}
            )
    messages.append({"role": "user", "content": tool_results})

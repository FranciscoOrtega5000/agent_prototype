# Travel agent prototype (LangGraph + SerpAPI)

Turns a natural-language travel question or a structured `TravelRequest` JSON into **structured JSON**: flight and hotel options backed by **SerpAPI** (Google Flights / Google Hotels), with an **NVIDIA NIM** chat model for parsing and light text polish.

Every invocation is **stateless** — one call, one result. Results are intended to be persisted by the backend, not the agent.

## Requirements

- Python 3.11+
- API keys: **NVIDIA** (`NVIDIA_API_KEY`) and **SerpAPI** (`SERPAPI_API_KEY`)

## Setup

```bash
cd prototype_agent
python3.11 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your keys
```

## Run — natural language

```bash
python run_agent.py "Flights from MEX to CDG on 2026-07-15 returning 2026-07-30"
```

## Run — structured JSON (simulates frontend form)

```bash
python run_agent.py --json-path my_request.json
```

Where `my_request.json` looks like:

```json
{
  "travel_request": {
    "client_name": "John Smith",
    "client_email": "client@example.com",
    "destination": "Paris, France",
    "departure_city": "New York, USA",
    "start_date": "2026-07-15",
    "end_date": "2026-07-30",
    "travelers": "2 Adults",
    "min_budget": 5000,
    "max_budget": 10000,
    "special_preferences": "Direct flights preferred. Hotel near city centre."
  }
}
```

## Run — hybrid (form fields + NL dates in special_preferences)

Dates can be omitted from the form and described in `special_preferences` instead:

```json
{
  "travel_request": {
    "destination": "Ibiza, Spain",
    "departure_city": "Mexico City",
    "travelers": "2 Adults",
    "max_budget": 8000,
    "special_preferences": "We want to travel August 10 to 18, 2026. Prefer boutique hotels near the beach."
  }
}
```

## Run — tests

```bash
python run_agent_test.py
```

Runs 8 test cases covering pure NL, structured JSON, hybrid, flight-only, hotel-only, and missing-date scenarios.

### Optional environment variables

| Variable | Purpose |
|---|---|
| `NVIDIA_MODEL` | Model id (default `nvidia/nemotron-3-super-120b-a12b`) |
| `INCLUDE_RAW` | `true` to embed full SerpAPI blobs per option in `raw_option_jsonb` fields |
| `MAX_OPTIONS` | Max flights and hotels listed (default `3`, max `10`) |

## Project layout

| Path | Role |
|---|---|
| `run_agent.py` | CLI entry: loads env, runs graph, prints JSON |
| `travel_graph.py` | LangGraph `StateGraph`: parse → guard → tools → summarize → validate |
| `graph_state.py` | Pydantic models aligned to DB schema (`FLIGHT_OPTIONS`, `HOTEL_OPTIONS`, `PACKAGES`) |
| `serpapi_tools.py` | LangChain tools wrapping SerpAPI HTTP calls |
| `run_agent_test.py` | 8-case test suite; run directly with `python run_agent_test.py` |
| `CAMBIOS_CAMPOS.md` | Spanish field-change reference for the backend/DB team |
| `docs/langgraph_migration.md` | Architecture deep-dive and scaling path |

## Output shape

Final JSON matches `TravelQueryOutput`:

```
{
  "summary": "...",
  "flight_options": [ { "title", "total_price", "total_duration_min", "layover_count",
                         "departure_token", "segments_jsonb", "emissions_kg",
                         "ranking_score", "raw_option_jsonb", ... } ],
  "hotel_options":  [ { "property_name", "total_rate", "nightly_rate",
                         "overall_rating", "property_token", "amenities_jsonb",
                         "free_cancellation", "ranking_score", "raw_option_jsonb", ... } ],
  "warnings": [],
  "meta": { "intent", "timings", "serpapi_signals", ... },
  "registration": {
    "destination", "departure_city", "trip_start_iso", "trip_end_iso",
    "total_price", "within_budget", "tier", "quality_score",
    "price_breakdown", "normalized_search", ...
  }
}
```

See [`CAMBIOS_CAMPOS.md`](CAMBIOS_CAMPOS.md) for the full field mapping to the database schema.

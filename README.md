# TravelOS — AI Travel Agent

LangGraph + SerpAPI agent that converts a travel request (structured JSON form or natural language) into a ranked package of flight and hotel options, aligned to the production database schema.

Built as the AI backend for the TravelOS project. Stateless, single-shot, ready to wrap in a FastAPI service.

---

## What it does

1. Accepts a `TravelRequest` JSON (from the frontend form) and/or a natural-language string
2. Parses origin, destination, dates, travelers, budget, and intent using a 3-stage pipeline (heuristic → LLM → merge)
3. Resolves any city name to its IATA airport code via the LLM
4. Calls SerpAPI (Google Flights + Google Hotels) in parallel
5. Returns a single `TravelQueryOutput` JSON with ranked options and a `registration` block ready for DB insertion

---

## Project structure

```
prototype_agent/
├── travel_graph.py       LangGraph pipeline (parse → search → package)
├── graph_state.py        Pydantic models — TravelRequest, TravelQueryOutput, DB-aligned option models
├── serpapi_tools.py      SerpAPI HTTP wrappers (flights + hotels)
├── run_agent.py          CLI entry point
├── run_agent_test.py     8-case automated test suite
└── requirements.txt      Pinned dependencies

docs/
├── ARCHITECTURE.md       Graph design, parsing pipeline, node reference
├── OUTPUT_SCHEMA.md      Full output schema + DB field mapping (for backend team)
└── BACKEND_INTEGRATION.md  How to call the agent from a backend service

CHANGELOG.md              Version history with all changes
.env.example              Required environment variables
```

---

## Setup

```bash
cd prototype_agent
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
cp ../.env.example .env       # then fill in your API keys
```

### Required environment variables

| Variable | Where to get it |
|---|---|
| `NVIDIA_API_KEY` | [build.nvidia.com](https://build.nvidia.com) |
| `SERPAPI_API_KEY` | [serpapi.com](https://serpapi.com) |

### Optional

| Variable | Default | Description |
|---|---|---|
| `NVIDIA_MODEL` | `nvidia/nemotron-3-super-120b-a12b` | Override the LLM model |
| `MAX_OPTIONS` | `3` | Max flight/hotel options returned (1–10) |
| `INCLUDE_RAW` | `false` | Embed full SerpAPI JSON blobs in output |

---

## Running

### Natural language query

```bash
python run_agent.py "Flights from Mexico City to Madrid on 2026-07-15 returning 2026-07-25, hotel in Madrid"
```

### Structured JSON (frontend form payload)

```bash
python run_agent.py --json-path my_request.json
```

Where `my_request.json` matches the `TravelRequest` schema:

```json
{
  "client_name": "Ana García",
  "client_email": "ana@example.com",
  "departure_city": "Mexico City",
  "destination": "Madrid",
  "start_date": "2026-07-15",
  "end_date": "2026-07-25",
  "travelers": 2,
  "min_budget": 3000,
  "max_budget": 6000,
  "currency": "USD",
  "locale": "es",
  "special_preferences": "Prefiero vuelos directos si es posible."
}
```

### Stdin pipe (for backend subprocess calls)

```bash
echo '{"departure_city": "Bogota", "destination": "Lima", "start_date": "2026-09-10", "end_date": "2026-09-17"}' | python run_agent.py
```

### Run the test suite

```bash
python run_agent_test.py
```

---

## Output shape (abbreviated)

```json
{
  "summary": "Found 3 flight option(s). Found 3 hotel option(s).",
  "flight_options": [
    {
      "title": "Round trip option",
      "total_price": 2701.0,
      "currency": "USD",
      "total_duration_min": 835,
      "layover_count": 1,
      "airline": "Air Canada",
      "departure_token": "...",
      "segments_jsonb": [...],
      "emissions_kg": 1115.0,
      "ranking_score": 1.0
    }
  ],
  "hotel_options": [...],
  "warnings": [],
  "meta": {
    "intent": "both",
    "timings": { "flight_ms": 1413, "hotel_ms": 3547 }
  },
  "registration": {
    "origin": "MEX",
    "destination": "MAD",
    "total_price": 2701.0,
    "within_budget": true,
    "tier": "budget"
  }
}
```

Full schema and DB field mapping → [docs/OUTPUT_SCHEMA.md](docs/OUTPUT_SCHEMA.md)

---

## Documentation

| Doc | Audience | Contents |
|---|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Dev team | Graph nodes, parsing pipeline, IATA resolution, intent detection |
| [docs/OUTPUT_SCHEMA.md](docs/OUTPUT_SCHEMA.md) | Backend + DB teams | Every output field, DB table mapping, integration notes |
| [docs/BACKEND_INTEGRATION.md](docs/BACKEND_INTEGRATION.md) | Backend team | How to call the agent, recommended flow, what's needed next |
| [CHANGELOG.md](CHANGELOG.md) | Everyone | Version history |

---

## What's next before production

The agent logic is complete. The remaining step before backend connection is a **FastAPI HTTP wrapper** — a thin service that accepts POST requests and calls `graph.invoke()`. See [docs/BACKEND_INTEGRATION.md](docs/BACKEND_INTEGRATION.md) for details.

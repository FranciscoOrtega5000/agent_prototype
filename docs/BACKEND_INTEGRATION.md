# Backend Integration Guide

How to connect the TravelOS agent service to your backend.

---

## Current interface

The agent runs as a **CLI process**. For backend integration it must be wrapped in an HTTP service. The recommended approach is a thin FastAPI layer (see below).

### Direct CLI call (subprocess)

The backend can call the agent as a subprocess and parse stdout:

```bash
echo '{"departure_city": "Mexico City", "destination": "Madrid", ...}' | python run_agent.py
```

**Not recommended for production** — no connection pooling, no error signaling via HTTP status codes, harder to scale.

---

## Recommended: FastAPI wrapper

A `POST /search` endpoint that accepts `TravelRequest` and returns `TravelQueryOutput`:

```python
from fastapi import FastAPI, HTTPException
from graph_state import TravelRequest, TravelQueryOutput
from travel_graph import build_travel_graph

app = FastAPI()
graph = build_travel_graph()   # built once at startup

@app.post("/search", response_model=TravelQueryOutput)
def search(req: TravelRequest) -> TravelQueryOutput:
    inputs = {
        "travel_request": req,
        "user_query": req.special_preferences or "",
        "package_mode": True,
        "output_config": {"include_raw": False, "max_options": 3},
    }
    result = graph.invoke(inputs)
    output = result.get("output")
    if not isinstance(output, TravelQueryOutput):
        raise HTTPException(status_code=500, detail="Agent produced no output")
    return output
```

This is the **next step** before the backend team can connect. The agent code itself is ready.

---

## Request schema — TravelRequest

```json
{
  "client_name":        "string | null",
  "client_email":       "string | null",
  "departure_city":     "string | null  — city name, e.g. 'Mexico City'",
  "destination":        "string | null  — city name, e.g. 'Madrid'",
  "start_date":         "date | null    — YYYY-MM-DD or DD/MM/YYYY",
  "end_date":           "date | null    — YYYY-MM-DD or DD/MM/YYYY",
  "travelers":          "string | int | null  — e.g. 2 or '2 Adults'",
  "min_budget":         "float | null",
  "max_budget":         "float | null",
  "currency":           "string | null  — ISO code, e.g. 'USD', 'EUR', 'MXN'",
  "locale":             "string | null  — 'en' or 'es' for language hints",
  "special_preferences":"string | null  — natural language preferences"
}
```

All fields are optional. Minimum viable request:

```json
{
  "departure_city": "Bogota",
  "destination": "Lima",
  "start_date": "2026-09-10",
  "end_date": "2026-09-17"
}
```

---

## Intent rules

| Condition | Result |
|---|---|
| Both `departure_city` and `destination` present | Searches **both** flights and hotels |
| `departure_city` null + `destination` present | Hotel-only search |
| `end_date` null | One-way flight; hotel search skipped |
| `special_preferences` contains "solo el vuelo" / "ya tengo hotel" | Flight-only |
| `special_preferences` contains "solo el hotel" / "ya tengo vuelo" | Hotel-only |

Flight preferences like "round trip", "economy class", "vuelo de ida y vuelta" do **not** suppress hotel search.

---

## Output contract

See [OUTPUT_SCHEMA.md](OUTPUT_SCHEMA.md) for the full field reference.

Key points for the backend:

- `registration.quote_request_id` is always `null` — the backend assigns it after inserting `QUOTE_REQUESTS`
- `flight_options` and `hotel_options` are empty lists `[]` when no results (never null)
- `warnings` contains user-readable strings for any non-fatal issues (SerpAPI errors, missing fields)
- `serpapi_signals` in `meta` has non-null values when SerpAPI returned an HTTP or API error
- `price_breakdown` is `null` when no prices were found

---

## Recommended backend flow

```
1. Frontend  POST /quote-requests  →  Backend
2. Backend   INSERT INTO quote_requests, get quote_request_id
3. Backend   POST /search (agent API) with TravelRequest payload
4. Agent     returns TravelQueryOutput
5. Backend   INSERT INTO flight_options   (from flight_options[])
6. Backend   INSERT INTO hotel_options    (from hotel_options[])
7. Backend   INSERT INTO packages         (from registration.*)
8. Backend   UPDATE quote_requests SET status='complete'
9. Backend   return structured response to Frontend
```

The `registration.normalized_search` block contains the exact IATA codes and dates used in the API calls — useful to store in `QUOTE_REQUESTS` for re-running searches.

---

## Environment variables

Must be set in the service environment (not committed to source):

```bash
NVIDIA_API_KEY=nvapi_...
SERPAPI_API_KEY=...
```

Optional tuning:

```bash
NVIDIA_MODEL=nvidia/nemotron-3-super-120b-a12b
MAX_OPTIONS=3         # 1–10
INCLUDE_RAW=false     # true to embed full SerpAPI JSON blobs
```

---

## Error handling

| Scenario | Agent behaviour |
|---|---|
| SerpAPI HTTP error | Error string in `warnings`; `flight_options` or `hotel_options` is `[]` |
| SerpAPI API error (e.g. invalid route) | `"Google Flights hasn't returned any results"` in `warnings` |
| LLM unavailable | Falls back to heuristic-only parsing; `warnings` contains a note |
| Missing required fields (no destination, no dates) | Recorded in `warnings`; agent returns empty options rather than crashing |
| Malformed TravelRequest JSON | Pydantic validation error — FastAPI wrapper returns 422 |

---

## What's still needed before production

| Item | Owner | Priority |
|---|---|---|
| FastAPI wrapper service | Backend / Agent team | P0 — blocks all integration |
| Request ID / tracing header | Backend | P0 — needed for debugging |
| Structured logging (JSON format) | Agent team | P1 |
| Rate limiting for SerpAPI (60 req/min) | Backend | P1 |
| `try/except` around `TravelRequest.model_validate()` in `run_agent.py` | Agent team | P1 |
| SERPAPI_API_KEY: change `os.environ[]` to `.get()` | Agent team | P1 |
| Lock file for reproducible installs | Agent team | P2 |
| Response caching for identical queries | Backend | P2 |

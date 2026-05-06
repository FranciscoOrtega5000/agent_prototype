# Architecture — LangGraph Travel Agent

## Overview

The agent is a **stateless, single-shot LangGraph `StateGraph`** that:
1. Parses a travel request (structured form and/or natural language)
2. Calls SerpAPI (Google Flights / Google Hotels)
3. Returns a structured `TravelQueryOutput` aligned to the production DB schema

Every invocation is independent — no conversation memory, no checkpoints. Results are persisted by the backend, not the agent.

---

## Graph nodes

```
START
  └─► llm_parser_planner
        └─► input_guard
              ├─► flight_tool_node ──► [hotel_tool_node] ──► response_summarizer
              ├─► hotel_tool_node ──────────────────────────► response_summarizer
              └─► response_summarizer  (if both tools blocked)
                    └─► llm_response_writer
                          └─► output_validate
                                └─► END
```

### `llm_parser_planner`
- Builds a composite text from the `TravelRequest` form + `user_query` string
- Runs heuristic parser (regex + dateparser) for dates, airport codes, intent
- Optionally calls LLM (NVIDIA NIM) for structured `ParsedIntentPlan` output
- Merges LLM + heuristic results (form fields always win)
- Applies NL date backfill from `special_preferences`
- Respects explicit intent (flight-only / hotel-only) even in package mode
- Normalises origin/destination to IATA codes via lookup map (65+ cities)

### `input_guard`
- Records any missing required fields into `warnings`
- Does not block — routes to whatever tools are possible

### `flight_tool_node` / `hotel_tool_node`
- Calls SerpAPI via `search_google_flights` / `search_google_hotels`
- Appends API errors to `warnings` instead of crashing
- Flight node: retry with normalised 3-letter codes if initial call returns empty

### `response_summarizer`
- Maps SerpAPI results to `FlightOption` / `HotelOption` models (DB-aligned fields)
- Computes package-level fields: `total_price`, `within_budget`, `tier`, `quality_score`, `price_breakdown`
- Builds `PackageRegistration` snapshot for backend persistence

### `llm_response_writer`
- Optionally rewrites the one-line `summary` for a cleaner read
- Skipped if LLM unavailable or no results found

### `output_validate`
- Final Pydantic validation of `TravelQueryOutput`
- Fallback to empty output with warnings on any error

---

## Pydantic contracts

| Model | Purpose |
|---|---|
| `TravelRequest` | UI/backend form input — client info, destination, dates, budget, preferences |
| `TravelQueryInput` | Internal tool parameters after parsing |
| `ParsedIntentPlan` | Intermediate planner state |
| `FlightOption` | Single flight result → `FLIGHT_OPTIONS` table |
| `HotelOption` | Single hotel result → `HOTEL_OPTIONS` table |
| `PackageRegistration` | Persistence snapshot → `PACKAGES` + `QUOTE_REQUESTS` |
| `TravelQueryOutput` | Final output contract |

Full field-change reference: [`CAMBIOS_CAMPOS.md`](../CAMBIOS_CAMPOS.md)

---

## Input modes

```python
# 1. Pure natural language
{"user_query": "Flights MEX to CDG on 2026-07-15 returning 2026-07-30, hotel in Paris"}

# 2. Structured form (simulates frontend POST body)
{"travel_request": {"destination": "Paris, France", "departure_city": "New York",
                    "start_date": "2026-07-15", "end_date": "2026-07-30",
                    "travelers": "2 Adults", "max_budget": 10000}}

# 3. Hybrid — form fields + NL dates in special_preferences
{"travel_request": {"destination": "Ibiza, Spain", "departure_city": "Mexico City",
                    "special_preferences": "Travel August 10-18 2026, boutique hotel near beach"}}
```

---

## Output sizing

| Env var | Default | Effect |
|---|---|---|
| `MAX_OPTIONS` | `3` | Max flight/hotel options returned (cap 10) |
| `INCLUDE_RAW` | `false` | Embed full SerpAPI JSON per option in `raw_option_jsonb` |

---

## Backend integration notes

The agent outputs `null` for all FK fields — the backend assigns them after insertion:

```
quote_request_id    -> set after INSERT INTO quote_requests
job_id              -> set after INSERT INTO quote_jobs
flight_option_id    -> set after INSERT INTO flight_options
hotel_option_id     -> set after INSERT INTO hotel_options
```

`package_snapshot_jsonb` in `PACKAGES` can be built by serializing the full `TravelQueryOutput` JSON.
`rationale_text` in `PACKAGES` maps to the agent `summary` field.

Recommended backend flow:
```
Frontend POST /quote-requests
  -> Backend inserts QUOTE_REQUESTS, gets quote_request_id
  -> Backend invokes agent with payload
  -> Agent returns TravelQueryOutput
  -> Backend inserts FLIGHT_OPTIONS, HOTEL_OPTIONS, PACKAGES
  -> Backend returns result to frontend
```

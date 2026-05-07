# Architecture — TravelOS AI Agent

## Overview

The agent is a **stateless, single-shot LangGraph `StateGraph`** that converts a travel request into a structured JSON package.

Every invocation is fully independent — no conversation memory, no checkpoints. Results are returned to the caller; persistence is the backend's responsibility.

---

## Graph topology

```
START
  └─► llm_parser_planner
        └─► input_guard
              ├─► flight_tool_node ──┐
              └─► hotel_tool_node ───┴─► response_summarizer
                                           └─► llm_response_writer
                                                 └─► output_validate
                                                       └─► END
```

`flight_tool_node` and `hotel_tool_node` run **in parallel**. Each self-gates by checking `tool_plan` in state and returns `{}` immediately if not needed. LangGraph joins both at `response_summarizer`.

---

## Node reference

### `llm_parser_planner`

The core parsing stage. Runs three sub-steps and merges results:

**1. Heuristic parse** (`_heuristic_plan`)
- Extracts ISO dates via regex
- Falls back to `dateparser` for natural-language dates (English + Spanish)
- Detects `IATA to IATA` patterns (e.g. "JFK to CDG")
- Extracts origin/destination via `from X to Y` regex
- Detects intent from explicit "flight only" / "hotel only" / "solo el vuelo" phrases

**2. LLM parse** (`_llm_plan`)
- Sends composite query to NVIDIA NIM (`ChatNVIDIA`) with structured output schema
- Prompt instructs the LLM to:
  - Always output IATA airport codes for origin/destination
  - Default intent to `"both"` unless user explicitly requests single-tool
  - Treat flight preferences ("round trip", "economy", "vuelo de ida y vuelta") as preferences, not intent signals
- Returns `ParsedIntentPlan` or `None` if LLM unavailable

**3. Merge** (`_merge_plans`)
- LLM values take priority over heuristic where present
- Heuristic fills gaps (missing dates, missing origin/destination)
- Structured `TravelRequest` fields then overlay the merged plan

**4. IATA resolution**
- `_overlay_structured`: does not overwrite a valid IATA code already resolved by the LLM with a raw city name from the form
- `_resolve_iata_if_needed`: if origin/destination are still city names after merging, calls LLM again with a targeted prompt (`"Output only the 3-letter IATA code for: {city}"`)
- `_NOT_IATA` guard: rejects known non-airport 3-letter strings (currency codes: USD, EUR, MXN, etc.)

---

### `input_guard`

Records missing required fields into `warnings`. Does not block execution — routes to whichever tools have enough data.

---

### `flight_tool_node`

- Builds SerpAPI `google_flights` payload from parsed plan
- Calls `DefaultFlightToolRunner.run()` → `search_google_flights` tool
- Appends HTTP or API errors to `flight_warnings`
- No retry logic — errors are surfaced cleanly

---

### `hotel_tool_node`

- Builds SerpAPI `google_hotels` payload from parsed plan
- Calls `DefaultHotelToolRunner.run()` → `search_google_hotels` tool
- Appends errors to `hotel_warnings`

---

### `response_summarizer`

- Maps SerpAPI results to `FlightOption` / `HotelOption` Pydantic models
- Computes package-level fields: `total_price`, `within_budget`, `tier`, `quality_score`, `price_breakdown`
- Builds `PackageRegistration` snapshot for backend persistence
- Merges `warnings`, `flight_warnings`, `hotel_warnings` into a single list

---

### `llm_response_writer`

- Rewrites the one-line `summary` using the LLM for a cleaner sentence
- Skipped if LLM unavailable or no results found

---

### `output_validate`

- Runs `TravelQueryOutput.model_validate()` on the full output
- Fallback to empty output with warnings if validation fails

---

## Intent detection

Intent controls which tools run. Rules (in priority order):

| Signal | Intent |
|---|---|
| Explicit "flight only" / "solo el vuelo" / "ya tengo hotel" | `flight` |
| Explicit "hotel only" / "solo el hotel" / "ya tengo vuelo" | `hotel` |
| Both departure city and destination present, no explicit override | `both` |
| Anything else | `both` (default) |

Flight preferences ("round trip", "economy class", "direct", "vuelo de ida y vuelta") do **not** change intent. Only explicit "I only need X" language does.

---

## IATA resolution pipeline

```
Input city name (e.g. "Barcelona")
  │
  ├─► LLM parser prompt → "Barcelona → BCN" (primary path)
  │     └─► stored in ParsedIntentPlan.origin/destination
  │
  ├─► _overlay_structured guard → skips overwriting BCN with "Barcelona"
  │
  └─► _resolve_iata_if_needed → no-op if already "BCN"
        └─► fallback: targeted LLM call if still a city name
              └─► _NOT_IATA guard → rejects USD, EUR, MXN etc.
```

---

## Pydantic models

| Model | File | Purpose |
|---|---|---|
| `TravelRequest` | `graph_state.py` | Frontend form input |
| `TravelQueryInput` | `graph_state.py` | Internal tool parameters after parsing |
| `ParsedIntentPlan` | `graph_state.py` | Intermediate planner state |
| `FlightOption` | `graph_state.py` | Single flight result → `FLIGHT_OPTIONS` table |
| `HotelOption` | `graph_state.py` | Single hotel result → `HOTEL_OPTIONS` table |
| `PackageRegistration` | `graph_state.py` | Persistence snapshot → `PACKAGES` + `QUOTE_REQUESTS` |
| `TravelQueryOutput` | `graph_state.py` | Final output contract |
| `TravelGraphState` | `graph_state.py` | LangGraph `TypedDict` state |

---

## Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `NVIDIA_API_KEY` | Yes | — | NVIDIA NIM API key |
| `SERPAPI_API_KEY` | Yes | — | SerpAPI key |
| `NVIDIA_MODEL` | No | `nvidia/nemotron-3-super-120b-a12b` | LLM model ID |
| `MAX_OPTIONS` | No | `3` | Max results per tool (1–10) |
| `INCLUDE_RAW` | No | `false` | Embed full SerpAPI blobs in `raw_option_jsonb` |

---

## Degraded mode

If `NVIDIA_API_KEY` is missing or the LLM init fails:
- `llm_parser = None`, `_LLM_AVAILABLE = False`
- A `WARNING` is logged at startup
- Parsing falls back to heuristic-only (regex + dateparser)
- IATA resolution falls back to passing city names directly to SerpAPI
- All other graph nodes run normally

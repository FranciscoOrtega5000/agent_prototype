# Travel helper — explained simply

This folder is a **program** that reads what you type (in plain English, or a JSON form) and answers with a **fixed JSON shape** so a website or another service can show flights and hotels cleanly.

You do **not** need to know LangGraph to understand what it does.

## What problem does it solve?

Someone submits a travel form or types something like:

> "Find a flight from Guadalajara to Tokyo on July 25 and a hotel in Tokyo until the 28th."

The program should:

1. Figure out what they want (flights, hotels, or both).
2. Extract the places and dates (from the form, from the text, or from both combined).
3. Call **real search APIs** (SerpAPI → Google Flights / Google Hotels style results).
4. Return a **small, predictable JSON** your app can trust and save to the database.

## What are the moving parts?

Think of four layers:

### 1) Your input

Either a **JSON form** (like what the frontend sends) or **plain text**. The program extracts:

- Cities or airport codes (knows 65+ city → IATA mappings)
- Dates (ISO format, dd/mm/yyyy, or natural language like "August 10–18")
- Whether you asked for flights, hotels, or both
- Budget, number of travelers, currency, preferences

### 2) A checklist before making API calls

If important details are missing (no destination, no dates), it records **warnings** instead of pretending it searched correctly. It never crashes — it just reports what it could and couldn't do.

### 3) External search (SerpAPI)

When it has enough information, it calls SerpAPI:

- **Flights** → Google Flights results
- **Hotels** → Google Hotels results

If a call fails, it **captures the error in warnings** instead of crashing the whole run.

### 4) A neat answer package

Everything is packed into **one JSON object**:

- **summary** — one sentence a human can read
- **flight_options** — ranked list with price, duration, stops, airline, departure token
- **hotel_options** — ranked list with name, rate, rating, amenities, free cancellation
- **warnings** — what went wrong or what is missing
- **meta** — timing, intent detected, SerpAPI signals
- **registration** — structured snapshot ready to save to the database (total price, budget fit, tier, quality score)

## "Compact" vs "detailed" output

Same JSON shape — you only control **how big** it is via environment variables:

```bash
# Compact (default) — 3 options per type, no raw API blobs
python run_agent.py "Your question"

# Detailed — 5 options, full SerpAPI JSON embedded
MAX_OPTIONS=5 INCLUDE_RAW=true python run_agent.py "Your question"
```

## What is LangGraph, in one analogy?

A **flowchart**:

```
Start → parse request → check fields → search flights → search hotels → pack answer → Done
```

LangGraph is the library that runs that flowchart as code. Each box is a **step** ("node"), and lines show what happens next. Every run is completely independent — no memory between runs.

## What we built (story so far)

1. **First prototype** — Tested Apify scrapers and a LangChain agent loop.
2. **SerpAPI** — Switched to SerpAPI for faster, more predictable HTTP responses.
3. **LangGraph + Pydantic contracts** — Replaced free-form agent chatter with a fixed pipeline and typed models so the backend knows exactly what JSON to expect.
4. **Robust parsing** — Added city→IATA lookup, date year-range validation, budget-label sanitization, explicit intent detection, and structured form overlay so the agent works reliably with both NL queries and frontend form payloads.
5. **DB-aligned output** — Renamed and added fields to match the production schema (`FLIGHT_OPTIONS`, `HOTEL_OPTIONS`, `PACKAGES`, `QUOTE_REQUESTS`).

## How to try it

See [`README.md`](README.md) for full setup. Then:

```bash
# Natural language
python run_agent.py "Flights from MEX to CDG on 2026-07-15 returning 2026-07-30, and hotel in Paris"

# Structured form (JSON file)
python run_agent.py --json-path my_request.json

# Run all 8 automated tests
python run_agent_test.py
```

# Changelog

## [0.3.0] — 2026-05-06

Production audit pass. Bug fixes, parallel graph execution, observability improvements, and documentation consolidation.

---

### Fixed

| Bug | File | Fix |
|---|---|---|
| Hotel `nightly_rate` / `total_rate` always `null` | `travel_graph.py` | Read `extracted_lowest` (numeric) instead of `lowest` (string like `"$105"`) from SerpAPI |
| `emissions_kg` stored in grams — 1000× too large | `travel_graph.py` | Divide `carbon_emissions.this_flight` by 1000 before storing |
| Default currency `"MXN"` for queries with no explicit currency | `travel_graph.py` | Changed fallback from `"MXN"` to `"USD"` |
| `state["parsed_input"]` raises `KeyError` if parser node fails | `travel_graph.py` | Changed to `state.get("parsed_input")` with `None` guard in both tool nodes |
| `cp .env.example .env` fails — file is in repo root, not `prototype_agent/` | `prototype_agent/README.md` | Fixed path to `cp ../.env.example .env` |

---

### Changed

#### Parallel graph execution (`travel_graph.py`)

Flight and hotel searches now run **simultaneously** instead of sequentially. For `intent=both` queries this halves the API wait time.

- Removed `_route_from_guard()` and `_post_flight_edge()` — sequential conditional routing functions, no longer needed
- `build_travel_graph()` now fans out from `input_guard` to both `flight_tool_node` and `hotel_tool_node` via direct edges; LangGraph joins at `response_summarizer` once both complete
- Each tool node self-gates via `tool_plan` check and returns `{}` immediately if not in plan
- Parallel nodes write to dedicated state keys (`flight_warnings`, `hotel_warnings`) instead of the shared `warnings` key, avoiding LangGraph channel conflicts; `response_summarizer` merges all three at start

#### LLM initialization observability (`travel_graph.py`)

- Added `import logging` and module-level `logger = logging.getLogger(__name__)`
- LLM init failure now logs `WARNING` with exception type + message instead of silently setting `llm_parser = None`
- Added `_LLM_AVAILABLE` module flag so operators can detect degraded mode at startup

#### State schema (`graph_state.py`)

| New field | Type | Purpose |
|---|---|---|
| `flight_warnings` | `list[str]` | Warnings emitted by the flight tool node (parallel-safe) |
| `hotel_warnings` | `list[str]` | Warnings emitted by the hotel tool node (parallel-safe) |

---

### Added

| Item | Description |
|---|---|
| `prototype_agent/docs/examples/example_runs.md` | Verified input + output JSON for both query modes (NL and structured), including bug-fix confirmation |
| `prototype_agent/docs/examples/input_q1_nl.json` | Reference NL query input (Paris, Jul 2026) |
| `prototype_agent/docs/examples/input_q2_structured.json` | Reference structured query input (Tokyo, Oct 2026) |
| `prototype_agent/docs/examples/output_q1_nl.json` | Captured SerpAPI output for Q1 |
| `prototype_agent/docs/examples/output_q2_structured.json` | Captured SerpAPI output for Q2 |
| Canonical JSON output spec | Added to `docs/CAMBIOS_CAMPOS.md` — full annotated example, envelope field mappings, DB action items for backend and DB teams |

---

### Reorganized

| Before | After |
|---|---|
| `prototype_agent/CAMBIOS_CAMPOS.md` | `prototype_agent/docs/CAMBIOS_CAMPOS.md` |
| `prototype_agent/SIMPLE_GUIDE.md` | `prototype_agent/docs/SIMPLE_GUIDE.md` |

---

## [0.2.0] — 2026-05-06

Complete stabilisation pass. Agent now works reliably with structured JSON input (simulating the frontend form), pure natural-language queries, and hybrid combinations. Output fields aligned to the production DB schema.

---

### Removed

| Item | Reason |
|---|---|
| `prototype_agent/booking_tool.py` | Apify/Booking.com scraper — never imported, never used |
| `prototype_agent/skyscanner_tool.py` | Apify/Skyscanner scraper — never imported, never used |
| `APIFY_API_TOKEN` from `.env` | No longer needed |
| `LANGGRAPH_USE_CHECKPOINT` env var | Checkpoints removed; agent is always stateless one-shot |
| `LANGGRAPH_CHECKPOINT_DB` env var | Same |
| `LANGGRAPH_THREAD_ID` env var | Same |
| `langgraph-checkpoint-sqlite` dependency | Same |
| `highlights` field on `FlightOption` | Not in DB schema; data moved to `raw_option_jsonb` |
| `highlights` field on `HotelOption` | Same |

---

### Fixed — parsing bugs (root cause of "only works with one query")

| Bug | Fix |
|---|---|
| Hotel dates only set when "hotel" appeared in the query | `hc_in/hc_out` now always populated from trip dates; intent detection controls whether hotels are searched, not date assignment |
| `hotel_city` never extracted for non-"hotel in X from DATE" phrasings | Already fell back to `destination` in `_heuristic_plan`; confirmed and kept |
| Destination extraction grabbed full sentence for queries with multiple "to" occurrences | `_extract_between` now picks the shortest match ≤ 4 words across all regex matches |
| LLM parser failures were completely silent | Now emits a warning when LLM is available but returns no result |
| Budget value (e.g. `8000`) was parsed as a year by `dateparser` | Budget line in composite query labelled `"USD 8000"` to prevent numeric year misparse |
| Dates outside 2020–2040 accepted silently | Added year-range guard to both ISO regex path and `dateparser` path |
| Return date only set when "return"/"round trip" in query | Added Spanish signals: `"vuelta"`, `"ida y vuelta"` |
| Explicit flight-only / hotel-only intent from NL overridden by `package_mode` | `_apply_package_invariants` now preserves single-tool intent when set explicitly |
| City names like "New York, USA" → `"New"` (invalid IATA) | Replaced with `_CITY_TO_IATA` lookup map (65+ cities) + skip list for common English words |

---

### Changed — Pydantic models (`graph_state.py`)

#### `FlightOption` → aligns to `FLIGHT_OPTIONS` table

| Before | After | Note |
|---|---|---|
| `total_price: str` | `total_price: float \| None` | Numeric for DB storage |
| `duration: str` | `total_duration_min: int \| None` | Renamed; SerpAPI already returns minutes |
| `stops: int` | `layover_count: int \| None` | Renamed to match column |
| `raw: dict` | `raw_option_jsonb: dict` | Renamed to match column |
| _(missing)_ | `departure_token: str \| None` | SerpAPI token for return-leg lookups |
| _(missing)_ | `segments_jsonb: list \| None` | Flight legs / segments |
| _(missing)_ | `emissions_kg: float \| None` | CO₂ from `carbon_emissions.this_flight` |
| _(missing)_ | `ranking_score: float \| None` | `1 / (rank + 1)` for UI sorting |

#### `HotelOption` → aligns to `HOTEL_OPTIONS` table

| Before | After | Note |
|---|---|---|
| `name: str` | `property_name: str` | Renamed |
| `total_price: str` | `total_rate: float \| None` | Renamed + numeric |
| `nightly_price: str` | `nightly_rate: float \| None` | Renamed + numeric |
| `rating: float` | `overall_rating: float \| None` | Renamed |
| `raw: dict` | `raw_option_jsonb: dict` | Renamed |
| _(missing)_ | `property_token: str \| None` | SerpAPI property token |
| _(missing)_ | `location_rating: float \| None` | From SerpAPI |
| _(missing)_ | `review_count: int \| None` | From SerpAPI `reviews` |
| _(missing)_ | `amenities_jsonb: list \| None` | From SerpAPI |
| _(missing)_ | `free_cancellation: bool \| None` | From SerpAPI |
| _(missing)_ | `ranking_score: float \| None` | `1 / (rank + 1)` |

#### `PackageRegistration` → aligns to `PACKAGES` + `QUOTE_REQUESTS`

| Added field | Type | Note |
|---|---|---|
| `quote_request_id` | `str \| None` | FK set by backend post-insert; agent emits `null` |
| `total_price` | `float \| None` | Combined flight + hotel price |
| `currency` | `str \| None` | Currency of total |
| `within_budget` | `bool \| None` | `total_price <= max_budget` |
| `tier` | `str \| None` | `"budget"` / `"standard"` / `"premium"` |
| `quality_score` | `float \| None` | Average `ranking_score` of selected options |
| `price_breakdown` | `dict \| None` | `{flight, hotel, total, currency}` |

---

### Changed — mapper functions (`travel_graph.py`)

- `_to_flight_options`: extracts `departure_token`, `segments_jsonb`, `emissions_kg`, `total_duration_min` (int), `layover_count`, `total_price` (float), `ranking_score`
- `_to_hotel_options`: extracts `property_token`, `overall_rating`, `location_rating`, `review_count`, `amenities_jsonb`, `free_cancellation`, `nightly_rate` / `total_rate` (float), `ranking_score`
- `_summarizer_node`: computes `total_price`, `within_budget`, `tier`, `quality_score`, `price_breakdown` and writes them into `PackageRegistration`
- `build_travel_graph()`: removed `checkpointer` parameter; always compiles stateless

---

### Added

| File | Description |
|---|---|
| `prototype_agent/run_agent_test.py` | 8-case test suite (pure NL, structured JSON, hybrid, flight-only, hotel-only, no-dates fallback) |
| `prototype_agent/CAMBIOS_CAMPOS.md` | Full field-change reference in Spanish for the backend/DB team |
| `README.md` (repo root) | Top-level project overview |
| `.gitignore` (repo root) | Moved from `prototype_agent/`; added `*.sqlite`, `*.db`, `test_*.json` |
| `.env.example` (repo root) | Moved from `prototype_agent/`; removed checkpoint env vars |
| `prototype_agent/.venv/` | Local virtual environment (gitignored) |

---

### Updated docs

| File | What changed |
|---|---|
| `prototype_agent/README.md` | Full rewrite: new input modes, JSON examples, test runner, output shape |
| `prototype_agent/SIMPLE_GUIDE.md` | Removed Apify / checkpoint references; added city→IATA and NL date parsing notes |
| `prototype_agent/docs/langgraph_migration.md` | Full rewrite: current architecture, no stale checkpoint content |

---

## [0.1.0] — initial prototype

- LangChain → LangGraph migration
- SerpAPI integration (Google Flights + Google Hotels)
- Pydantic contracts (`TravelRequest`, `TravelQueryOutput`)
- Heuristic + optional LLM intent parser
- Single-shot CLI (`run_agent.py`)

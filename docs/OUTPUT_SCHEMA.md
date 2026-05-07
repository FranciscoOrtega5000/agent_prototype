# Output Schema — TravelQueryOutput

Full reference for the JSON the agent emits. Every `null` value is valid; the backend must tolerate nullable fields.

---

## Top-level envelope

```json
{
  "summary":        "string — one sentence describing what was found",
  "flight_options": [...],
  "hotel_options":  [...],
  "warnings":       ["string", ...],
  "meta":           { ... },
  "registration":   { ... }
}
```

| Field | Type | DB destination | Notes |
|---|---|---|---|
| `summary` | `str` | `rationale_text` in `PACKAGES` | Written by LLM writer; falls back to template sentence |
| `flight_options` | `list[FlightOption]` | `FLIGHT_OPTIONS` table | Empty list when no results or flight not in plan |
| `hotel_options` | `list[HotelOption]` | `HOTEL_OPTIONS` table | Empty list when no results or hotel not in plan |
| `warnings` | `list[str]` | `package_snapshot_jsonb` | SerpAPI errors, missing fields, parser fallbacks |
| `meta` | `dict` | `package_snapshot_jsonb` | Execution metadata — see below |
| `registration` | `PackageRegistration \| null` | `PACKAGES` + `QUOTE_REQUESTS` | Null only if no TravelRequest was provided |

---

## FlightOption → `FLIGHT_OPTIONS` table

```json
{
  "title":              "Round trip option",
  "total_price":        2701.0,
  "currency":           "USD",
  "total_duration_min": 835,
  "layover_count":      1,
  "airline":            "Air Canada",
  "departure_token":    "WyJDalJJ...",
  "segments_jsonb":     [...],
  "emissions_kg":       1115.0,
  "ranking_score":      1.0,
  "raw_option_jsonb":   {}
}
```

| Field | Type | DB column | Notes |
|---|---|---|---|
| `title` | `str` | display only | Always `"Round trip option"` or `"Flight option"` |
| `total_price` | `float \| null` | `total_price` | Per-person price from SerpAPI |
| `currency` | `str \| null` | `currency` | From search parameters |
| `total_duration_min` | `int \| null` | `total_duration_min` | Total minutes including layovers |
| `layover_count` | `int \| null` | `layover_count` | Number of stops |
| `airline` | `str \| null` | in `segments_jsonb` | First leg airline; also in segments |
| `departure_token` | `str \| null` | `departure_token` | SerpAPI token for return-leg lookup |
| `segments_jsonb` | `list \| null` | `segments_jsonb` | Full leg data: airports, times, flight numbers |
| `emissions_kg` | `float \| null` | `emissions_kg` | CO₂ in kg (converted from grams) |
| `ranking_score` | `float \| null` | `ranking_score` | `1 / position` for UI sorting |
| `raw_option_jsonb` | `dict` | `raw_option_jsonb` | Full SerpAPI blob; empty `{}` unless `INCLUDE_RAW=true` |

---

## HotelOption → `HOTEL_OPTIONS` table

```json
{
  "property_name":    "YOTEL New York Times Square",
  "total_rate":       1189.0,
  "nightly_rate":     198.0,
  "currency":         "USD",
  "overall_rating":   3.9,
  "location":         "Snug rooms in a hip hotel near Times Square.",
  "property_token":   "ChcIiv7q...",
  "location_rating":  4.3,
  "review_count":     9540,
  "amenities_jsonb":  ["Free Wi-Fi", "Fitness center", "Restaurant"],
  "free_cancellation": null,
  "ranking_score":    0.3333,
  "raw_option_jsonb": {}
}
```

| Field | Type | DB column | Notes |
|---|---|---|---|
| `property_name` | `str` | `property_name` | Hotel display name |
| `total_rate` | `float \| null` | `total_rate` | Total stay cost (all nights) |
| `nightly_rate` | `float \| null` | `nightly_rate` | Per-night lowest rate |
| `currency` | `str \| null` | `currency` | From search parameters |
| `overall_rating` | `float \| null` | `overall_rating` | Guest rating (0–5) |
| `location` | `str \| null` | display only | Short description from SerpAPI |
| `property_token` | `str \| null` | `property_token` | SerpAPI token for deep link |
| `location_rating` | `float \| null` | `location_rating` | Location score from SerpAPI |
| `review_count` | `int \| null` | `review_count` | Number of guest reviews |
| `amenities_jsonb` | `list \| null` | `amenities_jsonb` | String list of amenities |
| `free_cancellation` | `bool \| null` | `free_cancellation` | Null when SerpAPI doesn't specify |
| `ranking_score` | `float \| null` | `ranking_score` | `1 / position` |
| `raw_option_jsonb` | `dict` | `raw_option_jsonb` | Full SerpAPI blob; empty unless `INCLUDE_RAW=true` |

---

## PackageRegistration → `PACKAGES` + `QUOTE_REQUESTS`

```json
{
  "quote_request_id": null,
  "client_name":      "Ana García",
  "client_email":     "ana@example.com",
  "destination":      "Madrid",
  "departure_city":   "Mexico City",
  "trip_start_iso":   "2026-07-15",
  "trip_end_iso":     "2026-07-25",
  "travelers":        "2",
  "min_budget":       3000.0,
  "max_budget":       6000.0,
  "special_preferences": "Prefiero vuelos directos si es posible.",
  "normalized_search": {
    "origin":         "MEX",
    "destination":    "MAD",
    "depart_date":    "2026-07-15",
    "return_date":    "2026-07-25",
    "hotel_city":     "Madrid",
    "hotel_checkin":  "2026-07-15",
    "hotel_checkout": "2026-07-25"
  },
  "total_price":      2701.0,
  "currency":         "USD",
  "within_budget":    true,
  "tier":             "budget",
  "quality_score":    0.6111,
  "price_breakdown": {
    "flight":   2701.0,
    "hotel":    null,
    "total":    2701.0,
    "currency": "USD"
  }
}
```

### `QUOTE_REQUESTS` fields

| Field | Type | DB column | Notes |
|---|---|---|---|
| `quote_request_id` | `str \| null` | `id` | **Set by backend after insert; agent emits null** |
| `client_name` | `str \| null` | `client_name` | From TravelRequest |
| `client_email` | `str \| null` | `client_email` | From TravelRequest |
| `destination` | `str \| null` | `destination_label` | Raw city name from form |
| `departure_city` | `str \| null` | `origin_label` | Raw city name from form |
| `trip_start_iso` | `str \| null` | `depart_date` | YYYY-MM-DD |
| `trip_end_iso` | `str \| null` | `return_date` | YYYY-MM-DD |
| `travelers` | `str \| null` | travelers fields | Raw value from form |
| `min_budget` | `float \| null` | `budget_min` | From form |
| `max_budget` | `float \| null` | `budget_max` | From form |
| `special_preferences` | `str \| null` | `submitted_payload` | Natural language preferences |
| `normalized_search` | `dict` | `normalized_search_jsonb` | Resolved IATA codes + dates used in API calls |

### `PACKAGES` fields

| Field | Type | DB column | Notes |
|---|---|---|---|
| `total_price` | `float \| null` | `total_price` | flight + hotel combined |
| `currency` | `str \| null` | `currency` | Currency of total_price |
| `within_budget` | `bool \| null` | `within_budget` | `total_price <= max_budget` |
| `tier` | `str \| null` | `tier` | `"budget"` (<60%), `"standard"` (60–90%), `"premium"` (>90%) of max_budget |
| `quality_score` | `float \| null` | `quality_score` | Average ranking_score of top flight + hotel |
| `price_breakdown` | `dict \| null` | `price_breakdown_jsonb` | `{flight, hotel, total, currency}` |

---

## meta block

```json
{
  "source":          "langgraph",
  "intent":          "both",
  "composite_query": "...",
  "timings": {
    "flight_ms": 1413,
    "hotel_ms":  3547
  },
  "warnings_count": 0,
  "tool_keys": { "flight": [...], "hotel": [...] },
  "serpapi_signals": {
    "flight_http": null,
    "flight_api":  null,
    "hotel_http":  null,
    "hotel_api":   null
  }
}
```

| Field | Destination | Notes |
|---|---|---|
| `source` | `package_snapshot_jsonb` | Always `"langgraph"` |
| `intent` | `package_snapshot_jsonb` | `"flight"`, `"hotel"`, `"both"`, `"unknown"` |
| `composite_query` | `package_snapshot_jsonb` | Full query text used internally — may contain PII |
| `timings` | `package_snapshot_jsonb` | Per-tool API latency in ms |
| `serpapi_signals` | `package_snapshot_jsonb` | Non-null when SerpAPI returned an error |

---

## Backend action items

| # | Team | Action |
|---|---|---|
| 1 | Backend | Assign `quote_request_id` after inserting `QUOTE_REQUESTS`; pass it back if re-invoking |
| 2 | Backend | `package_snapshot_jsonb` in `PACKAGES` can be built by serializing the full `TravelQueryOutput` JSON |
| 3 | Backend | `rationale_text` in `PACKAGES` maps to `summary` |
| 4 | Backend | `submitted_payload` in `QUOTE_REQUESTS` should be the raw frontend POST body (save before invoking agent) |
| 5 | DB | Consider adding `search_intent (text)` column in `PACKAGES` for analytics on `meta.intent` |
| 6 | DB | `normalized_search_jsonb` in `QUOTE_REQUESTS` is useful for re-running searches |

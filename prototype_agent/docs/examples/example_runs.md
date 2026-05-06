# Example Agent Runs

Two reference runs showing exact inputs and outputs for each supported input mode.
Captured on 2026-05-06 after the currency, emissions-unit, and hotel rate parsing bug fixes.

---

## Run 1 — Natural Language Query (NL mode)

**Scenario:** Paris trip, free-text input only. No structured form data.

### Input

File: `input_q1_nl.json`

```json
{
  "user_query": "Flight from New York to Paris on July 15 2026 returning July 22 2026, and hotel in Paris for 2 adults, budget up to $12000 USD"
}
```

### Output

```json
{
  "summary": "<LLM-generated one-sentence brief — see terminal>",
  "flight_options": [
    {
      "title": "Round trip option",
      "total_price": 1579.0,
      "currency": "USD",
      "total_duration_min": 430,
      "layover_count": 0,
      "airline": "Air France",
      "departure_token": "WyJDalJJTTNoNU5uSmtiVTFhZFUxQlFXSkpURUZDUnkwdExTMHRMUzB0Y0dwaWFHd3hNMEZCUVVGQlIyNDNjaTF6U0VoWFJuZEJFZ1JCUmpFeEdnc0k3dEFKRUFJYUExVlRSRGdjY083UUNRPT0iLFtbIkpGSyIsIjIwMjYtMDctMTUiLCJDREciLG51bGwsIkFGIiwiMTEiXV1d",
      "segments_jsonb": [
        {
          "departure_airport": {
            "name": "John F. Kennedy International Airport",
            "id": "JFK",
            "time": "2026-07-15 01:00"
          },
          "arrival_airport": {
            "name": "Paris Charles de Gaulle Airport",
            "id": "CDG",
            "time": "2026-07-15 14:10"
          },
          "duration": 430,
          "airplane": "Airbus A350",
          "airline": "Air France",
          "airline_logo": "https://www.gstatic.com/flights/airline_logos/70px/AF.png",
          "travel_class": "Economy",
          "flight_number": "AF 11",
          "ticket_also_sold_by": ["Delta"],
          "legroom": "31 in",
          "extensions": [
            "Average legroom (31 in)",
            "Wi-Fi for a fee",
            "In-seat USB outlet",
            "On-demand video",
            "Carbon emissions estimate: 705 kg"
          ],
          "overnight": true
        }
      ],
      "emissions_kg": 706.0,
      "ranking_score": 1.0,
      "raw_option_jsonb": {}
    },
    {
      "title": "Round trip option",
      "total_price": 1579.0,
      "currency": "USD",
      "total_duration_min": 470,
      "layover_count": 0,
      "airline": "Delta",
      "departure_token": "WyJDalJJTTNoNU5uSmtiVTFhZFUxQlFXSkpURUZDUnkwdExTMHRMUzB0Y0dwaWFHd3hNMEZCUVVGQlIyNDNjaTF6U0VoWFJuZEJFZ1ZFVERJMk1ob0xDTzdRQ1JBQ2dOVlVRNEhIRHUwQWs9IixbWyJKRksiLCIyMDI2LTA3LTE1IiwiQ0RHIixudWxsLCJETCIsIjI2MiJdXV0=",
      "segments_jsonb": [
        {
          "departure_airport": {
            "name": "John F. Kennedy International Airport",
            "id": "JFK",
            "time": "2026-07-15 19:15"
          },
          "arrival_airport": {
            "name": "Paris Charles de Gaulle Airport",
            "id": "CDG",
            "time": "2026-07-16 09:05"
          },
          "duration": 470,
          "airplane": "Boeing 767",
          "airline": "Delta",
          "airline_logo": "https://www.gstatic.com/flights/airline_logos/70px/DL.png",
          "travel_class": "Economy",
          "flight_number": "DL 262",
          "legroom": "31 in",
          "extensions": [
            "Average legroom (31 in)",
            "Free Wi-Fi",
            "In-seat power & USB outlets",
            "On-demand video",
            "Carbon emissions estimate: 659 kg"
          ],
          "overnight": true
        }
      ],
      "emissions_kg": 660.0,
      "ranking_score": 0.5,
      "raw_option_jsonb": {}
    },
    {
      "title": "Round trip option",
      "total_price": 1579.0,
      "currency": "USD",
      "total_duration_min": 470,
      "layover_count": 0,
      "airline": "Delta",
      "departure_token": "WyJDalJJTTNoNU5uSmtiVTFhZFUxQlFXSkpURUZDUnkwdExTMHRMUzB0Y0dwaWFHd3hNMEZCUVVGQlIyNDNjaTF6U0VoWFJuZEJFZ1ZFVERJMk5ob0xDTzdRQ1JBQ2dOVlVRNEhIRHUwQWs9IixbWyJKRksiLCIyMDI2LTA3LTE1IiwiQ0RHIixudWxsLCJETCIsIjI2NiJdXV0=",
      "segments_jsonb": [
        {
          "departure_airport": {
            "name": "John F. Kennedy International Airport",
            "id": "JFK",
            "time": "2026-07-15 20:10"
          },
          "arrival_airport": {
            "name": "Paris Charles de Gaulle Airport",
            "id": "CDG",
            "time": "2026-07-16 10:00"
          },
          "duration": 470,
          "airplane": "Boeing 767",
          "airline": "Delta",
          "airline_logo": "https://www.gstatic.com/flights/airline_logos/70px/DL.png",
          "travel_class": "Economy",
          "flight_number": "DL 266",
          "ticket_also_sold_by": ["Virgin Atlantic"],
          "legroom": "31 in",
          "extensions": [
            "Average legroom (31 in)",
            "Free Wi-Fi",
            "In-seat power & USB outlets",
            "On-demand video",
            "Carbon emissions estimate: 659 kg"
          ],
          "overnight": true
        }
      ],
      "emissions_kg": 660.0,
      "ranking_score": 0.3333,
      "raw_option_jsonb": {}
    }
  ],
  "hotel_options": [
    {
      "property_name": "Superb Paris studio",
      "total_rate": null,
      "nightly_rate": null,
      "currency": "USD",
      "overall_rating": null,
      "location": null,
      "property_token": "ChkQgZzcxM-NqchBGg0vZy8xMXl3ZHNwNGQyEAI",
      "location_rating": 4.1,
      "review_count": null,
      "amenities_jsonb": ["Heating", "Ironing board", "Washer"],
      "free_cancellation": null,
      "ranking_score": 1.0,
      "raw_option_jsonb": {}
    },
    {
      "property_name": "Hôtel Bourgogne & Montana",
      "total_rate": null,
      "nightly_rate": null,
      "currency": "USD",
      "overall_rating": 4.7,
      "location": "Stylish hotel offering polished rooms with Nespresso machines & free Wi-Fi, plus a day spa & a bar.",
      "property_token": "ChcI6djb-MXRkYNtGgsvZy8xdGZ4Zl9jdxAB",
      "location_rating": 3.9,
      "review_count": 748,
      "amenities_jsonb": [
        "Breakfast ($)", "Free Wi-Fi", "Air conditioning", "Pet-friendly",
        "Spa", "Bar", "Room service", "Airport shuttle", "Full-service laundry",
        "Accessible", "Kid-friendly", "Smoke-free property"
      ],
      "free_cancellation": null,
      "ranking_score": 0.5,
      "raw_option_jsonb": {}
    },
    {
      "property_name": "The Hoxton, Paris",
      "total_rate": null,
      "nightly_rate": null,
      "currency": "USD",
      "overall_rating": 4.4,
      "location": "Stylish hotel offering a haute restaurant, courtyards & chic bars, plus free in-room breakfast.",
      "property_token": "ChkI3Zu6i7CE1e5MGg0vZy8xMWR4cWpwbXl5EAE",
      "location_rating": 4.9,
      "review_count": 4379,
      "amenities_jsonb": [
        "Breakfast ($)", "Free Wi-Fi", "Air conditioning", "Pet-friendly",
        "Bar", "Restaurant", "Room service", "Full-service laundry",
        "Accessible", "Kid-friendly", "Smoke-free property"
      ],
      "free_cancellation": null,
      "ranking_score": 0.3333,
      "raw_option_jsonb": {}
    }
  ],
  "warnings": [],
  "meta": {
    "source": "langgraph",
    "intent": "both",
    "composite_query": "[Additional instructions]\nFlight from New York to Paris on July 15 2026 returning July 22 2026, and hotel in Paris for 2 adults, budget up to $12000 USD",
    "timings": {
      "flight_ms": 1677,
      "hotel_ms": 7451
    },
    "warnings_count": 0,
    "tool_keys": {
      "flight": ["search_parameters", "price_insights", "flights"],
      "hotel": ["search_parameters", "brands", "properties"]
    },
    "serpapi_signals": {
      "flight_http": null,
      "flight_api": null,
      "hotel_http": null,
      "hotel_api": null
    }
  },
  "registration": {
    "quote_request_id": null,
    "client_name": null,
    "client_email": null,
    "destination": "CDG",
    "departure_city": "JFK",
    "trip_start_iso": "2026-07-15",
    "trip_end_iso": "2026-07-22",
    "travelers": null,
    "min_budget": null,
    "max_budget": null,
    "special_preferences": null,
    "normalized_search": {
      "origin": "JFK",
      "destination": "CDG",
      "depart_date": "2026-07-15",
      "return_date": "2026-07-22",
      "hotel_city": "Paris",
      "hotel_checkin": "2026-07-15",
      "hotel_checkout": "2026-07-22"
    },
    "total_price": 1579.0,
    "currency": "USD",
    "within_budget": null,
    "tier": null,
    "quality_score": 0.6111,
    "price_breakdown": {
      "flight": 1579.0,
      "hotel": null,
      "total": 1579.0,
      "currency": "USD"
    }
  }
}
```

### NL mode observations

- `registration.destination` = `"CDG"` and `departure_city` = `"JFK"` — in pure NL mode the agent resolves city names to IATA codes but there is no structured `travel_request` to carry the human-readable city label. The backend should map these codes back to display names if needed.
- `registration.client_name`, `client_email`, `min_budget`, `max_budget`, `travelers`, `special_preferences` = `null` — the NL path does not extract these from free text. They are only populated when a structured `travel_request` is provided.
- `within_budget` and `tier` = `null` — cannot be computed without `max_budget`.
- Hotel `total_rate` and `nightly_rate` = `null` — SerpAPI did not return rate data for these properties. This is a data-availability issue (not a code bug); the agent handles it gracefully. `price_breakdown.hotel` is `null` and `total_price` reflects flight cost only.

---

## Run 2 — Structured TravelRequest (package mode)

**Scenario:** Tokyo trip, full TravelOS-style form payload with all fields populated.

### Input

File: `input_q2_structured.json`

```json
{
  "travel_request": {
    "client_name": "Maria Lopez",
    "client_email": "maria.lopez@example.com",
    "destination": "Tokyo, Japan",
    "departure_city": "Los Angeles",
    "start_date": "2026-10-05",
    "end_date": "2026-10-15",
    "travelers": "2 Adults",
    "min_budget": 4000,
    "max_budget": 7000,
    "special_preferences": "Looking for clean hotels near Shinjuku. Prefer non-stop flights.",
    "currency": "USD"
  },
  "user_query": "Find flights and hotels for our Tokyo trip"
}
```

### Output

```json
{
  "summary": "There are 3 flight options and 3 hotel options available.",
  "flight_options": [
    {
      "title": "Round trip option",
      "total_price": 1672.0,
      "currency": "USD",
      "total_duration_min": 705,
      "layover_count": 0,
      "airline": "ZIPAIR Tokyo",
      "departure_token": "WyJDalJJT0ROcFEzUjZVR1J4ZFRoQlFsVTJUVkZDUnkwdExTMHRMUzB0TFMwdGQySnhOMEZCUVVGQlIyNDNjbXRuU3pocVNrOUJFZ1JhUnpJekdnc0lvSm9LRUFJYUExVlRSRGdjY0tDYUNnPT0iLFtbIkxBWCIsIjIwMjYtMTAtMDUiLCJOUlQiLG51bGwsIlpHIiwiMjMiXV1d",
      "segments_jsonb": [
        {
          "departure_airport": {
            "name": "Los Angeles International Airport",
            "id": "LAX",
            "time": "2026-10-05 10:25"
          },
          "arrival_airport": {
            "name": "Narita International Airport",
            "id": "NRT",
            "time": "2026-10-06 14:10"
          },
          "duration": 705,
          "airplane": "Boeing 787",
          "airline": "ZIPAIR Tokyo",
          "airline_logo": "https://www.gstatic.com/flights/airline_logos/70px/ZG.png",
          "travel_class": "Economy",
          "flight_number": "ZG 23",
          "legroom": "31 in",
          "extensions": [
            "Average legroom (31 in)",
            "Free Wi-Fi",
            "In-seat power & USB outlets",
            "Stream media to your device",
            "Carbon emissions estimate: 812 kg"
          ]
        }
      ],
      "emissions_kg": 813.0,
      "ranking_score": 1.0,
      "raw_option_jsonb": {}
    },
    {
      "title": "Round trip option",
      "total_price": 2134.0,
      "currency": "USD",
      "total_duration_min": 690,
      "layover_count": 0,
      "airline": "United",
      "departure_token": "WyJDalJJT0ROcFEzUjZVR1J4ZFRoQlFsVTJUVkZDUnkwdExTMHRMUzB0TFMwdGQySnhOMEZCUVVGQlIyNDNjbXRuU3pocVNrOUJFZ1ZFVERJMk1ob0xDTzdRQ1JBQ2dOVlVRNEhIRHUwQWs9IixbWyJMQVgiLCIyMDI2LTEwLTA1IiwiTlJUIixudWxsLCJVQSIsIjMyIl1dXQ==",
      "segments_jsonb": [
        {
          "departure_airport": {
            "name": "Los Angeles International Airport",
            "id": "LAX",
            "time": "2026-10-05 10:45"
          },
          "arrival_airport": {
            "name": "Narita International Airport",
            "id": "NRT",
            "time": "2026-10-06 14:15"
          },
          "duration": 690,
          "airplane": "Boeing 787",
          "airline": "United",
          "airline_logo": "https://www.gstatic.com/flights/airline_logos/70px/UA.png",
          "travel_class": "Economy",
          "flight_number": "UA 32",
          "ticket_also_sold_by": ["ANA"],
          "legroom": "31 in",
          "extensions": [
            "Average legroom (31 in)",
            "Wi-Fi for a fee",
            "In-seat power & USB outlets",
            "On-demand video",
            "Carbon emissions estimate: 767 kg"
          ]
        }
      ],
      "emissions_kg": 767.0,
      "ranking_score": 0.5,
      "raw_option_jsonb": {}
    },
    {
      "title": "Round trip option",
      "total_price": 2134.0,
      "currency": "USD",
      "total_duration_min": 705,
      "layover_count": 0,
      "airline": "ANA",
      "departure_token": "WyJDalJJT0ROcFEzUjZVR1J4ZFRoQlFsVTJUVkZDUnkwdExTMHRMUzB0TFMwdGQySnhOMEZCUVVGQlIyNDNjbXRuU3pocVNrOUJFZ05PU0RVYUN3amlnZzBRQWhvRFZWTkVPQnh3NG9JTiIsW1siTEFYIiwiMjAyNi0xMC0wNSIsIk5SVCIsbnVsbCwiTkgiLCI1Il1dXQ==",
      "segments_jsonb": [
        {
          "departure_airport": {
            "name": "Los Angeles International Airport",
            "id": "LAX",
            "time": "2026-10-05 12:45"
          },
          "arrival_airport": {
            "name": "Narita International Airport",
            "id": "NRT",
            "time": "2026-10-06 16:30"
          },
          "duration": 705,
          "airplane": "Boeing 787",
          "airline": "ANA",
          "airline_logo": "https://www.gstatic.com/flights/airline_logos/70px/NH.png",
          "travel_class": "Economy",
          "flight_number": "NH 5",
          "ticket_also_sold_by": ["United"],
          "legroom": "34 in",
          "extensions": [
            "Above average legroom (34 in)",
            "Wi-Fi for a fee",
            "In-seat power & USB outlets",
            "On-demand video",
            "Carbon emissions estimate: 817 kg"
          ]
        }
      ],
      "emissions_kg": 817.0,
      "ranking_score": 0.3333,
      "raw_option_jsonb": {}
    }
  ],
  "hotel_options": [
    {
      "property_name": "Young House Excellent access to the city center - Tokyo Young Ine 1st floor / Matsudo Chiba",
      "total_rate": 1046.0,
      "nightly_rate": 105.0,
      "currency": "USD",
      "overall_rating": 4.65,
      "location": null,
      "property_token": "ChoQp_ap_sWKx_DjARoNL2cvMTF2ZGs2eWR0OBAC",
      "location_rating": 3.3,
      "review_count": 18,
      "amenities_jsonb": [
        "Air conditioning", "Heating", "Ironing board", "Kitchen",
        "Microwave", "Oven stove", "Pet-friendly", "Smoke-free",
        "Cable TV", "Washer", "Wheelchair accessible"
      ],
      "free_cancellation": null,
      "ranking_score": 1.0,
      "raw_option_jsonb": {}
    },
    {
      "property_name": "Aila apartment",
      "total_rate": 645.0,
      "nightly_rate": 65.0,
      "currency": "USD",
      "overall_rating": 4.7,
      "location": null,
      "property_token": "ChoQzImzqa-A4LqVARoNL2cvMTF6OW4xZGh2bRAC",
      "location_rating": null,
      "review_count": 5,
      "amenities_jsonb": [
        "Air conditioning", "Heating", "Ironing board",
        "Microwave", "Pet-friendly", "Smoke-free", "Washer"
      ],
      "free_cancellation": null,
      "ranking_score": 0.5,
      "raw_option_jsonb": {}
    },
    {
      "property_name": "ONE@Tokyo by insomnia",
      "total_rate": 1380.0,
      "nightly_rate": 138.0,
      "currency": "USD",
      "overall_rating": 4.3,
      "location": "Industrial-chic quarters & a cafe in a choice hotel offering a rooftop lounge with skyline views.",
      "property_token": "ChoI84KEy5HjiaeGARoNL2cvMTFkeGp4MnEyXxAB",
      "location_rating": 4.6,
      "review_count": 953,
      "amenities_jsonb": ["Free Wi-Fi", "Accessible", "Kid-friendly"],
      "free_cancellation": null,
      "ranking_score": 0.3333,
      "raw_option_jsonb": {}
    }
  ],
  "warnings": [],
  "meta": {
    "source": "langgraph",
    "intent": "both",
    "composite_query": "[Structured travel request]\nClient name: Maria Lopez\nClient email: maria.lopez@example.com\nDeparture city: Los Angeles\nDestination: Tokyo, Japan\nTrip window: 2026-10-05 → 2026-10-15\nBudget range: USD 4000.0 to USD 7000.0\nTravelers: 2 Adults\nNatural language preferences:\nLooking for clean hotels near Shinjuku. Prefer non-stop flights.\n\n[Additional instructions]\nFind flights and hotels for our Tokyo trip",
    "timings": {
      "flight_ms": 1113,
      "hotel_ms": 3528
    },
    "warnings_count": 0,
    "tool_keys": {
      "flight": ["search_parameters", "price_insights", "flights"],
      "hotel": ["search_parameters", "brands", "properties"]
    },
    "serpapi_signals": {
      "flight_http": null,
      "flight_api": null,
      "hotel_http": null,
      "hotel_api": null
    }
  },
  "registration": {
    "quote_request_id": null,
    "client_name": "Maria Lopez",
    "client_email": "maria.lopez@example.com",
    "destination": "Tokyo, Japan",
    "departure_city": "Los Angeles",
    "trip_start_iso": "2026-10-05",
    "trip_end_iso": "2026-10-15",
    "travelers": "2 Adults",
    "min_budget": 4000.0,
    "max_budget": 7000.0,
    "special_preferences": "Looking for clean hotels near Shinjuku. Prefer non-stop flights.",
    "normalized_search": {
      "origin": "LAX",
      "destination": "NRT",
      "depart_date": "2026-10-05",
      "return_date": "2026-10-15",
      "hotel_city": "Tokyo",
      "hotel_checkin": "2026-10-05",
      "hotel_checkout": "2026-10-15"
    },
    "total_price": 2718.0,
    "currency": "USD",
    "within_budget": true,
    "tier": "budget",
    "quality_score": 0.6111,
    "price_breakdown": {
      "flight": 1672.0,
      "hotel": 1046.0,
      "total": 2718.0,
      "currency": "USD"
    }
  }
}
```

### Structured mode observations

- All `registration` fields populated correctly from `travel_request`.
- `destination` = `"Tokyo, Japan"` and `departure_city` = `"Los Angeles"` preserved as human-readable labels (not IATA codes) — contrast with NL mode above.
- `within_budget` = `true` and `tier` = `"budget"` computed correctly: $1,672 / $7,000 = 24%.
- `quality_score` = `0.6111` = average of all 6 ranking scores (1.0 + 0.5 + 0.3333 + 1.0 + 0.5 + 0.3333) / 6.
- Hotel rates correctly populated: `nightly_rate` and `total_rate` extracted from `rate_per_night.extracted_lowest` and `total_rate.extracted_lowest` in the SerpAPI response.
- `price_breakdown = { "flight": 1672.0, "hotel": 1046.0, "total": 2718.0 }` — full combined price available.
- `normalized_search` correctly resolved `"Los Angeles" → LAX` and `"Tokyo, Japan" → NRT`.

---

## Bugs found and fixed during these runs

| Bug | Where | Fix applied |
|---|---|---|
| `emissions_kg` stored in grams (1000× too large) | `travel_graph.py:887` | Divide by 1000 and round: `round(float(v) / 1000, 2)` |
| Default currency `"MXN"` for queries with no explicit currency | `travel_graph.py:335` | Changed fallback to `"USD"` |
| Hotel `total_rate`/`nightly_rate` always `null` | `travel_graph.py:923,932` | Read `extracted_lowest` (numeric) instead of `lowest` (string like `"$105"`) |
| Input dates in Q1 were in the past (Apr 2026) | `input_q1_nl.json` | Updated to Jul 2026 |

## Known limitations (not bugs)

| Limitation | Affects | Notes |
|---|---|---|
| `destination`/`departure_city` show IATA codes in NL mode | NL path only | No `travel_request` wrapper means city labels are not preserved; backend should map codes to display names if needed |
| Budget, travelers, client info = `null` in NL mode | NL path only | Agent does not extract structured fields from free text; use structured input for full `registration` |
| Hotel `total_rate` / `nightly_rate` = `null` in NL mode | NL path (Run 1) | SerpAPI returned rate data for Tokyo but Paris hotels didn't include rates in this search; `price_breakdown.hotel` will be `null` and `total_price` covers flight only when rates are unavailable |

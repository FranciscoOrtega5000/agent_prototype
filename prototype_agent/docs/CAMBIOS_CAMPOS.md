# Cambios en los campos de salida del agente

## Contexto

El agente de viajes genera un JSON de salida que el backend debe parsear y persistir en la base de datos.
Este documento describe **qué campos cambiaron**, por qué, y cómo mapean a cada tabla del esquema.

> **Nota para el backend:** Los FKs (`quote_request_id`, `job_id`, `flight_option_id`, `hotel_option_id`)
> son asignados por el backend después de insertar. El agente los emite como `null`.

---

## FlightOption → tabla `FLIGHT_OPTIONS`

| Campo anterior | Campo nuevo | Tipo Python | Columna BD | Cambio / Motivo |
|---|---|---|---|---|
| `title` | `title` | `str` | _(solo display)_ | Sin cambio |
| `total_price` | `total_price` | `float \| None` | `total_price (numeric)` | Era `str`; ahora es número para cálculos en BD |
| `currency` | `currency` | `str \| None` | `currency` | Sin cambio |
| `duration` | `total_duration_min` | `int \| None` | `total_duration_min (int)` | Renombrado; SerpAPI ya devuelve minutos como entero |
| `stops` | `layover_count` | `int \| None` | `layover_count (int)` | Renombrado para coincidir con el nombre de columna |
| `airline` | `airline` | `str \| None` | _(dentro de `segments_jsonb`)_ | Se mantiene como atajo rápido; también en segmentos |
| `highlights` | _(eliminado)_ | — | — | No existe en el esquema de BD; datos están en `raw_option_jsonb` |
| `raw` | `raw_option_jsonb` | `dict` | `raw_option_jsonb (jsonb)` | Renombrado para coincidir con la convención de BD |
| _(nuevo)_ | `departure_token` | `str \| None` | `departure_token (text)` | Token de SerpAPI necesario para buscar vuelos de vuelta |
| _(nuevo)_ | `segments_jsonb` | `list \| None` | `segments_jsonb (jsonb)` | Lista de piernas/segmentos del vuelo (escalas, aerolíneas) |
| _(nuevo)_ | `emissions_kg` | `float \| None` | `emissions_kg (numeric)` | CO₂ en kg, campo `carbon_emissions.this_flight` de SerpAPI |
| _(nuevo)_ | `ranking_score` | `float \| None` | `ranking_score (numeric)` | Score `1 / (posición + 1)` para ordenamiento en UI |

---

## HotelOption → tabla `HOTEL_OPTIONS`

| Campo anterior | Campo nuevo | Tipo Python | Columna BD | Cambio / Motivo |
|---|---|---|---|---|
| `name` | `property_name` | `str` | `property_name (string)` | Renombrado para coincidir con la columna |
| `total_price` | `total_rate` | `float \| None` | `total_rate (numeric)` | Renombrado + convertido a número |
| `nightly_price` | `nightly_rate` | `float \| None` | `nightly_rate (numeric)` | Renombrado + convertido a número |
| `currency` | `currency` | `str \| None` | `currency` | Sin cambio |
| `rating` | `overall_rating` | `float \| None` | `overall_rating (numeric)` | Renombrado para coincidir con la columna |
| `location` | `location` | `str \| None` | _(descripción textual)_ | Se conserva como ayuda visual; no es columna de BD independiente |
| `highlights` | _(eliminado)_ | — | — | No existe en el esquema; información en `raw_option_jsonb` |
| `raw` | `raw_option_jsonb` | `dict` | `raw_option_jsonb (jsonb)` | Renombrado |
| _(nuevo)_ | `property_token` | `str \| None` | `property_token (text)` | Token de SerpAPI para enlace directo a la propiedad |
| _(nuevo)_ | `location_rating` | `float \| None` | `location_rating (numeric)` | Rating de ubicación de SerpAPI |
| _(nuevo)_ | `review_count` | `int \| None` | `review_count (int)` | Número de reseñas del hotel (campo `reviews` en SerpAPI) |
| _(nuevo)_ | `amenities_jsonb` | `list \| None` | `amenities_jsonb (jsonb)` | Lista de amenidades (piscina, wifi, etc.) |
| _(nuevo)_ | `free_cancellation` | `bool \| None` | `free_cancellation (boolean)` | Indica si el hotel ofrece cancelación gratuita |
| _(nuevo)_ | `ranking_score` | `float \| None` | `ranking_score (numeric)` | Score `1 / (posición + 1)` para ordenamiento |

---

## PackageRegistration → tablas `PACKAGES` + `QUOTE_REQUESTS`

Los campos de `QUOTE_REQUESTS` (destino, fechas, presupuesto, viajeros, preferencias) ya existían
y no cambian de nombre. Los campos nuevos corresponden a `PACKAGES`.

| Campo anterior | Campo nuevo | Tipo Python | Columna BD | Cambio / Motivo |
|---|---|---|---|---|
| _(existente)_ | `client_name` | `str \| None` | `client_name (text)` en `QUOTE_REQUESTS` | Nombre del cliente; columna no documentada hasta ahora |
| _(existente)_ | `client_email` | `str \| None` | `client_email (text)` en `QUOTE_REQUESTS` | Email del cliente; columna no documentada hasta ahora |
| _(existente)_ | `destination` | `str \| None` | `destination_label` | Sin cambio |
| _(existente)_ | `departure_city` | `str \| None` | `origin_label` | Sin cambio |
| _(existente)_ | `trip_start_iso` | `str \| None` | `depart_date` | Sin cambio |
| _(existente)_ | `trip_end_iso` | `str \| None` | `return_date` | Sin cambio |
| _(existente)_ | `travelers` | `str \| None` | _(travelers fields)_ | Sin cambio |
| _(existente)_ | `min_budget` | `float \| None` | `budget_max` (min implícito) | Sin cambio |
| _(existente)_ | `max_budget` | `float \| None` | `budget_max` | Sin cambio |
| _(existente)_ | `special_preferences` | `str \| None` | `submitted_payload` | Sin cambio |
| _(existente)_ | `normalized_search` | `dict` | _(referencia interna)_ | Sin cambio |
| _(nuevo)_ | `quote_request_id` | `str \| None` | `id` en `QUOTE_REQUESTS` | FK asignado por backend; el agente lo emite como `null` |
| _(nuevo)_ | `total_price` | `float \| None` | `total_price` en `PACKAGES` | Suma de vuelo + hotel calculada por el agente |
| _(nuevo)_ | `currency` | `str \| None` | `currency` en `PACKAGES` | Moneda del precio total |
| _(nuevo)_ | `within_budget` | `bool \| None` | `within_budget` en `PACKAGES` | `true` si `total_price <= max_budget` |
| _(nuevo)_ | `tier` | `str \| None` | `tier` en `PACKAGES` | `"budget"` / `"standard"` / `"premium"` según ratio precio/presupuesto |
| _(nuevo)_ | `quality_score` | `float \| None` | `quality_score` en `PACKAGES` | Promedio de `ranking_score` de vuelo y hotel seleccionados |
| _(nuevo)_ | `price_breakdown` | `dict \| None` | `price_breakdown_jsonb` en `PACKAGES` | Desglose: `{ "flight": x, "hotel": y, "total": z, "currency": "..." }` |

---

## Campos y archivos eliminados

| Elemento | Motivo |
|---|---|
| `highlights` en `FlightOption` y `HotelOption` | No existe en el esquema de BD; la información relevante pasa a `raw_option_jsonb` |
| `booking_tool.py` | Integración Apify para Booking.com — nunca se importó ni usó |
| `skyscanner_tool.py` | Integración Apify para Skyscanner — nunca se importó ni usó |
| `APIFY_API_TOKEN` en `.env` | Variable del token de Apify — ya no necesaria |
| `LANGGRAPH_USE_CHECKPOINT` | El agente es siempre stateless one-shot; los checkpoints fueron eliminados |
| `LANGGRAPH_CHECKPOINT_DB` | Ídem |
| `LANGGRAPH_THREAD_ID` | Ídem |
| `langgraph-checkpoint-sqlite` | Dependencia de checkpoints — removida de `requirements.txt` |

---

## Notas de integración para el backend

1. **FKs que asigna el backend, no el agente:**
   `quote_request_id`, `job_id`, `flight_option_id`, `hotel_option_id`
   El agente los devuelve como `null`; el backend los asigna al insertar.

2. **`package_snapshot_jsonb`** (tabla `PACKAGES`):
   Se puede construir serializando el JSON de salida completo del agente.
   No es necesario que el agente lo genere explícitamente.

3. **`rationale_text`** (tabla `PACKAGES`):
   Corresponde al campo `summary` del agente (frase generada por el LLM writer).

4. **`submitted_payload`** (tabla `QUOTE_REQUESTS`):
   Corresponde al payload JSON original que envió el frontend.
   El backend debe guardarlo antes de invocar al agente.

5. **Flujo recomendado:**
   ```
   Frontend → POST /quote-requests  →  Backend inserta QUOTE_REQUESTS, obtiene quote_request_id
                                    →  Backend invoca agente con payload + quote_request_id
                                    →  Agente devuelve TravelQueryOutput
                                    →  Backend inserta FLIGHT_OPTIONS, HOTEL_OPTIONS, PACKAGES
                                    →  Backend devuelve resultado al frontend
   ```

---

## TravelQueryOutput — campos del envelope no cubiertos antes

Los campos de nivel raíz del JSON de salida (`summary`, `warnings`, `meta`) no estaban documentados
con su destino en BD. Se completan aquí.

### `summary` y `warnings`

| Campo agente | Tipo | Destino BD | Nota |
|---|---|---|---|
| `summary` | `str` | `rationale_text` en `PACKAGES` | Frase corta generada por el LLM writer (ya mencionado en Nota 3) |
| `warnings` | `list[str]` | `package_snapshot_jsonb` en `PACKAGES` | Sin columna dedicada; el blob completo lo captura |

### `meta` — bloque de metadatos de ejecución

| Campo agente | Tipo | Destino BD | Nota |
|---|---|---|---|
| `meta.source` | `str` | `package_snapshot_jsonb` | Siempre `"langgraph"`; identifica el motor del agente |
| `meta.intent` | `str` | `package_snapshot_jsonb` | `"flight"` / `"hotel"` / `"both"` / `"unknown"`. **Recomendación:** agregar columna `search_intent (text)` en `PACKAGES` para analíticas |
| `meta.composite_query` | `str \| null` | `package_snapshot_jsonb` | Query combinada que usó el agente internamente |
| `meta.timings.flight_ms` | `int \| null` | `package_snapshot_jsonb` | Tiempo de respuesta de la herramienta de vuelos en ms |
| `meta.timings.hotel_ms` | `int \| null` | `package_snapshot_jsonb` | Tiempo de respuesta de la herramienta de hoteles en ms |
| `meta.warnings_count` | `int` | — | Derivado de `len(warnings)`; no requiere columna |
| `meta.tool_keys` | `dict` | `package_snapshot_jsonb` | Claves presentes en la respuesta de SerpAPI; solo para debugging |
| `meta.serpapi_signals` | `dict` | `package_snapshot_jsonb` | Errores HTTP y de API de SerpAPI (`null` cuando todo OK) |

---

## Acciones pendientes para los equipos

| # | Equipo | Acción |
|---|---|---|
| 1 | **BD** | Confirmar que columna `rationale_text (text)` existe en `PACKAGES` |
| 2 | **BD** | Confirmar nombres exactos `client_name` y `client_email` en `QUOTE_REQUESTS` |
| 3 | **BD** | Evaluar agregar `search_intent (text)` en `PACKAGES` para consultas analíticas sobre `meta.intent` |
| 4 | **BD** | Confirmar si `normalized_search` debe persistirse como `normalized_search_jsonb` en `QUOTE_REQUESTS` (útil para re-ejecutar búsquedas) |
| 5 | **Backend** | El campo `meta` completo y `warnings` quedan cubiertos por `package_snapshot_jsonb`; no se necesitan columnas adicionales salvo lo indicado en punto 3 |

---

## JSON de salida canónico (referencia completa)

Forma exacta que emite el agente. Todos los campos `null` son válidos; el backend debe tolerarlos.

```json
{
  "summary": "Found 3 flight option(s). Found 3 hotel option(s).",
  "flight_options": [
    {
      "title": "Best flights option",
      "total_price": 1308.0,
      "currency": "USD",
      "total_duration_min": 465,
      "layover_count": 0,
      "airline": "Air France",
      "departure_token": "WyJKRksiLCIyMDI2LTA0LTE1IiwiQ0RHIiwiMjAyNi0wNC0xNSIsbnVsbCwyXQ==",
      "segments_jsonb": [
        {
          "departure_airport": { "id": "JFK", "time": "2026-04-15 10:30" },
          "arrival_airport": { "id": "CDG", "time": "2026-04-15 23:15" },
          "duration": 465,
          "airline": "Air France",
          "flight_number": "AF007"
        }
      ],
      "emissions_kg": 245.0,
      "ranking_score": 1.0,
      "raw_option_jsonb": {}
    }
  ],
  "hotel_options": [
    {
      "property_name": "Hotel Le Marais",
      "total_rate": 1435.0,
      "nightly_rate": 205.0,
      "currency": "USD",
      "overall_rating": 4.2,
      "location": "Le Marais District, Paris",
      "property_token": "ChcIop2Ij...",
      "location_rating": 4.5,
      "review_count": 1240,
      "amenities_jsonb": ["Free WiFi", "Breakfast included", "Spa access"],
      "free_cancellation": true,
      "ranking_score": 1.0,
      "raw_option_jsonb": {}
    }
  ],
  "warnings": [],
  "meta": {
    "source": "langgraph",
    "intent": "both",
    "composite_query": "Flights and hotels to Paris Apr 15-22 2026 for 2 adults budget 8000-12000 USD",
    "timings": {
      "flight_ms": 1234,
      "hotel_ms": 987
    },
    "warnings_count": 0,
    "tool_keys": {
      "flight": ["search_metadata", "search_parameters", "flights", "other_flights"],
      "hotel": ["search_metadata", "search_parameters", "properties"]
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
    "client_name": "Jane Doe",
    "client_email": "client@example.com",
    "destination": "Paris, France",
    "departure_city": "New York",
    "trip_start_iso": "2026-04-15",
    "trip_end_iso": "2026-04-22",
    "travelers": "2 Adults",
    "min_budget": 8000.0,
    "max_budget": 12000.0,
    "special_preferences": "Romantic experiences, fine dining, boutique hotels in central locations",
    "normalized_search": {
      "origin": "JFK",
      "destination": "CDG",
      "depart_date": "2026-04-15",
      "return_date": "2026-04-22",
      "hotel_city": "Paris",
      "hotel_checkin": "2026-04-15",
      "hotel_checkout": "2026-04-22"
    },
    "total_price": 2743.0,
    "currency": "USD",
    "within_budget": true,
    "tier": "budget",
    "quality_score": 1.0,
    "price_breakdown": {
      "flight": 1308.0,
      "hotel": 1435.0,
      "total": 2743.0,
      "currency": "USD"
    }
  }
}
```

> **Nota `tier`:** el agente emite `"budget"` / `"standard"` / `"premium"` según el ratio `total_price / max_budget`.
> El frontend puede mapear estos valores a etiquetas de display (p.ej. "Economy Package", "Standard Package", "Premium Package") sin que el agente deba conocer esos nombres.

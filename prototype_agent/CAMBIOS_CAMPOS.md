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

"""
Travel agent test suite — 8 cases covering all input modes and known failure patterns.

Run with:
    python run_agent_test.py

Each test directly calls build_travel_graph().invoke(...) and checks for:
- Whether flights / hotels were returned
- Whether the intent is correct
- Whether blocking warnings appear

No external test framework required.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Any

from dotenv import load_dotenv

load_dotenv()

if not os.environ.get("NVIDIA_API_KEY"):
    sys.exit("Set NVIDIA_API_KEY in .env before running tests.")
if not os.environ.get("SERPAPI_API_KEY"):
    sys.exit("Set SERPAPI_API_KEY in .env before running tests.")

from graph_state import TravelQueryOutput, TravelRequest
from travel_graph import build_travel_graph


# ── Result container ─────────────────────────────────────────────────────────

@dataclass
class TestResult:
    name: str
    passed: bool
    flight_count: int = 0
    hotel_count: int = 0
    intent: str = "unknown"
    warnings: list[str] = field(default_factory=list)
    failure_reason: str = ""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _run(inputs: dict[str, Any]) -> TravelQueryOutput:
    inputs.setdefault("output_config", {"include_raw": False, "max_options": 2})
    graph = build_travel_graph()
    state = graph.invoke(inputs)
    output = state.get("output")
    if isinstance(output, TravelQueryOutput):
        return output
    return TravelQueryOutput(
        summary="No output",
        warnings=state.get("warnings", []),
    )


def _has_blocking_error(output: TravelQueryOutput) -> bool:
    blocking_keys = ("_http_error", "_serpapi_error", "HTTP 4", "HTTP 5", "SerpAPI error")
    for w in output.warnings:
        if any(k in w for k in blocking_keys):
            return True
    return False


def _check(
    output: TravelQueryOutput,
    *,
    expect_flights: bool = True,
    expect_hotels: bool = True,
    expect_intent: str | None = None,
) -> tuple[bool, str]:
    if expect_flights and not output.flight_options:
        return False, f"Expected flights but got none. Warnings: {output.warnings}"
    if expect_hotels and not output.hotel_options:
        return False, f"Expected hotels but got none. Warnings: {output.warnings}"
    if expect_intent and output.meta.get("intent") != expect_intent:
        actual = output.meta.get("intent")
        return False, f"Expected intent={expect_intent!r} but got {actual!r}"
    return True, ""


# ── Test cases ────────────────────────────────────────────────────────────────

def test_a_pure_nl_iata_codes() -> TestResult:
    """Pure NL with IATA codes and ISO dates — word 'flights' drives flight-only intent."""
    output = _run({"user_query": "Flights from MEX to CDG on 2026-07-15 returning 2026-07-30"})
    # "Flights from X to Y" → intent=flight (no hotel keyword). That is correct.
    passed, reason = _check(output, expect_flights=True, expect_hotels=False, expect_intent="flight")
    return TestResult(
        name="A: Pure NL — IATA + ISO dates (flight-only NL)",
        passed=passed,
        flight_count=len(output.flight_options),
        hotel_count=len(output.hotel_options),
        intent=output.meta.get("intent", "?"),
        warnings=output.warnings,
        failure_reason=reason,
    )


def test_b_pure_nl_city_names() -> TestResult:
    """Pure NL with city names resolved via IATA lookup and natural-language dates.
    Uses 'hotel in Paris' phrasing so both hotel and flight intent are clear."""
    output = _run({
        "user_query": (
            "Flight from Mexico City to Paris on July 15 2026 returning July 30 2026, "
            "and hotel in Paris"
        )
    })
    # "Flight ... and hotel" triggers both intent; city names → MEX/CDG via lookup
    passed, reason = _check(output, expect_flights=True, expect_hotels=True)
    return TestResult(
        name="B: Pure NL — city names + NL dates (both intent)",
        passed=passed,
        flight_count=len(output.flight_options),
        hotel_count=len(output.hotel_options),
        intent=output.meta.get("intent", "?"),
        warnings=output.warnings,
        failure_reason=reason,
    )


def test_c_pure_nl_no_dates() -> TestResult:
    """Pure NL with no dates at all — agent should warn, not crash."""
    output = _run({"user_query": "I want to travel to Tokyo from New York sometime next year"})
    # No flights/hotels expected — just check it doesn't crash and emits warnings
    passed = isinstance(output, TravelQueryOutput)
    reason = "" if passed else "Graph crashed"
    return TestResult(
        name="C: Pure NL — no dates (graceful fallback)",
        passed=passed,
        flight_count=len(output.flight_options),
        hotel_count=len(output.hotel_options),
        intent=output.meta.get("intent", "?"),
        warnings=output.warnings,
        failure_reason=reason,
    )


def test_d_full_structured_json() -> TestResult:
    """Full structured TravelRequest — all fields populated."""
    output = _run({
        "travel_request": TravelRequest.model_validate({
            "client_name": "John Smith",
            "client_email": "client@example.com",
            "destination": "Paris, France",
            "departure_city": "New York, USA",
            "start_date": "2026-07-15",
            "end_date": "2026-07-30",
            "travelers": "2 Adults",
            "min_budget": 5000,
            "max_budget": 10000,
            "special_preferences": "Direct flights preferred. Hotel near city centre.",
            "currency": "USD",
        }),
    })
    passed, reason = _check(output, expect_flights=True, expect_hotels=True)
    # Also verify registration is populated
    if passed and output.registration is None:
        passed, reason = False, "registration is None — expected PackageRegistration"
    if passed and output.registration and output.registration.client_name != "John Smith":
        passed, reason = False, f"client_name mismatch: {output.registration.client_name!r}"
    return TestResult(
        name="D: Full structured JSON — all fields",
        passed=passed,
        flight_count=len(output.flight_options),
        hotel_count=len(output.hotel_options),
        intent=output.meta.get("intent", "?"),
        warnings=output.warnings,
        failure_reason=reason,
    )


def test_e_structured_json_dates_in_preferences() -> TestResult:
    """Structured form without explicit dates — dates inferred from special_preferences."""
    output = _run({
        "travel_request": TravelRequest.model_validate({
            "destination": "Ibiza, Spain",
            "departure_city": "Mexico City",
            "travelers": "2 Adults",
            "max_budget": 8000,
            "special_preferences": (
                "We want to travel from August 10 to August 18, 2026. "
                "Prefer boutique hotels near the beach."
            ),
        }),
    })
    passed, reason = _check(output, expect_flights=True, expect_hotels=True)
    # Check dates were inferred
    if passed:
        reg = output.registration
        if reg and not reg.trip_start_iso:
            passed, reason = False, "trip_start_iso was not inferred from NL preferences"
    return TestResult(
        name="E: Structured JSON — dates from special_preferences",
        passed=passed,
        flight_count=len(output.flight_options),
        hotel_count=len(output.hotel_options),
        intent=output.meta.get("intent", "?"),
        warnings=output.warnings,
        failure_reason=reason,
    )


def test_f_flight_only_intent() -> TestResult:
    """Structured request with explicit flight-only preference."""
    output = _run({
        "travel_request": TravelRequest.model_validate({
            "destination": "Cancun, Mexico",
            "departure_city": "Mexico City",
            "start_date": "2026-08-01",
            "end_date": "2026-08-08",
            "travelers": "2 Adults",
            "special_preferences": "Only looking for flights, no hotel needed.",
        }),
    })
    passed, reason = _check(output, expect_flights=True, expect_hotels=False, expect_intent="flight")
    return TestResult(
        name="F: Structured JSON — flight-only intent",
        passed=passed,
        flight_count=len(output.flight_options),
        hotel_count=len(output.hotel_options),
        intent=output.meta.get("intent", "?"),
        warnings=output.warnings,
        failure_reason=reason,
    )


def test_g_hotel_only_intent() -> TestResult:
    """Structured request with explicit hotel-only preference."""
    output = _run({
        "travel_request": TravelRequest.model_validate({
            "destination": "Barcelona, Spain",
            "start_date": "2026-09-10",
            "end_date": "2026-09-17",
            "travelers": "2 Adults",
            "special_preferences": "Only need a hotel, flights already booked.",
        }),
    })
    passed, reason = _check(output, expect_flights=False, expect_hotels=True, expect_intent="hotel")
    return TestResult(
        name="G: Structured JSON — hotel-only intent",
        passed=passed,
        flight_count=len(output.flight_options),
        hotel_count=len(output.hotel_options),
        intent=output.meta.get("intent", "?"),
        warnings=output.warnings,
        failure_reason=reason,
    )


def test_h_inline_dict_simulation() -> TestResult:
    """Simulates what run_agent.py does when passed an inline JSON blob."""
    payload = {
        "travel_request": {
            "destination": "Tokyo, Japan",
            "departure_city": "Los Angeles",
            "start_date": "2026-10-05",
            "end_date": "2026-10-15",
            "travelers": "1 Adult",
            "max_budget": 4000,
            "currency": "USD",
        },
        "user_query": "Please include budget hotel options.",
    }
    # Mimic _graph_inputs_from_payload
    inputs: dict[str, Any] = {
        "user_query": payload.get("user_query", ""),
        "travel_request": TravelRequest.model_validate(payload["travel_request"]),
        "package_mode": True,
    }
    output = _run(inputs)
    passed, reason = _check(output, expect_flights=True, expect_hotels=True)
    return TestResult(
        name="H: Inline dict simulation (backend-style call)",
        passed=passed,
        flight_count=len(output.flight_options),
        hotel_count=len(output.hotel_options),
        intent=output.meta.get("intent", "?"),
        warnings=output.warnings,
        failure_reason=reason,
    )


# ── Runner ────────────────────────────────────────────────────────────────────

ALL_TESTS = [
    test_a_pure_nl_iata_codes,
    test_b_pure_nl_city_names,
    test_c_pure_nl_no_dates,
    test_d_full_structured_json,
    test_e_structured_json_dates_in_preferences,
    test_f_flight_only_intent,
    test_g_hotel_only_intent,
    test_h_inline_dict_simulation,
]


def _bar(n: int, total: int, width: int = 20) -> str:
    filled = int(width * n / total) if total else 0
    return "#" * filled + "-" * (width - filled)


def main() -> None:
    results: list[TestResult] = []
    total = len(ALL_TESTS)

    for i, test_fn in enumerate(ALL_TESTS, 1):
        print(f"\n[{i}/{total}] Running: {test_fn.__name__} ...")
        try:
            result = test_fn()
        except Exception as exc:
            result = TestResult(
                name=test_fn.__name__,
                passed=False,
                failure_reason=f"Exception: {exc}",
            )
        results.append(result)
        status = "PASS" if result.passed else "FAIL"
        marker = "[+]" if result.passed else "[!]"
        print(f"  {marker} {status}  flights={result.flight_count}  hotels={result.hotel_count}  intent={result.intent}")
        if not result.passed:
            print(f"  Reason: {result.failure_reason}")
        if result.warnings:
            for w in result.warnings:
                print(f"  [W] {w}")

    passed_count = sum(1 for r in results if r.passed)
    print("\n" + "=" * 64)
    print(f"  RESULTS  {_bar(passed_count, total)}  {passed_count}/{total} passed")
    print("=" * 64)
    print(f"  {'Test':<45} {'Status':<8} {'Flt':>4} {'Htl':>4}")
    print("  " + "-" * 60)
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"  {r.name:<45} {status:<8} {r.flight_count:>4} {r.hotel_count:>4}")
    print("=" * 64)

    if passed_count < total:
        sys.exit(1)


if __name__ == "__main__":
    main()

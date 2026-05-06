"""
Single-shot CLI for the travel LangGraph prototype.

Passes either a natural-language text query or a JSON payload describing a structured
`TravelRequest` (optionally merged with a `user_query` string).

Every invocation is stateless — one call, one result, no conversation memory.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

if not os.environ.get("NVIDIA_API_KEY"):
    sys.exit("Set NVIDIA_API_KEY in .env (copy from .env.example).")
if not os.environ.get("SERPAPI_API_KEY"):
    sys.exit("Set SERPAPI_API_KEY in .env (copy from .env.example).")

from graph_state import TravelQueryOutput, TravelRequest
from travel_graph import build_travel_graph

RESERVED_PAYLOAD_KEYS = frozenset({"travel_request", "user_query", "package_mode", "output_config"})


def _env_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _sanitize_output(text: str) -> str:
    """Remove accidental reasoning traces from model output."""
    cleaned = text
    cleaned = re.sub(r"<think>[\s\S]*?</think>", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(
        r"```(?:reasoning|thoughts|analysis)[\s\S]*?```",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"(?im)^\s*(reasoning|thought process|analysis)\s*:.*$", "", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned


def _graph_inputs_from_payload(data: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    oc = data.get("output_config")
    if isinstance(oc, dict):
        out["output_config"] = oc
    if isinstance(data.get("package_mode"), bool):
        out["package_mode"] = data["package_mode"]
    uq = data.get("user_query")
    out["user_query"] = str(uq).strip() if uq else ""

    nested = data.get("travel_request")
    if isinstance(nested, dict):
        out["travel_request"] = TravelRequest.model_validate(nested)
        return out

    candidate = {
        key: val
        for key, val in data.items()
        if key not in RESERVED_PAYLOAD_KEYS
    }
    if candidate:
        out["travel_request"] = TravelRequest.model_validate(candidate)
    return out


def _maybe_parse_argv_json(blob: str) -> dict[str, Any] | None:
    trimmed = blob.strip()
    if not trimmed.startswith("{") or not trimmed.endswith("}"):
        return None
    try:
        return json.loads(trimmed)
    except json.JSONDecodeError:
        return None


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Travel package LangGraph one-shot prototype.")
    parser.add_argument("--json-path", metavar="PATH", help="JSON file with travel payload")
    parser.add_argument(
        "query_rest",
        nargs="*",
        help="Natural language query or inline JSON payload.",
    )
    return parser.parse_args(argv)


def main() -> None:
    args_ns = parse_args(sys.argv[1:])
    include_raw = _env_bool(os.environ.get("INCLUDE_RAW"), default=False)
    max_options = int(os.environ.get("MAX_OPTIONS", "3"))

    payload_override: dict[str, Any] | None = None
    stdin_payload: dict[str, Any] | None = None

    if not sys.stdin.isatty():
        raw_stdin = sys.stdin.read().strip()
        if raw_stdin.startswith("{"):
            try:
                stdin_payload = json.loads(raw_stdin)
            except json.JSONDecodeError:
                print("stdin started with `{` but is not valid JSON", file=sys.stderr)
                sys.exit(2)

    if args_ns.json_path:
        path = Path(args_ns.json_path).expanduser()
        payload_override = json.loads(path.read_text(encoding="utf-8"))

    positional = (" ".join(args_ns.query_rest)).strip()

    merged_for_invoke: dict[str, Any]
    payload_inline: dict[str, Any] | None = None
    if (
        positional
        and not payload_override
        and not stdin_payload
        and (payload_inline := _maybe_parse_argv_json(positional)) is not None
    ):
        merged_for_invoke = _graph_inputs_from_payload(payload_inline)
        positional = ""
    elif payload_override is not None or stdin_payload is not None:
        base_payload: dict[str, Any] = {}
        if stdin_payload:
            base_payload.update(stdin_payload)
        if payload_override:
            base_payload.update(payload_override)
        merged_for_invoke = _graph_inputs_from_payload(base_payload)
        merged_for_invoke["user_query"] = str(
            merged_for_invoke.get("user_query", "") + (" " + positional if positional else "")
        ).strip()
    elif positional:
        merged_for_invoke = {"user_query": positional}
    else:
        typed = input("You: ").strip()
        merged_for_invoke = {"user_query": typed}

    if not merged_for_invoke.get("user_query") and not merged_for_invoke.get("travel_request"):
        print("Provide --json-path, stdin JSON, a positional query string, or type a prompt.")
        return

    merged_for_invoke.setdefault("package_mode", bool(merged_for_invoke.get("travel_request")))
    oc = merged_for_invoke.setdefault("output_config", {})
    if isinstance(oc, dict):
        oc.setdefault("include_raw", include_raw)
        oc.setdefault("max_options", max(1, min(max_options, 10)))

    graph = build_travel_graph()
    out = graph.invoke(merged_for_invoke)

    output = out.get("output")
    if isinstance(output, TravelQueryOutput):
        print(_sanitize_output(output.model_dump_json(indent=2, ensure_ascii=False)))
        return
    if isinstance(output, dict):
        print(_sanitize_output(TravelQueryOutput(**output).model_dump_json(indent=2, ensure_ascii=False)))
        return

    warnings = out.get("warnings", [])
    fallback = TravelQueryOutput(
        summary="No structured output was produced.",
        warnings=warnings if isinstance(warnings, list) else [str(warnings)],
    )
    print(_sanitize_output(fallback.model_dump_json(indent=2, ensure_ascii=False)))


if __name__ == "__main__":
    main()

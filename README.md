# TravelOS — AI Travel Agent Prototype

LangGraph + SerpAPI prototype that converts a travel request (structured form or natural language) into a structured JSON package with ranked flight and hotel options.

Built as the AI backend foundation for the TravelOS school project — single-shot, stateless, output aligned to the production DB schema.

## Structure

```
prototype_agent/      Main agent code
├── run_agent.py          CLI entry point
├── run_agent_test.py     8-case test suite
├── travel_graph.py       LangGraph graph (parse → search → package)
├── graph_state.py        Pydantic models (aligned to DB schema)
├── serpapi_tools.py      SerpAPI HTTP wrappers
├── requirements.txt
├── README.md             Setup and usage guide
├── CAMBIOS_CAMPOS.md     Field-change reference for the backend team (ES)
├── SIMPLE_GUIDE.md       Non-technical architecture overview
└── docs/
    └── langgraph_migration.md   Architecture deep-dive
```

## Quick start

```bash
cd prototype_agent
python -m venv .venv
.venv/Scripts/activate      # Windows
pip install -r requirements.txt
cp ../.env.example .env     # then fill in your keys
```

```bash
python run_agent.py "Flights from MEX to CDG on 2026-07-15 returning 2026-07-30, and hotel in Paris"
python run_agent_test.py    # run all 8 tests
```

See [`prototype_agent/README.md`](prototype_agent/README.md) for full usage including JSON form input.

## Keys required

| Variable | Where to get it |
|---|---|
| `NVIDIA_API_KEY` | [build.nvidia.com](https://build.nvidia.com) |
| `SERPAPI_API_KEY` | [serpapi.com](https://serpapi.com) |

# Team Research Bot Build

A practical multi-agent project that teaches structured communication using a Researcher → Writer → Fact-Checker → Editor workflow.

The project demonstrates how agent teams pass serialized JSON messages, validate outputs with Pydantic, maintain shared pipeline state, and use a critic-style review loop before returning a final report.

## Prerequisites

- Python 3.10 or 3.11
- VS Code, Jupyter, or another notebook environment
- OpenAI API key for real LLM calls
- No database, Docker, web-search API, or GPU required

The package also supports `USE_MOCK_LLM=true`, which runs a deterministic no-cost version for setup checks and classroom walkthroughs.

## Setup

### Option A — venv

```bash
cd team_research_bot
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### Option B — conda

```bash
cd team_research_bot
conda create -n team-research-bot python=3.11 -y
conda activate team-research-bot
pip install -r requirements.txt
```

### Configure environment

```bash
cp .env.sample .env
```

For the no-cost walkthrough:

```text
USE_MOCK_LLM=true
```

For real OpenAI calls:

```text
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
USE_MOCK_LLM=false
```

## How to run

### Run the notebook

```bash
jupyter notebook notebook.ipynb
```

The notebook walks through:

1. loading the local source pack
2. inspecting schemas
3. creating a serialized agent message
4. running each agent independently
5. running the full pipeline
6. inspecting the saved JSON trace
7. trying validation and debugging exercises

### Run the command-line demo

No-cost mock mode:

```bash
python main.py --mock
```

Real OpenAI mode:

```bash
python main.py --query "What should an organization consider before using AI agents in customer support?"
```

Run smoke tests:

```bash
python tests_smoke.py
```

## What each file does

- `notebook.ipynb` — guided classroom walkthrough for the practical session
- `main.py` — command-line entry point for the complete pipeline
- `schemas.py` — Pydantic contracts for messages, research reports, drafts, checks, and final reports
- `llm.py` — OpenAI JSON wrapper with deterministic mock mode and validation repair
- `prompts.py` — role prompts for each agent
- `source_loader.py` — loads and formats the local markdown source pack
- `orchestrator.py` — coordinates the full multi-agent workflow and saves traces
- `agents/researcher.py` — extracts evidence-backed findings
- `agents/writer.py` — drafts the research brief
- `agents/fact_checker.py` — verifies draft claims against evidence
- `agents/editor.py` — produces the final answer
- `data/source_pack/` — classroom source documents used by the Researcher
- `traces/` — saved run-level JSON traces
- `tests_smoke.py` — quick pre-class checks
- `.env.sample` — environment variable template
- `trainer_guide.md` — live teaching flow, likely questions, and troubleshooting

## Expected output

A successful run prints:

- run ID
- pipeline status
- number of messages passed
- trace file path
- final edited research brief
- key takeaways
- references used

A local trace is saved in `traces/run_XXXXXXXXXX.json`. Open this file to inspect every inter-agent message and intermediate output.

## Estimated API cost

Using the bundled source pack and `gpt-4o-mini`, a full live run is designed to stay comfortably below USD $0.50. Cost increases if you add longer documents, increase revision loops, or replace the source pack with live web search.

Mock mode uses no API calls and costs nothing.

## Troubleshooting

### `OPENAI_API_KEY is missing`

Either add a valid key to `.env` or run:

```bash
python main.py --mock
```

### `Source directory not found`

Run commands from the project root:

```bash
cd team_research_bot
python main.py --mock
```

### JSON validation fails in real LLM mode

The wrapper attempts one repair call automatically. If failures continue, lower the temperature, simplify the schema, or show the class how schema strictness exposes weak agent handoffs.

### Notebook imports fail

Check that Jupyter is running from the `team_research_bot` directory, not the parent directory.

## Further reading

- OpenAI structured outputs and JSON mode documentation
- Pydantic model validation and JSON parsing documentation
- LangSmith tracing documentation for production observability

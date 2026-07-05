# Trainer Guide — Team Research Bot Build

## Demo goal

By the end of the practical, the class should understand that a multi-agent system is not just "many prompts." It is a coordinated workflow where every handoff has:

- a sender and receiver
- a task
- a validated payload
- confidence metadata
- a trace ID
- shared state
- a stop condition for review loops

The final deliverable is a working Researcher → Writer → Fact-Checker → Editor research bot.

## Recommended teaching flow

### 0–10 min — Set the practical frame

Start with the theory deck's main bridge: roles alone are not enough. Roles define responsibility; protocols define reliable handoffs.

Show the source pack and explain why local documents are used: the objective is inter-agent communication, not live web search.

### 10–25 min — Inspect the project structure

Open the project tree. Spend time on:

- `schemas.py` as the contract layer
- `agents/` as role implementation
- `orchestrator.py` as the workflow controller
- `traces/` as the debugging record

Avoid diving into every prompt immediately. First establish the architecture.

### 25–45 min — Teach schemas as contracts

Open `schemas.py` and walk through:

- `AgentMessage`
- `ResearchReport`
- `DraftReport`
- `FactCheckReport`
- `PipelineState`

Key line to emphasize: "A schema is an API contract between two agents."

Run the notebook cells that create a valid message and then intentionally create an invalid confidence value.

### 45–70 min — Run individual agents

Run the Researcher, Writer, Fact-Checker, and Editor independently in the notebook.

Suggested narration:

- Researcher: "Finds evidence, does not write prose."
- Writer: "Writes clearly, but must stay inside the evidence."
- Fact-Checker: "Maps draft claims back to evidence."
- Editor: "Polishes without hiding uncertainty."

Use `USE_MOCK_LLM=true` first so there is no API friction.

### 70–100 min — Run the full orchestrated pipeline

Run the full pipeline from the notebook or CLI:

```bash
python main.py --mock
```

Then open the trace file. Ask the class:

- Which agent produced the first structured payload?
- Where does the draft become reviewable?
- Where would we add a human approval gate?
- What would happen if the Fact-Checker keeps asking for revisions?

### 100–115 min — Real LLM run or controlled variation

If API keys are available, set:

```text
USE_MOCK_LLM=false
OPENAI_API_KEY=...
```

Run the same query with the real model. Compare:

- Does the model obey the schema?
- Are the findings more nuanced?
- Did validation or repair trigger?
- Did the final answer preserve caveats?

### 115–130 min — Debugging drill

Break one thing intentionally:

1. Add an unknown source ID to `source_ids_used`
2. Set an invalid confidence value
3. Remove a required field from a JSON payload

Show how the validation layer catches the problem earlier than a human reading a long transcript.

### 130–155 min — Exercise window

Assign one of these:

- Add a "Compliance Reviewer" agent before the Editor.
- Modify the Researcher schema to include `risk_level`.
- Increase `max_revisions` and inspect how trace length changes.
- Add a new source document and check whether the Researcher uses it.

### 155–160 min — Close

End with this summary:

"Reliable agent collaboration depends on contracts. Prompts define behavior, schemas define handoffs, state defines memory, and traces define debuggability."

## Likely questions and suggested answers

### Why use local sources instead of live web search?

Because the session is about collaboration protocols. Live search introduces API keys, network failures, ranking issues, and freshness questions. Once the protocol works, live tools can replace the local source pack.

### Why not use CrewAI or AutoGen here?

Those frameworks are useful, and earlier framework sessions introduced them. This build intentionally exposes the underlying mechanics: message schemas, state, validation, and orchestration. Frameworks are easier to understand after this layer is clear.

### Why Pydantic?

Pydantic makes schemas executable. It validates that an agent's output has the fields the next agent expects. This is much safer than hoping a plain-text answer is well-formed.

### Is the Fact-Checker the same as Reflexion?

It is Reflexion adapted to a team setting. Instead of one model privately reflecting, a separate role critiques the draft and sends structured revision instructions.

### Why limit revisions?

Without a limit, critic loops can become expensive and unproductive. Production systems need stop conditions.

### Can this become a real product?

Yes, but add production concerns: real retrieval/search tools, observability, auth, human approval gates, data governance, rate limits, and cost monitoring.

## Common errors and fixes

### Missing API key

Use mock mode for setup:

```bash
python main.py --mock
```

### Notebook cannot import local files

Launch Jupyter from the project directory:

```bash
cd team_research_bot
jupyter notebook notebook.ipynb
```

### Model returns invalid JSON

Lower temperature, simplify the schema, show the repair step, or keep mock mode for classroom timing.

### The class confuses state with memory

Explain that memory is the information an agent may use; state is the structured record of this specific run.

### The class over-focuses on prompt wording

Redirect to the bigger lesson: prompts are only one layer. Contracts and state are what make collaboration robust.

## What to skip if running short

Skip:

- Real OpenAI comparison
- Adding a new agent
- Deep prompt editing

Do not skip:

- `AgentMessage`
- `PipelineState`
- full orchestrated run
- trace inspection

## Extension ideas

- Add a Compliance Reviewer agent before final editing.
- Replace the local source pack with a RAG retriever.
- Add LangSmith tracing around each agent call.
- Add a Streamlit UI for query input and trace display.
- Store traces in SQLite for later evaluation.

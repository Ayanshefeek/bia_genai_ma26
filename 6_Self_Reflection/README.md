# Self-Reflection & Critique Practical

Build a writing critic agent that improves a draft through a generate → critique → refine loop.

This practical connects the prompting and ReAct patterns covered earlier with a new capability: the system can judge its own output against explicit criteria, create reflection memory, revise the draft, and stop when a threshold is met.

## Prerequisites

- Python 3.10 or 3.11
- VS Code, Jupyter, or another notebook runner
- An OpenAI API key for live model calls
- Optional: AutoGen packages for the evaluator-agent preview cell

## Setup

Download or clone this folder, then open a terminal in the project root.

### Option A: virtual environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Option B: conda environment

```bash
conda create -n self-reflection-critique python=3.11 -y
conda activate self-reflection-critique
pip install -r requirements.txt
```

### Configure environment variables

```bash
cp .env.sample .env
```

Add your OpenAI API key to `.env`:

```text
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

For a no-network classroom fallback, set:

```text
BIA_OFFLINE_DEMO=true
```

## How to run

### Notebook path

```bash
jupyter notebook notebook.ipynb
```

Run all cells from top to bottom.

### Command-line path

```bash
python main.py
```

The CLI prints the iteration trace and saves outputs to `demo_outputs/`.

### Optional AutoGen preview

AutoGen is only previewed here. Install the optional dependencies when you want to run the AutoGen evaluator-agent cell:

```bash
pip install -r requirements_autogen.txt
```

## What each file does

- `notebook.ipynb` — guided practical walkthrough for the classroom.
- `main.py` — command-line version of the same practical.
- `critic_loop.py` — reusable generate, critique, refine, and loop functions.
- `llm_client.py` — OpenAI client wrapper with JSON mode and offline fallback.
- `prompts.py` — prompt builders for generator, critic, and refiner roles.
- `schemas.py` — Pydantic models for structured evaluator output.
- `autogen_evaluator_preview.py` — optional AutoGen wrapper for a critic agent.
- `data/writing_brief.txt` — main classroom writing task.
- `data/weak_draft.txt` — deliberately weak draft for critique.
- `data/rubric.md` — scoring criteria.
- `data/constitution.md` — principles for safe and useful critique.
- `data/travel_planner_bridge_brief.txt` — bridge to the upcoming travel planner build.
- `.env.sample` — environment variable template.
- `requirements.txt` — pinned core dependencies.
- `requirements_autogen.txt` — pinned optional AutoGen dependencies.
- `trainer_guide.md` — teaching flow, timings, questions, and troubleshooting.

## Expected output

The first critique should usually score the weak draft around the middle of the scale because it is short and professional but vague, hype-heavy, and weak on evidence.

A successful run will show:

- one to three critique iterations,
- structured JSON critique,
- reflection memory after each attempt,
- a final draft that is more specific, credible, and audience-aware,
- saved files in `demo_outputs/`.

## Estimated API cost

With `gpt-4o-mini`, the full demo usually uses a small number of short text calls. A typical classroom run should stay well below ₹50 / US$0.50, depending on current provider pricing, prompt length, and the number of retries.

## Troubleshooting

**`OPENAI_API_KEY was not found`**  
Copy `.env.sample` to `.env`, add the key, and restart the notebook kernel.

**Evaluator output is not valid JSON**  
Re-run the critique cell. If it repeats, lower the model temperature to `0.0` and confirm the prompt still says “Return ONLY valid JSON.”

**AutoGen import error**  
The AutoGen preview uses a separate optional requirements file. Run `pip install -r requirements_autogen.txt`.

**The loop keeps improving without stopping**  
Reduce the passing threshold to 7 for a quick classroom demo, or increase `max_iterations` for deeper refinement.

## Further reading

- Reflexion: Language Agents with Verbal Reinforcement Learning — https://arxiv.org/abs/2303.11366
- Self-Refine: Iterative Refinement with Self-Feedback — https://arxiv.org/abs/2303.17651
- Constitutional AI: Harmlessness from AI Feedback — https://arxiv.org/abs/2212.08073
- OpenAI Python SDK — https://pypi.org/project/openai/
- AutoGen AgentChat documentation — https://microsoft.github.io/autogen/stable/

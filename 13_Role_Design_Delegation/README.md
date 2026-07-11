# Role-Design & Delegation Practical Package

This package teaches how to convert multi-agent team design into concrete artifacts: role cards, RACI ownership, handoff contracts, incentive-risk controls, and a build-ready blueprint for a research bot.

The practical is intentionally **framework-light**. It prepares the team design before the next build session turns the blueprint into working agents.

---

## Prerequisites

- Python 3.10 or 3.11 recommended
- VS Code, Jupyter, or another notebook environment
- Basic Python familiarity
- No GPU required
- OpenAI API key is optional only for the LLM critique section

The main validator runs offline. The optional LLM critique uses `gpt-4o-mini` by default and can be skipped.

---

## Setup

### Option A: venv

```bash
cd role_design_delegation
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

### Option B: conda

```bash
cd role_design_delegation
conda create -n role-design-delegation python=3.11 -y
conda activate role-design-delegation
pip install -r requirements.txt
```

### Configure environment variables

```bash
cp .env.sample .env
```

Fill `OPENAI_API_KEY` only if the trainer wants to run the optional LLM critique.

---

## How to run

### 1. Run the notebook

Open:

```text
notebook.ipynb
```

Run all cells from top to bottom. The notebook walks through:

1. Loading the research-bot blueprint
2. Inspecting role cards
3. Validating RACI ownership
4. Reviewing handoff contracts
5. Scanning incentive risks
6. Debugging an intentionally flawed blueprint
7. Optional LLM critique

### 2. Run the validator from terminal

Validate the good sample:

```bash
python run_blueprint_check.py data/sample_research_bot_blueprint.json
```

Validate the flawed sample:

```bash
python run_blueprint_check.py data/flawed_research_bot_blueprint.json
```

Save a report:

```bash
python run_blueprint_check.py data/sample_research_bot_blueprint.json --save outputs/sample_report.txt
```

### 3. Run tests

```bash
pytest -q
```

---

## What each file does

```text
notebook.ipynb
```

Main classroom practical notebook.

```text
role_models.py
```

Pydantic data models for role cards, RACI entries, handoff contracts, incentive policy, and loop controls.

```text
validators.py
```

Deterministic design validators that identify role conflicts, RACI gaps, weak handoffs, incentive risks, and loop-control problems.

```text
llm_reviewer.py
```

Optional OpenAI-powered blueprint critique. The package works without it.

```text
run_blueprint_check.py
```

Command-line validator for blueprint JSON files.

```text
data/sample_research_bot_blueprint.json
```

Build-ready example for an evidence-backed research bot.

```text
data/flawed_research_bot_blueprint.json
```

Intentionally broken blueprint for the classroom debugging exercise.

```text
data/blank_role_card_template.json
```

Starter template for designing a new role.

```text
data/handoff_contract_template.json
```

Starter template for defining role-to-role handoffs.

```text
data/raci_worksheet.csv
```

Editable RACI worksheet.

```text
docs/
```

Facilitation worksheets, rubrics, and handout material.

```text
tests/
```

Small regression tests for validators.

---

## Expected output

For the good blueprint, the validator should report a high score and either no findings or a small number of improvement suggestions.

For the flawed blueprint, the validator should flag issues such as:

- Missing Responsible or Accountable owners
- Unknown role references
- Multiple roles owning the same final output
- Missing handoff schemas
- Missing stop conditions
- Speed/cost-only incentive policy
- Missing termination rule

---

## Estimated API cost

The core practical costs **₹0 / $0** because it runs offline.

The optional LLM critique uses the configured OpenAI model. With `gpt-4o-mini`, the bundled sample blueprint is expected to cost only a few cents or less per run, depending on current provider pricing and token usage.

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'pydantic'`

Run:

```bash
pip install -r requirements.txt
```

Make sure the terminal and notebook use the same Python environment.

### `OPENAI_API_KEY is not set`

This is only needed for the optional LLM critique. The offline validators still work.

### `ValidationError` when editing JSON

Check that every JSON field uses the expected type. Lists must use square brackets, strings must use quotes, and commas must be valid JSON.

### The notebook cannot import local files

Open the notebook from the package root folder, not from inside the `data/` folder.

---

## Further reading

- Pydantic documentation: https://docs.pydantic.dev/
- OpenAI Python SDK: https://github.com/openai/openai-python
- RACI overview: https://en.wikipedia.org/wiki/Responsibility_assignment_matrix
- Agent design pattern reference: revisit the manager-worker and critic patterns from earlier course sessions

# Student Worksheet — Role-Design & Delegation

## Practical challenge

Design a multi-agent team for an evidence-backed research bot.

Your team should answer a user question by researching evidence, drafting a response, checking claims, and producing a final answer.

---

## Step 1 — Choose roles

Minimum recommended roles:

- Editor Orchestrator
- Researcher
- Writer
- Fact-Checker
- Memory Manager or memory component

Optional roles:

- Planner
- Compliance Reviewer
- Tool Specialist

For each role, define:

```text
Role name:
Mission:
Inputs expected:
Outputs owned:
Decision rights:
Stop conditions:
Escalation path:
Failure modes:
```

---

## Step 2 — Build RACI

Use the worksheet in `data/raci_worksheet.csv`.

Check every task:

- Does it have at least one Responsible role?
- Does it have exactly one Accountable role?
- Are Consulted roles truly needed?
- Are Informed roles not overloaded?
- Is the expected artifact clear?
- Is "done" measurable?

---

## Step 3 — Write handoff contracts

Create at least two handoff contracts:

1. Researcher → Writer
2. Writer → Fact-Checker

For each contract:

```text
Source role:
Target role:
Trigger:
Required input fields:
Required output fields:
Quality checks:
Retry policy:
Escalation path:
Logging fields:
```

---

## Step 4 — Scan incentives

Complete these prompts:

```text
If the Researcher optimizes for speed, the failure is:
Mitigation:

If the Writer optimizes for polish, the failure is:
Mitigation:

If the Fact-Checker optimizes for finding issues, the failure is:
Mitigation:

If the Editor optimizes for cost, the failure is:
Mitigation:
```

---

## Step 5 — Run the validator

Run:

```bash
python run_blueprint_check.py data/sample_research_bot_blueprint.json
```

Then edit a copy of the sample blueprint and run:

```bash
python run_blueprint_check.py your_blueprint.json
```

The goal is not a perfect score. The goal is to make design problems visible before implementation.

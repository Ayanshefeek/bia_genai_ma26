# AgentOps & Production Scaling – Guardrails & Safety (Practical Package)

This folder contains the **hands-on material** for the Guardrails & Safety session.  
You’ll implement filters, safety prompts, and a red-team drill using open-source tools.

## Structure
```
agentops-guardrails-safety/
├── app/
│   ├── regex_filter.py
│   ├── semantic_filter.py
│   ├── policy_prompt_demo.py
│   ├── red_team_test.py
│   └── utils.py
├── notebooks/
│   ├── 01_regex_semantic_demo.ipynb
│   └── 02_redteam_evaluation.ipynb
├── .env.example
├── README.md
├── README_trainer.md
└── requirements.txt
```

## Quick Start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your OpenAI API key
```
Then run any demo under `app/` or open the notebooks.

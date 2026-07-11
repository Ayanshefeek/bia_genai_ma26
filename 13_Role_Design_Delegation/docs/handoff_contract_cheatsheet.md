# Handoff Contract Cheatsheet

A handoff contract is the API between roles.

## Bad handoff

```text
Researcher sends notes to Writer.
```

Why it fails:

- "Notes" is undefined.
- Writer does not know which claims are supported.
- Fact-Checker cannot trace claims back to evidence.
- No retry or escalation rule exists.

## Better handoff

```json
{
  "claims": [
    {
      "claim_id": "C1",
      "text": "Claim written as one checkable statement",
      "source_label": "S1",
      "confidence": "medium",
      "limitations": "Only one source supports this"
    }
  ],
  "evidence_gaps": [
    "Missing recent data for market size"
  ]
}
```

Why it works:

- Claims are atomic.
- Sources are traceable.
- Confidence is visible.
- Gaps are not hidden.
- The next role can validate the artifact.

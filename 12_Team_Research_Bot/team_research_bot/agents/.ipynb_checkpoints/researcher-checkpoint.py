"""Researcher agent: extracts evidence-backed findings from local sources."""

from __future__ import annotations

import json

from llm import StructuredLLMClient
from prompts import RESEARCHER_SYSTEM_PROMPT, schema_instruction
from schemas import EvidenceItem, ResearchFinding, ResearchReport
from source_loader import (
    SourceDocument,
    first_relevant_snippet,
    keyword_overlap_score,
    render_sources_for_prompt,
    top_sources_by_overlap,
)


class ResearcherAgent:
    """Agent responsible for evidence gathering."""

    def __init__(self, llm_client: StructuredLLMClient) -> None:
        """Create a Researcher agent."""

        self.llm_client = llm_client

    def run(self, query: str, documents: list[SourceDocument]) -> ResearchReport:
        """Extract evidence-backed findings for a user query.

        Args:
            query: User research question.
            documents: Local source pack.

        Returns:
            Validated ResearchReport.
        """

        source_block = render_sources_for_prompt(documents)
        schema_json = json.dumps(ResearchReport.model_json_schema(), indent=2)
        user_prompt = (
            f"User query: {query}\n\n"
            f"Available sources:\n{source_block}\n\n"
            f"{schema_instruction(schema_json)}"
        )
        return self.llm_client.complete_json(
            system_prompt=RESEARCHER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_schema=ResearchReport,
            fallback_factory=lambda: self._mock_report(query, documents),
        )

    def _mock_report(self, query: str, documents: list[SourceDocument]) -> ResearchReport:
        """Create deterministic findings for no-key classroom mode."""

        selected = top_sources_by_overlap(query, documents, limit=3)
        findings: list[ResearchFinding] = []

        for doc in selected:
            score = max(0.45, keyword_overlap_score(query, doc.text))
            evidence = EvidenceItem(
                source_id=doc.source_id,
                title=doc.title,
                snippet=first_relevant_snippet(doc.text, query),
                relevance_score=round(score, 2),
            )
            if "customer" in query.lower() or "support" in query.lower():
                claim = (
                    f"{doc.title} shows that AI-assisted customer support works best "
                    f"when automation is paired with escalation paths and quality controls."
                )
            elif "hiring" in query.lower() or "recruit" in query.lower():
                claim = (
                    f"{doc.title} indicates that AI hiring workflows need human review, "
                    f"bias checks, and clear audit trails before operational use."
                )
            elif "health" in query.lower() or "clinical" in query.lower():
                claim = (
                    f"{doc.title} suggests that healthcare administrative agents should "
                    f"prioritize de-identification, review gates, and traceability."
                )
            else:
                claim = (
                    f"{doc.title} provides evidence relevant to the query, especially around "
                    f"governance, workflow integration, and measurable operational outcomes."
                )
            findings.append(
                ResearchFinding(
                    claim=claim,
                    evidence=[evidence],
                    confidence=round(min(0.9, 0.55 + score), 2),
                    limitations=(
                        "The source pack is intentionally small, so this finding should be "
                        "treated as classroom evidence rather than exhaustive market research."
                    ),
                )
            )

        return ResearchReport(
            topic=query,
            findings=findings,
            unresolved_questions=[
                "Would live external sources confirm the same pattern today?",
                "Which organization-specific constraints would change the recommendation?",
            ],
            overall_confidence=0.74,
        )

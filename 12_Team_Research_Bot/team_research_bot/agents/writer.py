"""Writer agent: converts structured research into a draft report."""

from __future__ import annotations

import json

from llm import StructuredLLMClient
from prompts import WRITER_SYSTEM_PROMPT, schema_instruction
from schemas import DraftReport, DraftSection, FactCheckReport, ResearchReport


class WriterAgent:
    """Agent responsible for drafting the answer."""

    def __init__(self, llm_client: StructuredLLMClient) -> None:
        """Create a Writer agent."""

        self.llm_client = llm_client

    def run(
        self,
        query: str,
        research_report: ResearchReport,
        fact_check_report: FactCheckReport | None = None,
    ) -> DraftReport:
        """Write or revise a draft based on research findings.

        Args:
            query: User research question.
            research_report: Evidence-backed research report.
            fact_check_report: Optional critique to address in a revision.

        Returns:
            Validated DraftReport.
        """

        schema_json = json.dumps(DraftReport.model_json_schema(), indent=2)
        critique_block = (
            "\n\nFact-check critique to address:\n"
            f"{fact_check_report.model_dump_json(indent=2)}"
            if fact_check_report
            else ""
        )
        user_prompt = (
            f"User query: {query}\n\n"
            f"Research report:\n{research_report.model_dump_json(indent=2)}"
            f"{critique_block}\n\n"
            f"{schema_instruction(schema_json)}"
        )

        return self.llm_client.complete_json(
            system_prompt=WRITER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_schema=DraftReport,
            fallback_factory=lambda: self._mock_draft(query, research_report, fact_check_report),
        )

    def _mock_draft(
        self,
        query: str,
        research_report: ResearchReport,
        fact_check_report: FactCheckReport | None,
    ) -> DraftReport:
        """Create a deterministic classroom draft."""

        source_ids = sorted(
            {
                evidence.source_id
                for finding in research_report.findings
                for evidence in finding.evidence
            }
        )
        sections: list[DraftSection] = []
        for index, finding in enumerate(research_report.findings, start=1):
            content = (
                f"{finding.claim} The supporting evidence comes from "
                f"{', '.join(e.source_id for e in finding.evidence)}. "
                f"The practical implication is to design the workflow with clear ownership, "
                f"logged decisions, and an explicit point where a human or reviewer can intervene."
            )
            sections.append(
                DraftSection(
                    heading=f"Finding {index}: Evidence-backed design implication",
                    content=content,
                    claim_ids=[index - 1],
                )
            )

        summary_prefix = "Revised draft" if fact_check_report else "Initial draft"
        return DraftReport(
            title=f"Research Brief: {query}",
            executive_summary=(
                f"{summary_prefix}: The source pack suggests that this topic should be handled "
                f"as a workflow design problem, not just a model-selection problem. The strongest "
                f"pattern is to combine automation with evidence tracking, review gates, and "
                f"clear escalation criteria."
            ),
            sections=sections,
            risks_or_uncertainties=[
                "The sample sources are limited and should not be treated as live market coverage.",
                "Recommendations may change when real organization policies or regulations are added.",
            ],
            source_ids_used=source_ids,
        )

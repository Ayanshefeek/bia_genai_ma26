"""Fact-Checker agent: verifies draft claims against research findings."""

from __future__ import annotations

import json

from llm import StructuredLLMClient
from prompts import FACT_CHECKER_SYSTEM_PROMPT, schema_instruction
from schemas import ClaimCheck, DraftReport, FactCheckReport, ResearchReport


class FactCheckerAgent:
    """Agent responsible for claim-level verification."""

    def __init__(self, llm_client: StructuredLLMClient) -> None:
        """Create a Fact-Checker agent."""

        self.llm_client = llm_client

    def run(self, draft_report: DraftReport, research_report: ResearchReport) -> FactCheckReport:
        """Check a draft against available evidence.

        Args:
            draft_report: Writer's draft.
            research_report: Researcher output.

        Returns:
            Validated FactCheckReport.
        """

        schema_json = json.dumps(FactCheckReport.model_json_schema(), indent=2)
        user_prompt = (
            f"Draft report:\n{draft_report.model_dump_json(indent=2)}\n\n"
            f"Research report:\n{research_report.model_dump_json(indent=2)}\n\n"
            f"{schema_instruction(schema_json)}"
        )

        return self.llm_client.complete_json(
            system_prompt=FACT_CHECKER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_schema=FactCheckReport,
            fallback_factory=lambda: self._mock_fact_check(draft_report, research_report),
        )

    def _mock_fact_check(
        self,
        draft_report: DraftReport,
        research_report: ResearchReport,
    ) -> FactCheckReport:
        """Create deterministic fact checks for no-key classroom mode."""

        known_source_ids = {
            evidence.source_id
            for finding in research_report.findings
            for evidence in finding.evidence
        }
        checks: list[ClaimCheck] = []

        for section in draft_report.sections:
            used_sources = set(draft_report.source_ids_used)
            unsupported_sources = sorted(used_sources - known_source_ids)
            verdict = "supported" if not unsupported_sources else "partially_supported"
            issue = (
                "The claim is grounded in the research report."
                if verdict == "supported"
                else f"The draft references unknown sources: {unsupported_sources}."
            )
            recommendation = (
                "Keep the claim and preserve source references."
                if verdict == "supported"
                else "Remove unknown source references or send the task back to the Researcher."
            )
            checks.append(
                ClaimCheck(
                    claim=section.heading,
                    verdict=verdict,
                    evidence_refs=sorted(known_source_ids),
                    issue=issue,
                    recommendation=recommendation,
                )
            )

        revision_required = any(check.verdict != "supported" for check in checks)
        return FactCheckReport(
            checks=checks,
            summary=(
                "Most claims are supported by the bundled source pack. "
                "Limitations should remain visible because the research set is intentionally small."
            ),
            revision_required=revision_required,
            overall_reliability=0.82 if not revision_required else 0.66,
        )

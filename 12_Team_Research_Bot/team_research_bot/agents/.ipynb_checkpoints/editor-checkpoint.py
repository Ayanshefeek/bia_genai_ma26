"""Editor agent: produces the final evidence-grounded answer."""

from __future__ import annotations

import json

from llm import StructuredLLMClient
from prompts import EDITOR_SYSTEM_PROMPT, schema_instruction
from schemas import DraftReport, FactCheckReport, FinalReport


class EditorAgent:
    """Agent responsible for final answer quality."""

    def __init__(self, llm_client: StructuredLLMClient) -> None:
        """Create an Editor agent."""

        self.llm_client = llm_client

    def run(self, draft_report: DraftReport, fact_check_report: FactCheckReport) -> FinalReport:
        """Create a polished final report.

        Args:
            draft_report: Latest writer draft.
            fact_check_report: Fact-checker critique.

        Returns:
            Validated FinalReport.
        """

        schema_json = json.dumps(FinalReport.model_json_schema(), indent=2)
        user_prompt = (
            f"Draft report:\n{draft_report.model_dump_json(indent=2)}\n\n"
            f"Fact-check report:\n{fact_check_report.model_dump_json(indent=2)}\n\n"
            f"{schema_instruction(schema_json)}"
        )

        return self.llm_client.complete_json(
            system_prompt=EDITOR_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_schema=FinalReport,
            fallback_factory=lambda: self._mock_final(draft_report, fact_check_report),
        )

    def _mock_final(
        self,
        draft_report: DraftReport,
        fact_check_report: FactCheckReport,
    ) -> FinalReport:
        """Create deterministic final answer for no-key classroom mode."""

        supported_sections = [
            section
            for section, check in zip(draft_report.sections, fact_check_report.checks, strict=False)
            if check.verdict in {"supported", "partially_supported"}
        ]
        body_parts = [
            draft_report.executive_summary,
            *[f"{section.heading}: {section.content}" for section in supported_sections],
        ]
        return FinalReport(
            title=draft_report.title,
            final_answer="\n\n".join(body_parts),
            key_takeaways=[
                "Use structured handoffs so each agent receives exactly the fields it needs.",
                "Keep source IDs attached to claims so review agents can verify evidence quickly.",
                "Use a revision limit to prevent critic loops from becoming infinite.",
            ],
            caveats=draft_report.risks_or_uncertainties,
            references=draft_report.source_ids_used,
            editor_notes=(
                "Unsupported or uncertain claims were softened. The final answer keeps caveats "
                "visible instead of hiding uncertainty."
            ),
        )

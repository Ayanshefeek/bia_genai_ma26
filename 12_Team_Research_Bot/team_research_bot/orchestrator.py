"""Orchestrator for the Team Research Bot pipeline."""

from __future__ import annotations

from pathlib import Path

from agents.editor import EditorAgent
from agents.fact_checker import FactCheckerAgent
from agents.researcher import ResearcherAgent
from agents.writer import WriterAgent
from llm import StructuredLLMClient
from schemas import AgentRole, MessageType, PipelineState, make_message
from source_loader import SourceDocument


class ResearchBotOrchestrator:
    """Coordinates the multi-agent research workflow."""

    def __init__(
        self,
        llm_client: StructuredLLMClient,
        documents: list[SourceDocument],
        trace_dir: str | Path = "traces",
        max_revisions: int = 1,
    ) -> None:
        """Create the orchestrator and agent instances.

        Args:
            llm_client: Shared LLM client.
            documents: Local source pack.
            trace_dir: Directory where JSON traces are saved.
            max_revisions: Maximum Writer revision attempts after fact-checking.
        """

        self.documents = documents
        self.trace_dir = Path(trace_dir)
        self.trace_dir.mkdir(parents=True, exist_ok=True)
        self.max_revisions = max_revisions

        self.researcher = ResearcherAgent(llm_client)
        self.writer = WriterAgent(llm_client)
        self.fact_checker = FactCheckerAgent(llm_client)
        self.editor = EditorAgent(llm_client)

    def run(self, user_query: str) -> PipelineState:
        """Run the full Researcher → Writer → Fact-Checker → Editor pipeline.

        Args:
            user_query: Research question from the user.

        Returns:
            Completed PipelineState with messages and final report.
        """

        state = PipelineState(
            user_query=user_query,
            max_revisions=self.max_revisions,
            status="running",
        )

        try:
            research = self.researcher.run(user_query, self.documents)
            state.research_report = research
            state.source_ids_consulted = sorted(
                {
                    evidence.source_id
                    for finding in research.findings
                    for evidence in finding.evidence
                }
            )
            state.messages.append(
                make_message(
                    sender=AgentRole.RESEARCHER,
                    receiver=AgentRole.WRITER,
                    message_type=MessageType.RESULT,
                    task="Use these evidence-backed findings to draft a research brief.",
                    payload_model=research,
                    confidence=research.overall_confidence,
                )
            )

            draft = self.writer.run(user_query, research)
            state.draft_report = draft
            state.messages.append(
                make_message(
                    sender=AgentRole.WRITER,
                    receiver=AgentRole.FACT_CHECKER,
                    message_type=MessageType.RESULT,
                    task="Check this draft against the Researcher evidence.",
                    payload_model=draft,
                    confidence=0.72,
                )
            )

            fact_check = self.fact_checker.run(draft, research)
            state.fact_check_report = fact_check
            state.messages.append(
                make_message(
                    sender=AgentRole.FACT_CHECKER,
                    receiver=AgentRole.WRITER if fact_check.revision_required else AgentRole.EDITOR,
                    message_type=MessageType.CRITIQUE,
                    task="Revise the draft if needed; otherwise prepare final editing.",
                    payload_model=fact_check,
                    confidence=fact_check.overall_reliability,
                )
            )

            if fact_check.revision_required and state.revision_count < state.max_revisions:
                state.status = "needs_revision"
                state.revision_count += 1
                draft = self.writer.run(user_query, research, fact_check)
                state.draft_report = draft
                state.messages.append(
                    make_message(
                        sender=AgentRole.WRITER,
                        receiver=AgentRole.FACT_CHECKER,
                        message_type=MessageType.RESULT,
                        task="Check the revised draft against the Researcher evidence.",
                        payload_model=draft,
                        confidence=0.78,
                    )
                )
                fact_check = self.fact_checker.run(draft, research)
                state.fact_check_report = fact_check
                state.messages.append(
                    make_message(
                        sender=AgentRole.FACT_CHECKER,
                        receiver=AgentRole.EDITOR,
                        message_type=MessageType.CRITIQUE,
                        task="Use this final check to produce the final answer.",
                        payload_model=fact_check,
                        confidence=fact_check.overall_reliability,
                    )
                )

            if state.draft_report is None or state.fact_check_report is None:
                raise RuntimeError("Pipeline reached editing without a draft or fact-check report.")

            final = self.editor.run(state.draft_report, state.fact_check_report)
            state.final_report = final
            state.status = "completed"
            state.messages.append(
                make_message(
                    sender=AgentRole.EDITOR,
                    receiver=AgentRole.ORCHESTRATOR,
                    message_type=MessageType.FINAL,
                    task="Return the final answer to the user.",
                    payload_model=final,
                    confidence=state.fact_check_report.overall_reliability,
                )
            )

        except Exception as exc:  # noqa: BLE001 - teaching demo should capture and show failures.
            state.status = "failed"
            state.errors.append(str(exc))

        self.save_trace(state)
        return state

    def save_trace(self, state: PipelineState) -> Path:
        """Save the pipeline trace as JSON for inspection.

        Args:
            state: Current pipeline state.

        Returns:
            Path to saved trace file.
        """

        trace_path = self.trace_dir / f"{state.run_id}.json"
        trace_path.write_text(state.model_dump_json(indent=2), encoding="utf-8")
        return trace_path

    @staticmethod
    def pretty_message_table(state: PipelineState) -> list[dict[str, str]]:
        """Return a simple message table for notebook display."""

        rows: list[dict[str, str]] = []
        for message in state.messages:
            rows.append(
                {
                    "trace_id": message.trace_id,
                    "sender": message.sender.value,
                    "receiver": message.receiver.value,
                    "type": message.message_type.value,
                    "task": message.task[:80],
                }
            )
        return rows

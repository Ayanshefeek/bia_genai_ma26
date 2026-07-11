"""Validation utilities for multi-agent role-design blueprints.

These checks turn design concepts into concrete feedback:
- Does every task have an owner?
- Is there exactly one accountable role per task?
- Are handoffs explicit enough to implement?
- Are incentives balanced instead of over-optimizing speed or cost?
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

from pydantic import ValidationError

from role_models import AgentTeamBlueprint, Severity


Finding = Dict[str, str]


def make_finding(severity: Severity, area: str, message: str, recommendation: str) -> Finding:
    """Create a normalized validation finding."""
    return {
        "severity": severity.value,
        "area": area,
        "message": message,
        "recommendation": recommendation,
    }


def load_blueprint(path: str | Path) -> AgentTeamBlueprint:
    """Load and parse an AgentTeamBlueprint from a JSON file.

    Args:
        path: Path to a blueprint JSON file.

    Returns:
        Parsed AgentTeamBlueprint.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValidationError: If the JSON does not match the Pydantic schema.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    blueprint_path = Path(path)
    data = json.loads(blueprint_path.read_text(encoding="utf-8"))
    return AgentTeamBlueprint.model_validate(data)


def known_role_names(blueprint: AgentTeamBlueprint) -> set[str]:
    """Return the set of valid role names for a blueprint."""
    return set(blueprint.role_names)


def validate_role_cards(blueprint: AgentTeamBlueprint) -> List[Finding]:
    """Validate completeness and boundaries of role cards."""
    findings: List[Finding] = []
    names = blueprint.role_names

    if len(names) != len(set(names)):
        findings.append(
            make_finding(
                Severity.ERROR,
                "Role cards",
                "At least two role cards use the same name.",
                "Give each role a unique name so RACI and handoffs are unambiguous.",
            )
        )

    output_owners: Dict[str, List[str]] = {}
    for role in blueprint.roles:
        for output in role.outputs_owned:
            normalized = output.strip().lower()
            if normalized:
                output_owners.setdefault(normalized, []).append(role.name)

        required_lists = {
            "responsibilities": role.responsibilities,
            "decision rights": role.decision_rights,
            "outputs owned": role.outputs_owned,
            "success metrics": role.success_metrics,
            "failure modes": role.failure_modes,
            "stop conditions": role.stop_conditions,
        }
        for label, values in required_lists.items():
            if not values:
                findings.append(
                    make_finding(
                        Severity.WARNING,
                        "Role cards",
                        f"{role.name} has no {label}.",
                        f"Add 2-4 concrete {label} so the role is implementable.",
                    )
                )

        if role.max_iterations > 3 and role.role_type.value in {"Critic", "Fact-Checker"}:
            findings.append(
                make_finding(
                    Severity.WARNING,
                    "Loop control",
                    f"{role.name} can iterate {role.max_iterations} times.",
                    "Critic-style roles should usually have a low iteration cap to avoid endless review loops.",
                )
            )

    for output, owners in output_owners.items():
        if len(owners) > 1:
            findings.append(
                make_finding(
                    Severity.WARNING,
                    "Role conflict",
                    f"The output '{output}' is owned by multiple roles: {', '.join(owners)}.",
                    "Choose one Accountable owner and make other roles Consulted or Responsible only.",
                )
            )

    return findings


def _unknown_roles(references: Iterable[str], valid_names: set[str]) -> List[str]:
    """Return role references that are not present in the blueprint."""
    return sorted({name for name in references if name and name not in valid_names})


def validate_raci(blueprint: AgentTeamBlueprint) -> List[Finding]:
    """Validate RACI rows for ownership, accountability, and role references."""
    findings: List[Finding] = []
    valid_names = known_role_names(blueprint)

    if not blueprint.raci:
        return [
            make_finding(
                Severity.ERROR,
                "RACI",
                "The blueprint has no RACI entries.",
                "Add one row per major task before implementation begins.",
            )
        ]

    final_accountable_tasks = []
    for entry in blueprint.raci:
        if not entry.responsible:
            findings.append(
                make_finding(
                    Severity.ERROR,
                    "RACI",
                    f"'{entry.task}' has no Responsible role.",
                    "Assign at least one role that performs the work.",
                )
            )

        if not entry.accountable or not entry.accountable.strip():
            findings.append(
                make_finding(
                    Severity.ERROR,
                    "RACI",
                    f"'{entry.task}' has no Accountable role.",
                    "Assign exactly one Accountable role that signs off on the task.",
                )
            )

        all_refs = list(entry.responsible) + [entry.accountable] + list(entry.consulted) + list(entry.informed)
        unknown = _unknown_roles(all_refs, valid_names)
        if unknown:
            findings.append(
                make_finding(
                    Severity.ERROR,
                    "RACI",
                    f"'{entry.task}' references unknown role(s): {', '.join(unknown)}.",
                    "Use only names defined in role cards, or add the missing role cards.",
                )
            )

        if entry.accountable in entry.informed:
            findings.append(
                make_finding(
                    Severity.WARNING,
                    "RACI",
                    f"'{entry.task}' lists {entry.accountable} as both Accountable and Informed.",
                    "The Accountable role already receives task context; remove it from Informed.",
                )
            )

        if not entry.acceptance_criteria:
            findings.append(
                make_finding(
                    Severity.WARNING,
                    "RACI",
                    f"'{entry.task}' has no acceptance criteria.",
                    "Define what 'done' means so agents know when to stop.",
                )
            )

        if any(word in entry.task.lower() for word in ["final", "publish", "submit", "approve"]):
            final_accountable_tasks.append(entry)

    if not final_accountable_tasks:
        findings.append(
            make_finding(
                Severity.WARNING,
                "RACI",
                "No final sign-off task was found.",
                "Add a final approval/finalize task with one Accountable owner.",
            )
        )

    return findings


def validate_handoff_contracts(blueprint: AgentTeamBlueprint) -> List[Finding]:
    """Validate handoff contracts for schemas, retry rules, and escalation paths."""
    findings: List[Finding] = []
    valid_names = known_role_names(blueprint)

    if not blueprint.handoff_contracts:
        return [
            make_finding(
                Severity.ERROR,
                "Handoff contracts",
                "No handoff contracts are defined.",
                "Add at least one contract for every role-to-role transfer.",
            )
        ]

    for contract in blueprint.handoff_contracts:
        unknown = _unknown_roles([contract.source_role, contract.target_role], valid_names)
        if unknown:
            findings.append(
                make_finding(
                    Severity.ERROR,
                    "Handoff contracts",
                    f"'{contract.name}' references unknown role(s): {', '.join(unknown)}.",
                    "Use role names exactly as defined in the role cards.",
                )
            )

        if not contract.input_schema:
            findings.append(
                make_finding(
                    Severity.ERROR,
                    "Handoff contracts",
                    f"'{contract.name}' has no input schema.",
                    "List required input fields and their meaning.",
                )
            )

        if not contract.output_schema:
            findings.append(
                make_finding(
                    Severity.ERROR,
                    "Handoff contracts",
                    f"'{contract.name}' has no output schema.",
                    "List required output fields and their meaning.",
                )
            )

        for label, values in {
            "quality checks": contract.quality_checks,
            "stop conditions": contract.stop_conditions,
            "logging fields": contract.logging_fields,
        }.items():
            if not values:
                findings.append(
                    make_finding(
                        Severity.WARNING,
                        "Handoff contracts",
                        f"'{contract.name}' has no {label}.",
                        f"Add concrete {label}; otherwise implementation will rely on vague prompts.",
                    )
                )

        if not contract.retry_policy.strip():
            findings.append(
                make_finding(
                    Severity.WARNING,
                    "Handoff contracts",
                    f"'{contract.name}' has no retry policy.",
                    "Define when to retry, how many times, and when to escalate.",
                )
            )

        if not contract.escalation_path.strip():
            findings.append(
                make_finding(
                    Severity.WARNING,
                    "Handoff contracts",
                    f"'{contract.name}' has no escalation path.",
                    "Name the role that resolves failed handoffs.",
                )
            )

    return findings


def validate_incentives(blueprint: AgentTeamBlueprint) -> List[Finding]:
    """Detect incentive policies that encourage shallow or unsafe behavior."""
    findings: List[Finding] = []
    policy = blueprint.incentive_policy
    combined = " ".join(
        [policy.primary_success_metric]
        + policy.balancing_metrics
        + policy.anti_goals
        + policy.incentive_risks
        + policy.mitigation_rules
    ).lower()

    required_dimensions = {
        "evidence": ["evidence", "source", "citation", "claim"],
        "correctness": ["correct", "accurate", "faithful", "verified"],
        "safety": ["safe", "privacy", "pii", "injection", "policy"],
        "completion": ["complete", "coverage", "answer", "useful"],
    }

    for dimension, keywords in required_dimensions.items():
        if not any(keyword in combined for keyword in keywords):
            findings.append(
                make_finding(
                    Severity.WARNING,
                    "Incentive alignment",
                    f"The incentive policy does not clearly mention {dimension}.",
                    f"Add at least one metric or anti-goal covering {dimension}.",
                )
            )

    risky_primary = ["speed", "fast", "low cost", "cheap", "token"]
    if any(keyword in policy.primary_success_metric.lower() for keyword in risky_primary):
        findings.append(
            make_finding(
                Severity.WARNING,
                "Incentive alignment",
                "The primary success metric focuses on speed or cost.",
                "Use speed/cost as balancing metrics, not as the only definition of success.",
            )
        )

    if not policy.mitigation_rules:
        findings.append(
            make_finding(
                Severity.ERROR,
                "Incentive alignment",
                "No mitigation rules are defined for incentive risks.",
                "Add rules such as 'unsupported claims must be removed' or 'escalate after two failed verification cycles'.",
            )
        )

    return findings


def validate_loop_controls(blueprint: AgentTeamBlueprint) -> List[Finding]:
    """Validate controls that prevent runaway replanning, review, or revision loops."""
    findings: List[Finding] = []
    loop_control = blueprint.loop_control

    if loop_control.max_revision_cycles > 3:
        findings.append(
            make_finding(
                Severity.WARNING,
                "Loop control",
                "The team allows more than three revision cycles.",
                "Keep revision cycles low for classroom and production cost control.",
            )
        )

    if not loop_control.human_escalation_rule.strip():
        findings.append(
            make_finding(
                Severity.WARNING,
                "Loop control",
                "No human escalation rule is defined.",
                "Define when the system should stop and ask for human judgment.",
            )
        )

    if not loop_control.termination_rule.strip():
        findings.append(
            make_finding(
                Severity.ERROR,
                "Loop control",
                "No termination rule is defined.",
                "Define the condition that ends the workflow.",
            )
        )

    return findings


def validate_blueprint(blueprint: AgentTeamBlueprint) -> List[Finding]:
    """Run all validation checks on a blueprint.

    Args:
        blueprint: Parsed agent team blueprint.

    Returns:
        Ordered list of validation findings.
    """
    findings: List[Finding] = []
    findings.extend(validate_role_cards(blueprint))
    findings.extend(validate_raci(blueprint))
    findings.extend(validate_handoff_contracts(blueprint))
    findings.extend(validate_incentives(blueprint))
    findings.extend(validate_loop_controls(blueprint))
    return findings


def score_blueprint(findings: Sequence[Finding]) -> Dict[str, Any]:
    """Convert validation findings into a simple teaching score.

    Args:
        findings: Validation findings from validate_blueprint().

    Returns:
        Score summary with counts and a 0-100 score.
    """
    errors = sum(1 for finding in findings if finding["severity"] == Severity.ERROR.value)
    warnings = sum(1 for finding in findings if finding["severity"] == Severity.WARNING.value)
    infos = sum(1 for finding in findings if finding["severity"] == Severity.INFO.value)

    score = max(0, 100 - errors * 15 - warnings * 5)
    return {
        "score": score,
        "errors": errors,
        "warnings": warnings,
        "infos": infos,
        "status": "build-ready" if errors == 0 and warnings <= 3 else "needs design revision",
    }


def render_report(findings: Sequence[Finding]) -> str:
    """Render findings as a human-readable report."""
    score = score_blueprint(findings)
    lines = [
        "Role-Design Blueprint Validation Report",
        "=" * 45,
        f"Score: {score['score']}/100",
        f"Status: {score['status']}",
        f"Errors: {score['errors']} | Warnings: {score['warnings']} | Info: {score['infos']}",
        "",
    ]

    if not findings:
        lines.append("No findings. The blueprint is ready to convert into implementation tasks.")
        return "\n".join(lines)

    for index, finding in enumerate(findings, start=1):
        lines.extend(
            [
                f"{index}. [{finding['severity'].upper()}] {finding['area']}",
                f"   Finding: {finding['message']}",
                f"   Fix: {finding['recommendation']}",
                "",
            ]
        )

    return "\n".join(lines)


def save_report(report: str, path: str | Path) -> None:
    """Save a validation report to disk.

    Args:
        report: Report text.
        path: Output file path.
    """
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")


def validate_file(path: str | Path) -> tuple[AgentTeamBlueprint, List[Finding]]:
    """Load and validate a blueprint file in one call."""
    blueprint = load_blueprint(path)
    return blueprint, validate_blueprint(blueprint)

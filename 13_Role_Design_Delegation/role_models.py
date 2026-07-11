"""Pydantic models for designing multi-agent roles, delegation, RACI, and handoffs.

The models are intentionally framework-neutral. They describe what a team should do
before the class turns the blueprint into AutoGen, CrewAI, LangGraph, or custom code.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class DelegationPattern(str, Enum):
    """Supported delegation styles for an agent team."""

    HIERARCHICAL = "hierarchical"
    PIPELINE = "pipeline"
    FLAT = "flat"
    BLACKBOARD = "blackboard"
    HYBRID = "hybrid"


class RoleType(str, Enum):
    """Common role types used in multi-agent systems."""

    ORCHESTRATOR = "Orchestrator"
    PLANNER = "Planner"
    RESEARCHER = "Researcher"
    EXECUTOR = "Executor"
    WRITER = "Writer"
    CRITIC = "Critic"
    FACT_CHECKER = "Fact-Checker"
    MEMORY_MANAGER = "Memory Manager"
    COMPLIANCE = "Compliance"
    TOOL_SPECIALIST = "Tool Specialist"
    EDITOR = "Editor"


class MemoryAccess(str, Enum):
    """Memory permissions for a role."""

    NONE = "none"
    READ_ONLY = "read_only"
    WRITE_ONLY = "write_only"
    READ_WRITE = "read_write"


class Severity(str, Enum):
    """Severity levels used in validation findings."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class RoleCard(BaseModel):
    """Defines the mission, boundaries, outputs, and escalation rules for one role."""

    name: str = Field(..., description="Human-readable role name, e.g., Researcher")
    role_type: RoleType
    mission: str = Field(..., description="One-sentence purpose of this role")
    responsibilities: List[str] = Field(default_factory=list)
    decision_rights: List[str] = Field(default_factory=list)
    tools_allowed: List[str] = Field(default_factory=list)
    inputs_expected: List[str] = Field(default_factory=list)
    outputs_owned: List[str] = Field(default_factory=list)
    success_metrics: List[str] = Field(default_factory=list)
    failure_modes: List[str] = Field(default_factory=list)
    stop_conditions: List[str] = Field(default_factory=list)
    escalation_path: str = Field(..., description="Who this role escalates to and when")
    memory_access: MemoryAccess = MemoryAccess.NONE
    max_iterations: int = Field(default=1, ge=1, le=10)

    @field_validator("name", "mission", "escalation_path")
    @classmethod
    def must_not_be_blank(cls, value: str) -> str:
        """Prevent blank names and core role definitions."""
        if not value or not value.strip():
            raise ValueError("value must not be blank")
        return value.strip()


class RACIEntry(BaseModel):
    """One RACI row for a task owned by the agent team."""

    task: str
    responsible: List[str] = Field(default_factory=list)
    accountable: str
    consulted: List[str] = Field(default_factory=list)
    informed: List[str] = Field(default_factory=list)
    artifact: str = Field(default="", description="Expected artifact from this task")
    acceptance_criteria: List[str] = Field(default_factory=list)

    @field_validator("task")
    @classmethod
    def task_must_not_be_blank(cls, value: str) -> str:
        """Ensure every RACI entry names a task."""
        if not value or not value.strip():
            raise ValueError("task must not be blank")
        return value.strip()


class HandoffContract(BaseModel):
    """Defines the schema and rules for transferring work from one role to another."""

    name: str
    source_role: str
    target_role: str
    trigger: str
    input_schema: Dict[str, str] = Field(default_factory=dict)
    output_schema: Dict[str, str] = Field(default_factory=dict)
    quality_checks: List[str] = Field(default_factory=list)
    stop_conditions: List[str] = Field(default_factory=list)
    retry_policy: str = ""
    escalation_path: str = ""
    logging_fields: List[str] = Field(default_factory=list)


class IncentivePolicy(BaseModel):
    """Captures what the team is optimized for and what it must not optimize away."""

    primary_success_metric: str
    balancing_metrics: List[str] = Field(default_factory=list)
    anti_goals: List[str] = Field(default_factory=list)
    incentive_risks: List[str] = Field(default_factory=list)
    mitigation_rules: List[str] = Field(default_factory=list)


class LoopControl(BaseModel):
    """Controls that prevent infinite critique, replanning, or handoff loops."""

    max_team_iterations: int = Field(default=3, ge=1, le=20)
    max_revision_cycles: int = Field(default=2, ge=0, le=10)
    escalation_after_failures: int = Field(default=2, ge=1, le=10)
    human_escalation_rule: str = ""
    termination_rule: str = ""


class AgentTeamBlueprint(BaseModel):
    """Complete role-design blueprint for a multi-agent system."""

    project_name: str
    user_goal: str
    delegation_pattern: DelegationPattern
    roles: List[RoleCard]
    raci: List[RACIEntry]
    handoff_contracts: List[HandoffContract]
    incentive_policy: IncentivePolicy
    loop_control: LoopControl
    notes_for_next_build: Optional[str] = None

    @property
    def role_names(self) -> List[str]:
        """Return role names in definition order."""
        return [role.name for role in self.roles]

    def get_role(self, name: str) -> Optional[RoleCard]:
        """Return a role by name, or None when missing."""
        return next((role for role in self.roles if role.name == name), None)

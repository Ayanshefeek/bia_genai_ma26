"""Pydantic schemas for the self-reflection and critique practical."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


Severity = Literal["minor", "major", "blocking"]


class CritiqueIssue(BaseModel):
    """One concrete issue found by the evaluator.

    Params:
        criterion: Rubric criterion the issue relates to.
        severity: Impact level for the issue.
        explanation: Plain-language explanation of the problem.
        revision_instruction: Specific instruction the refiner can use.
    Returns:
        A validated critique issue.
    """

    criterion: str = Field(..., min_length=2)
    severity: Severity
    explanation: str = Field(..., min_length=10)
    revision_instruction: str = Field(..., min_length=10)


class CritiqueResult(BaseModel):
    """Structured evaluator output for a draft.

    Params:
        score: Overall score from 1 to 10.
        passed: Whether the draft is good enough to stop retrying.
        summary: Short overall judgment.
        strengths: What should be preserved in the next version.
        issues: Concrete problems to fix.
        reflection_memory: Reusable lesson for the next iteration.
        revised_strategy: How the refiner should approach the rewrite.
    Returns:
        A validated critique result.
    """

    score: int = Field(..., ge=1, le=10)
    passed: bool
    summary: str = Field(..., min_length=10)
    strengths: list[str] = Field(default_factory=list)
    issues: list[CritiqueIssue] = Field(default_factory=list)
    reflection_memory: str = Field(..., min_length=10)
    revised_strategy: str = Field(..., min_length=10)

    @field_validator("strengths")
    @classmethod
    def limit_strengths(cls, strengths: list[str]) -> list[str]:
        """Keep output readable for classroom inspection."""
        return strengths[:4]

    @field_validator("issues")
    @classmethod
    def limit_issues(cls, issues: list[CritiqueIssue]) -> list[CritiqueIssue]:
        """Keep the refiner focused on the highest-impact issues."""
        return issues[:5]


class IterationRecord(BaseModel):
    """One pass through the generate-critique-refine loop.

    Params:
        iteration: Iteration number.
        draft: Draft text evaluated during this iteration.
        critique: Structured critique for the draft.
    Returns:
        A validated loop record.
    """

    iteration: int = Field(..., ge=1)
    draft: str = Field(..., min_length=1)
    critique: CritiqueResult

    @property
    def score(self) -> int:
        """Return the score for quick trace printing."""
        return self.critique.score

    @property
    def passed(self) -> bool:
        """Return whether this iteration met the stopping threshold."""
        return self.critique.passed

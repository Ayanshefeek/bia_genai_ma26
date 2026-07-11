"""Tests for the role-design validators."""

from pathlib import Path

from validators import load_blueprint, score_blueprint, validate_blueprint


ROOT = Path(__file__).resolve().parents[1]


def test_sample_blueprint_is_build_ready() -> None:
    """The bundled good blueprint should pass without errors."""
    blueprint = load_blueprint(ROOT / "data" / "sample_research_bot_blueprint.json")
    findings = validate_blueprint(blueprint)
    score = score_blueprint(findings)

    assert score["errors"] == 0
    assert score["score"] >= 80
    assert blueprint.project_name == "Evidence-Backed Research Bot"


def test_flawed_blueprint_is_flagged() -> None:
    """The intentionally flawed blueprint should produce multiple errors."""
    blueprint = load_blueprint(ROOT / "data" / "flawed_research_bot_blueprint.json")
    findings = validate_blueprint(blueprint)
    score = score_blueprint(findings)

    assert score["errors"] >= 3
    assert score["warnings"] >= 5
    assert score["status"] == "needs design revision"


def test_unknown_role_detection() -> None:
    """The flawed blueprint should flag an unknown role in RACI."""
    blueprint = load_blueprint(ROOT / "data" / "flawed_research_bot_blueprint.json")
    findings = validate_blueprint(blueprint)

    assert any("Unknown Manager" in finding["message"] for finding in findings)


def test_handoff_schema_detection() -> None:
    """The flawed blueprint should flag missing handoff schemas."""
    blueprint = load_blueprint(ROOT / "data" / "flawed_research_bot_blueprint.json")
    findings = validate_blueprint(blueprint)

    assert any("input schema" in finding["message"] for finding in findings)
    assert any("output schema" in finding["message"] for finding in findings)

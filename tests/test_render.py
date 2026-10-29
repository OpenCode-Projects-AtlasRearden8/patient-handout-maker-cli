"""Tests for rendering the print-ready sheet."""

import pytest

from patient_handout_maker.render import (
    BRAND_LINE,
    DISCLAIMER,
    FOOTER,
    QUESTIONS_LINES,
    SHEET_WIDTH,
    render_body,
    render_sheet,
)
from patient_handout_maker.templates import (
    BUILT_IN_TEMPLATES,
    TemplateError,
    get_built_in_template,
)

TOPIC = "Type 2 Diabetes Basics"


@pytest.fixture
def sheet():
    template = get_built_in_template("what-it-is")
    return render_sheet(TOPIC, template, "plain")


def test_title_and_level_note(sheet):
    assert "TYPE 2 DIABETES BASICS" in sheet.upper()
    assert "WHAT IT IS" in sheet.upper()
    assert "8th-grade" in sheet


def test_topics_interpolated(sheet):
    assert "Type 2 Diabetes Basics" in sheet
    assert "{topic}" not in sheet
    assert "{" not in sheet


def test_questions_block(sheet):
    assert "QUESTIONS TO ASK YOUR CARE TEAM" in sheet
    marks = [line for line in sheet.splitlines() if line.startswith("  1.")]
    assert len(marks) >= 1
    for number in range(1, QUESTIONS_LINES + 1):
        assert f"{number}.  ___" in sheet.replace(
            f"  {number}.", f"{number}."
        ) or f"{number}.  " in sheet


def test_footer_disclaimers(sheet):
    assert "education only" in sheet
    assert "not medical advice" in sheet
    for phrase in (
        "Talk to your own care team about your situation,",
        "what is right for you.",
    ):
        assert phrase in sheet
    assert "Asdale Dynamics, LLC" in sheet


def test_lines_within_width(sheet):
    assert all(len(line) <= SHEET_WIDTH for line in sheet.splitlines())


def test_trailing_newline(sheet):
    assert sheet.endswith("\n")


@pytest.mark.parametrize("name", sorted(BUILT_IN_TEMPLATES))
@pytest.mark.parametrize("level", sorted({l for t in BUILT_IN_TEMPLATES.values() for l in t["sections"]}))
def test_all_combinations_render(name, level):
    template = get_built_in_template(name)
    out = render_sheet("Test Topic", template, level)
    assert "QUESTIONS TO ASK YOUR CARE TEAM" in out
    assert "Test Topic" in out


def test_unknown_level_raises():
    template = get_built_in_template("what-it-is")
    with pytest.raises(TemplateError):
        render_sheet(TOPIC, template, "fancy")


def test_empty_topic_raises():
    template = get_built_in_template("what-it-is")
    with pytest.raises(TemplateError):
        render_sheet("   ", template, "plain")


def test_topic_whitespace_collapsed():
    template = get_built_in_template("what-it-is")
    for level in ("easy", "plain", "standard"):
        out = render_sheet("  Test\nTopic  ", template, level)
        assert "Test Topic" in out


def test_custom_topic_not_duplicated_as_header_only():
    body = render_body(TOPIC, get_built_in_template("what-it-is"), "plain")
    assert "Type 2 Diabetes Basics" in body
    assert "QUESTIONS TO ASK" not in body  # body has no sheet furniture

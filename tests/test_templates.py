"""Tests for built-in templates and template fixture loading."""

from pathlib import Path

import pytest

from patient_handout_maker.templates import (
    BUILT_IN_TEMPLATES,
    LEVEL_LABELS,
    TemplateError,
    get_built_in_template,
    list_built_in_templates,
    load_template_file,
    validate_template,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_every_built_in_template_validates():
    for name, template in BUILT_IN_TEMPLATES.items():
        validate_template(template)  # should not raise
        assert template["name"] == name
        assert template["title"]


def test_built_in_templates_cover_all_levels():
    for name, template in BUILT_IN_TEMPLATES.items():
        assert set(template["sections"]) == set(LEVEL_LABELS), name
        for level, sections in template["sections"].items():
            assert sections, f"{name}/{level} has no sections"
            for section in sections:
                assert section["heading"]
                assert all(line.strip() for line in section["lines"])


def test_topic_placeholder_present():
    for template in BUILT_IN_TEMPLATES.values():
        flat = "\n".join(
            line
            for sections in template["sections"].values()
            for section in sections
            for line in section["lines"]
        )
        assert "{topic}" in flat


def test_list_returns_summaries():
    summaries = list_built_in_templates()
    names = {item["name"] for item in summaries}
    assert names == set(BUILT_IN_TEMPLATES)


def test_load_template_fixture():
    template = load_template_file(FIXTURES / "custom_template.json")
    assert template["name"] == "meds-review"
    assert template["title"] == "Medicine Review"
    assert set(template["sections"]) <= set(LEVEL_LABELS)


def test_load_bad_level_fixture_raises():
    with pytest.raises(TemplateError):
        load_template_file(FIXTURES / "bad_level_template.json")


def test_unknown_built_in_raises():
    with pytest.raises(TemplateError):
        get_built_in_template("does-not-exist")


def test_returned_copy_is_independent():
    original = BUILT_IN_TEMPLATES["what-it-is"]
    template = get_built_in_template("what-it-is")
    template["sections"]["easy"][0]["lines"][0] = "mutated"
    assert "mutated" not in "\n".join(
        line
        for section in original["sections"]["easy"]
        for line in section["lines"]
    )


@pytest.mark.parametrize(
    "bad_template",
    [
        {},
        {"name": "x", "title": "y"},  # missing sections
        {"name": "x", "title": "y", "sections": {}},
        {"name": "x", "title": "y", "sections": {"easy": []}},
        {"name": "x", "title": "y", "sections": {"easy": [{"heading": "h"}]}},
        {"name": "x", "title": "y", "sections": {"easy": [{"lines": ["a"]}]}},
    ],
)
def test_validate_rejects_malformed(bad_template):
    with pytest.raises(TemplateError):
        validate_template(bad_template)

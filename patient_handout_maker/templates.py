"""Built-in handout templates and support for loading custom ones.

A template defines sections for each supported reading level. Section
text uses ``{topic}`` placeholders that the renderer replaces with the
handout topic. Templates are plain data (dicts) so they can live in
Python, in JSON files, or be shared between nurse educators.
"""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Dict, List

# Reading levels. Each maps to a friendly label shown on the sheet.
LEVEL_LABELS: Dict[str, str] = {
    "easy": "Plain and simple (about a 5th-grade reading level)",
    "plain": "Plain language (about an 8th-grade reading level)",
    "standard": "Standard (everyday adult readers)",
}


class TemplateError(ValueError):
    """Raised when a template is missing fields or malformed."""


def validate_template(template: dict) -> None:
    """Check that *template* follows the expected schema.

    Raises TemplateError (a ValueError) with a helpful message if not.
    """
    if not isinstance(template, dict):
        raise TemplateError("template must be a JSON object / dict")
    for key in ("name", "title", "sections"):
        if key not in template:
            raise TemplateError(f"template is missing required field: {key}")
    sections = template["sections"]
    if not isinstance(sections, dict) or not sections:
        raise TemplateError("template 'sections' must be a non-empty object")
    for level, level_sections in sections.items():
        if level not in LEVEL_LABELS:
            raise TemplateError(
                f"unknown reading level {level!r}; "
                f"expected one of {sorted(LEVEL_LABELS)}"
            )
        if not isinstance(level_sections, list) or not level_sections:
            raise TemplateError(
                f"reading level {level!r} must map to a non-empty list of sections"
            )
        for section in level_sections:
            if not isinstance(section, dict):
                raise TemplateError(f"section in {level!r} must be an object")
            if "heading" not in section or "lines" not in section:
                raise TemplateError(
                    "each section needs 'heading' and 'lines' "
                    f"(in reading level {level!r})"
                )
            if not isinstance(section["lines"], list) or not section["lines"]:
                raise TemplateError(
                    f"section {section.get('heading')!r} in {level!r} needs at "
                    "least one line of text"
                )


def load_template_file(path) -> dict:
    """Load and validate a template from a JSON file."""
    with open(path, "r", encoding="utf-8") as handle:
        try:
            template = json.load(handle)
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive
            raise TemplateError(f"could not parse template file {path}: {exc}")
    validate_template(template)
    return template


def get_built_in_template(name: str) -> dict:
    """Return a validated copy of a built-in template by short name."""
    available = BUILT_IN_TEMPLATES.get(name)
    if available is None:
        raise TemplateError(
            f"unknown template {name!r}; built-in templates: "
            f"{sorted(BUILT_IN_TEMPLATES)}"
        )
    validate_template(available)
    return deepcopy(available)


def list_built_in_templates() -> List[dict]:
    """Summaries of the built-in templates for CLI --list output."""
    summaries = []
    for name, tmpl in BUILT_IN_TEMPLATES.items():
        summaries.append(
            {
                "name": name,
                "title": tmpl["title"],
                "description": tmpl.get("description", ""),
            }
        )
    return summaries


# ---------------------------------------------------------------------------
# Built-in templates
# ---------------------------------------------------------------------------

_WHAT_IT_IS = {
    "name": "what-it-is",
    "title": "What It Is",
    "description": "Explains a condition or treatment in plain language",
    "sections": {
        "easy": [
            {
                "heading": "What is {topic}?",
                "lines": [
                    "{topic} is a health thing your care team wants you to "
                    "understand. This sheet explains it in simple words.",
                    "You do not need to know every medical term. Knowing the "
                    "basics helps you make safe choices.",
                ],
            },
            {
                "heading": "Why it matters",
                "lines": [
                    "When you understand {topic}, you can spot problems early "
                    "and ask better questions at your visits.",
                    "Your care team is on your side. Learning about it is a "
                    "team effort, not a test.",
                ],
            },
            {
                "heading": "Things to watch for",
                "lines": [
                    "Every person is different. Ask your care team which "
                    "warning signs matter most for you.",
                    "If something feels new, unusual, or scary, tell your "
                    "care team. It is always okay to ask.",
                ],
            },
        ],
        "plain": [
            {
                "heading": "What is {topic}?",
                "lines": [
                    "{topic} is something your care team is helping you "
                    "manage. This sheet explains, in plain words, what it is "
                    "and why it matters.",
                    "It is not a full medical record. It is a starting point "
                    "for a conversation with your own care team.",
                ],
            },
            {
                "heading": "Why it matters",
                "lines": [
                    "Many people who deal with {topic} feel better and stay "
                    "healthier when they understand it early and follow their "
                    "care plan.",
                    "You are part of the plan. Your questions and what you "
                    "notice at home matter a great deal.",
                ],
            },
            {
                "heading": "Things to watch for",
                "lines": [
                    "Warning signs can differ from person to person. Ask your "
                    "care team to circle the ones that apply to you.",
                    "Write down anything new or unusual between visits so you "
                    "remember to mention it.",
                ],
            },
        ],
        "standard": [
            {
                "heading": "What is {topic}?",
                "lines": [
                    "{topic} is a health condition or concern your care team "
                    "has asked you to learn about. This sheet gives you the "
                    "basics in everyday language.",
                    "It is teaching material only. Your care team will tailor "
                    "the details to your own history, tests, and treatment "
                    "plan.",
                ],
            },
            {
                "heading": "Why it matters",
                "lines": [
                    "People who understand {topic} tend to recognize changes "
                    "sooner, keep appointments, and feel more confident "
                    "sharing decisions about their care.",
                    "Ask how {topic} fits with your other conditions and "
                    "medicines, since plans work best as one whole picture.",
                ],
            },
            {
                "heading": "Things to watch for",
                "lines": [
                    "Signs and symptoms vary. Review this sheet with your "
                    "care team and note which items are most relevant to you.",
                    "Keep a simple log of anything new or that gets worse, and "
                    "bring it to your next visit.",
                ],
            },
        ],
    },
}

_BEFORE_YOUR_VISIT = {
    "name": "before-your-visit",
    "title": "Before Your Visit",
    "description": "How to get ready for an appointment about this topic",
    "sections": {
        "easy": [
            {
                "heading": "Why this visit matters",
                "lines": [
                    "Your care team wants to talk with you about {topic}. "
                    "This visit is for you and your questions.",
                    "Getting ready helps you get more out of the visit.",
                ],
            },
            {
                "heading": "What to bring",
                "lines": [
                    "Bring your medicines (or a photo of the bottles), your "
                    "insurance card, and a pen.",
                    "Bring a family member or friend if that helps you feel "
                    "comfortable.",
                ],
            },
            {
                "heading": "Get your questions ready",
                "lines": [
                    "Write your questions down before the visit. It is easy "
                    "to forget them once you are in the room.",
                    "There is no such thing as a silly question. Your care "
                    "team wants to hear them.",
                ],
            },
        ],
        "plain": [
            {
                "heading": "Why this visit matters",
                "lines": [
                    "Your upcoming visit is a chance to talk about {topic} "
                    "with your care team and plan your next steps together.",
                    "You will get more from the visit if you spend a few "
                    "minutes getting ready.",
                ],
            },
            {
                "heading": "What to bring",
                "lines": [
                    "Medicines and doses (or a phone photo of each label), "
                    "your pharmacy name, and any test results from other "
                    "spots.",
                    "A short list of how you have been feeling, including "
                    "anything that is better, worse, or new.",
                ],
            },
            {
                "heading": "Get your questions ready",
                "lines": [
                    "Jot down your top two or three questions. Put the most "
                    "important one first in case time runs short.",
                    "Tell your care team what matters most to you, like side "
                    "effects, cost, or getting back to normal activities.",
                ],
            },
        ],
        "standard": [
            {
                "heading": "Why this visit matters",
                "lines": [
                    "This appointment is a working conversation about {topic}: "
                    "what you have noticed, what the evidence supports, and "
                    "what you want to achieve together.",
                    "Preparation is the single easiest way to make the visit "
                    "count.",
                ],
            },
            {
                "heading": "What to bring",
                "lines": [
                    "An up-to-date list of medicines, vitamins, and "
                    "supplements with doses, plus any records from other "
                    "clinicians or urgent-care visits.",
                    "Notes on your symptoms: when they started, what makes "
                    "them better or worse, and how they affect daily life.",
                ],
            },
            {
                "heading": "Get your questions ready",
                "lines": [
                    "Bring a written list and lead with your highest-priority "
                    "question. Shared decision-making starts with what "
                    "matters to you.",
                    "Ask for clarification any time; it is reasonable to say "
                    "'can you explain that another way?'",
                ],
            },
        ],
    },
}

_GOING_HOME = {
    "name": "going-home",
    "title": "Going Home Basics",
    "description": "Everyday care after a visit, procedure, or hospital stay",
    "sections": {
        "easy": [
            {
                "heading": "Care at home",
                "lines": [
                    "You are heading home after care for {topic}. Go slowly "
                    "for the first little while. Rest, light food, and water "
                    "are a good start for most people.",
                    "Follow the specific home instructions your care team "
                    "gave you about {topic}. This sheet is a reminder, not a "
                    "full list.",
                ],
            },
            {
                "heading": "Your medicines",
                "lines": [
                    "Take your medicines the way your care team told you: "
                    "the right dose, at the right time.",
                    "If a medicine is confusing, too costly, or bothering "
                    "you, call your care team or pharmacist before you "
                    "change anything.",
                ],
            },
            {
                "heading": "When to call for help",
                "lines": [
                    "Call your care team if anything feels wrong: new pain, "
                    "fever, trouble breathing, or if you just feel much "
                    "worse.",
                    "For an emergency, call 911. It is always okay to call "
                    "and ask.",
                ],
            },
        ],
        "plain": [
            {
                "heading": "Care at home",
                "lines": [
                    "Plan a gentle first few days after care for {topic}: "
                    "rest, easy meals, and water unless your care team said "
                    "otherwise.",
                    "Ask before you leave: who do I call with questions about "
                    "{topic}, and during what hours?",
                ],
            },
            {
                "heading": "Your medicines",
                "lines": [
                    "Keep taking prescribed medicines the way your care team "
                    "explained for {topic}. Do not skip or adjust doses on "
                    "your own, and write down anything new you notice.",
                    "One pharmacy for all your medicines makes it easier to "
                    "spot interactions and refill problems.",
                ],
            },
            {
                "heading": "When to call for help",
                "lines": [
                    "Know your warning signs before you leave. Write them "
                    "below and the number to call, day or night.",
                    "Call right away for serious trouble like chest pain, "
                    "hard breathing, or confusion. Otherwise call your care "
                    "team first; they often can help without a trip.",
                ],
            },
        ],
        "standard": [
            {
                "heading": "Care at home",
                "lines": [
                    "Ease back into your routine over the first several days "
                    "of recovery from {topic}. Rest, hydration, and light "
                    "movement are a sensible baseline; follow the written "
                    "plan your care team gave you.",
                    "Line up help at home if you expect low energy or limited "
                    "mobility, even briefly.",
                ],
            },
            {
                "heading": "Your medicines",
                "lines": [
                    "Take prescriptions exactly as written, and confirm "
                    "refill timing for your {topic} medicines before you run "
                    "out.",
                    "Watch for side effects and note them with dates so your "
                    "care team can adjust with good information.",
                ],
            },
            {
                "heading": "When to call for help",
                "lines": [
                    "Clarify your specific warning signs and the numbers to "
                    "call before you go home, including after-hours and "
                    "next-day follow-up.",
                    "Treat emergencies as emergencies: call 911 for anything "
                    "severe or sudden. For everything else, one call to your "
                    "care team usually settles the question.",
                ],
            },
        ],
    },
}

BUILT_IN_TEMPLATES: Dict[str, dict] = {
    "what-it-is": _WHAT_IT_IS,
    "before-your-visit": _BEFORE_YOUR_VISIT,
    "going-home": _GOING_HOME,
}

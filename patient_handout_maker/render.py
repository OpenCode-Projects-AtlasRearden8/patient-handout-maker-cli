"""Render a clean, print-ready patient teaching sheet.

The sheet is plain text, wrapped to a fixed width so it prints well from
any editor or terminal, and always includes:

* a centered title and reading-level note
* the template's sections, plain-language by design
* a "Questions to ask your care team" fill-in block
* an education-only, talk-to-your-own-care-team footer
"""

from __future__ import annotations

import textwrap
from typing import Dict, List

from .templates import LEVEL_LABELS, TemplateError

SHEET_WIDTH = 72
QUESTIONS_LINES = 5

DISCLAIMER = (
    "This sheet is for education only. It is not medical advice, and it "
    "does not replace talking with your own doctor, nurse, or pharmacist."
)
FOOTER = (
    "Talk to your own care team about your situation, your questions, and "
    "what is right for you."
)
BRAND_LINE = "Patient Handout Maker - Asdale Dynamics, LLC"
BRAND_URL = "dylanasdale.github.io"


def _rule(char: str, width: int = SHEET_WIDTH) -> str:
    return char * width


def _center(text: str, width: int = SHEET_WIDTH) -> str:
    return text.center(width).rstrip()


def _wrap_paragraph(text: str, width: int = SHEET_WIDTH - 4) -> str:
    return textwrap.fill(
        textwrap.dedent(text).strip(),
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
    )


def _checks_or_blanks(count: int, width: int = SHEET_WIDTH - 4) -> List[str]:
    """Numbered fill-in lines for the questions block."""
    return [f"  {i}.  {'_' * (width - 8)}" for i in range(1, count + 1)]


def _section_text(section: dict, topic: str) -> List[str]:
    """Turn one template section into wrapped output lines."""
    heading = f"{section['heading'].format(topic=topic)}"
    block = [heading.upper(), _rule("-", len(heading))]
    for line in section["lines"]:
        block.append("")
        block.extend(_wrap_paragraph(line.format(topic=topic)).splitlines())
    return block


def render_body(topic: str, template: dict, level: str) -> str:
    """Render just the teaching sections of the sheet."""
    if not topic or not topic.strip():
        raise TemplateError("topic must not be empty")
    topic = " ".join(topic.split())
    sections = template["sections"].get(level)
    if sections is None:
        raise TemplateError(
            f"template {template.get('name')!r} has no {level!r} level; "
            f"it supports {sorted(template['sections'])}"
        )
    blocks: List[str] = []
    for section in sections:
        if blocks:
            blocks.append("")
        blocks.extend(_section_text(section, topic))
    return "\n".join(blocks)


def render_sheet(
    topic: str,
    template: dict,
    level: str,
    questions_title: str = "Questions to ask your care team",
) -> str:
    """Render the full printable sheet as plain text."""
    if not topic or not topic.strip():
        raise TemplateError("topic must not be empty")
    topic = " ".join(topic.split())
    if level not in LEVEL_LABELS:
        raise TemplateError(
            f"unknown reading level {level!r}; expected one of "
            f"{sorted(LEVEL_LABELS)}"
        )

    title_wrapped = _wrap_paragraph(f"{topic.upper()} - {template['title'].upper()}")
    title_lines: List[str] = []
    for line in title_wrapped.splitlines():
        title_lines.extend(
            textwrap.wrap(line, width=SHEET_WIDTH - 12) or [""]
        )

    out: List[str] = []
    out.append(_rule("="))
    out.append(_center(BRAND_LINE))
    out.append(_center(BRAND_URL))
    out.append(_rule("="))
    out.append("")
    out.extend(_center(line).rstrip() for line in title_lines)
    out.append(_center(LEVEL_LABELS[level]))
    out.append("")
    out.append(_rule("="))
    out.append("")
    out.append(render_body(topic, template, level))
    out.append("")
    out.append("QUESTIONS TO ASK YOUR CARE TEAM")
    out.append(_rule("-", len(questions_title)))
    out.extend(_checks_or_blanks(QUESTIONS_LINES))
    out.append("")
    out.append(_rule("-"))
    out.append("")
    out.append(_wrap_paragraph("TALK WITH YOUR OWN CARE TEAM").splitlines()[0])
    out.append("")
    out.extend(_wrap_paragraph(DISCLAIMER).splitlines())
    out.append("")
    out.extend(_wrap_paragraph(FOOTER).splitlines())
    out.append("")
    out.append(_center("Prepared for patient education use"))
    out.append(_rule("="))
    return "\n".join(out) + "\n"

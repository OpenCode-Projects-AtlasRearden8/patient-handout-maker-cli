"""Command-line interface for Patient Handout Maker.

Example
-------
    handout "Type 2 Diabetes Basics" --template what-it-is --level plain \\
        --out diabetes-basics.txt

Optional plain-speak polish:

    handout "Asthma Basics" --level easy --polish \\
        --base-url http://localhost:11434/v1 --model llama3.2

The polish step talks to any OpenAI-compatible base_url (default: local
Ollama at http://localhost:11434/v1). It never sends API keys or auth
headers. Education only -- never medical advice.
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Sequence

from . import __version__
from .levels import estimated_grade
from .polish import (
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    PolishError,
    polish_text,
)
from .render import LEVEL_LABELS
from .templates import (
    BUILT_IN_TEMPLATES,
    TemplateError,
    get_built_in_template,
    list_built_in_templates,
    load_template_file,
)
from .render import render_sheet

BANNER = (
    "Patient Handout Maker (education only, never medical advice) "
    f"v{__version__}"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="handout",
        description=(
            "Draft a plain-language patient teaching handout "
            "(education only, never medical advice)."
        ),
        epilog="Patient Handout Maker - Asdale Dynamics, LLC",
    )
    parser.add_argument(
        "topic",
        nargs="?",
        help="handout topic, e.g. 'Type 2 Diabetes Basics'",
    )
    parser.add_argument(
        "--template",
        "-t",
        default="what-it-is",
        help=(
            "built-in template name (what-it-is, before-your-visit, "
            "going-home) or path to a JSON template file"
        ),
    )
    parser.add_argument(
        "--level",
        "-l",
        default="plain",
        choices=sorted(LEVEL_LABELS),
        help="reading level for the handout (default: plain)",
    )
    parser.add_argument(
        "--out",
        "-o",
        help="write the sheet to this file (default: print to stdout)",
    )
    parser.add_argument(
        "--list",
        dest="list_templates",
        action="store_true",
        help="list built-in templates and reading levels, then exit",
    )
    parser.add_argument(
        "--polish",
        action="store_true",
        help="optionally polish wording via a local, OpenAI-compatible endpoint",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=(
            "OpenAI-compatible base_url for polish "
            f"(default: {DEFAULT_BASE_URL}); no API keys are ever used"
        ),
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"model name for polish (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--grade-check",
        action="store_true",
        help="print a rough reading-grade estimate for the draft",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__} (Asdale Dynamics, LLC)",
    )
    return parser


def _list_templates() -> str:
    lines = ["Built-in templates:", ""]
    for item in list_built_in_templates():
        lines.append(f"  {item['name']}")
        if item["description"]:
            lines.append(f"      {item['description']}")
    lines.append("")
    lines.append("Reading levels:")
    for level, label in sorted(LEVEL_LABELS.items()):
        lines.append(f"  {level:10s} {label}")
    lines.append("")
    lines.append("Custom templates: pass a path to a JSON template file "
                 "with --template.")
    return "\n".join(lines)


def _resolve_template(name: str):
    """Accept built-in names or a path to a JSON template file."""
    if name in BUILT_IN_TEMPLATES:
        return get_built_in_template(name)
    try:
        return load_template_file(name)
    except FileNotFoundError:
        raise TemplateError(
            f"no built-in template {name!r} and no template file at {name!r}; "
            "run with --list to see options"
        )


def _write_or_print(sheet: str, out_path: str | None) -> None:
    if out_path:
        with open(out_path, "w", encoding="utf-8") as handle:
            handle.write(sheet)
        print(f"Wrote handout to {out_path}")
    else:
        sys.stdout.write(sheet)


def run(argv: Sequence[str] | None = None) -> int:
    """Run the CLI; returns a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    print(BANNER, file=sys.stderr)
    if args.list_templates:
        print(_list_templates())
        return 0

    if not args.topic or not args.topic.strip():
        parser.error("please give a topic, e.g. handout \"Type 2 Diabetes Basics\"")

    try:
        template = _resolve_template(args.template)
        level = args.level
        topic = " ".join(args.topic.split())
        sheet = render_sheet(topic, template, level)
    except TemplateError as exc:
        parser.error(str(exc))

    if args.grade_check:
        grade = estimated_grade(sheet)
        print(
            f"Rough reading-grade estimate for the draft: about grade {grade}",
            file=sys.stderr,
        )

    if args.polish:
        label = LEVEL_LABELS[level]
        try:
            print(
                f"Polishing with {args.model} at {args.base_url} "
                "(no API keys are sent)...",
                file=sys.stderr,
            )
            sheet = polish_text(
                sheet,
                base_url=args.base_url,
                model=args.model,
                level_label=label,
            )
            print("Polish complete.", file=sys.stderr)
        except PolishError as exc:
            print(
                f"warning: polish unavailable ({exc}). Keeping the "
                "plain-language draft.",
                file=sys.stderr,
            )

    _write_or_print(sheet, args.out)
    return 0


def main(argv: List[str] | None = None) -> None:  # pragma: no cover
    sys.exit(run(argv))


if __name__ == "__main__":
    main()

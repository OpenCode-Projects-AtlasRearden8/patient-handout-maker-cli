# STATUS

Project: **Patient Handout Maker** — nurse-educator CLI that drafts
plain-language patient teaching handouts (education only, never medical
advice).

Maintainer: Asdale Dynamics, LLC · Last updated: 2026-10-29

## What was built

- **CLI (`handout`)** — pick a topic, a reading level (`easy`, `plain`,
  `standard`), and a template (`what-it-is`, `before-your-visit`,
  `going-home`). Renders a clean, 72-character, print-ready text sheet
  with a "Questions to ask your care team" fill-in block and an
  education-only "talk to your own care team" footer. Save with `--out`
  or print to stdout. `--list` shows all templates and levels.
- **Optional plain-speak polish** — `--polish` calls any OpenAI-compatible
  `base_url` (default: local Ollama at `http://localhost:11434/v1`).
  By design it never sends, asks for, or stores API keys or auth headers.
  If the endpoint is unreachable, it warns and keeps the plain-language
  draft; drafting never depends on the network.
- **Three built-in templates × three reading levels**, all with
  `{topic}` interpolation, written in warm plain language.
- **Custom templates as JSON files** with a validated schema and a
  complete example fixture in `tests/fixtures/custom_template.json`.
- **Rough reading-grade estimator** (`--grade-check`) — an internal
  Flesch-Kincaid style sanity check, not a clinical instrument.
- **Zero runtime dependencies** — Python standard library only;
  `pytest` is the only dev dependency.
- **LICENSE** — MIT, copyright line exactly
  `Copyright (c) 2026 Asdale Dynamics, LLC`.
- **README** — credits Asdale Dynamics, LLC, includes safety positioning,
  install/usage/custom-template/testing docs.

## How to run it

```bash
pip install .                      # or: pip install -e '.[test]' for dev
handout "Type 2 Diabetes Basics" -t what-it-is -l easy -o diabetes.txt
handout --list
handout "Asthma Basics" --level easy --polish     # needs local Ollama
pytest                                            # run the tests
```

## Verification results (2026-10-29)

- **pytest: 53 passed, 0 failed, 0 errors** (`tests/test_templates.py`,
  `test_render.py`, `test_levels.py`, `test_polish.py`, `test_cli.py`).
- **Install / build**: editable install succeeded; `pip wheel .` produced
  a valid wheel (`patient_handout_maker-0.1.0`) containing all 6 modules
  and the LICENSE file (`License-Expression: MIT` in metadata).
- **End-to-end CLI runs**: `--list`, sheet generation to file for
  `what-it-is` (easy) and `going-home` (plain), `--grade-check`, and
  polish success/fallback paths (fake endpoint + unreachable endpoint)
  all verified; rendered sheets contain the title, heading, questions
  block, and both disclaimers, wrapped within 72 columns.
- **Polish endpoint details verified in tests**: no `Authorization`
  header is ever sent; request shape matches OpenAI chat-completions;
  HTTP 500 / malformed / empty responses raise a friendly error and keep
  the draft.

## Known gaps / next steps

- Only text output; markdown, HTML, and PDF/word-Pad-style export are not
  implemented yet.
- Built-in content is generic starter copy for the three templates;
  individual clinics should review and tailor wording before use
  (the tool reiterates this on every sheet).
- The reading-grade estimator is a rough heuristic, not a validated
  readability tool.
- Polish is wording-only by design: it rewrites, but never adds or removes
  facts, headings, or disclaimers; a diff view showing exactly what
  changed would be a nice addition.
- No translation support (English only for now).
- Test fixtures cover one custom template example; more sample templates
  (e.g., meal teaching, lab-test prep) could grow the library.

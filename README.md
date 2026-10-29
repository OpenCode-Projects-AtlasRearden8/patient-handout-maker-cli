# Patient Handout Maker

A friendly command-line tool that helps **nurse educators draft plain-language
patient teaching handouts** — quickly, locally, and for free.

> **Education only. Never medical advice.**
> This tool drafts teaching sheets that always remind patients to talk to
> their own care team. It is a writing helper, not a clinical decision tool,
> and it never makes recommendations about anyone's care.

Built with care by **Asdale Dynamics, LLC** — part of the beginner-friendly
AI library at [dylanasdale.github.io](https://dylanasdale.github.io) from
Dylan Asdale, RN, author of *The Massive AI Manual*.

---

## What it does

Pick a **topic**, a **reading level**, and one of three built-in **templates**:

| Template | Use it when |
|---|---|
| `what-it-is` | Explaining a condition or treatment in plain words |
| `before-your-visit` | Getting a patient ready for an appointment |
| `going-home` | Everyday care after a visit, procedure, or hospital stay |

| Reading level | Plain talk for |
|---|---|
| `easy` | About a 5th-grade reading level |
| `plain` | About an 8th-grade reading level (default) |
| `standard` | Everyday adult readers |

The output is a clean, **print-ready text sheet** that always includes:

- a centered title with the reading-level note
- short, warm teaching sections (heading + a few sentences)
- a **"Questions to ask your care team"** block with fill-in lines
- an unmissable footer: **education only — talk to your own care team**

The sheets wrap to 72 characters, so they print neatly from any editor,
terminal, or printer.

## Install

Requires Python 3.9+. Nothing to sign up for and no dependencies beyond the
standard library.

```bash
pip install .
```

For development (editable install plus pytest):

```bash
pip install -e '.[test]'
```

## Quick start

Draft a sheet and print it to the terminal:

```bash
handout "Type 2 Diabetes Basics" --template what-it-is --level plain
```

Save it to a file ready to print:

```bash
handout "Type 2 Diabetes Basics" -t what-it-is -l easy -o diabetes-basics.txt
```

See every template and reading level:

```bash
handout --list
```

Sanity-check the wording with a rough Flesch-Kincaid style grade estimate:

```bash
handout "Asthma Action Plan" --grade-check
```

## Optional "plain-speak polish" with a local AI

If you have [Ollama](https://ollama.com) running, one flag asks a local model
to polish the wording — keeping every heading, fact, and disclaimer exactly
as written:

```bash
ollama pull llama3.2        # once
handout "Asthma Basics" --level easy --polish
```

That default talks to Ollama at `http://localhost:11434/v1`. Any
**OpenAI-compatible `base_url`** works, such as:

```bash
handout "Hand Care" --polish --base-url http://localhost:1234/v1 --model llama3.2
```

Important design choices, on purpose:

- **No API keys, ever.** The tool never asks for, sends, or stores keys or
  auth headers. It is built for local models.
- **Nothing leaves your machine by default.** If the endpoint is unreachable,
  you get a clear warning and the plain-language draft is used as-is.
  Drafting never depends on a network.

## Custom templates

Templates are simple JSON — easy to adapt for your clinic, unit, or class.
Load a template file as easily as the built-ins:

```bash
handout "Flu Shots" --template ./my-clinic-template.json -l easy -o flu.txt
```

The shape (see [`tests/fixtures/custom_template.json`](tests/fixtures/custom_template.json)
for a complete example):

```json
{
  "name": "my-template",
  "title": "My Template",
  "sections": {
    "easy": [
      {"heading": "About {topic}", "lines": ["{topic} is ..."]}
    ],
    "plain":  [ { "...": "..." } ],
    "standard": [ { "...": "..." } ]
  }
}
```

Every line may use a `{topic}` placeholder, which is replaced with your
handout topic. The questions block and the care-team footer are added
automatically.

## Testing

```bash
pytest
```

The test suite covers built-in templates, custom template fixture files,
sheet rendering (width, placeholders, questions block, disclaimers), the
reading-grade estimator, the CLI end to end, and the polish endpoint using
a local fake server — including the never-send-an-API-key guarantee and the
fall-back-when-offline behavior.

## Roadmap / known gaps

See [`STATUS.md`](STATUS.md) for the current build status and a short list
of planned improvements.

## License

MIT — see [LICENSE](LICENSE).

Copyright (c) 2026 Asdale Dynamics, LLC

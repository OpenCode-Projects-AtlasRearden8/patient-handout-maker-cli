"""Optional "plain-speak polish" using an OpenAI-compatible chat endpoint.

Design rules (important):

* Configurable ``base_url`` only. The default is a local Ollama server:
  ``http://localhost:11434/v1``. Any other OpenAI-compatible base_url works.
* We never send, ask for, or store API keys or auth headers. This tool is
  built for local models like Ollama; if you point it at a hosted endpoint,
  the request is still unauthenticated by design.
* If the endpoint is unreachable or returns something unexpected, the
  original draft is kept and a friendly warning is printed. Drafting never
  depends on a network.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Dict, List

DEFAULT_BASE_URL = "http://localhost:11434/v1"
DEFAULT_MODEL = "llama3.2"
DEFAULT_TIMEOUT = 45.0

POLISH_SYSTEM_PROMPT = (
    "You are a nurse educator's writing assistant. Rewrite the patient "
    "teaching sheet below in clear, warm, plain language for the stated "
    "reading level. Keep every fact, heading, and section exactly as given; "
    "only simplify wording. Never add medical advice, doses, or new "
    "recommendations. Never remove the education-only disclaimers. "
    "Return only the rewritten sheet text."
)


class PolishError(RuntimeError):
    """Polish could not complete; the caller should keep the draft."""


def polish_text(
    draft: str,
    base_url: str = DEFAULT_BASE_URL,
    model: str = DEFAULT_MODEL,
    level_label: str = "",
    timeout: float = DEFAULT_TIMEOUT,
) -> str:
    """Rewrite *draft* via an OpenAI-compatible chat completion.

    Raises PolishError on any failure. Never sends an Authorization header.
    """
    if not base_url:
        raise PolishError("polish needs a base_url (OpenAI-compatible endpoint)")
    url = base_url.rstrip("/") + "/chat/completions"
    payload: Dict[str, object] = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": POLISH_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Reading level: {level_label}\n\n{draft}",
            },
        ],
    }
    headers = {"Content-Type": "application/json"}  # no auth headers, ever
    try:
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except (urllib.error.URLError, OSError) as exc:
        raise PolishError(
            f"could not reach polish endpoint {url} ({exc.__class__.__name__})"
        ) from exc
    except Exception as exc:  # unexpected transport issue
        raise PolishError(f"polish request failed: {exc}") from exc

    try:
        result = json.loads(body)
        content: List[str] = [
            choice["message"]["content"] for choice in result["choices"]
        ]
        polished = content[0].strip()
    except (ValueError, KeyError, TypeError, IndexError):
        raise PolishError(
            "polish endpoint did not return the expected OpenAI-style response"
        )
    if not polished:
        raise PolishError("polish endpoint returned an empty response")
    return polished

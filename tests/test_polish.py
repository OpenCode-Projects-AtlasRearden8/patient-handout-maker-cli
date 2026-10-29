"""Tests for the optional polish step.

Uses a tiny local HTTP server that mimics an OpenAI-compatible
chat-completions endpoint, so every test is fully local.
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from patient_handout_maker.polish import (
    DEFAULT_BASE_URL,
    PolishError,
    polish_text,
)

DRAFT = "QUESTIONS TO ASK YOUR CARE TEAM\n  1.  ___"


class FakeEndpoint(BaseHTTPRequestHandler):
    last_path = None
    last_auth = None
    last_payload = None
    fail = False

    def do_POST(self):  # noqa: N802 (stdlib naming)
        FakeEndpoint.last_path = self.path
        FakeEndpoint.last_auth = self.headers.get("Authorization")
        length = int(self.headers.get("Content-Length", 0))
        FakeEndpoint.last_payload = json.loads(self.rfile.read(length))
        if FakeEndpoint.fail:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"{}")
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        body = json.dumps({"choices": [{"message": {"content": "POLISHED " + DRAFT}}]})
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, *args):  # silence request logging
        pass


class BadShapeEndpoint(BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802
        self.rfile.read(int(self.headers.get("Content-Length", 0)))
        body = json.dumps({"error": "no choices here"})
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, *args):
        pass


class EmptyEndpoint(BadShapeEndpoint):
    def do_POST(self):  # noqa: N802
        self.rfile.read(int(self.headers.get("Content-Length", 0)))
        body = json.dumps({"choices": [{"message": {"content": "   "}}]})
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, *args):
        pass


def start(handler):
    httpd = HTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd


def test_polish_success_and_request_shape():
    httpd = start(FakeEndpoint)
    base_url = f"http://127.0.0.1:{httpd.server_address[1]}/v1"
    result = polish_text(
        DRAFT, base_url=base_url, model="test-model", level_label="Plain language"
    )
    assert result.startswith("POLISHED")
    assert FakeEndpoint.last_path == "/v1/chat/completions"
    assert FakeEndpoint.last_auth is None  # never sends API keys
    payload = FakeEndpoint.last_payload
    assert payload["model"] == "test-model"
    assert payload["messages"][0]["role"] == "system"
    assert "plain" in payload["messages"][1]["content"].lower()
    assert "http" not in json.dumps(payload["messages"]).lower()
    httpd.shutdown()


def test_no_auth_header_always():
    httpd = start(FakeEndpoint)
    polish_text(DRAFT, base_url=f"http://127.0.0.1:{httpd.server_address[1]}/v1")
    assert FakeEndpoint.last_auth is None
    httpd.shutdown()


def test_http_500_raises_error():
    FakeEndpoint.fail = True
    try:
        httpd = start(FakeEndpoint)
        with pytest.raises(PolishError):
            polish_text(DRAFT, base_url=f"http://127.0.0.1:{httpd.server_address[1]}/x")
        httpd.shutdown()
    finally:
        FakeEndpoint.fail = False


def test_unexpected_response_shape():
    httpd = start(BadShapeEndpoint)
    with pytest.raises(PolishError):
        polish_text(DRAFT, base_url=f"http://127.0.0.1:{httpd.server_address[1]}/x")
    httpd.shutdown()


def test_empty_response():
    httpd = start(EmptyEndpoint)
    with pytest.raises(PolishError):
        polish_text(DRAFT, base_url=f"http://127.0.0.1:{httpd.server_address[1]}/x")
    httpd.shutdown()


def test_unreachable_endpoint_raises_friendly_error():
    # Port 9 on localhost is not serving anything in this environment.
    with pytest.raises(PolishError) as excinfo:
        polish_text(DRAFT, base_url="http://127.0.0.1:9/v1", timeout=1.0)
    assert "could not reach" in str(excinfo.value)


def test_default_base_url_is_local_ollama():
    assert DEFAULT_BASE_URL == "http://localhost:11434/v1"

"""End-to-end CLI tests."""

import json
from pathlib import Path

import pytest

from patient_handout_maker import cli

FIXTURES = Path(__file__).parent / "fixtures"


def run_cli(args, monkeypatch, capsys=None):
    return cli.run(args)


def test_list_templates(capsys):
    code = cli.run(["--list"])
    out = capsys.readouterr().out
    assert code == 0
    assert "what-it-is" in out
    assert "before-your-visit" in out
    assert "going-home" in out
    assert "easy" in out


def test_basic_sheet_to_file(tmp_path, capsys):
    out_file = tmp_path / "sheet.txt"
    code = cli.run(
        ["Type 2 Diabetes Basics", "--template", "what-it-is", "--level", "easy",
         "--out", str(out_file)]
    )
    assert code == 0
    text = out_file.read_text(encoding="utf-8")
    assert "TYPE 2 DIABETES BASICS" in text.upper()
    assert "education only" in text
    assert "5th-grade" in text
    assert "Asdale Dynamics, LLC" in text


def test_custom_template_fixture_file(tmp_path, capsys):
    out_file = tmp_path / "custom-sheet.txt"
    code = cli.run(
        ["Flu Shots", "--template", str(FIXTURES / "custom_template.json"),
         "--level", "plain", "--out", str(out_file)]
    )
    assert code == 0
    text = out_file.read_text(encoding="utf-8")
    assert "MEDICINE REVIEW" in text.upper()
    assert "Flu Shots" in text


def test_missing_topic_errors(capsys):
    with pytest.raises(SystemExit) as excinfo:
        cli.run([])
    assert excinfo.value.code != 0


def test_unknown_template_errors(capsys):
    with pytest.raises(SystemExit) as excinfo:
        cli.run(["Some Topic", "--template", "not-real"])
    assert excinfo.value.code != 0


def test_missing_template_file_errors(capsys):
    with pytest.raises(SystemExit) as excinfo:
        cli.run(["Some Topic", "--template", str(tmp_missing())])
    assert excinfo.value.code != 0


def tmp_missing():
    import tempfile
    return Path(tempfile.gettempdir()) / "patient-handout-maker-no-such-file.json"


def test_grade_check_flag(capsys):
    code = cli.run(["Asthma Basics", "--grade-check"])
    err = capsys.readouterr().err
    assert code == 0
    assert "reading-grade estimate" in err


def test_polish_with_fake_local_endpoint(monkeypatch, tmp_path, capsys):
    # Use the same fake OpenAI-compatible server from test_polish to run the
    # full CLI including the polish step.
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):  # noqa: N802
            length = int(self.headers.get("Content-Length", 0))
            self.rfile.read(length)
            body = json.dumps(
                {
                    "choices": [
                        {"message": {"content": "SIMPLIFIED DRAFT TEXT<" "end>"}},
                    ]
                }
            )
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body.encode())
            self.local_called = True

        def log_message(self, *args):
            pass

    httpd = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    base_url = f"http://127.0.0.1:{httpd.server_address[1]}/v1"
    try:
        code = cli.run(
            ["Hand Care", "--level", "easy", "--polish",
             "--base-url", base_url, "--model", "fake"]
        )
        out = capsys.readouterr().out
        assert code == 0
        assert "SIMPLIFIED DRAFT TEXT" in out
    finally:
        httpd.shutdown()


def test_polish_failure_falls_back_to_draft(capsys, monkeypatch):
    # Point at a port where nothing is listening.
    code = cli.run(
        ["Hand Care", "--level", "easy", "--polish",
         "--base-url", "http://127.0.0.1:9/v1", "--model", "fake",
         "--out", str(__import__("tempfile").gettempdir() + "/phm-fallback.txt")]
    )
    err = capsys.readouterr().err
    assert code == 0
    assert "Keeping the plain-language draft" in err
    Path(__import__("tempfile").gettempdir(), "phm-fallback.txt").unlink()

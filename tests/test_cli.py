# tests/test_cli.py
import json
from pathlib import Path
import pytest

from ophishal import cli

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "examples" / "config.json"
PKG_TEMPLATES = ROOT / "ophishal" / "templates"

@pytest.fixture
def tmpdir(tmp_path):
    return tmp_path

def run(argv):
    return cli.main(argv)

def test_help_shows_usage(capsys):
    with pytest.raises(SystemExit):
        cli.build_parser().parse_args(["-h"])
    out = capsys.readouterr().out + capsys.readouterr().err
    assert "ophishal" in out and "email" in out

def test_version(capsys):
    rc = run(["--version"])
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert out

def test_email_stdout_with_url_override(capsys):
    rc = run([
            "email",
            "--config", str(CFG),
            "--url",
            "http://example.com/x",
            "--output-only",
            "--output-email",
            "-"
    ])
    assert rc == 0
    out = capsys.readouterr().out
    assert "http://example.com/x" in out
    assert "<html>" in out and "Randy" in out

def test_email_with_template_override_file(tmpdir):
    custom = tmpdir / "tmpl.jinja"
    custom.write_text("X-TEST {{ url }} {{ sender }}", encoding="utf-8")
    out_html = tmpdir / "out.html"
    rc = run([
        "email",
        "--config", str(CFG),
        "--template", str(custom),
        "--url",
        "http://cb",
        "--output-only",
        "--output-email", str(out_html),
    ])
    assert rc == 0
    assert out_html.exists()
    s = out_html.read_text(encoding="utf-8")
    assert "X-TEST http://cb" in s

def test_attach_template_generates_ics_to_file(tmpdir):
    out_ics = tmpdir / "invite.ics"
    rc = run([
        "email",
        "--config", str(CFG),
        "--output-only",
        "--output-attach", str(out_ics),
    ])
    assert rc == 0
    t = out_ics.read_text(encoding="utf-8")
    assert "BEGIN:VCALENDAR" in t
    assert "SUMMARY:Action Required: Q3 Financials Access Expiration" in t
    assert "ORGANIZER;CN=Randy Marsh" in t

def test_attach_pass_through_file(tmpdir):
    src = tmpdir / "file.txt"
    src.write_text("abc", encoding="utf-8")
    dst = tmpdir / "out.dat"
    rc = run([
        "email",
        "--config", str(CFG),
        "--attachment", str(src),
        "--output-only",
        "--output-attach", str(dst),
    ])
    assert rc == 0
    assert dst.read_text(encoding="utf-8") == "abc"

def test_missing_template_errors(tmpdir, capsys):
    bad = tmpdir / "missing.jinja"
    with pytest.raises(FileNotFoundError):
        rc = run([
            "email",
            "--config", str(CFG),
            "--template", str(bad),
            "--output-only"
        ])
        assert rc == 2

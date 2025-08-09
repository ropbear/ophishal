# tests/test_cli.py
import json
from pathlib import Path
import pytest

from ophishal import cli

ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "examples" / "engagement.json"
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
    assert "ophishal" in out and "render" in out

def test_version(capsys):
    rc = run(["--version"])
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert out  # prints something like 0.0.0 in dev

def test_render_stdout_with_callback_override(capsys):
    rc = run(["render", "--config", str(ENG), "--callback-url", "http://example.com/x"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "http://example.com/x" in out
    assert "<html>" in out and "Microsoft Teams meeting" in out

def test_render_with_template_override_file(tmpdir):
    custom = tmpdir / "tmpl.jinja"
    custom.write_text("X-TEST {{ callback }} {{ body }}", encoding="utf-8")
    out_html = tmpdir / "out.html"
    rc = run([
        "render", "--config", str(ENG),
        "--template", str(custom),
        "--callback-url", "http://cb",
        "--out-email", str(out_html),
    ])
    assert rc == 0
    assert out_html.exists()
    s = out_html.read_text(encoding="utf-8")
    assert "X-TEST http://cb" in s

def test_render_with_package_template_override_by_name(tmpdir):
    # use the packaged name to ensure resolver finds it in ophishal/templates
    out_html = tmpdir / "out.html"
    rc = run([
        "render", "--config", str(ENG),
        "--template", "msft-teams.jinja",
        "--out-email", str(out_html),
    ])
    assert rc == 0
    assert out_html.exists()
    s = out_html.read_text(encoding="utf-8")
    assert "Microsoft Teams meeting" in s

def test_attach_template_generates_ics_to_file(tmpdir):
    out_ics = tmpdir / "invite.ics"
    rc = run([
        "render", "--config", str(ENG),
        "--attach-template",
        "--out-attach", str(out_ics),
    ])
    assert rc == 0
    t = out_ics.read_text(encoding="utf-8")
    assert "BEGIN:VCALENDAR" in t
    assert "SUMMARY:Action Required: Q3 Financials Access Expiration" in t
    assert "ORGANIZER;CN=Randy Marsh:" in t

def test_attach_pass_through_file(tmpdir):
    src = tmpdir / "file.txt"
    src.write_text("abc", encoding="utf-8")
    dst = tmpdir / "out.dat"
    rc = run([
        "render", "--config", str(ENG),
        "--attach", str(src),
        "--out-attach", str(dst),
    ])
    assert rc == 0
    assert dst.read_text(encoding="utf-8") == "abc"

def test_missing_template_errors(tmpdir, capsys):
    bad = tmpdir / "missing.jinja"
    rc = run([
        "render", "--config", str(ENG),
        "--template", str(bad)
    ])
    assert rc == 2
    err = capsys.readouterr().err + capsys.readouterr().out
    assert "Template not found" in err

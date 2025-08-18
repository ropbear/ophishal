# tests/test_cli.py

"""
This test suite relies on the following files:
config.json
- msft-teams.jinja
- icalendar.jinja
simple.json
- msft-teams.jinja
- icalendar.jinja
"""

import json
import toml
from pathlib import Path
import pytest
from logging import INFO

from ophishal import cli
from ophishal.log import LOG_COLORS

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "examples" / "config.json"
MIN_CFG = ROOT / "examples" / "simple.json"
MIN_ATTACH_CFG = ROOT / "examples" / "simple-attachment.json"
PKG_TEMPLATES = ROOT / "ophishal" / "templates"
PYPROJECT = ROOT / "pyproject.toml"


@pytest.fixture
def tmpdir(tmp_path):
    return tmp_path

def run(argv):
    return cli.main(argv)

### START core unit tests

def test_help_rc():
    with pytest.raises(SystemExit):
        rc = run(["--help"])
        assert rc == 0

def test_help_flag(capsys):
    with pytest.raises(SystemExit):
        cli.build_parser().parse_args(["-h"])
    out = capsys.readouterr().out + capsys.readouterr().err
    assert all([x in out for x in ["usage:", "positional arguments:", "options:"]])

def test_help_full_arg(capsys):
    with pytest.raises(SystemExit):
        cli.build_parser().parse_args(["--help"])
    out = capsys.readouterr().out + capsys.readouterr().err
    assert all([x in out for x in ["usage:", "positional arguments:", "options:"]])

def test_version_rc():
    rc = run(["--version"])
    assert rc == 0

def test_version_full_arg(capsys):
    run(["--version"])
    out = capsys.readouterr().out.strip()
    ver = toml.load(PYPROJECT)['project']['version']
    assert f"ophishal v{ver}" == out

def test_version_flag_is_not_verbose_flag(capsys):
    rc = run(["-v"])
    out = capsys.readouterr().out.strip()
    assert rc == 1 and all([x in out for x in ["usage:", "positional arguments:", "options:"]])

def test_unknown_cmd_behavior():
    with pytest.raises(SystemExit):
        rc = run(["thiscommanddoesnotexistnorwilliteverbecausewhowouldnamesomethinglikethisunlesstheyaretrollingme"])
        assert rc == 2

### END core unit tests

### START email cmd unit tests

def test_email_no_params_rc():
    with pytest.raises(SystemExit):
        rc = run([
                "email"
        ])
        assert rc == 2

def test_email_no_params_default_output(capsys):
    with pytest.raises(SystemExit):
        rc = run([
                "email"
        ])
        err = capsys.readouterr().err.strip()
        assert 'the following arguments are required:' in err

def test_email_basic_params_rc():
    rc = run([
            "email",
            "--config", str(CFG),
            "--dryrun",
    ])
    assert rc == 0

def test_email_basic_params_default_output(capsys):
    rc = run([
            "email",
            "--config", str(CFG),
            "--dryrun",
    ])
    out = capsys.readouterr().out.strip()
    assert out == ''

def test_email_bad_params_rc():
    with pytest.raises(SystemExit):
        rc = run([
                "email",
                "--config", str(CFG),
                "--thiscommanddoesnotexistnorwilliteverbecausewhowouldnamesomethinglikethisunlesstheyaretrollingme"
        ])
        assert rc == 2

def test_email_bad_params_default_output(capsys):
    with pytest.raises(SystemExit):
        rc = run([
                "email",
                "--config", str(CFG),
                "--thiscommanddoesnotexistnorwilliteverbecausewhowouldnamesomethinglikethisunlesstheyaretrollingme"
        ])
        err = capsys.readouterr().err.strip()
        assert 'unrecognized arguments:' in err

def test_email_basic_params_default_output_colored(capsys):
    rc = run([
            "-v",
            "email",
            "--config", str(CFG),
            "--dryrun",
    ])
    err = capsys.readouterr().err.strip()
    assert LOG_COLORS[INFO] in err

def test_email_basic_params_default_output_no_color(capsys):
    rc = run([
            "-v",
            "--no-color",
            "email",
            "--config", str(CFG),
            "--dryrun"
    ])
    err = capsys.readouterr().err.strip()
    assert LOG_COLORS[INFO] not in err

def test_email_basic_params_nc_verbose_flag_output(capsys):
    rc = run([
            "-v",
            "--no-color",
            "email",
            "--config", str(CFG),
            "--dryrun"
    ])
    err = capsys.readouterr().err.strip()
    assert '[INFO]' in err
    assert '[DBUG]' not in err

def test_email_basic_params_nc_very_verbose_flag_output(capsys):
    rc = run([
            "-vv",
            "--no-color",
            "email",
            "--config", str(CFG),
            "--dryrun"
    ])
    err = capsys.readouterr().err.strip()
    assert '[DBUG]' in err

# individual param (to stdout) unit tests

def test_email_param_outupt_body_to_stdout(capsys):
    rc = run([
        "email",
        "--config", str(CFG),
        "--output-body", "-",
        "--dryrun"
    ])
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert "<p>Randy Marsh</p>" in out

def test_email_param_output_attach_to_stdout(capsys):
    rc = run([
        "email",
        "--config", str(CFG),
        "--output-attach", "-",
        "--dryrun",
    ])
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert "BEGIN:VCALENDAR" in out
    assert "SUMMARY:Action Required: Q3 Financials Access Expiration" in out
    assert "ORGANIZER;CN=Randy Marsh" in out

# output to file unit tests

def test_email_param_output_body_to_file(tmpdir):
    custom = tmpdir / "tmpl.jinja"
    custom.write_text("X-TEST {{ sender.name }}", encoding="utf-8")
    out_html = tmpdir / "out.html"
    rc = run([
        "email",
        "--config", str(CFG),
        "--template", str(custom),
        "--output-body", str(out_html),
        "--dryrun"
    ])
    assert rc == 0
    assert out_html.exists()
    s = out_html.read_text(encoding="utf-8")
    assert "X-TEST Randy Marsh" in s

def test_email_param_output_attach_to_file(tmpdir):
    out_ics = tmpdir / "invite.ics"
    rc = run([
        "email",
        "--config", str(CFG),
        "--output-attach", str(out_ics),
        "--dryrun",
    ])
    assert rc == 0
    t = out_ics.read_text(encoding="utf-8")
    assert "BEGIN:VCALENDAR" in t
    assert "SUMMARY:Action Required: Q3 Financials Access Expiration" in t
    assert "ORGANIZER;CN=Randy Marsh" in t

def test_attach_pass_through_attachment(tmpdir):
    src = tmpdir / "file.txt"
    src.write_text("abc", encoding="utf-8")
    dst = tmpdir / "out.dat"
    rc = run([
        "email",
        "--config", str(CFG),
        "--attachment", str(src),
        "--dryrun",
        "--output-attach", str(dst),
    ])
    assert rc == 0
    assert dst.read_text(encoding="utf-8") == "abc"

# file not found unit tests

def test_email_param_template_missing(tmpdir):
    bad = tmpdir / "missing.jinja"
    with pytest.raises(FileNotFoundError):
        rc = run([
            "email",
            "--config", str(CFG),
            "--template", str(bad),
            "--dryrun"
        ])
        assert rc == 2

# cli override config file unit tests

def test_email_param_template_cli_override(tmpdir, capsys):
    custom = tmpdir / "tmpl.jinja"
    custom.write_text("X-TEST {{ sender.name }}", encoding="utf-8")
    rc = run([
        "email",
        "--config", str(CFG),
        "--template", str(custom),
        "--output-body", "-",
        "--dryrun"
    ])
    out = capsys.readouterr().out.strip()
    assert "X-TEST" in out
    assert "Microsoft Teams meeting" not in out

def test_email_param_attachment_cli_override(tmpdir, capsys):
    custom = tmpdir / "newfile.txt"
    custom.write_text("abc123", encoding="utf-8")
    rc = run([
        "email",
        "--config", str(MIN_ATTACH_CFG),
        "--attachment", str(custom),
        "--output-attach", "-",
        "--dryrun"
    ])
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert "abc123" in out
    assert "testfile" not in out

def test_email_param_attach_template_cli_override(tmpdir, capsys):
    custom = tmpdir / "tmpl.jinja"
    custom.write_text("TEST:{{ dtg_start }}", encoding="utf-8")
    rc = run([
        "email",
        "--config", str(CFG),
        "--attach-template", str(custom),
        "--output-attach", "-",
        "--dryrun"
    ])
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert "TEST:20250806T073059Z" in out
    assert "DTSTART;TZID=UTC:" not in out

def test_email_param_attach_params_cli_override(capsys):
    params = {
        "filename":"test",
        "dtg_start":"19700101T000000Z",
        "dtg_created":"19700101T000000Z",
        "dtg_end":"19700101T000000Z",
        "description":"test",
        "event_uid":"test",
        "organizer_email":"randy@test",
        "organizer_name":"Mandy Rarsh",
        "summary":"test"
    }
    rc = run([
        "email",
        "--config", str(CFG),
        "--attach-params", json.dumps(params),
        "--output-attach", "-",
        "--dryrun"
    ])
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert "20250806T073059Z" not in out
    assert "19700101T000000Z" not in out

def test_email_param_server_cli_override(capsys):
    rc = run([
            "email",
            "--config", str(CFG),
            "--server",
            "THISISNOTANIPADDRESS",
            "--dryrun"
    ])
    assert rc == 0
    err = capsys.readouterr().err
    assert "THISISNOTANIPADDRESS" in err

def test_email_param_url_cli_override(capsys):
    rc = run([
            "email",
            "--config", str(CFG),
            "--url",
            "http://example.com/fromthecli",
            "--output-body", "-",
            "--dryrun"
    ])
    assert rc == 0
    out = capsys.readouterr().out
    assert "http://example.com/fromthecli" in out

# combined cli param unit tests (not exhaustive combos)

@pytest.mark.xfail(reason="Not yet implemented")
def test_email_param_attach_template_params_cli_override():
    pass

@pytest.mark.xfail(reason="Not yet implemented")
def test_email_param_attachment_with_attach_template():
    pass

@pytest.mark.xfail(reason="Not yet implemented")
def test_email_param_attachment_with_attach_params():
    pass

def test_email_param_url_with_template_cli_override(tmpdir):
    custom = tmpdir / "tmpl.jinja"
    custom.write_text("X-TEST {{ url }} {{ sender.name }}", encoding="utf-8")
    out_html = tmpdir / "out.html"
    rc = run([
        "email",
        "--config", str(CFG),
        "--template", str(custom),
        "--output-body", str(out_html),
        "--dryrun"
    ])
    assert rc == 0
    assert out_html.exists()
    s = out_html.read_text(encoding="utf-8")
    assert "X-TEST http://callback" in s

# template

@pytest.mark.xfail(reason="Not yet implemented")
def test_():
    pass

### END email cmd unit tests
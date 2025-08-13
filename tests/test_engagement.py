# tests/test_engagement.py
import pytest
import json
from pathlib import Path
from ophishal.engagement import Engagement
from ophishal.models import Employee, Department, Company


TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "ophishal" / "templates"
ENG_FILE = Path(__file__).resolve().parent.parent / "examples" / "config.json"

@pytest.fixture
def engagement_config():
    with open(ENG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture
def eng_obj(engagement_config):
    return Engagement(config=engagement_config)

@pytest.fixture
def eng_built(eng_obj):
    eng_obj.build()
    return eng_obj


def test_constructs(eng_obj):
    assert isinstance(eng_obj, Engagement)

def test_campaign(eng_obj):
    assert eng_obj.campaign == "sptg-q3-finance-credential-harvest"

def test_company(eng_obj):
    assert isinstance(eng_obj.company, Company)
    assert eng_obj.company.uid == "sptg"

def test_departments(eng_obj):
    assert isinstance(eng_obj.departments["eng"], Department)
    assert eng_obj.departments["eng"].company.uid == "sptg"

def test_department_head_linked(eng_obj):
    assert isinstance(eng_obj.departments["eng"].head, Employee)
    assert eng_obj.departments["eng"].head.uid == "emp_randy"

def test_sender(eng_obj):
    assert isinstance(eng_obj.sender, Employee)
    assert eng_obj.sender.uid == "emp_randy"

def test_targets(eng_obj):
    assert any(isinstance(t, Employee) and t.uid == "emp_stan" for t in eng_obj.targets)

def test_subject(eng_obj):
    assert eng_obj.subject == "Action Required: Q3 Financials Access Expiration"

def test_body_contains_expected_text(eng_built):
    assert "Action Required" in eng_built.body

def test_template_path(eng_obj):
    assert eng_obj.template.name == "msft-teams.jinja"
    assert eng_obj.template.exists()

def test_url(eng_obj):
    assert eng_obj.url == "http://callback"

def test_attachment_fields(eng_built):
    a = eng_built.attachment
    assert b"ABCDEF" in a
    assert b"20250805T073059Z" in a
    assert b"20250806T073059Z" in a
    assert b"20250806T083059Z" in a
    assert b"A meeting for HR sync" in a
    assert b"Action Required: Q3" in a

def test_sender_sample_text_parsed(eng_obj):
    assert isinstance(eng_obj.sender.sample_text, str)
    assert "quick sync" in eng_obj.sender.sample_text


def test_sender_sample_text_optional_when_missing(engagement_config):
    cfg = engagement_config
    for e in cfg["employees"]:
        if e["uid"] == cfg["sender"]:
            e.pop("sample_text", None)
    eng = Engagement(config=cfg)
    assert eng.sender.sample_text is None

@pytest.mark.parametrize("missing_key", [
    "campaign", "company", "departments", "employees", 
    "sender", "targets", "subject"
])
def test_missing_required_key_raises(engagement_config, missing_key):
    cfg = dict(engagement_config)
    cfg.pop(missing_key, None)
    with pytest.raises(AttributeError):
        Engagement(config=cfg)

@pytest.mark.parametrize(
    "key,bad_value,exc",
    [
        ("campaign", 123, TypeError),
        ("company", [], TypeError),
        ("departments", {}, TypeError),
        ("employees", {}, TypeError),
        ("sender", 999, TypeError),
        ("targets", "emp_stan", TypeError),
        ("subject", 42, TypeError),
    ],
)
def test_wrong_type_raises(engagement_config, key, bad_value, exc):
    cfg = dict(engagement_config)
    cfg[key] = bad_value
    with pytest.raises(exc):
        Engagement(config=cfg)

def test_invalid_target_uid_raises(engagement_config):
    cfg = dict(engagement_config)
    cfg["targets"] = ["does_not_exist"]
    with pytest.raises(ValueError):
        Engagement(config=cfg)

def test_invalid_sender_uid_raises(engagement_config):
    cfg = dict(engagement_config)
    cfg["sender"] = "does_not_exist"
    with pytest.raises(KeyError):
        Engagement(config=cfg)

# tests/test_context.py
import json
import pytest
from pathlib import Path
from ophishal.context import Context
from ophishal.models import Company, Department, Employee

CTX_FILE = Path(__file__).resolve().parent.parent / "examples" / "context.json"

@pytest.fixture
def context_config():
    with open(CTX_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture
def ctx_obj(context_config):
    return Context(config=context_config)


def test_context_constructs(ctx_obj):
    assert isinstance(ctx_obj, Context)

def test_campaign_loaded(ctx_obj):
    assert isinstance(ctx_obj.campaign, str)
    assert ctx_obj.campaign == "sptg-q3-finance-credential-harvest"

def test_company_parsed(ctx_obj):
    c = ctx_obj.company
    assert isinstance(c, Company)
    assert c.uid == "sptg"
    assert c.official_name == "South Park Technology Group"
    assert c.common_names == ["South Park Tech", "SPTG"]
    assert c.abbreviations == ["SPTG"]
    assert c.net_worth == "1.3B USD"
    assert c.number_of_employees == 134
    assert c.type == "Private"
    assert c.industry == "Media"

def test_departments_parsed(ctx_obj):
    assert isinstance(ctx_obj.departments, dict)
    assert "eng" in ctx_obj.departments
    d = ctx_obj.departments["eng"]
    assert isinstance(d, Department)
    assert d.uid == "eng"
    assert d.name == "Engineering"
    assert d.company is ctx_obj.company

def test_department_head_linked(ctx_obj):
    d = ctx_obj.departments["eng"]
    assert isinstance(d.head, Employee)
    assert d.head.uid == "emp_randy"

def test_employees_parsed(ctx_obj):
    emps = ctx_obj.employees
    assert isinstance(emps, dict)
    assert {"emp_randy", "emp_stan"} <= set(emps.keys())

def test_employee_fields_and_department(ctx_obj):
    stan = ctx_obj.employees["emp_stan"]
    assert isinstance(stan, Employee)
    assert stan.username == "smarsh"
    assert stan.work_title == "Software Engineer I"
    assert stan.department is ctx_obj.departments["eng"]

def test_employee_reports_to_linked(ctx_obj):
    stan = ctx_obj.employees["emp_stan"]
    randy = ctx_obj.employees["emp_randy"]
    assert stan.reports_to is randy

def test_sender_parsed(ctx_obj):
    assert isinstance(ctx_obj.sender, Employee)
    assert ctx_obj.sender.uid == "emp_randy"

def test_targets_resolved(ctx_obj):
    assert len(ctx_obj.targets) == 1
    tgt = ctx_obj.targets[0]
    assert isinstance(tgt, Employee)
    assert tgt.uid == "emp_stan"

def test_culture_parsed(ctx_obj):
    cu = ctx_obj.culture
    assert cu.city == "South Park"
    assert cu.province == "Colorado"
    assert cu.country_code == "US"
    assert cu.workplace == "Casual"

def test_tech_list(ctx_obj):
    assert ctx_obj.tech == [
        "Google Workspace", "Slack", "Zoom", "AWS",
        "Okta", "Jira", "CrowdStrike", "GitHub Enterprise"
    ]

def test_current_events_list(ctx_obj):
    assert ctx_obj.current_events == [
        "Preparing for launch of 'SP MetaVerse' VR platform",
        "Internal phishing test scheduled next week",
        "Recent outage in South Park data center",
        "Hiring freeze announced in non-engineering departments",
    ]

def test_employee_sample_text_parsed(ctx_obj):
    randy = ctx_obj.employees["emp_randy"]
    assert isinstance(randy.sample_text, str)
    assert "quick sync" in randy.sample_text


def test_employee_sample_text_optional_when_missing(context_config, tmp_path):
    cfg = context_config
    for e in cfg["employees"]:
        if e["uid"] == "emp_stan":
            e.pop("sample_text", None)

    ctx = Context(config=cfg)
    assert "emp_stan" in ctx.employees
    assert ctx.employees["emp_stan"].sample_text is None

@pytest.mark.parametrize("missing_key", [
    "campaign", "company", "departments", "employees",
    "sender", "targets", "culture", "tech", "current_events",
])
def test_missing_required_key_raises(context_config, missing_key):
    cfg = dict(context_config)
    cfg.pop(missing_key, None)
    with pytest.raises(AttributeError):
        Context(config=cfg)

@pytest.mark.parametrize(
    "key,bad_value,exc",
    [
        ("campaign", 123, TypeError),
        ("company", [], TypeError),
        ("departments", {}, TypeError),
        ("employees", {}, TypeError),
        ("sender", 999, TypeError),
        ("targets", "emp_stan", TypeError),
        ("culture", [], TypeError),
        ("tech", "Slack", TypeError),
        ("current_events", {"a": 1}, TypeError),
    ],
)
def test_wrong_type_raises(context_config, key, bad_value, exc):
    cfg = dict(context_config)
    cfg[key] = bad_value
    with pytest.raises(exc):
        Context(config=cfg)

def test_invalid_target_uid_raises(context_config):
    cfg = dict(context_config)
    cfg["targets"] = ["no_such_uid"]
    with pytest.raises(ValueError):
        Context(config=cfg)

def test_invalid_sender_uid_raises(context_config):
    cfg = dict(context_config)
    cfg["sender"] = "no_such_uid"
    # KeyError arises when BaseConfig tries to look up sender in employees
    with pytest.raises(KeyError):
        Context(config=cfg)

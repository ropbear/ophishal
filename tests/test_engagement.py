# tests/test_engagement.py

"""
This test suite relies on the following files:
config.json
- msft-teams.jinja
- icalendar.jinja
simple.json
- msft-teams.jinja
- icalendar.jinja

This test suite does not cover the following portions of a configuration file:
- culture
- tech
- current_events
- medium
- pretext
- desired_action
- constraints
"""

import pytest
import json
from pathlib import Path

from ophishal.engagement import EmailEngagement
from ophishal.model import Employee, Department, Company


ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR =  ROOT / "templates"
CFG = ROOT / "examples" / "config.json"
MIN_CFG = ROOT / "examples" / "simple.json"


@pytest.fixture
def engagement_config():
    with open(CFG, "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture
def eng_obj(engagement_config):
    return EmailEngagement(config=engagement_config)

@pytest.fixture
def eng_built(eng_obj):
    eng_obj.build()
    return eng_obj

### START core unit tests

@pytest.mark.parametrize("missing_key", [
    "campaign", "company", "departments", "employees", 
    "sender", "targets", "email"
])
def test_missing_required_key_raises(engagement_config, missing_key):
    cfg = dict(engagement_config)
    cfg.pop(missing_key, None)
    with pytest.raises(AttributeError):
        EmailEngagement(config=cfg)

@pytest.mark.parametrize(
    "key,bad_value,exc",
    [
        ("campaign", 123, TypeError),
        ("company", [], TypeError),
        ("departments", {}, TypeError),
        ("employees", {}, TypeError),
        ("sender", 999, TypeError),
        ("targets", "emp_stan", TypeError),
        ("email", 42, TypeError),
    ],
)
def test_wrong_type_raises(engagement_config, key, bad_value, exc):
    cfg = dict(engagement_config)
    cfg[key] = bad_value
    with pytest.raises(exc):
        EmailEngagement(config=cfg)

def test_invalid_target_uid_raises(engagement_config):
    cfg = dict(engagement_config)
    cfg["targets"] = ["does_not_exist"]
    with pytest.raises(ValueError):
        EmailEngagement(config=cfg)

def test_invalid_sender_uid_raises(engagement_config):
    cfg = dict(engagement_config)
    cfg["sender"] = "does_not_exist"
    with pytest.raises(ValueError):
        EmailEngagement(config=cfg)

### END core unit tests

### START examples/config.json unit tests

def test_object_creation_from_config(eng_obj):
    eng = eng_obj
    assert isinstance(eng, EmailEngagement)

# campaign unit tests

def test_campaign(eng_obj):
    assert eng_obj.campaign == "sptg-q3-finance-credential-harvest"

# company unit tests

def test_company_object(eng_obj):
    assert isinstance(eng_obj.company, Company)

def test_company_correct_uid(eng_obj):
    assert eng_obj.company.uid == "sptg"

# department unit tests

def test_department_object(eng_obj):
    assert isinstance(eng_obj.departments["eng"], Department)

def test_department_object_correct_uid(eng_obj):
    assert eng_obj.departments["eng"].uid == "eng"

def test_department_company_object(eng_obj):
    assert isinstance(eng_obj.departments["eng"].company, Company)

def test_department_correct_company_uid(eng_obj):
    assert eng_obj.departments["eng"].company.uid == "sptg"

def test_department_head_object(eng_obj):
    assert isinstance(eng_obj.departments["eng"].head, Employee)

def test_department_correct_head_uid(eng_obj):
    assert eng_obj.departments["eng"].head.uid == "emp_randy"

def test_department_email(eng_obj):
    assert eng_obj.departments["eng"].email == "engineering@localhost"

def test_department_name(eng_obj):
    assert eng_obj.departments["eng"].name == "Engineering"

# employee unit tests

def test_employee_objects(eng_obj):
    assert all([isinstance(e, Employee) for e in eng_obj.employees.values()])

def test_employee_uid(eng_obj):
    emp = eng_obj.employees["emp_randy"]
    assert emp.uid == "emp_randy"

def test_employee_name(eng_obj):
    emp = eng_obj.employees["emp_randy"]
    assert emp.name == "Randy Marsh"

def test_employee_username(eng_obj):
    emp = eng_obj.employees["emp_randy"]
    assert emp.username == "rmarsh"

def test_employee_dept_object(eng_obj):
    emp = eng_obj.employees["emp_randy"]
    assert isinstance(emp.department, Department)

def test_employee_dept_uid(eng_obj):
    emp = eng_obj.employees["emp_randy"]
    assert emp.department.uid == "eng"

def test_employee_email(eng_obj):
    emp = eng_obj.employees["emp_randy"]
    assert emp.email == "randy@localhost"

def test_employee_no_email(eng_obj):
    emp = eng_obj.employees["emp_stan"]
    assert emp.email is None

def test_employee_phone(eng_obj):
    emp = eng_obj.employees["emp_randy"]
    assert emp.phone == "(303) 555-1001"

def test_employee_no_phone(eng_obj):
    emp = eng_obj.employees["emp_stan"]
    assert emp.phone is None

def test_employee_reports_to_object(eng_obj):
    emp = eng_obj.employees["emp_stan"]
    assert isinstance(emp.reports_to, Employee)

def test_employee_reports_to_uid(eng_obj):
    emp = eng_obj.employees["emp_stan"]
    assert emp.reports_to.uid == "emp_randy"

def test_employee_no_reports_to(eng_obj):
    emp = eng_obj.employees["emp_randy"]
    assert emp.reports_to is None    

# sender unit tests

def test_sender_object(eng_obj):
    assert isinstance(eng_obj.sender, Employee)

def test_sender_uid(eng_obj):
    assert eng_obj.sender.uid == "emp_randy"

@pytest.mark.xfail(reason="Not yet implemented")
def test_sender_sample_text_exists(eng_obj):
    assert isinstance(eng_obj.sender.sample_text, str)

@pytest.mark.xfail(reason="Not yet implemented")
def test_sender_sample_text_optional_when_missing(engagement_config):
    cfg = engagement_config
    for e in cfg["employees"]:
        if e["uid"] == cfg["sender"]:
            e.pop("sample_text", None)
    eng = EmailEngagement(config=cfg)
    assert eng.sender.sample_text is None

# target unit tests

def test_targets(eng_obj):
    assert any(isinstance(t, Employee) and t.uid == "emp_stan" for t in eng_obj.targets)

# subject unit tests

def test_subject(eng_obj):
    assert eng_obj.subject == "Action Required: Q3 Financials Access Expiration"

# email body unit tests

def test_body_contains_expected_text(eng_built):
    assert "Action Required" in eng_built.body

# template unit tests

def test_template_exists(eng_obj):
    assert eng_obj.template.exists()

def test_template_path(eng_obj):
    assert eng_obj.template.name == "msft-teams.jinja"

# server unit tests

def test_server(eng_obj):
    assert eng_obj.server == "192.168.1.25"

# url unit tests

def test_url(eng_obj):
    assert eng_obj.url == "http://callback"

# attachment unit tests

def test_attachment_fields(eng_built):
    a = eng_built.attachment
    assert b"ABCDEF" in a
    assert b"20250805T073059Z" in a
    assert b"20250806T073059Z" in a
    assert b"20250806T083059Z" in a
    assert b"A meeting for HR sync" in a
    assert b"Action Required: Q3" in a

### END examples/config.json unit tests

### START examples/simple.json unit tests

### END examples/simple.json unit tests

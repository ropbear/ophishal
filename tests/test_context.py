# tests/test_context.py
import os
import json
import pytest
from ophishal.context.context import Context

TESTFILE = os.path.join(os.path.dirname(__file__), "..", "examples", "context.json")

@pytest.fixture
def generate_context():
    return Context(filepath=TESTFILE)

def test_context_parsing_from_file(generate_context):
    ctx = generate_context
    assert ctx
    assert isinstance(ctx, Context)

def test_context_parsing_null_json():
    assert None == Context()

def test_context_parsing_empty_json():
    assert None == Context(config={})

def test_context_parsing_company(generate_context):
    ctx = generate_context
    company = ctx.company
    assert company.uid == "sptg"
    assert company.official_name == "South Park Technology Group"
    assert company.common_names == ["South Park Tech", "SPTG"]
    assert company.abbreviations == ["SPTG"]
    assert company.net_worth == "1.3B USD"
    assert company.number_of_employees == 134
    assert company.type == "Private"
    assert company.industry == "Media"

def test_context_parsing_target_employees(generate_context):
    ctx = generate_context
    assert ctx.target_employees
    assert ctx.target_employees == ["emp_stan", "emp_cartman"]

def test_context_parsing_employees(generate_context):
    ctx = generate_context
    emp = ctx.employees["emp_stan"]
    assert emp.uid == "emp_stan"
    assert emp.first_name == "Stan"
    assert emp.last_name == "Marsh"
    assert emp.nickname == "Stan"
    assert emp.username == "smarsh"
    assert emp.department == "Engineering"
    assert emp.work_title == "Software Engineer I"
    assert emp.signature_block == "Stan Marsh | Software Engineer I"
    assert emp.work_email == "smarsh@sptg.com"
    assert emp.work_phone == None
    assert emp.personal_email == "stan@example.com"
    assert emp.personal_phone == "(303) 555-2020"
    assert emp.location == "South Park, CO"
    assert emp.reports_to == ctx.employees["emp_randy"].uid

def test_context_parsing_depts(generate_context):
    ctx = generate_context
    dept = ctx.departments["eng"]
    assert dept.uid == "eng"
    assert dept.name == "Engineering"
    assert dept.head_uid == "emp_stan"
    assert dept.company_uid == "sptg"

def test_context_parsing_culture(generate_context):
    ctx = generate_context
    assert ctx.culture.city == "South Park"
    assert ctx.culture.province == "Colorado"
    assert ctx.culture.country_code == "US"
    assert ctx.culture.workplace == "Casual"

def test_context_parsing_infotech(generate_context):
    ctx = generate_context
    assert ctx.information_technologies == [
        "Google Workspace",
        "Slack",
        "Zoom",
        "AWS",
        "Okta",
        "Jira",
        "CrowdStrike",
        "GitHub Enterprise"
    ]

def test_context_parsing_current_events(generate_context):
    ctx = generate_context
    assert ctx.current_events == [
        "Preparing for launch of 'SP MetaVerse' VR platform",
        "Internal phishing test scheduled next week",
        "Recent outage in South Park data center",
        "Hiring freeze announced in non-engineering departments"
    ]

def test_context_parsing_current_access(generate_context):
    ctx = generate_context
    assert ctx.current_access == ["emp_stan"]
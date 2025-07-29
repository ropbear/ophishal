# tests/test_context.py
import os
import json
import pytest
from ophishal.context.context import Context

TESTFILE = os.path.join(os.path.dirname(__file__), "..", "examples", "context.json")

def common_asserts(context:Context):
    # Basics
    assert context.company.official_name
    assert isinstance(context.employees, dict)

    # CompanyProfile attributes
    company = context.company
    assert company.uid == "sptg"
    assert company.official_name == "South Park Technology Group"
    assert company.common_names == ["South Park Tech", "SPTG"]
    assert company.abbreviations == ["SPTG"]
    assert company.net_worth == "1.3B USD"
    assert company.number_of_employees == 134
    assert company.type == "Private"
    assert company.industry == "Media"

    # EmployeeProfile attributes
    emp = context.employees["emp_stan"]
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
    assert emp.reports_to == context.employees["emp_randy"].uid

    # DepartmentProfile attributes
    dept = context.departments["eng"]
    assert dept.uid == "eng"
    assert dept.name == "Engineering"
    assert dept.head_uid == "emp_stan"

    # Additional context metadata
    assert context.culture["location"] == "South Park, CO"
    assert context.culture["majority_ethnicity"] == "White"
    assert context.culture["workplace_culture"] == "Casual"
    assert context.information_technologies == [
        "Google Workspace",
        "Slack",
        "Zoom",
        "AWS",
        "Okta",
        "Jira",
        "CrowdStrike",
        "GitHub Enterprise"
    ]
    assert context.current_events == [
        "Preparing for launch of 'SP MetaVerse' VR platform",
        "Internal phishing test scheduled next week",
        "Recent outage in South Park data center",
        "Hiring freeze announced in non-engineering departments"
    ]
    assert context.current_access == ["emp_stan"]

def test_context_parsing_from_json():
    with open(TESTFILE, "r") as f:
        config = json.load(f)
    context = Context(config=config)
    common_asserts(context)

def test_context_parsing_from_file():
    context = Context(filepath=TESTFILE)
    common_asserts(context)

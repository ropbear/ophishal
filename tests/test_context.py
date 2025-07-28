# tests/test_context.py

import os
import json
import pytest
from ophishal.context.context import Context

@pytest.fixture
def sample_context_json():
    return {
        "company": {
            "official_name": "South Park Technology Group",
            "common_names": ["South Park Tech", "SPTG"],
            "abbreviations": ["SPTG"],
            "net_worth": "1.3B USD",
            "number_of_employees": 134,
            "type": "Private",
            "industry": "Media"
        },
        "employees": {
            "emp_stan": {
                "employee_id": "emp_stan",
                "first_name": "Stan",
                "last_name": "Marsh",
                "nickname": "Stan",
                "username": "smarsh",
                "department": "Engineering",
                "work_title": "Software Engineer I",
                "signature_block": "Stan Marsh | Software Engineer I",
                "work_email": "smarsh@sptg.com",
                "work_phone": None,
                "personal_email": "stan@example.com",
                "personal_phone": "(303) 555-2020",
                "location": "South Park, CO",
                "reports_to": None
            }
        },
        "departments": [
            {
                "name": "Engineering",
                "head_id": "emp_stan"
            }
        ],
        "culture": {
            "location": "South Park, CO",
            "majority_ethnicity": "White",
            "workplace_culture": "Casual"
        },
        "information_technologies": ["Slack", "Zoom"],
        "current_events": ["Quarterly launch prep"],
        "current_access": ["emp_stan"]
    }

@pytest.fixture
def sample_context_file():
    testfile = os.path.join(os.path.dirname(__file__), "..", "examples", "context.json")
    with open(testfile, "r", encoding="utf-8") as f:
        return json.load(f)

def test_context_parsing_from_json(sample_context_json):
    context = Context.from_json(sample_context_json)

    # Basics
    assert context.company.official_name
    assert isinstance(context.employees, dict)

    # CompanyProfile attributes
    company = context.company
    assert company.official_name == "South Park Technology Group"
    assert company.common_names == ["South Park Tech", "SPTG"]
    assert company.abbreviations == ["SPTG"]
    assert company.net_worth == "1.3B USD"
    assert company.number_of_employees == 134
    assert company.type == "Private"
    assert company.industry == "Media"

    # EmployeeProfile attributes
    emp = context.employees["emp_stan"]
    assert emp.employee_id == "emp_stan"
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
    assert emp.reports_to is None

    # DepartmentProfile attributes
    dept = context.departments[0]
    assert dept.name == "Engineering"
    assert dept.head_id == "emp_stan"

    # Additional context metadata
    assert context.culture["location"] == "South Park, CO"
    assert context.culture["majority_ethnicity"] == "White"
    assert context.culture["workplace_culture"] == "Casual"
    assert context.information_technologies == ["Slack", "Zoom"]
    assert context.current_events == ["Quarterly launch prep"]
    assert context.current_access == ["emp_stan"]

def test_context_parsing_from_file(sample_context_file):
    context = Context.from_json(sample_context_file)

    # Basics
    assert context.company.official_name
    assert isinstance(context.employees, dict)

    # CompanyProfile attributes
    company = context.company
    assert company.official_name == "South Park Technology Group"
    assert company.common_names == ["South Park Tech", "SPTG"]
    assert company.abbreviations == ["SPTG"]
    assert company.net_worth == "1.3B USD"
    assert company.number_of_employees == 134
    assert company.type == "Private"
    assert company.industry == "Media"

    # EmployeeProfile attributes
    emp = context.employees["emp_stan"]
    assert emp.employee_id == "emp_stan"
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
    assert emp.reports_to == "emp_randy"

    # Departments (null in this case)
    assert context.departments == []

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
    assert context.current_access == ["emp_kyle", "emp_kenny"]
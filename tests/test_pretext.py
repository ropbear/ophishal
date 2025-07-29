# tests/test_pretext.py
import os
import json
import pytest
from pathlib import Path
from ophishal.pretext.pretext import Pretext

TESTFILE = os.path.join(os.path.dirname(__file__), "..", "examples", "pretext.json")

def common_asserts(p:Pretext):
    assert p.campaign_identifier == "sptg-q3-finance-credential-harvest"
    assert p.vector == "email"
    assert p.source.type == "employee"
    assert p.source.uid == "emp_randy"

    assert len(p.targets) == 2
    assert p.targets[0].type == "employee"
    assert p.targets[0].uid == "emp_stan"
    assert p.targets[1].uid == "emp_cartman"

    assert p.persuasion_mechanisms == ["urgency", "authority"]
    assert p.language_style == "corporate, direct, urgent"
    assert p.topic == "quarterly financial report access issue"
    assert p.phish_type == "credential phishing"
    assert p.email_subject == "Action Required: Q3 Financials Access Expiration"
    assert "https://sptg-financials-login.com" in p.email_body
    assert p.selected_template == "standard-access-urgency.html"

def test_pretext_json():
    with open(TESTFILE, "r") as f:
        config = json.load(f)
    common_asserts(Pretext(config=config))

def test_pretext_file():
    common_asserts(Pretext(filepath=TESTFILE))

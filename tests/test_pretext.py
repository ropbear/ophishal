# tests/test_pretext.py
import json
import pytest
from pathlib import Path
from ophishal.pretext.pretext import Pretext, PhishSource, PhishTarget

@pytest.fixture
def generate_pretext():
    testfile = Path(__file__).resolve().parent.parent / "examples" / "pretext.json"
    return Pretext(filepath=testfile)

def test_pretext_campaign_id(generate_pretext):
    ptx = generate_pretext
    assert ptx.campaign_identifier == "sptg-q3-finance-credential-harvest"
    assert isinstance(ptx.campaign_identifier, str)

def test_pretext_vector(generate_pretext):
    ptx = generate_pretext
    assert ptx.vector == "email"
    assert isinstance(ptx.vector, str)

def test_pretext_source(generate_pretext):
    ptx = generate_pretext
    assert isinstance(ptx.source, PhishSource)
    assert ptx.source.type == "employee"
    assert isinstance(ptx.source.type, str)
    assert ptx.source.uid == "emp_randy"
    assert isinstance(ptx.source.uid, str)

def test_pretext_targets(generate_pretext):
    ptx = generate_pretext
    assert isinstance(ptx.targets, list)
    assert all([isinstance(tgt, PhishTarget) for tgt in ptx.targets])
    assert ptx.targets[0].type == "employee"
    assert ptx.targets[1].uid == "emp_cartman"

def test_pretext_persuasion_mechs(generate_pretext):
    ptx = generate_pretext
    assert isinstance(ptx.persuasion_mechanisms, list)
    assert ptx.persuasion_mechanisms == ["urgency","authority"]

def test_pretext_language(generate_pretext):
    ptx = generate_pretext
    assert isinstance(ptx.language, str)
    assert ptx.language == "en"

def test_pretext_language_style(generate_pretext):
    ptx = generate_pretext
    assert isinstance(ptx.language_style, list)
    assert ptx.language_style == ["corporate", "direct", "urgent"]

def test_pretext_topic(generate_pretext):
    ptx = generate_pretext
    assert isinstance(ptx.topic, str)
    assert ptx.topic == "quarterly financial report access issue"

def test_pretext_phish_type(generate_pretext):
    ptx = generate_pretext
    assert isinstance(ptx.phish_type, str)
    assert ptx.phish_type == "credential phishing"

def test_pretext_email_subject(generate_pretext):
    ptx = generate_pretext
    assert isinstance(ptx.email_subject, str)
    assert ptx.email_subject == "Action Required: Q3 Financials Access Expiration"

def test_pretext_email_body(generate_pretext):
    ptx = generate_pretext
    assert isinstance(ptx.email_body, str)
    assert ptx.email_body == "Hi team,\n\nWe’ve identified an issue with your current permissions to view the Q3 financial documents in our internal system. As of today, your access will expire in 24 hours unless revalidated.\n\nPlease use the secure access portal below to re-authenticate:\n\nhttps://sptg-financials-login.com\n\nThis is time-sensitive and requires completion before COB today.\n\nThanks,\nRandy"

def test_pretext_template(generate_pretext):
    ptx = generate_pretext
    assert isinstance(ptx.template, Path)
    assert ptx.template == Path("standard-access-urgency.html")

def test_pretext_attachment(generate_pretext):
    ptx = generate_pretext
    assert isinstance(ptx.attachment, Path)
    assert ptx.attachment == Path("invite.ics")

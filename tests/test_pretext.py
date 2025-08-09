# tests/test_pretext.py
import pytest
import json
from pathlib import Path
from ophishal.pretext.pretext import Pretext


PRETEXT_FILE = Path(__file__).resolve().parent.parent / "examples" / "pretext.json"


@pytest.fixture
def pretext_config():
    with open(PRETEXT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture
def ptx_obj(pretext_config):
    return Pretext(config=pretext_config)


def test_constructs(ptx_obj):
    assert isinstance(ptx_obj, Pretext)

def test_medium(ptx_obj):
    assert ptx_obj.medium == "email"

def test_pretext_text(ptx_obj):
    assert "SP MetaVerse" in ptx_obj.pretext

def test_desired_action(ptx_obj):
    assert ptx_obj.desired_action == "download docx and enable macros"

def test_constraints(ptx_obj):
    assert isinstance(ptx_obj.constraints, list)
    assert "no spoofing legal department" in ptx_obj.constraints

def test_pretext_employee_sample_text(ptx_obj):
    emp = ptx_obj.employees["emp_randy"]
    assert isinstance(emp.sample_text, str)
    assert "quick sync on the VR" in emp.sample_text


def test_sender_sample_text_optional_when_missing(pretext_config):
    cfg = pretext_config
    for e in cfg["employees"]:
        if e["uid"] == cfg["sender"]:
            e.pop("sample_text", None)
    ptx = Pretext(config=cfg)
    assert ptx.sender.sample_text is None

@pytest.mark.parametrize(
    "missing_key",
    ["medium", "pretext", "desired_action", "constraints"]
)
def test_missing_required_key_raises(pretext_config, missing_key):
    cfg = dict(pretext_config)
    cfg.pop(missing_key, None)
    with pytest.raises(AttributeError):
        Pretext(config=cfg)

@pytest.mark.parametrize(
    "key,bad_value,exc_type",
    [
        ("medium", 123, TypeError),
        ("pretext", 456, TypeError),
        ("desired_action", ["click"], TypeError),
        ("constraints", "not-a-list", TypeError),
    ],
)
def test_wrong_type_raises(pretext_config, key, bad_value, exc_type):
    cfg = dict(pretext_config)
    cfg[key] = bad_value
    with pytest.raises(exc_type):
        Pretext(config=cfg)

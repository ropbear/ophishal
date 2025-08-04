# tests/test_pretext.py
import json
import pytest
from pathlib import Path
from ophishal.pretext.pretext import Pretext

@pytest.fixture
def generate_pretext():
    testfile = Path(__file__).resolve().parent.parent / "examples" / "pretext.json"
    return Pretext(filepath=testfile)

def test_pretext(generate_pretext):
    pass
# ophishal/engagement/engagement.py
from pathlib import Path
from ophishal.common.util import resolve_target
from ophishal.common.config import BaseConfig
from ophishal.models import Attachment
from typing import Optional

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"

class Engagement(BaseConfig):
    require = {
        "campaign": str,
        "company": dict,
        "departments": list,
        "employees": list,
        "sender": str,
        "targets": list,
        "subject": str
    }

    def parse(self, config: dict):
        self.subject = config["subject"]
        if "template" in config:
            self.template = TEMPLATE_DIR / config["template"]
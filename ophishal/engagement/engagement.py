# ophishal/engagement/engagement.py
from pathlib import Path
from ophishal.common.util import resolve_target
from ophishal.common.config import BaseConfig
from ophishal.common.models import Attachment

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"

class Engagement(BaseConfig):
    require = {
        "campaign": str,
        "company": dict,
        "departments": list,
        "employees": list,
        "sender": str,
        "targets": list,
        "subject": str,
        "body": str,
        "template": str,
        "callback": str,
        "attachment": dict
    }

    def parse(self, config: dict):
        self.subject = config["subject"]
        self.body = config["body"]
        self.template = TEMPLATE_DIR / config["template"]
        self.callback = config["callback"]
        self.attachment = Attachment(**config["attachment"])

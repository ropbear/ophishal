# ophishal/pretext/pretext.py
from pathlib import Path
from ophishal.config import BaseConfig

class Pretext(BaseConfig):
    require = {
        "campaign": str,
        "company": dict,
        "departments": list,
        "employees": list,
        "sender": str,
        "targets": list,
        "culture": dict,
        "tech": list,
        "current_events": list,
        "medium": str,
        "pretext": str,
        "desired_action": str,
        "constraints": list
    }

    def _parse(self, config: dict):
        self.medium = config["medium"]
        self.pretext = config["pretext"]
        self.desired_action = config["desired_action"]
        self.constraints = config["constraints"]
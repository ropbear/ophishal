# ophishal/context/context.py
from ophishal.common.config import BaseConfig

class Context(BaseConfig):
    require = {
        "campaign": str,
        "company": dict,
        "departments": list,
        "employees": list,
        "sender": str,
        "targets": list,
        "culture": dict,
        "tech": list,
        "current_events": list
    }

    def parse(self, config: dict):
        pass

# ophishal/common/config.py
import json
from pathlib import Path
from ophishal.common.util import resolve_target
from ophishal.common.models import Company, Department, Employee, Culture, Target

class BaseConfig:
    require = {}
    def __init__(self, config:dict=None, filepath:Path=None):
        if filepath is not None and config is not None:
            raise ValueError("Can't have both config and filepath")

        if filepath is not None and isinstance(filepath, Path):
            if filepath.exists():
                config = self.__from_file(filepath)
            else:
                raise FileNotFoundError("Configuration file does not exist")
        
        if config is not None and isinstance(config, dict):
            for key in self.require.keys():
                if key not in config.keys():
                    raise AttributeError(
                        "Configuration missing keys: " + \
                        f"{list(set(self.require.keys()) - set(config.keys()))}"
                    )
                elif not isinstance(config[key], self.require[key]):
                    raise TypeError(
                        f"Key '{key}' should be  of type {self.require[key]}" + \
                        f", got {type(config[key])}"
                    )
        else:
            raise ValueError("No valid configuration parameter specified")

        self.__common(config)
        self.parse(config)

    def __from_file(self, filepath:Path) -> dict:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def __common(self, config:dict):
        """
        These configuration attributes are going to be common across all
        proponents of the program.
        """
        self.company = Company(**config["company"])

        self.departments = {
            d["uid"]: Department(
                uid=d["uid"],
                name=d["name"],
                company=self.company,
                head=None  # placeholder
            )
            for d in config["departments"]
        }
        self.employees = {
            e["uid"]: Employee(
                uid=e["uid"],
                first_name=e["first_name"],
                last_name=e["last_name"],
                nickname=e.get("nickname"),
                username=e["username"],
                department=self.departments[e["department_uid"]],
                work_title=e["work_title"],
                signature_block=e["signature_block"],
                work_email=e.get("work_email"),
                work_phone=e.get("work_phone"),
                personal_email=e.get("personal_email"),
                personal_phone=e.get("personal_phone"),
                location=e["location"],
                reports_to=None,
                sample_text=e.get("sample_text")
            )
            for e in config["employees"]
        }

        for dept in config["departments"]:
            if dept.get("head_uid"):
                self.departments[dept["uid"]].head = self.employees[dept["head_uid"]]

        for e in config["employees"]:
            if e.get("reports_to"):
                self.employees[e["uid"]].reports_to = self.employees[e["reports_to"]]

        self.campaign = config["campaign"]
        self.sender = self.employees[config["sender"]]
        self.targets = [resolve_target(uid, self) for uid in config["targets"]]
        self.culture = Culture(**config["culture"])
        self.tech = config["tech"]
        self.current_events = config["current_events"]

    def parse(self, config:dict):
        """
        Classes which inherit this base class will use this function to
        parse out the details they need from the dictionary.
        """
        pass

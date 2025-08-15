# ophishal/common/config.py
import json
from pathlib import Path
from ophishal.util import resolve_uid
from ophishal.model import Company, Department, Employee, Culture, Target
from ophishal.log import create_logger

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
        self._parse(config)

    def __from_file(self, filepath:Path) -> dict:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def __common(self, config:dict):
        """
        These configuration attributes are going to be common across all
        proponents of the program.
        """
        logger = create_logger("config:common")

        self.campaign = config["campaign"]
        logger.info("Parsing %s campaign configuration file", self.campaign)

        c = config["company"]
        self.company = Company(
            uid=c["uid"]
        )
        logger.debug("Added company with uid: %s", self.company.uid)

        self.departments = {
            d["uid"]: Department(
                uid=d["uid"],
                name=d.get("name"),
                company=self.company,
                head=None,
                email=d.get("email")
            )
            for d in config["departments"]
        }
        logger.debug("Added %d departments", len(self.departments))

        self.employees = {
            e["uid"]: Employee(
                uid=e["uid"],
                name=e["name"],
                username=e["username"] if "username" in e else "",
                department=self.departments[e["department_uid"]] if "department_uid" in e else None,
                email=e.get("email"),
                phone=e.get("phone"),
                reports_to=None
            )
            for e in config["employees"]
        }
        logger.debug("Added %d employees", len(self.employees))

        for dept in config["departments"]:
            if dept.get("head_uid"):
                self.departments[dept["uid"]].head = self.employees[dept["head_uid"]]

        for e in config["employees"]:
            if e.get("reports_to"):
                self.employees[e["uid"]].reports_to = self.employees[e["reports_to"]]

        # support sender as department or employee
        self.sender = resolve_uid(config["sender"], self)
        self.targets = [resolve_uid(uid, self) for uid in config["targets"]]
        self.culture = config["culture"] if "culture" in config else None
        self.tech = config["tech"] if "tech" in config else None
        self.current_events = config["current_events"] if "current_events" in config else None

    def _parse(self, config:dict):
        """
        Classes which inherit this base class will use this function to
        parse out the details they need from the dictionary.
        """
        pass

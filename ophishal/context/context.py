# ophishal/context/context.py
import json
from typing import Dict, List, Optional
from pathlib import Path
from ophishal.context.profile import CompanyProfile, EmployeeProfile, DepartmentProfile

class Context:
    def __init__(self, config:dict=None, filepath:Path=None):
        if filepath is not None and config is not None:
            raise ValueError("Can't have both config and filepath")
        elif filepath is not None:
            config = self.__from_file(filepath)

        self.company = CompanyProfile(**config["company"])

        self.employees = {
            uid: EmployeeProfile(**profile) for uid, profile in config["employees"].items()
        }

        self.departments = {
            uid: DepartmentProfile(**dept) for uid, dept in config["departments"].items()
        }

        self.culture                    = config["culture"]
        self.information_technologies   = config["information_technologies"]
        self.current_events             = config["current_events"]
        self.current_access             = config["current_access"]

    def __from_file(self, filepath:Path) -> dict:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

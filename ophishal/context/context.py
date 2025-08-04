# ophishal/context/context.py

import json
from pathlib import Path

from ophishal.context.profile import CompanyProfile, EmployeeProfile, DepartmentProfile, CultureProfile
from ophishal.common.logging import create_logger
from ophishal.common.config import BaseConfig


class Context(BaseConfig):
    require = {
        "company":dict,
        "employees":dict,
        "departments":dict,
        "culture":dict,
        "information_technologies":list,
        "current_events":list,
        "current_access":list,
        "target_employees":list
    }

    def parse(self, config:dict):

        self.company = CompanyProfile(**config["company"])

        self.employees = {
            uid: EmployeeProfile(**profile) for uid, profile in config["employees"].items()
        }

        self.departments = {
            uid: DepartmentProfile(**dept) for uid, dept in config["departments"].items()
        }

        self.culture                    = CultureProfile(*config["culture"].values())
        self.information_technologies   = config["information_technologies"]
        self.current_events             = config["current_events"]
        self.current_access             = config["current_access"]
        self.target_employees           = config["target_employees"]

# ophishal/common/models.py
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union

@dataclass
class Company:
    uid: str

    def to_dict(self):
        return {"uid":self.uid}

@dataclass
class Department:
    uid: str
    company: "Company"
    name: Optional[str]
    email: Optional[str]
    head: Optional["Employee"]

    def to_dict(self):
        return {
            "uid":self.uid,
            "company":self.company.uid,
            "name":self.name,
            "email":self.email,
            "head":self.head.uid
        }

@dataclass
class Employee:
    uid: str
    name: str
    department: Department
    username: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    reports_to: Optional["Employee"]
    writing_sample: Optional[str]

    def to_dict(self):
        return {
            "uid":self.uid,
            "name":self.name,
            "department":self.department.uid if self.department is not None else None,
            "username":self.username,
            "email":self.email,
            "phone":self.phone,
            "reports_to":self.reports_to.uid if self.reports_to is not None else None,
            "writing_sample":self.writing_sample
        }

Target = Union[Employee, Department, Company]
